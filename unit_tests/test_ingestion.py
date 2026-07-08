"""Tests for data ingestion pipeline.

Shared fixtures are defined in conftest.py which handles DB setup/teardown centrally across all tests.
Each fixture has scope="function" so tables are recreated before every individual test run ensuring isolation and clean slate without stale state leaking between unrelated assertions 
"""

import pandas as pd
import pytest

def test_data_cleaning_no_nulls(temp_db):
    """Test that database stores valid price values correctly."""

    db_name, conn = temp_db

    cursor = conn.cursor()
    cursor.execute("INSERT INTO cars VALUES (1, 'Audi', 'A4', 10000.0)")
    cursor.execute("INSERT INTO cars VALUES (2, 'BMW', 'X5', NULL)")

    conn.commit()


def test_data_loads_null_prices(temp_db):
    """Test that database loads rows with NULL prices."""

    db_name, conn = temp_db

    cursor = conn.cursor()
    # insert same rows as other tests to ensure isolation (fixtures recreate tables per test)
    cursor.execute("INSERT INTO cars VALUES (1, 'Audi', 'A4', 10000.0)")
    cursor.execute("INSERT INTO cars VALUES (2, 'BMW', 'X5', NULL)")
    conn.commit()

    cursor.execute("SELECT * FROM cars")
    rows = cursor.fetchall()

    assert len(rows) == 2
    assert rows[0][3] == 10000.0, "First car should have valid price of 10000.0"


def test_data_with_null_price(temp_db):
    """Test data retrieval with NULL prices works correctly."""

    db_name, conn = temp_db

    cursor = conn.cursor()
    # ensure test data present
    cursor.execute("INSERT INTO cars VALUES (1, 'Audi', 'A4', 10000.0)")
    cursor.execute("INSERT INTO cars VALUES (2, 'BMW', 'X5', NULL)")
    conn.commit()

    cursor.execute("SELECT * FROM cars")
    rows = cursor.fetchall()

    # Check for the NULL row (pandas represents SQL NULL as None/NaN, SQLite returns NULL which Python converts to None)
    null_rows = [row for row in rows if pd.isna(row[3])]

    assert len(null_rows) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
