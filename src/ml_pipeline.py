import os
import joblib
import pandas as pd
import sqlite3
from sklearn.linear_model import LinearRegression
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline   


def load_data_for_training(db_name ):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    
    # Load data into a pandas DataFrame
    df = pd.read_sql_query("SELECT * FROM cars", conn)
    df = df.rename(columns={'engine_size': 'displacement'})  # Rename for consistency with the model's expected input
    
    # Close the connection
    conn.close()
    
    return df

def process_data(df):
    # First we need to drop noise
    df = df.drop(columns=['id'], errors='ignore')  # Drop 'id' if it exists, ignore if it doesn't

    # 1. Define which columns need encoding and which are already numbers
    categorical_features = ['make', 'model']
    numerical_features = ['year', 'cylinders', 'displacement', 'mileage']

    # 2. Build the Transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', drop='first'), categorical_features)
        ],
        remainder='passthrough' # Keeps the numerical columns as they are
    )

    # 3. Create the Bundle
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])
    return model_pipeline

def train_model(model_pipeline, df):
    # Separate features and target variable
    X = df.drop('price', axis=1)
    y = df['price']
    
    
    model_pipeline.fit(X, y)
    
    return model_pipeline

# --- RUN THE FULL ARCHITECTURE ---
if __name__ == "__main__":
    # Change this in your __main__ block
    db_name = os.path.join('database', 'car_data.db')
    raw_df = load_data_for_training(db_name)
    raw_df = raw_df.drop(columns=['id']) # Drop ID here
    
    # Get the structure
    my_pipeline = process_data(raw_df)
    
    # Train the structure
    final_model = train_model(my_pipeline, raw_df)
    
    # Save the FULL trained pipeline
    model_filename = os.path.join('models', 'final_model.joblib')
    joblib.dump(final_model, model_filename)
    
    print("\nSUCCESS: End-to-End Pipeline Complete and Model Saved.")