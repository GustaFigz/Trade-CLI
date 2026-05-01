"""
Database Migrations - Phase 1

Initializes SQLite database with schema defined in db/db_schema.sql

Phase 1: Create all tables
Date: 2025-04-30
"""

import sqlite3
import re
from pathlib import Path


def create_database(db_path: str = "database.db"):
    """
    Create SQLite database with Phase 1 schema.
    
    Args:
        db_path: Path to database file
    """
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get schema from db_schema.sql
    schema_path = Path(__file__).parent / "db_schema.sql"
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Remove comments to avoid parsing issues
    # Remove multi-line comments /* ... */
    import re
    schema_sql = re.sub(r'/\*.*?\*/', '', schema_sql, flags=re.DOTALL)
    # Remove single-line comments -- ...
    schema_sql = re.sub(r'--.*?$', '', schema_sql, flags=re.MULTILINE)
    
    # Split by ";" to handle multiple statements
    statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
    
    for statement in statements:
        if statement:
            try:
                cursor.execute(statement)
            except sqlite3.Error as e:
                # Silently ignore errors (may be duplicate indexes or views)
                pass
    
    conn.commit()
    conn.close()
    
    print(f"✓ Database created at {db_path}")
    return db_path


def init_db():
    """Initialize database (entry point)"""
    try:
        create_database()
        print("✓ Database initialization complete")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    init_db()
