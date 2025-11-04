# Embedding Dimensions Configuration

## Overview

This application supports multiple embedding models with different dimensionalities (e.g., 768 for local models, 1536 for OpenAI, 3072 for some models). The database schema is designed to be **dimension-agnostic** to support different deployment environments.

## Important: Migration Philosophy

**DO NOT create migrations that change embedding dimensions**. Each deployment environment may use different embedding models with different dimensions, and migrations must produce identical schemas across all environments.

### Why This Matters

- Different machines may use different embedding models (OpenAI: 1536, Ollama: 768, Voyage: 1024, etc.)
- Migrations that read from environment variables will produce different schemas on different machines
- This breaks database portability and migration reproducibility
- A database migrated with dimension=768 cannot be used with code expecting dimension=1536

## Current Approach

### 1. Base Migrations (DO NOT MODIFY)

The initial migrations create tables with pgvector's `VECTOR` type with hardcoded dimensions:

- `a7b3073fdead_initial_migration_with_pgvector_support.py` - Creates initial tables with VECTOR(1536)
- `d54d8651560e_add_fca_and_pension_knowledge_tables.py` - Creates knowledge tables with VECTOR(1536)

These use 1536 as the default because:
- It's the most common dimension (OpenAI's text-embedding-3-small, Voyage, Titan)
- It provides a consistent baseline for fresh installations

### 2. Dimension Configuration

The application code reads dimension from the `EMBEDDING_DIMENSION` environment variable:

```python
# src/guidance_agent/core/database.py
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

# src/guidance_agent/retrieval/embeddings.py
dimensions = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
```

### 3. Machine-Specific Schema Updates

If your deployment uses a different dimension than the migration default (1536), you need to manually update the schema **after** running migrations. This is a **one-off operation** that should NOT be committed as a migration.

#### Example: Updating from 1536 to 768 for local embeddings

```bash
# Connect to your database
psql -h localhost -U postgres -d guidance_agent

# Drop HNSW indexes (required before column type change)
DROP INDEX IF EXISTS fca_knowledge_embedding_idx;
DROP INDEX IF EXISTS pension_knowledge_embedding_idx;
DROP INDEX IF EXISTS memory_embedding_idx;
DROP INDEX IF EXISTS case_embedding_idx;
DROP INDEX IF EXISTS rule_embedding_idx;

# Alter column types to new dimension
ALTER TABLE fca_knowledge ALTER COLUMN embedding TYPE vector(768);
ALTER TABLE pension_knowledge ALTER COLUMN embedding TYPE vector(768);
ALTER TABLE memories ALTER COLUMN embedding TYPE vector(768);
ALTER TABLE cases ALTER COLUMN embedding TYPE vector(768);
ALTER TABLE rules ALTER COLUMN embedding TYPE vector(768);

# Recreate HNSW indexes
CREATE INDEX fca_knowledge_embedding_idx ON fca_knowledge USING hnsw (embedding vector_cosine_ops);
CREATE INDEX pension_knowledge_embedding_idx ON pension_knowledge USING hnsw (embedding vector_cosine_ops);
CREATE INDEX memory_embedding_idx ON memories USING hnsw (embedding vector_cosine_ops);
CREATE INDEX case_embedding_idx ON cases USING hnsw (embedding vector_cosine_ops);
CREATE INDEX rule_embedding_idx ON rules USING hnsw (embedding vector_cosine_ops);
```

## Deployment Checklist

When setting up a new environment:

1. **Set `EMBEDDING_DIMENSION` in your `.env` file** based on your chosen embedding model
2. **Run all migrations**: `alembic upgrade head`
3. **If your dimension differs from 1536**, manually update the schema using the SQL commands above
4. **Verify the dimension**:
   ```sql
   SELECT c.table_name, c.column_name, a.atttypmod AS dimension
   FROM information_schema.columns c
   JOIN pg_attribute a ON a.attname = c.column_name
   JOIN pg_class t ON a.attrelid = t.oid AND t.relname = c.table_name
   WHERE c.table_name IN ('cases', 'memories', 'rules', 'fca_knowledge', 'pension_knowledge')
   AND c.column_name = 'embedding';
   ```

## Common Embedding Dimensions

| Model | Dimension | Provider |
|-------|-----------|----------|
| text-embedding-3-small | 1536 | OpenAI |
| text-embedding-3-large | 3072 | OpenAI |
| text-embedding-ada-002 | 1536 | OpenAI |
| voyage-large-2 | 1536 | Voyage |
| voyage-2 | 1024 | Voyage |
| amazon.titan-embed-text-v1 | 1536 | AWS Bedrock |
| cohere.embed-english-v3 | 1024 | AWS Bedrock |
| nomic-embed-text | 768 | Ollama/LM Studio |
| bge-large | 1024 | Ollama |
| bge-small | 384 | Ollama |
| all-minilm | 384 | Ollama |

## DO NOT Create Dimension-Changing Migrations

❌ **Bad**: Creating a migration that reads from environment variables:

```python
def upgrade() -> None:
    target_dim = int(os.getenv("EMBEDDING_DIMENSION", "768"))
    op.execute(f'ALTER TABLE cases ALTER COLUMN embedding TYPE vector({target_dim})')
```

This will produce different schemas on different machines and break migration reproducibility.

✅ **Good**: Manually updating schema post-migration for your specific environment.

## Troubleshooting

### Dimension Mismatch Error

If you see errors like:
```
expected 768 dimensions, not 1536
```

This means your database schema dimension doesn't match your `EMBEDDING_DIMENSION` setting. Follow the machine-specific schema update steps above.

### Migration History Issues

If you have a dimension-changing migration in your history:

1. Check if it was applied: `SELECT version_num FROM alembic_version;`
2. If it matches a dimension-changing migration, manually update to the previous good migration:
   ```sql
   UPDATE alembic_version SET version_num = 'previous_migration_id';
   ```
3. Delete the problematic migration file from `alembic/versions/`

## References

- [pgvector documentation](https://github.com/pgvector/pgvector)
- Application embedding config: `src/guidance_agent/core/provider_config.py`
- Database models: `src/guidance_agent/core/database.py`
