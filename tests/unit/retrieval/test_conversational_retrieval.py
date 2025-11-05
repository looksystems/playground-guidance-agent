"""Tests for conversational context in retrieval system (Phase 3).

This module tests the enhanced case retrieval that considers conversational
context for better case matching based on conversation phase and quality.
"""

import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from guidance_agent.retrieval.retriever import CaseBase, retrieve_context


class TestCaseBaseConversationalRetrieval:
    """Tests for CaseBase retrieval with conversational context."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return Mock()

    @pytest.fixture
    def case_base(self, mock_session):
        """Create case base with mocked vector store."""
        base = CaseBase(mock_session)
        # Mock the vector store
        base.vector_store = Mock()
        return base

    def test_retrieve_without_conversational_context(self, case_base):
        """Test that retrieve works without conversational context (backward compatible)."""
        # Mock vector store results
        case_base.vector_store.search = Mock(return_value=[
            {
                "id": uuid4(),
                "similarity": 0.9,
                "metadata": {
                    "task_type": "pension_access",
                    "customer_situation": "Customer wants to access pension at 55",
                    "guidance_provided": "Explained options for accessing pension",
                    "outcome": "positive",
                }
            }
        ])

        query_embedding = [0.1] * 1536
        results = case_base.retrieve(query_embedding, top_k=3)

        assert len(results) == 1
        assert results[0]["task_type"] == "pension_access"
        assert results[0]["similarity"] == 0.9
        # Should not have conversational fields in result
        assert "conversational_boost" not in results[0] or results[0]["conversational_boost"] == 0.0

    def test_retrieve_with_conversational_context_no_boost(self, case_base):
        """Test retrieve with conversational context but no quality boost."""
        # Mock vector store results - case without conversational quality
        case_base.vector_store.search = Mock(return_value=[
            {
                "id": uuid4(),
                "similarity": 0.8,
                "metadata": {
                    "task_type": "pension_access",
                    "customer_situation": "Customer wants to access pension",
                    "guidance_provided": "Explained options",
                    "outcome": "positive",
                    # No conversational_quality field
                }
            }
        ])

        query_embedding = [0.1] * 1536
        conversation_context = {
            "phase": "middle",
            "emotional_state": "anxious",
            "literacy_level": "medium"
        }

        results = case_base.retrieve(
            query_embedding,
            top_k=3,
            conversation_context=conversation_context
        )

        assert len(results) == 1
        assert results[0]["similarity"] == 0.8
        assert results[0]["conversational_boost"] == 0.0
        assert results[0]["final_score"] == 0.8

    def test_retrieve_boosts_high_quality_cases(self, case_base):
        """Test that cases with high conversational quality get boosted."""
        # Mock vector store results - case WITH high conversational quality
        case_base.vector_store.search = Mock(return_value=[
            {
                "id": uuid4(),
                "similarity": 0.7,
                "metadata": {
                    "task_type": "pension_access",
                    "customer_situation": "Customer wants to access pension",
                    "guidance_provided": "Explained options naturally",
                    "outcome": "positive",
                    "conversational_quality": 0.85,  # High quality > 0.7
                }
            }
        ])

        query_embedding = [0.1] * 1536
        conversation_context = {
            "phase": "middle",
            "emotional_state": "anxious",
            "literacy_level": "medium"
        }

        results = case_base.retrieve(
            query_embedding,
            top_k=3,
            conversation_context=conversation_context
        )

        assert len(results) == 1
        assert results[0]["similarity"] == 0.7
        assert results[0]["conversational_boost"] == 0.2  # High quality boost
        assert abs(results[0]["final_score"] - 0.9) < 0.001  # 0.7 + 0.2 (floating point comparison)

    def test_retrieve_boosts_phase_matching_cases(self, case_base):
        """Test that cases matching conversation phase get boosted."""
        # Mock vector store results - case with dialogue techniques including phase
        case_base.vector_store.search = Mock(return_value=[
            {
                "id": uuid4(),
                "similarity": 0.75,
                "metadata": {
                    "task_type": "pension_access",
                    "customer_situation": "Customer in middle of conversation",
                    "guidance_provided": "Provided detailed information",
                    "outcome": "positive",
                    "conversational_quality": 0.65,  # Below 0.7, no quality boost
                    "dialogue_techniques": {
                        "phases_covered": ["opening", "middle"],
                        "effective_phrases": ["let me break this down"],
                    }
                }
            }
        ])

        query_embedding = [0.1] * 1536
        conversation_context = {
            "phase": "middle",  # Matches phases_covered
            "emotional_state": "neutral",
            "literacy_level": "medium"
        }

        results = case_base.retrieve(
            query_embedding,
            top_k=3,
            conversation_context=conversation_context
        )

        assert len(results) == 1
        assert results[0]["similarity"] == 0.75
        assert results[0]["conversational_boost"] == 0.1  # Phase match boost
        assert results[0]["final_score"] == 0.85  # 0.75 + 0.1

    def test_retrieve_boosts_high_quality_and_phase_match(self, case_base):
        """Test that cases get both boosts when applicable."""
        # Mock vector store results - case with both high quality AND phase match
        case_base.vector_store.search = Mock(return_value=[
            {
                "id": uuid4(),
                "similarity": 0.6,
                "metadata": {
                    "task_type": "pension_access",
                    "customer_situation": "Customer in opening phase",
                    "guidance_provided": "Natural, engaging opening",
                    "outcome": "positive",
                    "conversational_quality": 0.9,  # High quality
                    "dialogue_techniques": {
                        "phases_covered": ["opening"],
                        "effective_phrases": ["great to meet you"],
                    }
                }
            }
        ])

        query_embedding = [0.1] * 1536
        conversation_context = {
            "phase": "opening",  # Matches
            "emotional_state": "neutral",
            "literacy_level": "medium"
        }

        results = case_base.retrieve(
            query_embedding,
            top_k=3,
            conversation_context=conversation_context
        )

        assert len(results) == 1
        assert results[0]["similarity"] == 0.6
        assert abs(results[0]["conversational_boost"] - 0.3) < 0.001  # 0.2 (quality) + 0.1 (phase)
        assert abs(results[0]["final_score"] - 0.9) < 0.001  # 0.6 + 0.3

    def test_retrieve_re_ranks_cases_by_final_score(self, case_base):
        """Test that cases are re-ranked by final score (similarity + boost)."""
        # Mock two cases: one with lower similarity but high quality
        case_base.vector_store.search = Mock(return_value=[
            {
                "id": uuid4(),
                "similarity": 0.9,  # Higher similarity
                "metadata": {
                    "task_type": "pension_access",
                    "customer_situation": "Standard case",
                    "guidance_provided": "Standard guidance",
                    "outcome": "positive",
                    # No conversational quality
                }
            },
            {
                "id": uuid4(),
                "similarity": 0.75,  # Lower similarity
                "metadata": {
                    "task_type": "pension_consolidation",
                    "customer_situation": "High quality case",
                    "guidance_provided": "Natural, engaging guidance",
                    "outcome": "positive",
                    "conversational_quality": 0.85,  # High quality: +0.2 boost
                    "dialogue_techniques": {
                        "phases_covered": ["middle"],  # Matching phase: +0.1 boost
                    }
                }
            }
        ])

        query_embedding = [0.1] * 1536
        conversation_context = {
            "phase": "middle",
            "emotional_state": "neutral",
            "literacy_level": "medium"
        }

        results = case_base.retrieve(
            query_embedding,
            top_k=3,
            conversation_context=conversation_context
        )

        # Should be re-ranked by final score
        # Case 1: 0.9 similarity + 0.0 boost = 0.9
        # Case 2: 0.75 similarity + 0.3 boost = 1.05
        # Case 2 should come first
        assert len(results) == 2
        assert results[0]["task_type"] == "pension_consolidation", "High quality case should rank first"
        assert results[0]["final_score"] == 1.05
        assert results[1]["task_type"] == "pension_access"
        assert results[1]["final_score"] == 0.9

    def test_retrieve_respects_top_k_after_reranking(self, case_base):
        """Test that only top_k cases are returned after re-ranking."""
        # Mock 4 cases, request top_k=2
        case_base.vector_store.search = Mock(return_value=[
            {
                "id": uuid4(),
                "similarity": 0.9,
                "metadata": {
                    "task_type": f"case_{i}",
                    "customer_situation": "Situation",
                    "guidance_provided": "Guidance",
                    "outcome": "positive",
                    "conversational_quality": 0.5 if i < 2 else 0.8,  # Last 2 have higher quality
                }
            }
            for i in range(4)
        ])

        query_embedding = [0.1] * 1536
        conversation_context = {
            "phase": "middle",
            "emotional_state": "neutral",
            "literacy_level": "medium"
        }

        results = case_base.retrieve(
            query_embedding,
            top_k=2,
            conversation_context=conversation_context
        )

        # Should return exactly 2 cases (top_k=2)
        assert len(results) == 2
        # Should be the highest scoring ones after re-ranking
        # (conversational quality is in metadata, not in returned case dict)

    def test_retrieve_searches_more_cases_when_context_provided(self, case_base):
        """Test that retrieval fetches more cases for re-ranking when context provided."""
        case_base.vector_store.search = Mock(return_value=[])

        query_embedding = [0.1] * 1536

        # Without context, should search for exactly top_k
        case_base.retrieve(query_embedding, top_k=3, conversation_context=None)
        call_args = case_base.vector_store.search.call_args
        assert call_args[1]["top_k"] == 3

        # With context, should search for top_k * 2 for re-ranking
        conversation_context = {"phase": "middle", "emotional_state": "neutral"}
        case_base.retrieve(query_embedding, top_k=3, conversation_context=conversation_context)
        call_args = case_base.vector_store.search.call_args
        assert call_args[1]["top_k"] == 6  # 3 * 2


class TestRetrieveContextWithConversationalContext:
    """Tests for retrieve_context function with conversational context."""

    @pytest.fixture
    def mock_components(self):
        """Create mock components for retrieval."""
        memory_stream = Mock()
        memory_stream.retrieve = Mock(return_value=[])

        case_base = Mock()
        case_base.retrieve = Mock(return_value=[])

        rules_base = Mock()
        rules_base.retrieve = Mock(return_value=[])

        return memory_stream, case_base, rules_base

    def test_retrieve_context_passes_conversational_context_to_cases(self, mock_components):
        """Test that retrieve_context passes conversational context to case retrieval."""
        memory_stream, case_base, rules_base = mock_components

        query = "How much should I save?"
        query_embedding = [0.1] * 1536
        conversation_context = {
            "phase": "middle",
            "emotional_state": "anxious",
            "literacy_level": "low"
        }

        result = retrieve_context(
            query=query,
            query_embedding=query_embedding,
            memory_stream=memory_stream,
            case_base=case_base,
            rules_base=rules_base,
            conversation_context=conversation_context
        )

        # Verify case_base.retrieve was called with conversation_context
        case_base.retrieve.assert_called_once()
        call_args = case_base.retrieve.call_args
        assert call_args[1]["conversation_context"] == conversation_context

    def test_retrieve_context_without_conversational_context(self, mock_components):
        """Test that retrieve_context works without conversational context (backward compatible)."""
        memory_stream, case_base, rules_base = mock_components

        query = "How much should I save?"
        query_embedding = [0.1] * 1536

        result = retrieve_context(
            query=query,
            query_embedding=query_embedding,
            memory_stream=memory_stream,
            case_base=case_base,
            rules_base=rules_base,
            # No conversation_context provided
        )

        # Should still work, passing None to case retrieval
        case_base.retrieve.assert_called_once()
        call_args = case_base.retrieve.call_args
        assert call_args[1].get("conversation_context") is None

    def test_retrieve_context_returns_all_components(self, mock_components):
        """Test that retrieve_context returns all expected components."""
        memory_stream, case_base, rules_base = mock_components

        # Mock some return values
        memory_stream.retrieve = Mock(return_value=[Mock(description="Memory 1")])
        case_base.retrieve = Mock(return_value=[{"task_type": "Case 1"}])
        rules_base.retrieve = Mock(return_value=[{"principle": "Rule 1", "confidence": 0.8}])

        query = "How much should I save?"
        query_embedding = [0.1] * 1536
        fca_requirements = "FCA guidelines..."
        conversation_context = {"phase": "middle"}

        result = retrieve_context(
            query=query,
            query_embedding=query_embedding,
            memory_stream=memory_stream,
            case_base=case_base,
            rules_base=rules_base,
            fca_requirements=fca_requirements,
            conversation_context=conversation_context
        )

        # Verify all components are in result
        assert len(result.memories) == 1
        assert len(result.cases) == 1
        assert len(result.rules) == 1
        assert result.fca_requirements == fca_requirements
        assert result.reasoning is not None
