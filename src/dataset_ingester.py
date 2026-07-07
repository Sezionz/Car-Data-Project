import csv
from database_manager import DatabaseManager

def ingest_csv_to_db(csv_file_path):
    db_manager = DatabaseManager()
    
        # I want to first initialise the database
    db = DatabaseManager()
    db.clear_table()  # Clear any existing data for a clean test run

    records = []
    # Here I will read the CSV file and prepare the data for insertion
    with open(csv_file_path, mode='r') as csvfile:
        csv_reader = csv.DictReader(csvfile)


        for row in csv_reader:
            title_parts = row['title'].split(' ', 1)  # Split into make and model
            make = title_parts[0]
            model = title_parts[1] if len(title_parts) > 1 else 'Unknown'  # Handle cases where model might be missing
            mileage = int(row['Mileage(miles)'])
            engine_data_before = row['Engine'].replace('L', '')  # Remove 'L' suffix if present
            try:
                engine_size = float(engine_data_before)
            except ValueError:
                print(f"Invalid engine size value in row: {row}")
                engine_size = 0.0  # Default to 0.0 if conversion fails
                continue
            price = float(row['Price'])
            

            # I want to package the data into a tuple and append it to the records list
            records.append((make, model, mileage, engine_size, price))
    
    db_manager.bulk_insert_records(records)

    # Now we verify
    print("\nCurrent records in the database after CSV ingestion:")
    for car in db.fetch_all_records():
        print(car)


# Run the pipeline
if __name__ == "__main__":
    csv_file_path = 'data/used_cars_UK.csv'  # Ensure this path is correct
    ingest_csv_to_db(csv_file_path)