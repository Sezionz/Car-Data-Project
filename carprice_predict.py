import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

def train_and_save_model(file_path, model_filename):
    print("Loading data for model training...")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return

    # --- DEBUGGING LINE ---
    print(f"DEBUG: Data loaded successfully. Columns found: {list(df.columns)}")
    # ----------------------

    # Now, explicitly check for the columns we need to prevent KeyError
    required_cols = ['make', 'model', 'year', 'cylinders', 'displacement', 'mileage', 'price']
    if not all(col in df.columns for col in required_cols):
        print("ERROR: CSV is missing one or more required columns for prediction.")
        print(f"Expected columns: {required_cols}")
        print(f"Actual columns found: {list(df.columns)}")
        return

    # Drop columns not needed for this simple model
    # Note: We commented this out in the previous step, so let's stick to explicitly selecting columns

    # Fill NaN values with 0
    df[['cylinders', 'displacement', 'mileage']] = df[['cylinders', 'displacement', 'mileage']].fillna(0)

    # ... rest of the model code continues below this point ...
    # ... (The rest of the code is unchanged from the last successful version) ...
    # ...

    # Define the features and the target
    features = ['make', 'model', 'year', 'cylinders', 'displacement', 'mileage']
    X = df[features]
    y = df['price']
    
    # ... (rest of model training and saving code) ...

    # The unchanged model pipeline setup goes here...
    categorical_features = ['make', 'model']
    numerical_features = ['year', 'cylinders', 'displacement', 'mileage']
    
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.linear_model import LinearRegression
    from sklearn.pipeline import Pipeline
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='passthrough'
    )
    
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])

    print("Training the model...")
    model_pipeline.fit(X, y)
    joblib.dump(model_pipeline, model_filename)
    
    print(f"Model trained and saved as '{model_filename}'")


if __name__ == "__main__":
    data_file = "car_prices.csv"
    model_file = "car_price_model.joblib"
    train_and_save_model(data_file, model_file)