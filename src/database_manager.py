import sqlite3

class DatabaseManager:
    def __init__(self, db_name="database/car_data.db"):
        # Establish the connection and initialize the cursor
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        
        # Initialize the schema
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                mileage INTEGER,
                engine_size REAL,
                price REAL
                );""")
        

    def _validate_schema(self, make, model, mileage, engine_size, price):
        """
        Advanced Validation: Ensures data integrity before SQLite insertion.
        Raises ValueError if schema requirements are not met.
        """
        if not isinstance(make, str) or not make.strip():
            raise ValueError(f"Schema Error: 'make' must be a valid string. Got: {make}")
        
        if not isinstance(model, str) or not model.strip():
            raise ValueError(f"Schema Error: 'model' must be a valid string. Got: {model}")
        
        # Mileage can be 0 (brand new), but not negative
        if not isinstance(mileage, (int, float)) or mileage < 0:
            raise ValueError(f"Schema Error: 'mileage' must be a positive number. Got: {mileage}")
            
        if not isinstance(engine_size, (int, float)) or engine_size < 0:
            raise ValueError(f"Schema Error: 'engine_size' must be a positive number. Got: {engine_size}")
            
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError(f"Schema Error: 'price' must be greater than zero. Got: {price}")
    # This is here to commit one row at a time



    
    def insert_record(self, make, model, mileage, engine_size, price):
        # The automated insertion logic goes here
        self._validate_schema(make, model, mileage, engine_size, price)
        self.cursor.execute("""
            INSERT INTO cars (make, model, mileage, engine_size, price)
            VALUES (?, ?, ?, ?, ?)
        """, (make, model, mileage, engine_size, price))
        self.conn.commit()
    
    # In order to make our system more robust, we can add a method that can add many records at once. This is useful for batch processing or importing data from a CSV file.
    def bulk_insert_records(self, records):
        # Can ingest a list of tuples, where each tuple is a record
        self.cursor.executemany("""
            INSERT INTO cars (make, model, mileage, engine_size, price)
            VALUES (?, ?, ?, ?, ?)
        """, records)
        self.conn.commit()

    def clear_table(self):
        # Wipes all data from the table but keeps the schema intact
        self.cursor.execute("DELETE FROM cars")
        self.conn.commit()

    def fetch_all_records(self):
        # Retrieve all rows from the cars table
        self.cursor.execute("SELECT * FROM cars")
        return self.cursor.fetchall()
    


# --- TESTING THE PIPELINE ---
if __name__ == "__main__":
    # 1. Boot up the database manager
    db = DatabaseManager()
    
    db.clear_table()  # Clear any existing data for a clean test run

    # 2. Inject a test record (Make, Model, Mileage, Engine Size, Price)
    db.insert_record("Toyota", "Camry", 45000, 2.5, 15500.00)
    print("Test record injected.")

    # 3. Retrieve and print the data to verify
    records = db.fetch_all_records()
    print("Current Database Records:")
    for row in records:
        print(row)

    # 4. Test Bulk Ingestion
    bulk_cars = [
        ("Honda", "Civic", 32000, 1.5, 18000.00),
        ("Ford", "Focus", 60000, 2.0, 12000.00),
        ("BMW", "3 Series", 25000, 2.0, 28000.00)
    ]
    db.bulk_insert_records(bulk_cars)
    print("\nBulk records injected.")

    # 5. Retrieve and verify the batch
    print("Database Records after Batch Ingestion:")
    for row in db.fetch_all_records():
        print(row)