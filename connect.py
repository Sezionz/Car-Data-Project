import sqlite3

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



    # 6. Close the connection (Always lock the door on your way out)
    def __del__(self):
        self.conn.close()

# 1. Create an instance of the CarDatabase class
my_db = CarDatabase('my_first_database.db')

#2. Test the methods
my_db.filter_by_horsepower(0)
my_db.update_horsepower(1, 250)