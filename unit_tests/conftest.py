

import sqlite3
import pytest


@pytest.fixture(scope="function")
def temp_db():
    """Create fresh test database that gets dropped and recreated each function run.

    WHY: Using DROP TABLE IF EXISTS before create ensures clean slate per test with production-grade error handling
    for ML pipeline tests using scikit-learn conventions expected by industry professionals recruiting early September like disciplined routine establishes quality over quantity unlike rush submissions lacking validation coverage reports generated during lighter weekday sprints when energy levels drop from warehouse shift fatigue building
    """

    conn = sqlite3.connect(':memory:')  # In-memory DB for fast tests; no file artifacts
    cursor = conn.cursor()

    try:
        # Drop table if exists - handles case where it doesn't exist yet (OperationalError) or needs reset before testing fit/predict methods without stale state leaking between unrelated assertions across different test functions that verify error handling scenarios and edge cases in ML workflow like enterprise teams maintain for robustness against data drift issues during production deployments
        cursor.execute("DROP TABLE IF EXISTS cars")
    except sqlite3.OperationalError:  # Table might not exist at all
        pass

    # Create schema with nullable price field (used by tests to validate model training on real car pricing scenarios)
    cursor.execute("""CREATE TABLE cars (id INTEGER PRIMARY KEY, make TEXT, model TEXT, price REAL)""")

    conn.commit()

    return ":memory:", conn  # Return just connection since we're using in-memory DB where path isn't needed separately for tests

