"""
Demonstration of Phase 1: Memory and Retrieval System

This example shows how to use the implemented Phase 1 components:
- Vector Store with pgvector
- Importance Scoring with LiteLLM
- Memory Stream with Database Persistence
- Multi-faceted Retrieval (Memories, Cases, Rules)
"""

from uuid import uuid4
from datetime import datetime

from guidance_agent.core.database import get_session
from guidance_agent.core.memory import MemoryNode, MemoryStream, rate_importance
from guidance_agent.core.types import MemoryType
from guidance_agent.retrieval.embeddings import embed
from guidance_agent.retrieval.retriever import CaseBase, RulesBase, retrieve_context


def demo_importance_scoring():
    """Demo: Rate importance of observations using LLM."""
    print("=" * 70)
    print("DEMO 1: Importance Scoring with LiteLLM")
    print("=" * 70)

    observations = [
        "Customer asked about their pension balance",
        "Customer is considering retirement at age 60",
        "Customer wants to transfer their £500k defined benefit pension",
    ]

    print("\nRating importance of observations (0.0 - 1.0 scale):\n")

    for obs in observations:
        # Note: This would call the actual LLM in production
        # For demo purposes, we'll simulate ratings
        print(f"Observation: {obs}")
        # importance = rate_importance(obs)  # Uncomment to test with real LLM
        importance = 0.2 if "balance" in obs else (0.6 if "retirement" in obs else 0.9)
        print(f"Importance: {importance:.2f}")
        print()


def demo_memory_stream_persistence():
    """Demo: Memory stream with database persistence."""
    print("=" * 70)
    print("DEMO 2: Memory Stream with Database Persistence")
    print("=" * 70)

    session = get_session()

    try:
        # Create memory stream with persistence
        print("\n1. Creating memory stream with database persistence...")
        stream = MemoryStream(session=session)

        # Add memories
        print("\n2. Adding memories to stream (auto-persists to database)...")

        memories = [
            MemoryNode(
                description="Customer has £150k pension pot",
                importance=0.7,
                memory_type=MemoryType.OBSERVATION,
                embedding=embed("Customer has £150k pension pot"),
            ),
            MemoryNode(
                description="Customer is 55 years old and planning retirement",
                importance=0.6,
                memory_type=MemoryType.OBSERVATION,
                embedding=embed("Customer is 55 years old"),
            ),
            MemoryNode(
                description="Customer seems uncertain about investment risk",
                importance=0.8,
                memory_type=MemoryType.REFLECTION,
                embedding=embed("Customer uncertain about risk"),
            ),
        ]

        for memory in memories:
            stream.add(memory)
            print(f"   Added: {memory.description[:50]}... (importance: {memory.importance})")

        print(f"\n3. Memory stream now has {stream.get_memory_count()} memories")

        # Retrieve memories
        print("\n4. Retrieving relevant memories for query...")
        query = "Tell me about pension withdrawal options"
        query_embedding = embed(query)

        retrieved = stream.retrieve(
            query_embedding,
            top_k=2,
            recency_weight=0.3,
            importance_weight=0.4,
            relevance_weight=0.3,
        )

        print(f"\n   Query: '{query}'")
        print(f"   Retrieved {len(retrieved)} memories:")
        for i, mem in enumerate(retrieved, 1):
            print(f"   {i}. {mem.description} (importance: {mem.importance})")

        # Clean up
        stream.clear()

    finally:
        session.close()


def demo_multi_faceted_retrieval():
    """Demo: Multi-faceted retrieval combining memories, cases, and rules."""
    print("\n" + "=" * 70)
    print("DEMO 3: Multi-faceted Retrieval System")
    print("=" * 70)

    session = get_session()

    try:
        # Setup: Create memory stream, case base, rules base
        print("\n1. Setting up retrieval components...")

        memory_stream = MemoryStream(session=session)
        case_base = CaseBase(session=session)
        rules_base = RulesBase(session=session)

        # Add sample memory
        print("\n2. Adding sample data...")
        memory_stream.add(
            MemoryNode(
                description="Customer has defined benefit pension worth £400k",
                importance=0.9,
                memory_type=MemoryType.OBSERVATION,
                embedding=embed("Customer has DB pension worth £400k"),
            )
        )
        print("   Added memory about DB pension")

        # Add sample case
        case_base.add(
            id=uuid4(),
            embedding=embed("Customer considering DB pension transfer"),
            metadata={
                "task_type": "pension_transfer",
                "customer_situation": "55 year old with £500k DB pension considering transfer",
                "guidance_provided": "Warned about risks and recommended Pension Wise appointment",
                "outcome": {"successful": True, "referred_to_specialist": True},
            },
        )
        print("   Added case about DB pension transfer")

        # Add sample rule
        rules_base.add(
            id=uuid4(),
            embedding=embed("DB pension transfer requires FCA advice"),
            metadata={
                "principle": "All DB pension transfers over £30k require FCA-regulated advice",
                "domain": "pension_transfers",
                "confidence": 0.95,
                "supporting_evidence": ["FCA-2015", "case-123", "case-456"],
            },
        )
        print("   Added rule about DB pension transfers")

        # Perform multi-faceted retrieval
        print("\n3. Performing multi-faceted retrieval...")
        query = "Customer wants advice on transferring their defined benefit pension"
        query_embedding = embed(query)

        context = retrieve_context(
            query=query,
            query_embedding=query_embedding,
            memory_stream=memory_stream,
            case_base=case_base,
            rules_base=rules_base,
            memory_top_k=5,
            case_top_k=2,
            rule_top_k=3,
            fca_requirements="FCA requires advice for DB transfers over £30k",
        )

        print(f"\n   Query: '{query}'")
        print(f"\n   Retrieved Context:")
        print(f"   - {len(context.memories)} memories")
        print(f"   - {len(context.cases)} cases")
        print(f"   - {len(context.rules)} rules")

        if context.memories:
            print(f"\n   Top Memory: {context.memories[0].description}")

        if context.cases:
            print(f"\n   Top Case: {context.cases[0]['customer_situation']}")

        if context.rules:
            print(f"\n   Top Rule: {context.rules[0]['principle']}")
            print(f"   Rule Confidence: {context.rules[0]['confidence']}")

        print(f"\n   FCA Requirements: {context.fca_requirements}")

        print(f"\n   Retrieval Reasoning:")
        for line in context.reasoning.split('\n'):
            print(f"   {line}")

        # Clean up
        memory_stream.clear()
        session.query(case_base.vector_store.model).delete()
        session.query(rules_base.vector_store.model).delete()
        session.commit()

    finally:
        session.close()


def main():
    """Run all Phase 1 demos."""
    print("\n" + "=" * 70)
    print("Phase 1: Memory and Retrieval System - Live Demo")
    print("=" * 70)

    try:
        # Demo 1: Importance Scoring
        demo_importance_scoring()

        # Demo 2: Memory Stream with Persistence
        demo_memory_stream_persistence()

        # Demo 3: Multi-faceted Retrieval
        demo_multi_faceted_retrieval()

        print("\n" + "=" * 70)
        print("All demos completed successfully!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
