import joblib
import requests
import json
from src.database_manager import DatabaseManager
from fastapi import FastAPI, HTTPException  
import uvicorn
from pydantic import BaseModel
import pandas as pd


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
# Initialize the FastAPI server
app = FastAPI(title="Car Data API Microservice")

@app.get("/api/v1/get_car")
def get_car(make: str, model: str, year: int):
    """
    FastAPI endpoint that listens for requests from the Kivy frontend.
    """
    car = retrieve_car_details(make, model, year)
    
    if car:
        # FastAPI automatically converts Python dictionaries to JSON
        return car.__dict__ 
    else:
        raise HTTPException(status_code=404, detail=f"No data found for {year} {make} {model}")



# 1. Load the ML Engine into server memory
try:
    price_model = joblib.load("models/final_model.joblib")
except FileNotFoundError:
    print("Warning: ML Model not found. Prediction endpoint will fail.")
    price_model = None

# 2. The Architectural Schema (The Checkpoint)
class CarFeatures(BaseModel):
    """
    Strictly validates incoming data against the pipeline's required features.
    """
    make: str
    model: str
    mileage: int
    displacement: float

# 3. The Machine Learning Endpoint
@app.post("/api/v1/predict_price")
def predict_price(features: CarFeatures):
    """
    Receives validated vehicle specs, formats them into a Pandas DataFrame,
    feeds them to the Scikit-Learn pipeline, and returns the valuation.
    """
    if price_model is None:
        raise HTTPException(status_code=500, detail="ML Model offline.")

    try:
        # Transform the Pydantic object into a DataFrame matching your training ETL
        input_df = pd.DataFrame([{
            "make": features.make,
            "model": features.model,
            "mileage": features.mileage,
            "displacement": features.displacement
        }])
        
        predicted_value = price_model.predict(input_df)[0]
        
        return {"estimated_price": round(predicted_value, 2)}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    # This runs the server locally on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
