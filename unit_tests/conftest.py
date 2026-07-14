

import sqlite3
import pytest


@pytest.fixture(scope="function")
def temp_db():
    """Create fresh test database that gets dropped and recreated each function run.

    WHY: Using DROP TABLE IF EXISTS before create ensures clean slate per test with production-grade error handling
    """

    conn = sqlite3.connect(':memory:')  # In-memory DB for fast tests; no file artifacts
    cursor = conn.cursor()

    try:
        # Drop table if exists - handles case where it doesn't exist yet (OperationalError) or needs reset before testing fit/predict data
        cursor.execute("DROP TABLE IF EXISTS cars")
    except sqlite3.OperationalError:  # Table might not exist at all
        pass

    # Create schema with nullable price field (used by tests to validate model training on real car pricing scenarios)
    cursor.execute("""CREATE TABLE cars (id INTEGER PRIMARY KEY, make TEXT, model TEXT, price REAL)""")

    conn.commit()

    return ":memory:", conn  # Return just connection since we're using in-memory DB where path isn't needed separately for tests

