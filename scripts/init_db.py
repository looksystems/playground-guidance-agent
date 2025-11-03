"""Initialize database with pgvector extension and create tables."""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the database with pgvector extension and create tables."""
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/guidance_agent")

    print(f"Connecting to database...")
    conn = psycopg2.connect(database_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    try:
        # Enable pgvector extension
        print("Enabling pgvector extension...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✓ pgvector extension enabled")

        # Create memories table
        print("Creating memories table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id UUID PRIMARY KEY,
                description TEXT NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                last_accessed TIMESTAMPTZ NOT NULL,
                importance FLOAT NOT NULL CHECK (importance >= 0 AND importance <= 1),
                memory_type VARCHAR(50) NOT NULL CHECK (memory_type IN ('observation', 'reflection', 'plan')),
                embedding vector(1536),
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        print("✓ memories table created")

        # Create index for vector similarity search
        # Using HNSW instead of ivfflat to support higher dimensions (>2000)
        print("Creating vector similarity index on memories...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS memories_embedding_idx
            ON memories USING hnsw (embedding vector_cosine_ops);
        """)
        print("✓ Vector index created on memories (HNSW)")

        # Create cases table
        print("Creating cases table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id UUID PRIMARY KEY,
                task_type VARCHAR(100) NOT NULL,
                customer_situation TEXT NOT NULL,
                guidance_provided TEXT NOT NULL,
                outcome JSONB NOT NULL,
                embedding vector(1536),
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        print("✓ cases table created")

        # Create index for vector similarity search on cases
        print("Creating vector similarity index on cases...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS cases_embedding_idx
            ON cases USING hnsw (embedding vector_cosine_ops);
        """)
        print("✓ Vector index created on cases (HNSW)")

        # Create rules table
        print("Creating rules table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id UUID PRIMARY KEY,
                principle TEXT NOT NULL,
                domain VARCHAR(100) NOT NULL,
                confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
                supporting_evidence JSONB DEFAULT '[]',
                embedding vector(1536),
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        print("✓ rules table created")

        # Create index for vector similarity search on rules
        print("Creating vector similarity index on rules...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS rules_embedding_idx
            ON rules USING hnsw (embedding vector_cosine_ops);
        """)
        print("✓ Vector index created on rules (HNSW)")

        # Create consultations table for tracking
        print("Creating consultations table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultations (
                id UUID PRIMARY KEY,
                customer_id UUID NOT NULL,
                advisor_id UUID NOT NULL,
                conversation JSONB NOT NULL,
                outcome JSONB,
                start_time TIMESTAMPTZ NOT NULL,
                end_time TIMESTAMPTZ,
                duration_seconds INTEGER,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        print("✓ consultations table created")

        # Create index on timestamps for querying
        print("Creating indexes on consultation timestamps...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS consultations_start_time_idx
            ON consultations (start_time);

            CREATE INDEX IF NOT EXISTS consultations_customer_id_idx
            ON consultations (customer_id);
        """)
        print("✓ Timestamp indexes created")

        print("\n✅ Database initialization complete!")
        print("\nCreated tables:")
        print("  - memories (with vector index)")
        print("  - cases (with vector index)")
        print("  - rules (with vector index)")
        print("  - consultations")

    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_database()
