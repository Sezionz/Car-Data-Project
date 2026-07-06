import sqlite3
import csv

class CarDatabase:
    def __init__(self, db_name):
        # 1. Open a connection to the local database file
        self.conn = sqlite3.connect(db_name)

    # 2. Create a cursor (this is the tool that executes your SQL commands)
    def create_cursor(self):
        return self.conn.cursor()

    def filter_by_horsepower(self, min_hp):
        # 3. Write and execute your SQL query
        print(f"Fetching car data with horsepower greater than {min_hp}...\n")
        cursor = self.create_cursor()
        cursor.execute("SELECT make, model, horsepower FROM cars WHERE horsepower > ?;", (min_hp,))

        # 4. Fetch all the results from the query
        results = cursor.fetchall()

        # 5. Loop through and print the results in Python
        for row in results:
            make = row[0]
            model = row[1]
            horsepower = row[2]
            print(f"Make: {make} | Model: {model} | HP: {horsepower}")


    def update_horsepower(self, car_id, new_horsepower):
        cursor = self.create_cursor()
        cursor.execute("UPDATE cars SET horsepower = ? WHERE id = ?;", (new_horsepower, car_id))
        self.conn.commit()
  

    def delete_carmodel(self, car_id):
        cursor = self.create_cursor()
        cursor.execute("DELETE FROM cars WHERE id = ?;", (car_id,))
        self.conn.commit()

    def import_from_csv(self, csv_file):
        print(f"Importing data from {csv_file}...\n")
        cursor = self.create_cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS vehicle_data (iD INT PRIMARY KEY, make VARCHAR(50), model VARCHAR(50), year INT, mileage INT, price FLOAT);")

        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                make = row[8]
                model = row[9]
                year = int(row[11])
                mileage = int(row[12])
                price = float(row[13])
                cursor.execute("INSERT INTO vehicle_data (make, model, year, mileage, price) VALUES (?, ?, ?, ?, ?);", (make, model, year, mileage, price))
        self.conn.commit()



    def verify_data(self):
        cursor = self.create_cursor()
        cursor.execute("SELECT * FROM vehicle_data ORDER BY price DESC LIMIT 5 ;")
        results = cursor.fetchall()
        for row in results:
            print(f"make: {row[1]}, model: {row[2]}, year: {row[3]}, price: {row[5]}")



    # 6. Close the connection (Always lock the door on your way out)
    def __del__(self):
        self.conn.close()

# 1. Create an instance of the CarDatabase class
my_db = CarDatabase('my_first_database.db')

#2. Test the methods

my_db.import_from_csv('car_data.csv')
my_db.verify_data()