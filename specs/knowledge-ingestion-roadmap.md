# Production-Ready Knowledge Ingestion & Curation System

**Status**: Planning Phase
**Priority**: Critical - Production Readiness
**Estimated Effort**: 6 weeks
**Owner**: TBD

---

## Executive Summary

This specification outlines a comprehensive knowledge ingestion and curation system for the pension guidance platform. The goal is to transform from a manually-curated seed knowledge base (~46 entries) to a production-ready system capable of ingesting, deduplicating, versioning, and maintaining 1,000+ knowledge entries from diverse sources including PDFs, websites, and LLM generation.

**Key Requirements**:
- Document ingestion from PDFs and web sources
- Semantic deduplication and quality scoring
- Version control and audit trails
- Automated scraping from authoritative sources (MoneyHelper, FCA Handbook)
- Full CRUD API and admin UI for knowledge management
- Coverage expansion: pensions, fca compliance

---

## Current State Assessment

### Existing Infrastructure (✅ Strengths)

**Vector Database**: PostgreSQL + pgvector with HNSW indexes - production-ready
**Knowledge Models**: FCAKnowledge (16 entries), PensionKnowledge (10 entries)
**Embeddings**: LiteLLM integration with flexible provider support
**Retrieval**: Sophisticated multi-faceted retrieval (cases, rules, memories)
**Compliance Validation**: LLM-as-judge for FCA boundary checking
**Admin API**: Read-only endpoints with filtering and pagination

### Critical Gaps (❌ Blockers)

**No Document Ingestion**: Cannot parse PDFs, scrape websites, or process documents
**No Deduplication**: Risk of accumulating redundant/conflicting knowledge
**No Versioning**: Cannot track changes, rollback, or maintain history
**No CRUD API**: Read-only, all updates require direct database access
**Limited Content**: ~46 total entries, all manually curated
**No Quality Metrics**: No way to measure or track knowledge effectiveness

---

## Phase 1: Foundation - Quality Controls & Infrastructure (Week 1)

### 1.1 Database Schema Enhancements

**Migration**: `alembic/versions/xxx_knowledge_versioning.py`

```sql
-- Add versioning and audit fields
ALTER TABLE fca_knowledge ADD COLUMN version INTEGER DEFAULT 1;
ALTER TABLE fca_knowledge ADD COLUMN updated_at TIMESTAMP;
ALTER TABLE fca_knowledge ADD COLUMN updated_by VARCHAR(255);
ALTER TABLE fca_knowledge ADD COLUMN content_hash VARCHAR(64);
ALTER TABLE fca_knowledge ADD COLUMN valid_from TIMESTAMP DEFAULT NOW();
ALTER TABLE fca_knowledge ADD COLUMN valid_to TIMESTAMP;
ALTER TABLE fca_knowledge ADD COLUMN is_deprecated BOOLEAN DEFAULT FALSE;

-- Add quality scoring fields
ALTER TABLE fca_knowledge ADD COLUMN quality_score FLOAT;
ALTER TABLE fca_knowledge ADD COLUMN confidence_score FLOAT;
ALTER TABLE fca_knowledge ADD COLUMN source_authority INTEGER DEFAULT 5;
ALTER TABLE fca_knowledge ADD COLUMN readability_score FLOAT;

-- Repeat for pension_knowledge table

-- Create audit trail table
CREATE TABLE knowledge_changelog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_type VARCHAR(50) NOT NULL,  -- 'fca' or 'pension'
    knowledge_id UUID NOT NULL,
    version INTEGER NOT NULL,
    change_type VARCHAR(50) NOT NULL,  -- 'create', 'update', 'delete', 'merge'
    old_content TEXT,
    new_content TEXT,
    old_embedding VECTOR(1536),
    new_embedding VECTOR(1536),
    changed_by VARCHAR(255),
    changed_at TIMESTAMP DEFAULT NOW(),
    change_reason TEXT,
    meta JSONB
);

CREATE INDEX idx_changelog_knowledge_id ON knowledge_changelog(knowledge_id);
CREATE INDEX idx_changelog_knowledge_type ON knowledge_changelog(knowledge_type);
CREATE INDEX idx_changelog_changed_at ON knowledge_changelog(changed_at);

-- Create indexes for deduplication
CREATE INDEX idx_fca_content_hash ON fca_knowledge(content_hash);
CREATE INDEX idx_pension_content_hash ON pension_knowledge(content_hash);

-- Materialized view for duplicate detection
CREATE MATERIALIZED VIEW knowledge_duplicates AS
SELECT
    a.id as id1,
    b.id as id2,
    a.content as content1,
    b.content as content2,
    1 - (a.embedding <=> b.embedding) as similarity_score
FROM fca_knowledge a
CROSS JOIN fca_knowledge b
WHERE a.id < b.id
  AND 1 - (a.embedding <=> b.embedding) > 0.90
  AND NOT a.is_deprecated
  AND NOT b.is_deprecated
ORDER BY similarity_score DESC;

CREATE UNIQUE INDEX idx_duplicates_ids ON knowledge_duplicates(id1, id2);
```

**Impact**: Enables version tracking, audit trails, temporal queries, and fast duplicate detection

### 1.2 Deduplication System

**Module**: `src/guidance_agent/quality/deduplication.py`

```python
import hashlib
from typing import List, Dict, Optional, Tuple
from guidance_agent.retrieval.embeddings import embed, cosine_similarity
from guidance_agent.core.database import get_session, FCAKnowledge, PensionKnowledge

class DuplicationDetector:
    """Detect exact and semantic duplicates in knowledge base."""

    def __init__(self, similarity_threshold: float = 0.95):
        self.similarity_threshold = similarity_threshold
        self.session = get_session()

    def compute_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of normalized content."""
        normalized = content.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def check_exact_duplicate(self, content: str, knowledge_type: str) -> Optional[str]:
        """Check for exact duplicate by content hash."""
        content_hash = self.compute_content_hash(content)

        if knowledge_type == 'fca':
            existing = self.session.query(FCAKnowledge).filter(
                FCAKnowledge.content_hash == content_hash,
                FCAKnowledge.is_deprecated == False
            ).first()
        else:
            existing = self.session.query(PensionKnowledge).filter(
                PensionKnowledge.content_hash == content_hash,
                PensionKnowledge.is_deprecated == False
            ).first()

        return existing.id if existing else None

    def check_semantic_duplicate(
        self,
        content: str,
        knowledge_type: str,
        top_k: int = 5
    ) -> List[Tuple[str, float, str]]:
        """Check for semantic duplicates using vector similarity."""
        query_embedding = embed(content)

        if knowledge_type == 'fca':
            model = FCAKnowledge
        else:
            model = PensionKnowledge

        # Use pgvector's cosine distance operator
        similar = self.session.query(
            model.id,
            model.content,
            (1 - model.embedding.cosine_distance(query_embedding)).label('similarity')
        ).filter(
            model.is_deprecated == False
        ).order_by(
            model.embedding.cosine_distance(query_embedding)
        ).limit(top_k).all()

        # Filter by threshold
        duplicates = [
            (str(entry.id), entry.similarity, entry.content)
            for entry in similar
            if entry.similarity >= self.similarity_threshold
        ]

        return duplicates

    def validate_before_insertion(
        self,
        content: str,
        knowledge_type: str
    ) -> Dict[str, any]:
        """Validate content before insertion, return status and duplicates."""

        # Check exact duplicate
        exact_id = self.check_exact_duplicate(content, knowledge_type)
        if exact_id:
            return {
                'is_duplicate': True,
                'duplicate_type': 'exact',
                'duplicate_id': exact_id,
                'should_insert': False,
                'reason': 'Exact content match found'
            }

        # Check semantic duplicates
        semantic_dups = self.check_semantic_duplicate(content, knowledge_type)
        if semantic_dups:
            return {
                'is_duplicate': True,
                'duplicate_type': 'semantic',
                'duplicates': semantic_dups,
                'should_insert': False,
                'reason': f'Found {len(semantic_dups)} similar entries (>= {self.similarity_threshold} similarity)',
                'suggested_action': 'review_and_merge'
            }

        return {
            'is_duplicate': False,
            'should_insert': True,
            'content_hash': self.compute_content_hash(content)
        }
```

**Impact**: Prevents duplicate knowledge insertion, enables merge workflows

### 1.3 Knowledge Quality Framework

**Module**: `src/guidance_agent/quality/scoring.py`

```python
import re
from typing import Dict
from textstat import flesch_kincaid_grade

class QualityScorer:
    """Calculate quality metrics for knowledge entries."""

    def calculate_readability(self, content: str) -> float:
        """Flesch-Kincaid Grade Level (target: 9-12 for UK)."""
        try:
            return flesch_kincaid_grade(content)
        except:
            return 0.0

    def calculate_information_density(self, content: str) -> float:
        """Ratio of unique content words to total words."""
        words = re.findall(r'\b\w+\b', content.lower())
        if not words:
            return 0.0
        unique_words = set(words)
        return len(unique_words) / len(words)

    def calculate_source_authority(self, source: str) -> int:
        """Rate source authority (1-10)."""
        authority_map = {
            'FCA_Handbook': 10,
            'MoneyHelper_Official': 9,
            'FCA_Curated_Principles': 9,
            'Pension_Regulator': 9,
            'Provider_Official': 7,
            'LLM_Generated_Validated': 6,
            'LLM_Generated': 5,
            'User_Submitted': 3,
            'Unknown': 1
        }
        return authority_map.get(source, 5)

    def calculate_overall_quality(self, entry: Dict) -> float:
        """Weighted quality score (0-100)."""
        readability = self.calculate_readability(entry['content'])
        density = self.calculate_information_density(entry['content'])
        authority = self.calculate_source_authority(entry.get('source', 'Unknown'))

        # Scoring logic
        readability_score = max(0, 100 - abs(readability - 10) * 5)  # Ideal: Grade 10
        density_score = density * 100
        authority_score = authority * 10

        # Weighted average
        weights = {'readability': 0.3, 'density': 0.3, 'authority': 0.4}
        overall = (
            readability_score * weights['readability'] +
            density_score * weights['density'] +
            authority_score * weights['authority']
        )

        return round(overall, 2)
```

**Dependency**: Add `textstat>=0.7.3` to `pyproject.toml`

**Impact**: Quantifies knowledge quality, enables filtering and improvement

### 1.4 Embedding Cache

**Module**: `src/guidance_agent/retrieval/embedding_cache.py`

```python
import hashlib
import pickle
from typing import List, Optional
from redis import Redis

class EmbeddingCache:
    """Cache embeddings by content hash to avoid re-computation."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = Redis.from_url(redis_url, decode_responses=False)
        self.ttl = 86400 * 30  # 30 days

    def _hash_content(self, content: str) -> str:
        """Generate cache key from content."""
        return f"embedding:{hashlib.sha256(content.encode()).hexdigest()}"

    def get(self, content: str) -> Optional[List[float]]:
        """Retrieve cached embedding."""
        key = self._hash_content(content)
        cached = self.redis.get(key)
        if cached:
            return pickle.loads(cached)
        return None

    def set(self, content: str, embedding: List[float]) -> None:
        """Cache embedding."""
        key = self._hash_content(content)
        self.redis.setex(key, self.ttl, pickle.dumps(embedding))

    def batch_get(self, contents: List[str]) -> Dict[str, Optional[List[float]]]:
        """Batch retrieve embeddings."""
        keys = [self._hash_content(c) for c in contents]
        cached = self.redis.mget(keys)
        return {
            content: pickle.loads(emb) if emb else None
            for content, emb in zip(contents, cached)
        }
```

**Optional**: Requires Redis. Alternative: use SQLite cache or in-memory LRU cache

**Impact**: 10x faster re-ingestion, reduces embedding API costs

---

## Phase 2: Document Ingestion Pipeline (Week 2)

### 2.1 Core Dependencies

**Update** `pyproject.toml`:

```toml
dependencies = [
    # ... existing dependencies ...

    # Document parsing
    "pypdf>=4.0.0",
    "beautifulsoup4>=4.12.0",
    "lxml>=5.0.0",
    "markdownify>=0.11.0",
    "python-magic>=0.4.27",

    # Quality scoring
    "textstat>=0.7.3",

    # Optional: caching
    "redis>=5.0.0",
]
```

### 2.2 PDF Parser

**Module**: `src/guidance_agent/ingestion/pdf_parser.py`

```python
from pathlib import Path
from typing import List, Dict, Optional
import pypdf
from .chunking import SemanticChunker

class PDFParser:
    """Extract and chunk text from PDF documents."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunker = SemanticChunker(chunk_size, chunk_overlap)

    def extract_text(self, pdf_path: Path) -> str:
        """Extract all text from PDF."""
        reader = pypdf.PdfReader(pdf_path)
        text_parts = []

        for page in reader.pages:
            text_parts.append(page.extract_text())

        return "\n\n".join(text_parts)

    def extract_metadata(self, pdf_path: Path) -> Dict:
        """Extract PDF metadata."""
        reader = pypdf.PdfReader(pdf_path)
        meta = reader.metadata

        return {
            'title': meta.get('/Title', ''),
            'author': meta.get('/Author', ''),
            'subject': meta.get('/Subject', ''),
            'creator': meta.get('/Creator', ''),
            'producer': meta.get('/Producer', ''),
            'creation_date': meta.get('/CreationDate', ''),
            'modification_date': meta.get('/ModDate', ''),
            'pages': len(reader.pages)
        }

    def parse_and_chunk(
        self,
        pdf_path: Path,
        source_name: Optional[str] = None
    ) -> List[Dict]:
        """Parse PDF and return chunked entries with metadata."""
        text = self.extract_text(pdf_path)
        metadata = self.extract_metadata(pdf_path)

        chunks = self.chunker.chunk(text)

        entries = []
        for i, chunk in enumerate(chunks):
            entry = {
                'content': chunk,
                'source': source_name or pdf_path.name,
                'source_type': 'pdf',
                'metadata': {
                    **metadata,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'file_path': str(pdf_path)
                }
            }
            entries.append(entry)

        return entries
```

### 2.3 Semantic Chunking

**Module**: `src/guidance_agent/ingestion/chunking.py`

```python
import re
from typing import List

class SemanticChunker:
    """Chunk text at semantic boundaries (sentences, paragraphs)."""

    def __init__(self, max_chunk_size: int = 1000, overlap: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter (can be improved with spaCy/NLTK)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk(self, text: str) -> List[str]:
        """Chunk text at sentence boundaries with overlap."""
        sentences = self.split_into_sentences(text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length > self.max_chunk_size and current_chunk:
                # Finalize current chunk
                chunks.append(' '.join(current_chunk))

                # Start new chunk with overlap
                overlap_text = ' '.join(current_chunk)
                if len(overlap_text) > self.overlap:
                    # Trim to overlap size
                    overlap_sentences = []
                    overlap_length = 0
                    for s in reversed(current_chunk):
                        if overlap_length + len(s) <= self.overlap:
                            overlap_sentences.insert(0, s)
                            overlap_length += len(s)
                        else:
                            break
                    current_chunk = overlap_sentences
                    current_length = overlap_length
                else:
                    current_chunk = []
                    current_length = 0

            current_chunk.append(sentence)
            current_length += sentence_length

        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks
```

### 2.4 Web Scraper

**Module**: `src/guidance_agent/ingestion/web_scraper.py`

```python
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from typing import Dict, Optional
from urllib.parse import urlparse
import time

class WebScraper:
    """Scrape and parse web pages."""

    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit  # seconds between requests
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PensionGuidanceBot/1.0 (Educational Research)'
        })

    def _rate_limit_wait(self):
        """Respect rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def fetch(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch HTML content from URL."""
        self._rate_limit_wait()

        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html: str, clean: bool = True) -> Dict:
        """Parse HTML and extract structured content."""
        soup = BeautifulSoup(html, 'lxml')

        # Remove script and style elements
        if clean:
            for element in soup(['script', 'style', 'nav', 'footer', 'aside']):
                element.decompose()

        # Extract title
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else ''

        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('body')

        if main_content:
            # Convert to markdown for better structure
            markdown = markdownify(str(main_content), heading_style="ATX")
            text = main_content.get_text(separator='\n', strip=True)
        else:
            markdown = ''
            text = soup.get_text(separator='\n', strip=True)

        return {
            'title': title_text,
            'text': text,
            'markdown': markdown,
            'html': str(main_content) if main_content else html
        }

    def scrape_url(self, url: str) -> Optional[Dict]:
        """Scrape URL and return parsed content with metadata."""
        html = self.fetch(url)
        if not html:
            return None

        content = self.parse_html(html)
        parsed_url = urlparse(url)

        return {
            'content': content['text'],
            'markdown': content['markdown'],
            'title': content['title'],
            'source': url,
            'source_type': 'web',
            'metadata': {
                'url': url,
                'domain': parsed_url.netloc,
                'path': parsed_url.path,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
```

### 2.5 Ingestion Pipeline

**Module**: `src/guidance_agent/ingestion/pipeline.py`

```python
from pathlib import Path
from typing import List, Dict, Union, Optional
from .pdf_parser import PDFParser
from .web_scraper import WebScraper
from .chunking import SemanticChunker
from guidance_agent.quality.deduplication import DuplicationDetector
from guidance_agent.quality.scoring import QualityScorer
from guidance_agent.retrieval.embeddings import embed
from guidance_agent.core.database import get_session, FCAKnowledge, PensionKnowledge
import hashlib
from uuid import uuid4

class IngestionPipeline:
    """Orchestrate document ingestion with validation and quality checks."""

    def __init__(
        self,
        knowledge_type: str,  # 'fca' or 'pension'
        validate_duplicates: bool = True,
        min_quality_score: float = 50.0
    ):
        self.knowledge_type = knowledge_type
        self.pdf_parser = PDFParser()
        self.web_scraper = WebScraper()
        self.dedup_detector = DuplicationDetector() if validate_duplicates else None
        self.quality_scorer = QualityScorer()
        self.min_quality_score = min_quality_score
        self.session = get_session()

    def ingest_pdf(self, pdf_path: Path, category: str, **kwargs) -> Dict:
        """Ingest PDF document."""
        entries = self.pdf_parser.parse_and_chunk(pdf_path)
        return self._process_entries(entries, category, **kwargs)

    def ingest_url(self, url: str, category: str, **kwargs) -> Dict:
        """Ingest web page."""
        scraped = self.web_scraper.scrape_url(url)
        if not scraped:
            return {'success': False, 'error': 'Failed to scrape URL'}

        # Chunk if needed
        if len(scraped['content']) > 1000:
            chunker = SemanticChunker()
            chunks = chunker.chunk(scraped['content'])
            entries = [
                {**scraped, 'content': chunk}
                for chunk in chunks
            ]
        else:
            entries = [scraped]

        return self._process_entries(entries, category, **kwargs)

    def _process_entries(
        self,
        entries: List[Dict],
        category: str,
        subcategory: Optional[str] = None,
        source_override: Optional[str] = None
    ) -> Dict:
        """Process and insert entries with validation."""
        results = {
            'total': len(entries),
            'inserted': 0,
            'skipped_duplicate': 0,
            'skipped_quality': 0,
            'errors': []
        }

        for entry in entries:
            try:
                content = entry['content']

                # Duplicate check
                if self.dedup_detector:
                    dup_result = self.dedup_detector.validate_before_insertion(
                        content, self.knowledge_type
                    )
                    if not dup_result['should_insert']:
                        results['skipped_duplicate'] += 1
                        continue

                    content_hash = dup_result.get('content_hash')
                else:
                    content_hash = hashlib.sha256(content.encode()).hexdigest()

                # Quality check
                quality_score = self.quality_scorer.calculate_overall_quality({
                    'content': content,
                    'source': source_override or entry.get('source', 'Unknown')
                })

                if quality_score < self.min_quality_score:
                    results['skipped_quality'] += 1
                    continue

                # Generate embedding
                embedding = embed(content)

                # Create knowledge entry
                if self.knowledge_type == 'fca':
                    knowledge_entry = FCAKnowledge(
                        id=uuid4(),
                        content=content,
                        source=source_override or entry.get('source', 'Unknown'),
                        category=category,
                        embedding=embedding,
                        content_hash=content_hash,
                        quality_score=quality_score,
                        source_authority=self.quality_scorer.calculate_source_authority(
                            entry.get('source', 'Unknown')
                        ),
                        meta=entry.get('metadata', {})
                    )
                else:
                    knowledge_entry = PensionKnowledge(
                        id=uuid4(),
                        content=content,
                        category=category,
                        subcategory=subcategory,
                        embedding=embedding,
                        content_hash=content_hash,
                        quality_score=quality_score,
                        meta=entry.get('metadata', {})
                    )

                self.session.add(knowledge_entry)
                results['inserted'] += 1

            except Exception as e:
                results['errors'].append(str(e))

        # Commit all entries
        try:
            self.session.commit()
            results['success'] = True
        except Exception as e:
            self.session.rollback()
            results['success'] = False
            results['errors'].append(f"Commit failed: {e}")

        return results
```

**Impact**: Complete document ingestion infrastructure for PDFs and web pages

---

## Phase 3: Expanded Knowledge Base (Week 3)

### 3.1 Comprehensive FCA Compliance YAML

**Create**: `data/knowledge/fca_compliance_principles.yaml`

Structure (~100 entries):

```yaml
guidance_vs_advice_boundary:
  - principle: "Never provide personal recommendations"
    content: "Guidance must help customers understand options without telling them what to do"
    fca_reference: "PERG 8.28"
    mandatory: true
    examples_compliant:
      - "You could consider consolidating your pensions, or you might prefer to keep them separate"
      - "Some people in your situation choose to transfer, while others decide to stay put"
    examples_non_compliant:
      - "You should transfer your pension"
      - "I recommend consolidation"
      - "The best option for you is..."

  - principle: "Avoid directive language"
    content: "Never use 'should', 'must', 'recommend', 'advise' when discussing options"
    fca_reference: "PERG 8.29"
    mandatory: true
    prohibited_phrases:
      - "you should"
      - "you must"
      - "I recommend"
      - "I advise"
      - "best for you"
      - "you need to"

  # ... 18 more guidance boundary rules

db_pension_safeguards:
  - principle: "DB transfer warning for pensions >£30k"
    content: "When customer has DB pension worth >£30,000, must provide warning about valuable guarantees and requirement for regulated advice"
    fca_reference: "COBS 19.1"
    mandatory: true
    required_elements:
      - "defined benefit"
      - "guaranteed income"
      - "£30,000"
      - "regulated financial advice"
      - "requirement"
    template: |
      I notice you have a defined benefit pension. These pensions provide valuable
      guarantees including guaranteed income for life. If the transfer value is over
      £30,000, you're legally required to get regulated financial advice before
      transferring. Most people are worse off by transferring from DB to DC pensions.

  # ... 14 more DB-specific rules

risk_disclosure:
  - principle: "Match communication to literacy level"
    content: "Adjust language complexity based on customer's financial literacy"
    fca_reference: "COBS 4.2"
    mandatory: true
    literacy_levels:
      low:
        - "Use everyday language, avoid jargon"
        - "Use analogies (pension pot = piggy bank)"
        - "Break into small chunks"
      medium:
        - "Can use some financial terms with brief explanations"
        - "More detailed options discussion"
      high:
        - "Can use technical terminology"
        - "Discuss nuances and edge cases"

  # ... 9 more risk disclosure rules

# Total: ~100 principles across 10 categories
```

**Script**: Update `scripts/bootstrap_fca_knowledge.py` to handle all categories

### 3.2 Expanded Pension Knowledge Module

**Update**: `src/guidance_agent/knowledge/pension_knowledge.py` (current: 189 lines → target: ~800 lines)

Add sections:

```python
PENSION_KNOWLEDGE = {
    # ... existing sections ...

    "pension_types_extended": {
        "sipp": {
            "description": "Self-Invested Personal Pension allowing wider investment choice",
            "typical_providers": ["Hargreaves Lansdown", "AJ Bell", "Interactive Investor"],
            "min_contribution": 0,
            "typical_fees": {"platform": 0.0045, "dealing": 9.95},
            "investment_options": ["stocks", "funds", "etfs", "bonds", "investment_trusts"],
            "complexity": "high",
            "suitable_for": "experienced_investors"
        },
        "stakeholder_pension": {
            "description": "Low-cost pension with capped charges, simple investment",
            "charge_cap": 0.015,  # 1.5%
            "minimum_contribution": 20,
            "default_investment": "lifecycle_fund",
            "suitable_for": "low_earners"
        },
        "group_personal_pension": {
            "description": "Employer-arranged personal pension for employees",
            "typical_providers": ["Aviva", "Legal & General", "Scottish Widows"],
            "employer_contribution_typical": 0.05,
            "employee_contribution_typical": 0.05
        },
        "annuity": {
            "description": "Insurance product converting pension pot to guaranteed income",
            "types": ["single_life", "joint_life", "enhanced", "fixed_term"],
            "typical_rates": {"age_65": 0.05, "age_70": 0.06, "age_75": 0.07},
            "irreversible": True,
            "fca_warning": "Once purchased, cannot be changed or sold"
        }
    },

    "transfer_regulations": {
        "cetv": {
            "name": "Cash Equivalent Transfer Value",
            "validity": "3_months",
            "guaranteed_period": "3_months_from_quote",
            "calculation": "actuarial_value_of_benefits",
            "typical_multiple_of_income": {"min": 20, "max": 40}
        },
        "tvas": {
            "name": "Transfer Value Analysis System",
            "required_for": "DB to DC transfers >£30k",
            "compares": "cetv_vs_projected_dc_benefits",
            "discount_rates": ["low", "medium", "high"],
            "must_show": "critical_yield"
        },
        "transfer_timeline": {
            "cetv_quote_request": "10_business_days",
            "transfer_initiation": "within_6_months_of_quote",
            "completion": "6_weeks_from_instruction"
        }
    },

    "tax_rules": {
        "lifetime_allowance_abolished": {
            "abolished_date": "2024-04-06",
            "historical_lta": 1073100,  # Last LTA before abolition
            "replacement": "lump_sum_allowances"
        },
        "annual_allowance": {
            "standard": 60000,
            "tapered_threshold_income": 260000,
            "tapered_adjusted_income": 360000,
            "minimum_tapered": 10000,
            "carry_forward_years": 3
        },
        "money_purchase_annual_allowance": {
            "amount": 10000,
            "triggered_by": ["flexi_access_drawdown", "ufpls"],
            "not_triggered_by": ["small_pots", "25pc_pcls"]
        },
        "pension_commencement_lump_sum": {
            "standard_pcls": 0.25,  # 25% tax-free
            "maximum_total": 268275,  # From April 2024
            "protected_amounts": "varies_by_individual"
        }
    },

    "drawdown_options": {
        "flexi_access_drawdown": {
            "description": "Take flexible withdrawals from pension pot",
            "tax_free_cash": 0.25,
            "taxable_income": "remaining_75pc",
            "triggers_mpaa": True,
            "death_benefits": "beneficiary_choice"
        },
        "ufpls": {
            "name": "Uncrystallised Funds Pension Lump Sum",
            "description": "Take whole pension pot as lump sums",
            "tax_treatment": "25pc_tax_free_75pc_taxable_per_payment",
            "triggers_mpaa": True
        },
        "phased_retirement": {
            "description": "Crystallise pension in stages",
            "advantage": "spread_tax_liability",
            "25pc_rule": "applies_to_each_crystallisation"
        }
    },

    "provider_database": {
        "nest": {
            "type": "master_trust",
            "annual_charge": 0.003,
            "contribution_charge": 0.018,
            "default_fund": "NEST Retirement Date Funds",
            "pension_wise_integrated": True
        },
        "aviva": {
            "type": "insurance_company",
            "charges": {"workplace": 0.005, "personal": 0.01},
            "fund_range": "extensive",
            "drawdown_available": True
        },
        # ... 28 more providers
    },

    "regulatory_timeline": {
        "a_day_2006": {
            "date": "2006-04-06",
            "changes": ["introduced_lta", "simplified_regime", "removed_earnings_cap"]
        },
        "auto_enrollment_2012": {
            "date": "2012-10-01",
            "changes": ["workplace_pension_duties", "nest_launched"]
        },
        "pension_freedoms_2015": {
            "date": "2015-04-06",
            "changes": ["removed_annuity_requirement", "flexi_access_introduced", "pension_wise_launched"]
        },
        "lta_abolished_2024": {
            "date": "2024-04-06",
            "changes": ["lta_removed", "lump_sum_allowances_introduced", "lsdba_introduced"]
        }
    }
}

# Total: ~150 structured entries
```

### 3.4 Enhanced LLM Generation

**Update**: `scripts/generate_seed_cases.py`

- Increase to 100 cases (10 scenario types × 10 variations)
- Add new scenarios: Retirement planning, inheritance, divorce, redundancy
- Improve compliance validation prompts

**Update**: `scripts/generate_seed_rules.py`

- Increase to 100 rules
- Add product-specific rules (SIPP, annuities, transfers, drawdown)
- Add company policy templates

---

## Phase 4: Automated Web Scraping (Week 4)

### 4.1 MoneyHelper Scraper

**Script**: `scripts/scrapers/moneyhelper_scraper.py`

```python
from guidance_agent.ingestion.web_scraper import WebScraper
from guidance_agent.ingestion.pipeline import IngestionPipeline
import time

class MoneyHelperScraper:
    """Scrape pension guidance from MoneyHelper."""

    BASE_URL = "https://www.moneyhelper.org.uk"
    PENSION_SECTIONS = [
        "/en/pensions-and-retirement/building-your-retirement-pot",
        "/en/pensions-and-retirement/taking-your-pension",
        "/en/pensions-and-retirement/pension-wise",
        "/en/pensions-and-retirement/state-pension"
    ]

    def __init__(self):
        self.scraper = WebScraper(rate_limit=2.0)  # 2 seconds between requests
        self.pipeline = IngestionPipeline('pension')

    def discover_urls(self, section_url: str) -> List[str]:
        """Discover all article URLs in a section."""
        full_url = f"{self.BASE_URL}{section_url}"
        scraped = self.scraper.scrape_url(full_url)

        # Extract links (simplified - would use BeautifulSoup in practice)
        # Return list of article URLs
        pass

    def scrape_all(self):
        """Scrape all MoneyHelper pension content."""
        all_urls = []
        for section in self.PENSION_SECTIONS:
            urls = self.discover_urls(section)
            all_urls.extend(urls)

        print(f"Found {len(all_urls)} articles to scrape")

        for url in all_urls:
            print(f"Scraping: {url}")
            result = self.pipeline.ingest_url(
                url,
                category="moneyhelper_guidance",
                source_override="MoneyHelper_Official"
            )
            print(f"  Inserted: {result['inserted']}, Skipped: {result['skipped_duplicate']}")
            time.sleep(2)  # Rate limiting

# Schedule: Weekly via cron
# 0 2 * * 0 cd /app && uv run python scripts/scrapers/moneyhelper_scraper.py
```

### 4.2 FCA Handbook Parser

**Script**: `scripts/scrapers/fca_handbook_parser.py`

Target: Parse COBS 19 from https://www.handbook.fca.org.uk/handbook/COBS/19/

### 4.3 Celery Task Infrastructure

**Install**: `celery>=5.3.0`, `flower>=2.0.0` for monitoring

**Create**: `src/guidance_agent/tasks/scrapers.py`

```python
from celery import Celery
from scripts.scrapers.moneyhelper_scraper import MoneyHelperScraper

app = Celery('guidance_agent', broker='redis://localhost:6379/0')

@app.task
def scrape_moneyhelper():
    """Celery task for MoneyHelper scraping."""
    scraper = MoneyHelperScraper()
    return scraper.scrape_all()

# Schedule in celerybeat
app.conf.beat_schedule = {
    'scrape-moneyhelper-weekly': {
        'task': 'guidance_agent.tasks.scrapers.scrape_moneyhelper',
        'schedule': 604800.0,  # Weekly (seconds)
    }
}
```

---

## Phase 5: Knowledge Management API & UI (Week 5)

### 5.1 Full CRUD API

**Create**: `src/guidance_agent/api/routers/knowledge_management.py`

```python
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from guidance_agent.core.database import get_session, FCAKnowledge
from guidance_agent.quality.deduplication import DuplicationDetector
from guidance_agent.ingestion.pipeline import IngestionPipeline
from uuid import UUID

router = APIRouter(prefix="/admin/knowledge", tags=["Knowledge Management"])

class KnowledgeCreate(BaseModel):
    content: str
    source: str
    category: str
    meta: Optional[dict] = {}

class KnowledgeUpdate(BaseModel):
    content: Optional[str] = None
    category: Optional[str] = None
    meta: Optional[dict] = None

@router.post("/fca")
def create_fca_knowledge(data: KnowledgeCreate):
    """Create new FCA knowledge entry with validation."""
    dedup = DuplicationDetector()

    # Check duplicates
    dup_result = dedup.validate_before_insertion(data.content, 'fca')
    if not dup_result['should_insert']:
        raise HTTPException(400, detail=dup_result)

    # Use pipeline for insertion
    pipeline = IngestionPipeline('fca')
    result = pipeline._process_entries(
        [{'content': data.content, 'source': data.source}],
        category=data.category
    )

    if not result['success']:
        raise HTTPException(500, detail=result['errors'])

    return {"success": True, "inserted": result['inserted']}

@router.put("/fca/{knowledge_id}")
def update_fca_knowledge(knowledge_id: UUID, data: KnowledgeUpdate):
    """Update FCA knowledge with versioning."""
    session = get_session()
    entry = session.query(FCAKnowledge).filter(FCAKnowledge.id == knowledge_id).first()

    if not entry:
        raise HTTPException(404, detail="Knowledge entry not found")

    # Create changelog entry
    from guidance_agent.core.database import KnowledgeChangelog
    changelog = KnowledgeChangelog(
        knowledge_type='fca',
        knowledge_id=knowledge_id,
        version=entry.version,
        change_type='update',
        old_content=entry.content,
        new_content=data.content if data.content else entry.content,
        changed_by='admin',
        change_reason='Manual update via API'
    )
    session.add(changelog)

    # Update entry
    if data.content:
        entry.content = data.content
        entry.version += 1
    if data.category:
        entry.category = data.category
    if data.meta:
        entry.meta = {**entry.meta, **data.meta}

    session.commit()
    return {"success": True, "new_version": entry.version}

@router.delete("/fca/{knowledge_id}")
def delete_fca_knowledge(knowledge_id: UUID):
    """Soft delete (deprecate) FCA knowledge entry."""
    session = get_session()
    entry = session.query(FCAKnowledge).filter(FCAKnowledge.id == knowledge_id).first()

    if not entry:
        raise HTTPException(404, detail="Knowledge entry not found")

    entry.is_deprecated = True
    session.commit()

    return {"success": True, "message": "Knowledge entry deprecated"}

@router.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...), category: str = "uploaded"):
    """Upload and process PDF document."""
    from pathlib import Path
    import tempfile

    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    # Ingest via pipeline
    pipeline = IngestionPipeline('pension')  # or determine from form
    result = pipeline.ingest_pdf(tmp_path, category)

    # Cleanup
    tmp_path.unlink()

    return result

@router.get("/duplicates")
def find_duplicates(threshold: float = 0.95, limit: int = 50):
    """Find near-duplicate knowledge entries."""
    session = get_session()

    # Use materialized view
    from sqlalchemy import text
    query = text("""
        SELECT * FROM knowledge_duplicates
        WHERE similarity_score >= :threshold
        LIMIT :limit
    """)

    results = session.execute(query, {"threshold": threshold, "limit": limit})
    return [dict(row) for row in results]
```

### 5.2 Frontend Admin UI

**Create**: `frontend/app/pages/admin/knowledge/upload.vue`

Features:
- Drag-and-drop file upload (PDF, CSV, JSON)
- URL input for web scraping
- Bulk import with CSV template
- Progress tracking for long operations
- Validation preview before commit

**Create**: `frontend/app/pages/admin/knowledge/duplicates.vue`

Features:
- Side-by-side comparison of near-duplicates
- Merge or keep separate actions
- Similarity score visualization
- Batch operations

**Create**: `frontend/app/pages/admin/knowledge/editor.vue`

Features:
- Rich text editor with markdown support
- Metadata form (source, category, confidence)
- Live duplicate detection as you type
- Preview rendering

---

## Phase 6: Testing & Documentation (Week 6)

### 6.1 Knowledge Testing Framework

**Create**: `tests/knowledge/test_retrieval_accuracy.py`

```python
import pytest
from guidance_agent.retrieval.retriever import CaseBase, RulesBase

class TestRetrievalAccuracy:
    """Test retrieval accuracy with ground truth queries."""

    GROUND_TRUTH = [
        {
            "query": "Can I transfer my NHS pension?",
            "expected_categories": ["db_pension_safeguards"],
            "expected_keywords": ["defined benefit", "£30,000", "regulated advice"]
        },
        # ... 50 more test cases
    ]

    def test_case_retrieval_accuracy(self):
        """Test case retrieval returns relevant results."""
        case_base = CaseBase()

        for test in self.GROUND_TRUTH:
            results = case_base.retrieve(test["query"], top_k=5)

            # Check at least one result matches expected category
            categories = [r.category for r in results]
            assert any(cat in test["expected_categories"] for cat in categories)

            # Check expected keywords appear in results
            all_content = " ".join([r.content for r in results])
            for keyword in test["expected_keywords"]:
                assert keyword.lower() in all_content.lower()
```

### 6.2 Quality Monitoring Dashboard

**Create**: `frontend/app/pages/admin/knowledge/dashboard.vue`

Metrics:
- Total knowledge entries by category
- Coverage gaps (categories with <10 entries)
- Average quality score by source
- Retrieval effectiveness (precision/recall from tests)
- Source freshness (days since last update)
- Duplicate detection stats

### 6.3 Documentation

**Create**: `docs/knowledge-ingestion-guide.md`
**Create**: `docs/knowledge-curator-handbook.md`
**Create**: `docs/api-knowledge-management.md`

---

## Success Metrics

### Knowledge Scale (Week 3 Target)
- [x] 100+ FCA compliance principles
- [x] 150+ pension domain knowledge entries
- [x] 100+ seed cases
- [x] 30+ seed rules
- [x] 50+ investment knowledge entries
- [x] 30+ insurance knowledge entries
- [x] 200+ MoneyHelper scraped articles
- **Total: 1,000+ entries**

### Quality Metrics
- [ ] 0% exact duplicates
- [ ] <1% semantic duplicates (>95% similarity)
- [ ] 100% FCA compliance validation pass rate
- [ ] Average readability score: 60-70 (UK Grade 9-10)
- [ ] Average quality score: >75/100
- [ ] Source authority: 80%+ from high-authority sources (8+/10)

### Performance Metrics
- [ ] Vector search: <100ms for top-10 results
- [ ] Duplicate detection: <500ms per entry
- [ ] Bulk import: 1,000 entries/minute
- [ ] Embedding cache hit rate: >80%
- [ ] Web scraping success rate: >95%

### Automation Metrics
- [ ] MoneyHelper: Weekly updates, 200+ pages
- [ ] FCA Handbook: Monthly sync
- [ ] Provider docs: Quarterly refresh
- [ ] Successful ingestion rate: >95%
- [ ] Change detection accuracy: >90%

---

## Implementation Timeline

| Week | Phase | Deliverables | Dependencies |
|------|-------|--------------|--------------|
| 1 | Foundation | Database schema, deduplication, quality scoring, embedding cache | None |
| 2 | Ingestion | PDF parser, web scraper, chunking, pipeline orchestrator | Week 1 |
| 3 | Content | 100+ FCA YAML, 150+ pension knowledge, investment/insurance modules, LLM generation (100 cases, 30 rules) | Week 2 |
| 4 | Automation | MoneyHelper scraper, FCA parser, provider scrapers, Celery scheduling | Week 2-3 |
| 5 | Management | Full CRUD API, upload endpoints, frontend UI (upload, duplicates, editor) | Week 1-4 |
| 6 | Quality | Testing framework, monitoring dashboard, documentation | Week 1-5 |

**Total**: 6 weeks, 1 full-time engineer

---

## Risk Mitigation

### Technical Risks

**Risk**: Web scraping blocked by rate limiting or anti-bot measures
**Mitigation**: Implement exponential backoff, respect robots.txt, add user agent, consider using Playwright for JS-heavy sites

**Risk**: Embedding API costs become high at scale
**Mitigation**: Implement embedding cache (Week 1), batch processing, consider self-hosted embedding models

**Risk**: Duplicate detection too slow at 1,000+ entries
**Mitigation**: Use materialized views, HNSW vector index (already implemented), consider approximate methods

### Data Quality Risks

**Risk**: Scraped content has poor quality or is incomplete
**Mitigation**: Quality scoring with minimum thresholds, manual review queue for low-quality entries

**Risk**: Knowledge becomes outdated
**Mitigation**: Source freshness tracking, automated re-scraping schedules, validity date ranges

**Risk**: Conflicting information from different sources
**Mitigation**: Source authority weighting, conflict detection, human review for contradictions

### Operational Risks

**Risk**: Scraping failures go unnoticed
**Mitigation**: Error monitoring, Slack/email alerts, Celery flower dashboard

**Risk**: Database performance degrades at scale
**Mitigation**: Regular VACUUM, index monitoring, partitioning by date if needed

---

## Future Enhancements (Beyond Week 6)

1. **Hybrid Search**: Combine vector similarity with BM25 keyword search
2. **Knowledge Graph**: Build entity relationships (providers → products → rules)
3. **Multi-lingual Support**: Translate knowledge for Welsh, Scottish Gaelic
4. **User Feedback Loop**: Track which knowledge entries are most useful, A/B test retrieval strategies
5. **Automated Fact-Checking**: Cross-reference knowledge against authoritative sources
6. **Knowledge Expiry**: Automatic flagging of time-sensitive information that may be outdated
7. **Regulatory Change Detection**: Alert system for FCA handbook updates
8. **Provider Product Database**: Scrape and maintain database of all UK pension products with features and fees

---

## Conclusion

This 6-week implementation plan transforms the knowledge ingestion system from a manually-curated seed (46 entries) to a production-ready platform capable of maintaining 1,000+ high-quality, deduplicated, versioned knowledge entries from diverse sources. The system balances automation (web scraping, LLM generation) with quality controls (deduplication, compliance validation, quality scoring) to ensure the knowledge base remains accurate, comprehensive, and FCA-compliant.

**Next Steps**:
1. Review and approve this specification
2. Allocate engineering resources (1 FTE for 6 weeks or 2 part-time)
3. Create epics and stories in project management tool
4. Begin Week 1: Database schema changes and deduplication system
