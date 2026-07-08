"""Pytest fixtures for testing modules.

This conftest centralizes shared test infrastructure so tests can focus on assertions.
Fixtures defined here are auto-discoverable by pytest within this directory tree.
"""

import sqlite3
import pytest


@pytest.fixture(scope="function")
def temp_db():
    """ Here I will create fresh test database that gets dropped and recreated each function run.

    WHY: Using drop tables before create ensures clean slate per test showing production-grade error handling 
    """

    db_name = "test_cars_temp.db"  
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        # Here we drop table if exists 
        cursor.execute("DROP TABLE IF EXISTS cars")

    except sqlite3.OperationalError:
        # Handle case where table doesn't exist yet 
        cursor.execute("DROP TABLE IF EXISTS cars")

    # Create schema with NULLable price field (None in Python should be literal SQL keyword 'NULL')
    cursor.execute("""CREATE TABLE cars (id INTEGER PRIMARY KEY, make TEXT, model TEXT, price REAL)""")

    conn.commit()

    try:
        yield db_name, conn
    finally:
        # This cleanup after test completes regardless of pass/fail status
        try:
            conn.close()
            import os
            if os.path.exists(db_name):
                os.remove(db_name)  # Just simple file removal works fine for single-file test DBs 
        except Exception as e:
            print(f"Warning cleanup failed but tests still valid despite minor artifact remaining")
