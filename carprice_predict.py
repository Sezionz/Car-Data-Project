import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

def train_and_save_model(file_path, model_filename):
    """
    Loads data, trains a price prediction model, and saves it.
    """
    print("Loading data for model training...")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return

    # Drop columns not needed for this simple model
    df = df.drop(columns=['city_mpg', 'combination_mpg', 'highway_mpg'])

    # Fill NaN values with 0
    df[['cylinders', 'displacement']] = df[['cylinders', 'displacement']].fillna(0)

    # Define the features and the target
    # We will use 'year', 'cylinders', 'displacement', and 'mileage' as numerical features
    # and 'make' and 'model' as categorical features.
    X = df[['make', 'model', 'year', 'cylinders', 'displacement', 'mileage']]
    y = df['price']

    # Identify categorical and numerical features for the preprocessor
    categorical_features = ['make', 'model']
    numerical_features = ['year', 'cylinders', 'displacement', 'mileage']

    # Create a preprocessor to handle both categorical and numerical data
    preprocessor = ColumnTransformer(
        transformers=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='passthrough'
    )
    
    # Create the model pipeline
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])

    print("Training the model...")
    # Train the model
    model_pipeline.fit(X, y)

    # Save the trained model to a file
    joblib.dump(model_pipeline, model_filename)
    
    print(f"Model trained and saved as '{model_filename}'")


if __name__ == "__main__":
    # The file containing our car prices
    data_file = "car_prices.csv"
    # The file where we will save the trained model
    model_file = "car_price_model.joblib"
    
    train_and_save_model(data_file, model_file)