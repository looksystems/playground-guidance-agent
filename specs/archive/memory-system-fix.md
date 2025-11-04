# Memory System Fix: Root Cause Analysis and Implementation Plan

**Date:** 2025-11-04
**Status:** Investigation Complete - Ready for Implementation
**Priority:** CRITICAL

## Executive Summary

The memory system in guidance-agent is currently non-functional. Memories are created in-memory only and never persisted to the database. This document provides a comprehensive root cause analysis and step-by-step implementation plan to fix the issue.

---

## Root Cause Analysis

### Critical Finding: No Database Persistence

The `AdvisorAgent`'s `MemoryStream` is **NEVER connected to the database**. All memories exist only in RAM for the duration of a single API request and are garbage collected when the request completes.

### Key Problems Identified

#### 1. MemoryStream Initialized Without Database Session

**Location:** `src/guidance_agent/advisor/agent.py:74`

```python
# Current (BROKEN)
self.memory_stream = MemoryStream()

# The MemoryStream constructor accepts an optional session parameter
# but it's never passed, so self.session is None
```

**Impact:** Without a session, the `_persist_memory()` method is never called (`src/guidance_agent/core/memory.py:107-118`):

```python
def add(self, memory: MemoryNode) -> None:
    """Add a memory to the stream and optionally persist to database."""
    self.memories.append(memory)

    # Persist to database if session is available
    if self.session:  # <-- ALWAYS False in production!
        self._persist_memory(memory)
```

#### 2. Request-Scoped Agent Lifecycle

**Location:** `src/guidance_agent/api/dependencies.py:121-140`

```python
def get_advisor_agent(
    profile: AdvisorProfile = Depends(get_advisor_profile),
) -> AdvisorAgent:
    """Get advisor agent instance.

    Note:
        Creates a new agent instance per request.  # <-- PROBLEM!
    """
    return AdvisorAgent(
        profile=profile,
        use_chain_of_thought=True,
        enable_prompt_caching=True,
    )
```

**Impact:**
- New `AdvisorAgent` created for EVERY API request
- Each agent has isolated in-memory `MemoryStream`
- No database session passed
- Memories lost when request completes

#### 3. No Memory Creation During Consultations

**Location:** `src/guidance_agent/api/routers/consultations.py:214-361`

**Current State:**
- Customer messages are stored to database (line 214-228)
- Consultation messages table is updated
- **BUT:** No `MemoryNode` objects are created
- No observations extracted from conversation
- No memories persisted to `memories` table

**Problem:** The consultation endpoint has no integration with the memory system.

#### 4. Architecture Mismatch

**Location:** `src/guidance_agent/advisor/agent.py:38`

```python
class AdvisorAgent:  # <-- No inheritance from BaseAgent
```

**Location:** `src/guidance_agent/core/agent.py:48-69`

```python
class BaseAgent(ABC):
    def perceive(self, observation: str, importance: Optional[float] = None) -> MemoryNode:
        """Perceive and store an observation."""
        # This method creates MemoryNode and adds to stream
        # BUT AdvisorAgent doesn't inherit from BaseAgent!
```

**Impact:** `AdvisorAgent` doesn't have access to the `perceive()` method that would create memories from observations.

---

## Data Flow Analysis

### Current Flow (Broken)

```
1. Consultation Request → /api/consultations/{id}/stream
2. Create AdvisorAgent (new instance, no DB session)
   ↓
3. Generate Guidance → advisor.provide_guidance_stream()
   ↓
4. Retrieve Context → self._retrieve_context(customer)
   - Line 326: memories = self.memory_stream.retrieve(query, top_k=5)
   - Returns EMPTY list (no memories in stream)
   ↓
5. Stream Response → Guidance sent to user
   ↓
6. Agent Destroyed → All in-memory data lost ❌
```

### Expected Flow (Should Happen)

```
1. Consultation Request
   ↓
2. Create AdvisorAgent WITH database session
   - Load existing memories from database
   ↓
3. Process Customer Message
   - Extract important observations
   - Create MemoryNode objects
   - Persist to database ✓
   ↓
4. Generate Guidance
   - Retrieve relevant memories from database
   - Use memories to inform response
   ↓
5. Process Advisor Response
   - Extract key insights/decisions
   - Create MemoryNode objects
   - Persist to database ✓
   ↓
6. Agent Destroyed
   - Memories remain in database ✓
   - Available for next consultation ✓
```

---

## Database Schema Verification

**Location:** `alembic/versions/a7b3073fdead_initial_migration_with_pgvector_support.py:54-66`

The `memories` table exists and is properly configured:

```python
op.create_table(
    "memories",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("description", sa.Text(), nullable=False),
    sa.Column("timestamp", sa.DateTime(), nullable=False),
    sa.Column("importance", sa.Float(), nullable=False),
    sa.Column("memory_type", sa.String(length=50), nullable=False),
    sa.Column("embedding", Vector(1024), nullable=True),
    sa.Column("last_accessed", sa.DateTime(), nullable=True),
    sa.Column("access_count", sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint("id"),
)
# Has vector index for similarity search
op.create_index("idx_memories_embedding", "memories", ["embedding"], postgresql_using="ivfflat")
```

**Status:** ✅ Database schema is correct
**Issue:** ❌ No code writes to this table during normal operation

---

## Implementation Plan

### Phase 1: Enable Database Persistence (CRITICAL)

#### Step 1.1: Modify AdvisorAgent to Accept Database Session

**File:** `src/guidance_agent/advisor/agent.py`

**Change 1 - Update `__init__` signature (around line 49-60):**

```python
def __init__(
    self,
    profile: AdvisorProfile,
    session: Optional[Session] = None,  # <-- ADD THIS
    model: Optional[str] = None,
    use_chain_of_thought: bool = True,
    enable_prompt_caching: bool = True,
):
    """Initialize the advisor agent with profile and optional database session.

    Args:
        profile: Advisor profile with role and specialization
        session: SQLAlchemy database session for memory persistence
        model: Model identifier (default from profile)
        use_chain_of_thought: Enable chain-of-thought reasoning
        enable_prompt_caching: Enable prompt caching for performance
    """
    self.profile = profile
    self.model = model or profile.model or "claude-3-7-sonnet-20250219"
    self.use_chain_of_thought = use_chain_of_thought
    self.enable_prompt_caching = enable_prompt_caching

    # Initialize memory stream with database session
    self.memory_stream = MemoryStream(session=session, load_existing=True)  # <-- CHANGE THIS
```

#### Step 1.2: Update Dependency Injection

**File:** `src/guidance_agent/api/dependencies.py`

**Change - Update `get_advisor_agent` function (around line 121-140):**

```python
def get_advisor_agent(
    profile: AdvisorProfile = Depends(get_advisor_profile),
    db: Session = Depends(get_db),  # <-- ADD THIS
) -> AdvisorAgent:
    """Get advisor agent instance.

    Args:
        profile: Advisor profile configuration
        db: Database session for memory persistence

    Returns:
        Configured advisor agent instance with database-backed memory

    Note:
        Creates a new agent instance per request. Memory persistence
        is now enabled via the database session.
    """
    return AdvisorAgent(
        profile=profile,
        session=db,  # <-- ADD THIS
        use_chain_of_thought=True,
        enable_prompt_caching=True,
    )
```

**Verification:** After these changes, the `MemoryStream` will have `self.session` set and will call `_persist_memory()` when memories are added.

---

### Phase 2: Create Memories During Consultations

#### Step 2.1: Import Required Memory Components

**File:** `src/guidance_agent/api/routers/consultations.py`

**Add to imports (around line 1-30):**

```python
from guidance_agent.core.memory import MemoryNode, rate_importance
from guidance_agent.core.types import MemoryType
from guidance_agent.core.embedding import embed
```

#### Step 2.2: Record Customer Observations

**File:** `src/guidance_agent/api/routers/consultations.py`

**Location:** After line 229 (where customer message is stored to database)

**Add this code:**

```python
    # Store the message
    db.add(message)
    db.commit()
    db.refresh(message)

    # NEW: Extract and record customer observation as memory
    if advisor.memory_stream.session:
        try:
            # Rate the importance of this customer statement
            importance = rate_importance(request.content)

            # Only create memory if importance is above threshold (e.g., > 0.3)
            if importance > 0.3:
                memory = MemoryNode(
                    description=f"Customer inquiry: {request.content}",
                    importance=importance,
                    memory_type=MemoryType.OBSERVATION,
                    embedding=embed(request.content),
                    timestamp=message.timestamp,
                )
                advisor.memory_stream.add(memory)
                logger.info(f"Created customer observation memory (importance: {importance})")
        except Exception as e:
            logger.error(f"Failed to create customer memory: {e}")
            # Don't fail the request if memory creation fails
```

#### Step 2.3: Record Advisor Insights

**File:** `src/guidance_agent/api/routers/consultations.py`

**Location:** After line 338 (where guidance is completed)

**Add this code:**

```python
    # Store advisor message
    advisor_message = Message(
        consultation_id=consultation_id,
        role=MessageRole.ADVISOR,
        content=full_content,
        timestamp=datetime.now(UTC),
    )
    db.add(advisor_message)
    db.commit()

    # NEW: Extract and record key insights from advisor response
    if advisor.memory_stream.session and full_content:
        try:
            # Extract key decisions, recommendations, or facts from response
            # For now, use the full response; later could extract specific insights
            importance = rate_importance(full_content)

            if importance > 0.5:  # Higher threshold for advisor insights
                memory = MemoryNode(
                    description=f"Advisor insight: {full_content[:200]}...",  # Truncate long responses
                    importance=importance,
                    memory_type=MemoryType.REFLECTION,  # Or OBSERVATION
                    embedding=embed(full_content),
                    timestamp=advisor_message.timestamp,
                )
                advisor.memory_stream.add(memory)
                logger.info(f"Created advisor insight memory (importance: {importance})")
        except Exception as e:
            logger.error(f"Failed to create advisor memory: {e}")
```

---

### Phase 3: Add Logging and Verification

#### Step 3.1: Add Memory Persistence Logging

**File:** `src/guidance_agent/core/memory.py`

**Location:** In `_persist_memory` method (around line 164-180)

**Add logging:**

```python
def _persist_memory(self, memory: MemoryNode) -> None:
    """Persist a memory to the database."""
    try:
        from guidance_agent.models.database import Memory

        db_memory = Memory(
            description=memory.description,
            timestamp=memory.timestamp,
            importance=memory.importance,
            memory_type=memory.memory_type.value,
            embedding=memory.embedding,
            last_accessed=memory.last_accessed,
            access_count=memory.access_count,
        )
        self.session.add(db_memory)
        self.session.commit()
        self.session.refresh(db_memory)
        memory.id = db_memory.id

        logger.info(f"Persisted memory #{memory.id}: {memory.description[:50]}...")  # <-- ADD THIS

    except Exception as e:
        self.session.rollback()
        logger.error(f"Failed to persist memory: {e}")  # <-- ADD THIS
        raise
```

#### Step 3.2: Add Debug Endpoint to Verify Memories

**File:** `src/guidance_agent/api/routers/consultations.py`

**Add new endpoint:**

```python
@router.get("/{consultation_id}/memories")
async def get_consultation_memories(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """Get all memories associated with a consultation.

    Debug endpoint to verify memories are being recorded.
    """
    from guidance_agent.models.database import Memory

    # Get consultation to verify ownership
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    if consultation.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get all memories (for now; later could filter by consultation)
    memories = db.query(Memory).order_by(Memory.timestamp.desc()).limit(50).all()

    return [
        {
            "id": m.id,
            "description": m.description,
            "importance": m.importance,
            "memory_type": m.memory_type,
            "timestamp": m.timestamp.isoformat(),
            "access_count": m.access_count,
        }
        for m in memories
    ]
```

---

### Phase 4: Optional Improvements

#### Option 4.1: Make AdvisorAgent Inherit from BaseAgent

**File:** `src/guidance_agent/advisor/agent.py`

**Change class definition:**

```python
from guidance_agent.core.agent import BaseAgent

class AdvisorAgent(BaseAgent):  # <-- Add inheritance
    """Financial advisor agent for providing compliant guidance."""

    def __init__(
        self,
        profile: AdvisorProfile,
        session: Optional[Session] = None,
        model: Optional[str] = None,
        use_chain_of_thought: bool = True,
        enable_prompt_caching: bool = True,
    ):
        # Initialize BaseAgent
        super().__init__(session=session)

        # Initialize AdvisorAgent-specific attributes
        self.profile = profile
        self.model = model or profile.model
        # ... rest of init
```

**Benefits:**
- Access to `perceive()` method
- Consistent memory interface
- Better code reuse

**Note:** This requires careful review as `BaseAgent` may have other abstract methods that need implementation.

#### Option 4.2: Implement Automatic Memory Consolidation

**File:** `src/guidance_agent/learning/reflection.py`

**Status:** Infrastructure exists but not integrated

**Action:** Connect reflection system to run periodically (e.g., after every N consultations) to:
- Consolidate similar memories
- Extract higher-level insights
- Prune low-importance memories

---

## Testing Plan

### Manual Testing Steps

1. **Start the application:**
   ```bash
   python -m guidance_agent.api.main
   ```

2. **Create a consultation via API:**
   ```bash
   curl -X POST http://localhost:8000/api/consultations \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"customer_id": 1, "subject": "Test Memory Recording"}'
   ```

3. **Send messages to consultation:**
   ```bash
   curl -X POST http://localhost:8000/api/consultations/1/messages \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"content": "I want to invest $10,000 in retirement savings"}'
   ```

4. **Check database for memories:**
   ```sql
   SELECT id, description, importance, memory_type, timestamp
   FROM memories
   ORDER BY timestamp DESC
   LIMIT 10;
   ```

5. **Verify memories endpoint:**
   ```bash
   curl http://localhost:8000/api/consultations/1/memories \
     -H "Authorization: Bearer $TOKEN"
   ```

6. **Check logs for memory persistence messages:**
   ```
   Look for: "Created customer observation memory"
   Look for: "Persisted memory #..."
   ```

### Automated Tests

**File:** `tests/test_memory_persistence.py` (create new)

```python
import pytest
from sqlalchemy.orm import Session
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.core.memory import MemoryNode
from guidance_agent.core.types import MemoryType
from guidance_agent.models.database import Memory

def test_memory_persistence_with_session(db: Session):
    """Test that memories are persisted when session is provided."""
    # Create advisor with database session
    advisor = AdvisorAgent(
        profile=create_test_profile(),
        session=db,
    )

    # Add a memory
    memory = MemoryNode(
        description="Test memory",
        importance=0.8,
        memory_type=MemoryType.OBSERVATION,
    )
    advisor.memory_stream.add(memory)

    # Verify it was persisted
    db_memory = db.query(Memory).filter(
        Memory.description == "Test memory"
    ).first()

    assert db_memory is not None
    assert db_memory.importance == 0.8
    assert db_memory.memory_type == "observation"

def test_memory_persistence_without_session():
    """Test that memories are not persisted without session."""
    # Create advisor without database session
    advisor = AdvisorAgent(
        profile=create_test_profile(),
        session=None,
    )

    # Add a memory
    memory = MemoryNode(
        description="Test memory",
        importance=0.8,
        memory_type=MemoryType.OBSERVATION,
    )
    advisor.memory_stream.add(memory)

    # Memory should be in stream
    assert len(advisor.memory_stream.memories) == 1

    # But not persisted (no session, no database check needed)
    assert advisor.memory_stream.session is None
```

---

## Success Criteria

- ✅ Database session is injected into `AdvisorAgent`
- ✅ `MemoryStream` is initialized with `session` parameter
- ✅ Customer messages create `MemoryNode` objects
- ✅ Memories are persisted to `memories` table
- ✅ Memories can be retrieved in subsequent consultations
- ✅ Logs confirm memory creation and persistence
- ✅ Debug endpoint shows memories
- ✅ Automated tests verify persistence

---

## Rollback Plan

If issues occur after deployment:

1. **Quick Rollback:** Remove database session from dependency injection
   ```python
   # In dependencies.py, temporarily revert to:
   return AdvisorAgent(profile=profile, session=None)
   ```

2. **Database Cleanup:** If bad memories are created:
   ```sql
   DELETE FROM memories WHERE timestamp > 'YYYY-MM-DD HH:MM:SS';
   ```

3. **Disable Memory Creation:** Comment out memory creation code in consultations.py while keeping session injection (allows testing persistence without creating memories)

---

## Future Enhancements

1. **Intelligent Memory Extraction**
   - Use LLM to extract key facts from conversations
   - Identify important decisions vs casual chat
   - Tag memories with topics/categories

2. **Memory Lifecycle Management**
   - Implement decay for old memories
   - Consolidate similar memories
   - Prune low-value memories

3. **Cross-Customer Learning**
   - Anonymized insights from multiple customers
   - Pattern recognition across consultations
   - Aggregate knowledge base

4. **Memory Visualization**
   - Dashboard showing memory growth over time
   - Memory importance distribution
   - Most accessed memories

5. **Memory Quality Metrics**
   - Track memory usefulness in responses
   - Identify memories that improve guidance
   - Feedback loop for importance scoring

---

## References

- `src/guidance_agent/core/memory.py` - MemoryStream and MemoryNode implementation
- `src/guidance_agent/core/agent.py` - BaseAgent with perceive() method
- `src/guidance_agent/advisor/agent.py` - AdvisorAgent implementation
- `src/guidance_agent/api/dependencies.py` - Dependency injection
- `src/guidance_agent/api/routers/consultations.py` - Consultation endpoints
- `src/guidance_agent/learning/reflection.py` - Reflection and consolidation
- `alembic/versions/a7b3073fdead_*.py` - Database schema migration

---

## Conclusion

The memory system has all the necessary infrastructure (database schema, MemoryStream class, embedding support) but lacks the critical integration points to make it functional. The fixes are straightforward and low-risk:

1. Pass database session to agent (1 line change in 2 files)
2. Create memories during consultations (10-20 lines in 1 file)
3. Add logging for visibility (5-10 lines in 2 files)

**Estimated Implementation Time:** 2-4 hours
**Estimated Testing Time:** 1-2 hours
**Risk Level:** Low (changes are isolated, rollback is simple)

The benefits are significant: the advisor will be able to remember previous conversations, learn from interactions, and provide increasingly personalized guidance over time.
