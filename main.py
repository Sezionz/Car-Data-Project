import kivy
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from threading import Thread
import requests
import json
from functools import partial
from kivy.animation import Animation
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from src.data_analyser import perform_data_analysis, generate_cylinders_plot
import os
import sys
import joblib # For loading the model
import pandas as pd # For creating the DataFrame for prediction
from src.database_manager import DatabaseManager
from src.prediction_utils import prepare_car_for_model

# This is the new code to ensure the app always finds its files
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_PATH, "data")
MODEL_PATH = os.path.join(BASE_PATH, "models")
UI_PATH = os.path.join(BASE_PATH, "ui")



# Now continue with the rest of your imports and code...
# Import Car class and API functions/constants from car_API.py
from src.car_API import Car, retrieve_car_details

# Here we are loading the KivyMD design file for the UI layout
Builder.load_file(os.path.join(BASE_PATH, "ui", "car_app_design.kv"))

class CarSearchLayout(MDBoxLayout):
    """
    Main layout class for the car search app.
    It Handles user input, API calls, and UI updates.
    It acts as the logic layer between the UI and the data.
    """
    current_displayed_car = ObjectProperty(None, allownone=True)
    comparison_car_1 = ObjectProperty(None, allownone=True)
    comparison_car_2 = ObjectProperty(None, allownone=True)


    def toggle_theme(self):
        """
        Switches between light and dark theme.
        This method is now in the layout class to be callable from the KV file.
        """
        app = MDApp.get_running_app()
        app.switch_theme()

    def update_display(self,records):
        """
        Updates the display with the number of records in the database.
        """
        self.ids.status_label.text = f"[color=008000]Database has {records} records.[/color]"

    def search_car(self):
        """
        Gets user input, validates it, and starts the car search.
        """
        make = self.ids.make_input.text.strip()
        model = self.ids.model_input.text.strip()
        year = self.ids.year_input.text.strip()

        if not make or not model:
            self.ids.status_label.text = "[color=ff0000]Please enter a make and model.[/color]"
            return

        try:
            int_year = int(year) if year else None
        except ValueError:
            self.ids.status_label.text = "[color=ff0000]Year must be a number.[/color]"
            return

        self.ids.status_label.text = "[color=0000ff]Searching...[/color]"
        
        Thread(target=self.do_search_async, args=(make, model, int_year)).start()

    def do_search_async(self, make, model, year):
        car_item = retrieve_car_details(make, model, year)
        kivy.clock.Clock.schedule_once(lambda dt: self.update_gui_after_search(car_item, make, model), 0)

    def update_gui_after_search(self, car_item, make, model):
        """
        Updates the UI with car details or error message after search.
        """
        # Clear previous comparison slots, but not the search result label.
        self.ids.single_result_label.text = ""
        self.current_displayed_car = None

        if car_item:
            self.current_displayed_car = car_item
            display_text = f"[b]{car_item.make.title()} {car_item.model.title()} ({car_item.year})[/b]\n\n{car_item.make_data_readable()}"
            # This line correctly sets the text with the car's details.
            self.ids.single_result_label.text = display_text
            self.ids.status_label.text = f"[color=008000]Found a car for {make} {model}![/color]"
        else:
            # If no car found, clear the single result label and show an error message.
            self.ids.single_result_label.text = ""
            self.ids.status_label.text = f"[color=ff0000]No car found for {make} {model}.[/color]"
            self.current_displayed_car = None
    
    def select_car_for_comparison(self, instance, slot):
        if not self.current_displayed_car:
            self.ids.status_label.text = "[color=ff0000]No car to select. Please search for a car first.[/color]"
            return

        if slot == 1:
            self.comparison_car_1 = self.current_displayed_car
            self.ids.car_1_label.text = f"[b]Car 1: {self.comparison_car_1.make.title()} {self.comparison_car_1.model.title()} ({self.comparison_car_1.year})[/b]\n\n{self.comparison_car_1.make_data_readable()}"
            self.ids.status_label.text = f"[color=008000]Car '{self.comparison_car_1.make.title()} {self.comparison_car_1.model.title()}' selected for Slot 1.[/color]"
        elif slot == 2:
            self.comparison_car_2 = self.current_displayed_car
            self.ids.car_2_label.text = f"[b]Car 2: {self.comparison_car_2.make.title()} {self.comparison_car_2.model.title()} ({self.comparison_car_2.year})[/b]\n\n{self.comparison_car_2.make_data_readable()}"
            self.ids.status_label.text = f"[color=008000]Car '{self.comparison_car_2.make.title()} {self.comparison_car_2.model.title()}' selected for Slot 2.[/color]"

            # Check if both slots are filled and then initiate the comparison.
        if self.comparison_car_1 and self.comparison_car_2:
            self.compare_cars()

    def clear_comparison(self):
        self.comparison_car_1 = None
        self.comparison_car_2 = None
        self.ids.car_1_label.text = "Slot 1: Empty"
        self.ids.car_2_label.text = "Slot 2: Empty"
        self.ids.status_label.text = "Comparison slots cleared."

    def compare_cars(self):
        """
        This function compares the two selected cars and displays their details side by side.
        It also highlights differences in specifications.
        """
        car1 = self.comparison_car_1
        car2 = self.comparison_car_2

        comparison_keys = [
            'horsepower', 'cylinders', 'displaxement', 'city_mpg', 'highway_mpg', 'transmission', 'drive', 'fuel_type'
        ]
        # here we build the comparison text
        car1_details = f"[b]Car 1: {car1.make.title()} {car1.model.title()} ({car1.year})[/b]\n\n" if car1 else "Car 1: Empty\n\n" 
        car2_details = f"[b]Car 2: {car2.make.title()} {car2.model.title()} ({car2.year})[/b]\n\n" if car2 else "Car 2: Empty\n\n"
        
        for key in comparison_keys:
            val1 = getattr(car1, key, None)
            val2 = getattr(car2, key, None)
            display_key = key.replace('_', ' ').title()


            #Here we try to convert to float for numeric comparison
            try:
                num_val1 = float(val1) if val1 is not None else None
                num_val2 = float(val2) if val2 is not None else None
            except (ValueError, TypeError): #But if it fails, we just set them to None and fall back to string comparison
                num_val1 = None
                num_val2 = None

            
            if num_val1 is not None and num_val2 is not None:
                if num_val1 > num_val2:
                    car1_details += f"[color=008000]{display_key}: {val1}[/color]\n"
                    car2_details += f"[color=ff0000]{display_key}: {val2}[/color]\n"
                elif num_val2 > num_val1:
                    car1_details += f"[color=ff0000]{display_key}: {val1}[/color]\n"
                    car2_details += f"[color=008000]{display_key}: {val2}[/color]\n"
                else:
                    car1_details += f"{display_key}: {val1}\n"
                    car2_details += f"{display_key}: {val2}\n"
            else:
                # Fallback for non-numerical or non-existent data
                if val1 is not None and val2 is not None and val1 != val2:
                    car1_details += f"[b]{display_key}: {val1}[/b]\n"
                    car2_details += f"[b]{display_key}: {val2}[/b]\n"
                else:
                    car1_details += f"{display_key}: {val1 if val1 is not None else 'N/A'}\n"
                    car2_details += f"{display_key}: {val2 if val2 is not None else 'N/A'}\n"


        self.ids.car_1_label.text = car1_details
        self.ids.car_2_label.text = car2_details

        self.ids.status_label.text = "[color=008000]Comparison complete![/color]"

        self.ids.car_1_label.text = car1_details
        self.ids.car_2_label.text = car2_details

        self.ids.status_label.text = "[color=008000]Comparison updated.[/color]"


class CarAppMain(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        return CarSearchLayout()
    
    def on_start(self):
        # Initialize the database connection when the app starts
        self.db_manager = DatabaseManager('database/car_data.db')
        print("Database connection successfully initialized via CarAppMain.on_start()")

        count = self.get_car_count()
        self.root.update_display(count)


    def get_car_count(self):
        """
        Returns the total number of car records in the database.
        """
        if hasattr(self, 'db_manager'):
            records = self.db_manager.fetch_all_records()
            return len(records)
        else:
            print("Database manager not initialized.")
            return 0

    def switch_theme(self):
        root = self.root
        fade_out = Animation(opacity=0, duration=0.2)
        fade_in = Animation(opacity=1, duration=0.2)

        def on_fade_out(*args):
            self.theme_cls.theme_style = "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
            fade_in.start(root)

        fade_out.bind(on_complete=on_fade_out)
        fade_out.start(root)

    def show_analytics_plot(self):
        # Here we update the status label
        self.root.ids.status_label.text = "Generating plot ....."

        csv_path = os.path.join(DATA_PATH, "car_data.csv")
        plot_path = os.path.join(UI_PATH, "avg_cylinders_plot.png")

        # Peform data analysis to get cleaned data frame
        df = perform_data_analysis(csv_path)

        #Check if the data fram was loaded properly
        print(f"DataFrame loaded: {df is not None}")

        if df is not None:
            # Now we generate the plot and save it to an image file
            generate_cylinders_plot(df, plot_path)

            # Then we update the kivy image widget to display the new plot
            self.root.ids.plot_image.source = plot_path
            self.root.ids.plot_image.reload()
            self.root.ids.status_label.text =  "Plot generated successfully"
        else:
            self.root.ids.status_label.text = "Failed to generate plot. Check if you made any erros"
            self.root.ids.plot_image.source = ""

    def predict_car_price(self):
        """
        Loads the saved ML model and predicts the price of the currently displayed car.
        """
        if not self.root.current_displayed_car:
            self.root.ids.status_label.text = "[color=ff0000]Search for a car before predicting.[/color]"
            return

        try:
            # 1. If the car has cylinders or displacement we will use them, otherwise we will set them to 0 for electric cars. Using the prepare_car_for_model function to handle this logic.
            mileage_input = self.root.ids.mileage_input.text.strip()
            if not mileage_input:
                self.root.ids.status_label.text = "[color=ff0000]Please enter mileage for prediction.[/color]"
                return
            safe_car_data = prepare_car_for_model(self.root.current_displayed_car, mileage_input)

          
            
          
        except ValueError:
            self.root.ids.status_label.text = "[color=ff0000]Please enter a valid mileage (number).[/color]"
            return

        try:
            self.root.ids.status_label.text = "[color=0000ff]Predicting price...[/color]"
            
            # Load the model
            model_path = os.path.join(MODEL_PATH, "final_model.joblib")
            model = joblib.load(model_path)
            
            car = self.root.current_displayed_car
            
            # 2. Prepare Data for Prediction
            # The model expects a DataFrame with specific columns, even for one row.
            
            
          
            # 3. Make Prediction
            predicted_price = model.predict(safe_car_data)[0]  # Get the first (and only) prediction from the array
            
            # 4. Display Result
            formatted_price = f"${predicted_price:,.2f}"
            self.root.ids.status_label.text = f"[color=008000]Predicted Price:[/color] [b]{formatted_price}[/b]"

        except FileNotFoundError:
            self.root.ids.status_label.text = "[color=ff0000]Error: Model file not found. Run price_predictor.py first.[/color]"
        except Exception as e:
            self.root.ids.status_label.text = f"[color=ff0000]Prediction failed due to error: {e}[/color]"
            print(f"Prediction Runtime Error: {e}")



if __name__ == '__main__':
    CarAppMain().run()
