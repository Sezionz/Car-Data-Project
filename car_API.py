import requests
import json




# --- Configuration ---
# IMPORTANT: Replace "YOUR_API_NINJAS_API_KEY" with the actual API key you obtained.
API_KEY = "E+Cc/AN7edDA0riCb6EWgg==RXMlmtPCOa7Xxb69"

# This is the specific endpoint for the Cars API on API-Ninjas
BASE_API_URL = "https://api.api-ninjas.com/v1/cars"

class Car:
#This class contains all the specifications that are retrieved from the API-Ninjas xar api
    def __init__(self, make, model, year, **kwargs):
        """
        The class is initialised into the car object with the specified parameters.
        Here are the possible arguments:
            make (str): The make of the car (e.g., "Audi").
            model (str): The model of the car (e.g., "A4").
            year (int): The manufacturing year of the car.
            **kwargs: Stores any extra attributes from the API's response.
        """
        self.make = make
        self.model = model
        self.year = year
        # Dynamically set attributes from kwargs to capture all API data
        for key, value in kwargs.items():
            setattr(self, key, value)

    def make_data_readable(self):
        """
        This function formats the car details into a string for display.
        It dynamically iterates through all attributes of the Car object
        to ensure all available data is included.
        """
        details = []
        # Use a list of preferred order for common attributes
        ordered_keys = [
            'make', 'model', 'year', 'fuel_type', 'cylinders', 'displacement',
            'horsepower', 'torque', 'transmission', 'drive', 'city_mpg',
            'highway_mpg', 'combination_mpg', 'vehicle_class'
        ]

        # First, display the main attributes in a readable format
        for key in ordered_keys:
            if hasattr(self, key):
                value = getattr(self, key)
                if value:
                    display_key = key.replace('_', ' ').title()
                    details.append(f"{display_key}: {value}")

        # Then, append any additional specs that were not in the ordered list
        for key, value in self.__dict__.items():
            if key not in ordered_keys and not key.startswith('_') and value:
                display_key = key.replace('_', ' ').title()
                details.append(f"{display_key}: {value}")

        return "\n".join(details)
    
    def __repr__(self):
        """
        Provides a easy to work with representation of the Car object.
        """
        return f"Car(make='{self.make}', model='{self.model}', year={self.year})"




def retrieve_car_details(make: str, model: str, year: int) -> Car | None:
    """
    Retrieves car details from the API based on the make, model, and year.
    
    Args:
        make (str): The make of the car (e.g., "Audi").
        model (str): The model of the car (e.g., "A4").
        year (int): The manufacturing year of the car.
    
    Returns:
        Car | None: A Car object with the details or None if not found.
    """
    headers = {
        "X-Api-Key": API_KEY
    }
    
    params = {
        "make": make,
        "model": model,
        "year": year
    }
    #Here we are using a try and except block to catch any errors that may occur when making the request
    try:
        # This is the request to the API-Ninjas Cars API
        response = requests.get(BASE_API_URL, headers=headers, params=params)
        # Here we check if the response was successful
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        # Parse the JSON response
        car_data = response.json()

        #The API returns a list of cars, so we need to check if the list is empty
        if car_data:
            # Extract the first car's details
            car_info = car_data[0]
            # Create a Car object with the retrieved data
            return Car(**car_info)
        else:
            print(f"No car found for {make} {model} {year}.")
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return None
# So this function can be used to retrieve car details by calling it with the make, model, and year of the car
# Example usage:
# car = retrieve_car_details("Audi", "A4", 2020)
# if car:
#     print(car.make_data_readable())
#     print(car)
# else:
#     print("Car not found.")   

# This code defines a Car class and a function to retrieve car details from the API-Ninjas Cars API.
# The Car class has attributes for various car specifications and a method to format the details into a readable string.
# The retrieve_car_details function makes an API request to get car details based on the make, model, and year, returning a Car object or None if not found. 
"""
if __name__ == "__main__":
    print("--- Testing get_car_details function ---")
    
    # Test Case 1: A successful search for a known car
    print("\nAttempting to find a Audi A4 2020...")
    car1 = retrieve_car_details(make='audi', model='a4', year=2020)
    if car1:
        print("Success! Car found.")
        print(car1.make_data_readable())
    else:
        print("Failed to find the car.")
        
    print("\n" + "="*40)
    
    # Test Case 2: A search for a car that does not exist
    print("\nAttempting to find a Ford Piston 2025...")
    car2 = retrieve_car_details(make='ford', model='piston', year=2025)
    if car2:
        print("Success! Car found.")
        print(car2.make_data_readable())
    else:
        print("Failed as expected. Car not found.")
        
    print("\n" + "="*40)
    
    # Test Case 3: A search with an invalid API key (if you temporarily use a fake key)
    print("\nAttempting a search with an invalid API key...")
    # To test this, you would temporarily change your API_KEY variable
    # to something incorrect, then change it back after the test.
    # Note: This will likely return an HTTPError.
    
    # For now, we will just print a message about the test case
    print("This test case requires temporarily changing the API_KEY variable to an invalid value.")
    print("You would expect an error message like 'HTTP Error: 403 Client Error: Forbidden for url...'")
    
    print("\n--- End of tests ---")
    # This code is for testing purposes and should not be run in production.
"""
