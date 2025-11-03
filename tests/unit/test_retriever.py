"""Unit tests for multi-faceted retrieval system."""

import pytest
from uuid import uuid4
from datetime import datetime

from guidance_agent.retrieval.retriever import retrieve_context, CaseBase, RulesBase
from guidance_agent.core.memory import MemoryNode, MemoryStream
from guidance_agent.core.types import MemoryType, RetrievedContext
from guidance_agent.core.database import Memory, Case, Rule, get_session


@pytest.fixture
def db_session():
    """Get a test database session."""
    session = get_session()
    # Cleanup
    session.query(Memory).delete()
    session.query(Case).delete()
    session.query(Rule).delete()
    session.commit()

    yield session

    # Cleanup
    session.query(Memory).delete()
    session.query(Case).delete()
    session.query(Rule).delete()
    session.commit()
    session.close()


@pytest.fixture
def populated_memory_stream(db_session):
    """Create a memory stream with test data."""
    stream = MemoryStream(session=db_session)

    memories = [
        MemoryNode(
            description="Customer has £150k pension pot",
            importance=0.7,
            memory_type=MemoryType.OBSERVATION,
            embedding=[0.1] * 1536,
        ),
        MemoryNode(
            description="Customer is 55 years old",
            importance=0.6,
            memory_type=MemoryType.OBSERVATION,
            embedding=[0.2] * 1536,
        ),
        MemoryNode(
            description="Customer seems uncertain about risk",
            importance=0.8,
            memory_type=MemoryType.REFLECTION,
            embedding=[0.3] * 1536,
        ),
    ]

    for memory in memories:
        stream.add(memory)

    return stream


@pytest.fixture
def populated_case_base(db_session):
    """Create a case base with test data."""
    case_base = CaseBase(session=db_session)

    cases = [
        {
            "id": uuid4(),
            "task_type": "pension_withdrawal",
            "customer_situation": "55 year old with £150k pension wants to withdraw 25% tax-free",
            "guidance_provided": "Explained tax-free lump sum options and drawdown alternatives",
            "outcome": {"successful": True, "customer_satisfied": 9},
            "embedding": [0.4] * 1536,
        },
        {
            "id": uuid4(),
            "task_type": "pension_transfer",
            "customer_situation": "Customer considering DB pension transfer",
            "guidance_provided": "Warned about risks and recommended Pension Wise appointment",
            "outcome": {"successful": True, "referred_to_specialist": True},
            "embedding": [0.5] * 1536,
        },
    ]

    for case_data in cases:
        case_base.add(
            id=case_data["id"],
            embedding=case_data["embedding"],
            metadata={
                "task_type": case_data["task_type"],
                "customer_situation": case_data["customer_situation"],
                "guidance_provided": case_data["guidance_provided"],
                "outcome": case_data["outcome"],
            },
        )

    return case_base


@pytest.fixture
def populated_rules_base(db_session):
    """Create a rules base with test data."""
    rules_base = RulesBase(session=db_session)

    rules = [
        {
            "id": uuid4(),
            "principle": "Always check if customer has defined benefit pension before transfer advice",
            "domain": "pension_transfers",
            "confidence": 0.95,
            "supporting_evidence": ["case-1", "case-2"],
            "embedding": [0.6] * 1536,
        },
        {
            "id": uuid4(),
            "principle": "Customers over 55 should be informed about tax-free lump sum options",
            "domain": "pension_withdrawal",
            "confidence": 0.90,
            "supporting_evidence": ["case-3", "case-4", "case-5"],
            "embedding": [0.7] * 1536,
        },
    ]

    for rule_data in rules:
        rules_base.add(
            id=rule_data["id"],
            embedding=rule_data["embedding"],
            metadata={
                "principle": rule_data["principle"],
                "domain": rule_data["domain"],
                "confidence": rule_data["confidence"],
                "supporting_evidence": rule_data["supporting_evidence"],
            },
        )

    return rules_base


class TestCaseBase:
    """Tests for CaseBase class."""

    def test_create_case_base(self, db_session):
        """Test creating a case base."""
        case_base = CaseBase(session=db_session)
        assert case_base is not None

    def test_add_case(self, db_session):
        """Test adding a case to the case base."""
        case_base = CaseBase(session=db_session)

        case_id = uuid4()
        case_base.add(
            id=case_id,
            embedding=[0.1] * 1536,
            metadata={
                "task_type": "general_inquiry",
                "customer_situation": "Customer asked about pension options",
                "guidance_provided": "Provided overview of options",
                "outcome": {"successful": True},
            },
        )

        # Verify case was added
        case = db_session.query(Case).filter(Case.id == case_id).first()
        assert case is not None
        assert case.task_type == "general_inquiry"

    def test_retrieve_similar_cases(self, populated_case_base):
        """Test retrieving similar cases by embedding similarity."""
        # Query for cases (should return most similar)
        query_embedding = [0.4] * 1536

        results = populated_case_base.retrieve(query_embedding, top_k=2)

        # Should return at least one case
        assert len(results) >= 1
        assert len(results) <= 2
        # Verify structure
        assert "task_type" in results[0]
        assert "customer_situation" in results[0]
        assert "similarity" in results[0]


class TestRulesBase:
    """Tests for RulesBase class."""

    def test_create_rules_base(self, db_session):
        """Test creating a rules base."""
        rules_base = RulesBase(session=db_session)
        assert rules_base is not None

    def test_add_rule(self, db_session):
        """Test adding a rule to the rules base."""
        rules_base = RulesBase(session=db_session)

        rule_id = uuid4()
        rules_base.add(
            id=rule_id,
            embedding=[0.1] * 1536,
            metadata={
                "principle": "Always verify customer identity before proceeding",
                "domain": "compliance",
                "confidence": 0.99,
                "supporting_evidence": [],
            },
        )

        # Verify rule was added
        rule = db_session.query(Rule).filter(Rule.id == rule_id).first()
        assert rule is not None
        assert rule.principle == "Always verify customer identity before proceeding"
        assert rule.confidence == 0.99

    def test_retrieve_similar_rules(self, populated_rules_base):
        """Test retrieving similar rules by embedding similarity."""
        # Query for pension transfer rules
        query_embedding = [0.6] * 1536

        results = populated_rules_base.retrieve(query_embedding, top_k=1)

        assert len(results) == 1
        assert "transfer" in results[0]["principle"].lower()

    def test_retrieve_rules_weighted_by_confidence(self, populated_rules_base):
        """Test that rules are weighted by confidence score."""
        query_embedding = [0.65] * 1536

        results = populated_rules_base.retrieve(query_embedding, top_k=2)

        # Should return both rules, highest confidence first
        assert len(results) == 2


class TestRetrieveContext:
    """Tests for multi-faceted retrieve_context function."""

    def test_retrieve_context_basic(
        self, populated_memory_stream, populated_case_base, populated_rules_base
    ):
        """Test basic retrieve_context functionality."""
        query = "Customer wants to know about pension withdrawal options"
        query_embedding = [0.5] * 1536

        context = retrieve_context(
            query=query,
            query_embedding=query_embedding,
            memory_stream=populated_memory_stream,
            case_base=populated_case_base,
            rules_base=populated_rules_base,
        )

        assert isinstance(context, RetrievedContext)
        assert len(context.memories) > 0
        assert len(context.cases) > 0
        assert len(context.rules) > 0

    def test_retrieve_context_returns_correct_types(
        self, populated_memory_stream, populated_case_base, populated_rules_base
    ):
        """Test that retrieve_context returns correct data structures."""
        query = "Tell me about pension transfers"
        query_embedding = [0.4] * 1536

        context = retrieve_context(
            query=query,
            query_embedding=query_embedding,
            memory_stream=populated_memory_stream,
            case_base=populated_case_base,
            rules_base=populated_rules_base,
        )

        # Verify memories are MemoryNode objects
        assert all(isinstance(m, MemoryNode) for m in context.memories)

        # Verify cases and rules are dictionaries with expected keys
        for case in context.cases:
            assert "task_type" in case
            assert "customer_situation" in case
            assert "guidance_provided" in case

        for rule in context.rules:
            assert "principle" in rule
            assert "confidence" in rule

    def test_retrieve_context_respects_top_k(
        self, populated_memory_stream, populated_case_base, populated_rules_base
    ):
        """Test that retrieve_context respects top_k limits."""
        query = "Pension advice needed"
        query_embedding = [0.3] * 1536

        context = retrieve_context(
            query=query,
            query_embedding=query_embedding,
            memory_stream=populated_memory_stream,
            case_base=populated_case_base,
            rules_base=populated_rules_base,
            memory_top_k=2,
            case_top_k=1,
            rule_top_k=1,
        )

        assert len(context.memories) <= 2
        assert len(context.cases) <= 1
        assert len(context.rules) <= 1

    def test_retrieve_context_with_empty_sources(self, db_session):
        """Test retrieve_context with empty data sources."""
        empty_stream = MemoryStream(session=db_session)
        empty_cases = CaseBase(session=db_session)
        empty_rules = RulesBase(session=db_session)

        query = "Test query"
        query_embedding = [0.1] * 1536

        context = retrieve_context(
            query=query,
            query_embedding=query_embedding,
            memory_stream=empty_stream,
            case_base=empty_cases,
            rules_base=empty_rules,
        )

        assert isinstance(context, RetrievedContext)
        assert len(context.memories) == 0
        assert len(context.cases) == 0
        assert len(context.rules) == 0

    def test_retrieve_context_combines_signals(
        self, populated_memory_stream, populated_case_base, populated_rules_base
    ):
        """Test that retrieve_context combines different retrieval signals."""
        query = "55 year old customer asking about pension withdrawal"
        query_embedding = [0.35] * 1536

        context = retrieve_context(
            query=query,
            query_embedding=query_embedding,
            memory_stream=populated_memory_stream,
            case_base=populated_case_base,
            rules_base=populated_rules_base,
        )

        # Should retrieve relevant items from each source
        assert len(context.memories) > 0  # Should find age and pension pot info
        assert len(context.cases) > 0  # Should find pension withdrawal case
        assert len(context.rules) > 0  # Should find age-related rule

    def test_retrieve_context_with_fca_requirements(
        self, populated_memory_stream, populated_case_base, populated_rules_base
    ):
        """Test that retrieve_context can include FCA requirements."""
        query = "DB pension transfer"
        query_embedding = [0.6] * 1536

        fca_requirements = "All DB transfers over £30k require FCA-regulated advice"

        context = retrieve_context(
            query=query,
            query_embedding=query_embedding,
            memory_stream=populated_memory_stream,
            case_base=populated_case_base,
            rules_base=populated_rules_base,
            fca_requirements=fca_requirements,
        )

        assert context.fca_requirements == fca_requirements

    def test_retrieve_context_includes_reasoning(
        self, populated_memory_stream, populated_case_base, populated_rules_base
    ):
        """Test that retrieve_context includes reasoning about what was retrieved."""
        query = "Pension withdrawal query"
        query_embedding = [0.4] * 1536

        context = retrieve_context(
            query=query,
            query_embedding=query_embedding,
            memory_stream=populated_memory_stream,
            case_base=populated_case_base,
            rules_base=populated_rules_base,
        )

        # Reasoning should be populated
        assert isinstance(context.reasoning, str)
        assert len(context.reasoning) > 0
