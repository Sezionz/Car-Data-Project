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

from src.database_manager import DatabaseManager


# This is the new code to ensure the app always finds its files
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_PATH, "data")
MODEL_PATH = os.path.join(BASE_PATH, "models")
UI_PATH = os.path.join(BASE_PATH, "ui")




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
        """
        Microservice Client: Fetches data from the Docker API on a background thread.
        """
        api_url = "http://127.0.0.1:8000/api/v1/get_car"
        search_params = {
            "make": make,
            "model": model,
            "year": year
        }

        try:
            response = requests.get(api_url, params=search_params)
            response.raise_for_status() 
            
            # Extract the JSON payload
            car_data = response.json()
            
            # Pass the raw dictionary to the UI thread, NOT a formatted string
            kivy.clock.Clock.schedule_once(lambda dt: self.update_gui_after_search(car_data, make, model), 0)
            
        except requests.exceptions.HTTPError:
            error_msg = "[color=ff0000]Error: Car not found in the database.[/color]"
            kivy.clock.Clock.schedule_once(lambda dt: self.update_gui_after_search(error_msg, make, model), 0)
            
        except requests.exceptions.ConnectionError:
            error_msg = "[color=ff0000]Error: Backend server is offline.[/color]"
            kivy.clock.Clock.schedule_once(lambda dt: self.update_gui_after_search(error_msg, make, model), 0)

            
    def update_gui_after_search(self, payload, make, model):
        """
        Updates the UI and saves the JSON dictionary to local memory for predictions.
        """
        self.ids.single_result_label.text = ""
        self.current_displayed_car = None

        # Check if the network thread passed us a string error message
        if isinstance(payload, str) and "Error:" in payload:
            self.ids.status_label.text = payload
            self.current_car_data = None
        else:
            # STATE MANAGEMENT: Save the raw JSON dictionary to the app's memory
            self.current_car_data = payload

            # Format the dictionary into a readable string for the UI
            formatted_data = "\n".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in payload.items() if v])
            display_text = f"[b]{make.title()} {model.title()}[/b]\n\n{formatted_data}"
            
            self.ids.single_result_label.text = display_text
            self.ids.status_label.text = f"[color=008000]Found a car for {make.title()} {model.title()}![/color]"
    
    def select_car_for_comparison(self, instance, slot):
        """
        Extracts the raw JSON dictionary saved from the API search 
        and routes it to the correct comparison slot.
        """
        # 1. State Check: Ensure we have JSON data in memory
        if not hasattr(self, 'current_car_data') or not self.current_car_data:
            self.ids.status_label.text = "[color=ff0000]No car to select. Please search for a car first.[/color]"
            return

        # 2. Extract the raw dictionary
        car_data = self.current_car_data
        
        # Safely extract make and model, falling back to the input fields if missing
        make = car_data.get('make', self.ids.make_input.text.strip()).title()
        model = car_data.get('model', self.ids.model_input.text.strip()).title()
        
        # 3. Format the JSON dictionary for display
        formatted_data = "\n".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in car_data.items() if v])
        display_text = f"[b]{make} {model}[/b]\n\n{formatted_data}"

        if slot == 1:
            self.comparison_car_1 = car_data
            self.ids.car_1_label.text = f"[b]Car 1:[/b]\n{display_text}"
            self.ids.status_label.text = f"[color=008000]Car '{make} {model}' selected for Slot 1.[/color]"
        elif slot == 2:
            self.comparison_car_2 = car_data
            self.ids.car_2_label.text = f"[b]Car 2:[/b]\n{display_text}"
            self.ids.status_label.text = f"[color=008000]Car '{make} {model}' selected for Slot 2.[/color]"

        # Initiate comparison if both slots are populated
        if self.comparison_car_1 and self.comparison_car_2:
            self.compare_cars()

    def compare_cars(self):
        """
        Iterates through two JSON dictionaries, parses numerical values, 
        and highlights the statistical differences in the UI.
        """
        car1 = self.comparison_car_1
        car2 = self.comparison_car_2

        # Fixed spelling of displacement
        comparison_keys = [
            'horsepower', 'cylinders', 'displacement', 'city_mpg', 'highway_mpg', 'transmission', 'drive', 'fuel_type'
        ]
        
        c1_name = f"{car1.get('make', 'Car 1').title()} {car1.get('model', '').title()}"
        c2_name = f"{car2.get('make', 'Car 2').title()} {car2.get('model', '').title()}"

        car1_details = f"[b]{c1_name}[/b]\n\n"
        car2_details = f"[b]{c2_name}[/b]\n\n"
        
        for key in comparison_keys:
            # Dictionary extraction: using .get() instead of getattr()
            val1 = car1.get(key)
            val2 = car2.get(key)
            display_key = key.replace('_', ' ').title()

            try:
                num_val1 = float(val1) if val1 is not None else None
                num_val2 = float(val2) if val2 is not None else None
            except (ValueError, TypeError): 
                num_val1 = None
                num_val2 = None
            
            # The mathematical comparison logic remains identical
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
                if val1 is not None and val2 is not None and val1 != val2:
                    car1_details += f"[b]{display_key}: {val1}[/b]\n"
                    car2_details += f"[b]{display_key}: {val2}[/b]\n"
                else:
                    car1_details += f"{display_key}: {val1 if val1 is not None else 'N/A'}\n"
                    car2_details += f"{display_key}: {val2 if val2 is not None else 'N/A'}\n"

        self.ids.car_1_label.text = car1_details
        self.ids.car_2_label.text = car2_details
        self.ids.status_label.text = "[color=008000]Comparison complete![/color]"


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
        Gathers the stored JSON state and user mileage, then pings the Docker container.
        """
        # 1. Check the memory state we saved during the search
        if not hasattr(self.root, 'current_car_data') or not self.root.current_car_data:
            self.root.ids.status_label.text = "[color=ff0000]Search for a car before predicting.[/color]"
            return

        mileage_text = self.root.ids.mileage_input.text.strip()
        if not mileage_text:
            self.root.ids.status_label.text = "[color=ff0000]Please enter the mileage.[/color]"
            return

        try:
            mileage = int(mileage_text)
        except ValueError:
            self.root.ids.status_label.text = "[color=ff0000]Mileage must be a whole number.[/color]"
            return

        self.root.ids.status_label.text = "[color=0000ff]Running Neural Prediction...[/color]"
        
        # 2. Extract features from the saved JSON dictionary
        car_data = self.root.current_car_data
        make = car_data.get('make', self.root.ids.make_input.text.strip())
        model = car_data.get('model', self.root.ids.model_input.text.strip())
        displacement = car_data.get('displacement', car_data.get('engine_size', 2.0))
        
        # 3. Dispatch network request
        Thread(target=self.do_predict_async, args=(make, model, mileage, displacement)).start()

    def do_predict_async(self, make, model, mileage, displacement):
        """
        Microservice Client: Pings the FastAPI Docker endpoint containing the Scikit-Learn model.
        """
        api_url = "http://127.0.0.1:8000/api/v1/predict_price"
        
        # This payload strictly matches the Pydantic CarFeatures schema we built
        payload = {
            "make": make,
            "model": model,
            "mileage": mileage,
            "displacement": float(displacement) if displacement else 2.0
        }

        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status() 
            
            prediction_data = response.json()
            estimated_price = prediction_data.get("estimated_price", 0)
            
            # Update the UI safely on the main thread
            success_msg = f"[color=008000]Predicted Price:[/color] [b]£{estimated_price:,.2f}[/b]"
            kivy.clock.Clock.schedule_once(lambda dt: self.update_status_label(success_msg), 0)
            
        except Exception as e:
            error_msg = "[color=ff0000]Prediction Error: Server offline or model failed.[/color]"
            kivy.clock.Clock.schedule_once(lambda dt: self.update_status_label(error_msg), 0)

    def update_status_label(self, message):
        """Helper method to map text back to the Kivy UI from the background thread."""
        self.root.ids.status_label.text = message
        


          
            
          




if __name__ == '__main__':
    CarAppMain().run()
