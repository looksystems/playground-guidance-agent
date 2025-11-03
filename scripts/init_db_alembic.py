"""Initialize database using Alembic migrations.

This script uses Alembic to manage database schema instead of raw SQL.
"""

import subprocess
import sys
from pathlib import Path

def run_migrations():
    """Run Alembic migrations to initialize database."""
    print("🔧 Initializing database with Alembic migrations...")
    print()

    # Get project root
    project_root = Path(__file__).parent.parent

    try:
        # Run alembic upgrade to head
        result = subprocess.run(
            ["uv", "run", "alembic", "upgrade", "head"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )

        # Print output
        if result.stdout:
            print(result.stdout)

        print()
        print("✅ Database initialization complete!")
        print()
        print("Tables created:")
        print("  - memories (with HNSW vector index)")
        print("  - cases (with HNSW vector index)")
        print("  - rules (with HNSW vector index)")
        print("  - consultations (with indexes)")
        print("  - alembic_version (migration tracking)")
        print()
        print("To check migration status: uv run alembic current")
        print("To generate new migration: uv run alembic revision --autogenerate -m 'description'")

        return 0

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running migrations: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


def check_migration_status():
    """Check current migration status."""
    project_root = Path(__file__).parent.parent

    print("📊 Checking migration status...")

    try:
        result = subprocess.run(
            ["uv", "run", "alembic", "current"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking status: {e}")
        if e.stderr:
            print(e.stderr)


if __name__ == "__main__":
    # Check if --status flag is provided
    if "--status" in sys.argv:
        check_migration_status()
    else:
        exit_code = run_migrations()
        sys.exit(exit_code)
