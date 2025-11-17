# Car-Data-Project
Car Data Explorer & Analytics Dashboard

Project Overview

The Car Data Explorer is a robust, cross-platform desktop application designed for automotive enthusiasts and data scientists. It provides a user interface (UI) for quickly retrieving car specifications, performing side-by-side comparisons, and generating basic data visualizations.

This project demonstrates an end-to-end data pipeline, including API integration, desktop GUI development, data cleaning (ETL), and basic machine learning model integration.

Key Features

Car Search & Retrieval: Uses the requests library to fetch live data (make, model, year, engine specs) from the API-Ninjas Cars API.

Side-by-Side Comparison: Allows users to select two cars and displays their specifications in a parallel view, highlighting key differences.

Data Visualization (NEW!): Integrates pandas and matplotlib to analyze bulk data (cylinders, displacement) and display a custom bar chart directly in the application GUI.

Machine Learning Integration (In Progress): Designed to load a trained scikit-learn model (car_price_model.joblib) for making simple price predictions based on car features (year, mileage, engine size).

Cross-Platform GUI: Built using the KivyMD framework for a responsive, modern Material Design interface on desktop operating systems (Windows, macOS, Linux).

Robust Data Handling: Implements data cleaning routines to manage missing values (NaN) and data limitations (like the 'Premium Subscriber' restrictions from the free API tier).

Technology Stack

GUI Framework: Kivy / KivyMD

Core Language: Python

Data Processing: pandas

Data Visualization: matplotlib

API Requests: requests

Machine Learning: scikit-learn, joblib

Data Persistence: .csv files for bulk data/model training

Setup and Installation

Follow these steps to set up the project on your local machine.

1. Clone the Repository (Windows PC)

# Clone the repository from GitHub
git clone [https://github.com/Sezionz/Car-Data-Project.git](https://github.com/Sezionz/Car-Data-Project.git)
cd Car-Data-Project


2. Create and Activate Virtual Environment

It is essential to use a virtual environment to manage dependencies.

# Create the environment
python -m venv car_data_env

# Activate the environment (using the Windows batch file)
.\car_data_env\Scripts\activate.bat


3. Install Dependencies

Install all necessary libraries (KivyMD, pandas, scikit-learn, etc.).

pip install requests kivy kivymd pandas matplotlib scikit-learn joblib


4. API Key Configuration

Sign up for a free API-Ninjas account and obtain your unique API Key.

Open car_API.py and paste your API key into the designated spot within the retrieve_car_details function.

5. Generate Data Files

Before running the application, you must run the following scripts once to create the necessary local data files:

File

Purpose

Command

data_collection.py

Fetches the live car data from the API and creates car_data.csv.

python data_collection.py

price_predictor.py

Trains the ML model on car_prices.csv and creates the car_price_model.joblib file.

python price_predictor.py

How to Run the Application

With your environment activated, launch the GUI application from the terminal:

python main.py


Usage Tips

Analytics: Click the "Generate Analytics Plot" button to run the pandas analysis and display the resulting avg_cylinders_plot.png directly in the app.

Comparison: After searching for a car, use the "SELECT 1" and "SELECT 2" buttons to load data into the comparison slots.

Project Status and Future Enhancements

The core GUI, data collection, and analytics visualization features are complete.

Future Plans:

Implement the full price prediction feature using the car_price_model.joblib.

Integrate the price prediction into the main search flow, showing the estimated price immediately after a car is searched.

Add persistence to the comparison slots using a database (e.g., SQLite) to save selections between sessions.
