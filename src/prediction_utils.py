import pandas as pd

def prepare_car_for_model(car_object, mileage):
    # This is the "Contract." 
    # It ensures the data structure perfectly matches what the pipeline expects.
    return pd.DataFrame({
        'make': [car_object.make],
        'model': [car_object.model],
        'year': [car_object.year],
        'cylinders': [int(getattr(car_object, 'cylinders', 0) or 0)],
        'displacement': [float(getattr(car_object, 'displacement', 0.0) or 0.0)],
        'mileage': [int(mileage)]
    })