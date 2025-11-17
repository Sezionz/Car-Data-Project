import pandas as pd
import requests
import time


def retrieve_car_details(make, model, year):
    API_KEY = "E+Cc/AN7edDA0riCb6EWgg==RXMlmtPCOa7Xxb69"
    BASE_API_URL = "https://api.api-ninjas.com/v1/cars"

    params = {'make': make, 'model': model, 'year': year}


    try:
        response = requests.get(BASE_API_URL, headers={'X-Api-Key': API_KEY}, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {make} {model} {year}: {e}")
        return None
    except ValueError:
        print(f"Error decoding JSON for {make} {model} {year}")
        return None
    
def fetch_and_save_bulk_data():
    #Here we are going to use the data that we aregetting from and api and saving into a csv
    cars_data_toget = [
        {"make" : "audi", "model" : "a4", "year" : 2010},
        {"make" : "audi", "model" : "a3", "year" : 2018},
        {"make" : "honda", "model" : "civic", "year" : 2021},
        {"make" : "bmw", "model" : "2", "year" : 2016},
        {"make" : "mercedes-benz", "model" : "c-class", "year" : 2023},
        {"make" : "ford", "model" : "mustang", "year" : 2025},
        {"make" : "tesla", "model" : "model s", "year" : 2017},
        {"make" : "bmw", "model" : "x5", "year" : 2023},
        {"make" : "chevrolet", "model" : "silverado", "year" : 2020},
    ]

    # The limitation of the way we have to interact witht the api makes it unfeesible for the program to store all cars info

    all_car_data = []

    print("We are now collecting the necessary data please wait...")
    for car in cars_data_toget:
        print(f"Fetching the data for: {car['make']}{car['model']}{car['year']}.............")

        details = retrieve_car_details(car["make"], car["model"],car["year"])

        #Calling The API function to get the details we want

        if details:
            all_car_data.extend(details)

        #The API we are using has a limit on the amount of requests you can make in a short period of time

        time.sleep(1)

        #Using a time sleep allows the script to pause to respect the limit


    print(f"Data Retrieval Completion! We now have all the data for {len(all_car_data)}")

    df = pd.DataFrame(all_car_data)
    #We need to convert the data into the pandas data frame since that is what we are using

    df.to_csv("car_data.csv", index=False)
    print("Data now saved to car_data.csv")


if __name__ == "__main__":
    fetch_and_save_bulk_data()