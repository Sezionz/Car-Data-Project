import os
import sqlite3
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression

class CarPricePipeline:
    def __init__(self, model_path='models/final_model.joblib'):
        self.model_path = model_path
        self.pipeline = None


    def fit(self, df):
        """
        Fits the pipeline to the data. 
        Standard Scikit-Learn interface: fit(X, y)
        """
        # Separate features and target
        X = df.drop('price', axis=1)
        y = df['price']
        
        # Build the pipeline if it doesn't exist
        if self.pipeline is None:
            self.pipeline = self._build_pipeline()
            
        # Perform the fit
        self.pipeline.fit(X, y)
        print("Pipeline fitted successfully.")
        return self  # Returning self is a standard sklearn convention

    def _build_pipeline(self):
        """Internal method to define the structure."""
        categorical_features = ['make', 'model']
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore', drop='first'), categorical_features)
            ],
            remainder='passthrough'
        )

        return Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', LinearRegression())
        ])

    def load_and_prepare_data(self, db_name):
        """Extracts and formats data from SQLite."""
        conn = sqlite3.connect(db_name)
        df = pd.read_sql_query("SELECT * FROM cars", conn)
        conn.close()
        
        df = df.rename(columns={'engine_size': 'displacement'})
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
        return df

    def train(self, df):
        """Builds and fits the pipeline."""
        self.pipeline = self._build_pipeline()
        X = df.drop('price', axis=1)
        y = df['price']
        self.pipeline.fit(X, y)
        self.save_model()
        print("Pipeline trained and saved successfully.")

    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.pipeline, self.model_path)

    def load_model(self):
        if os.path.exists(self.model_path):
            self.pipeline = joblib.load(self.model_path)
        else:
            raise FileNotFoundError(f"No model found at {self.model_path}")

    def predict(self, input_df):
        """Inference wrapper."""
        if not self.pipeline:
            self.load_model()
        return self.pipeline.predict(input_df)

# --- RUN THE ARCHITECTURE ---
if __name__ == "__main__":
    db_path = os.path.join('database', 'car_data.db')
    
    # Initialize and Run
    trainer = CarPricePipeline()
    raw_data = trainer.load_and_prepare_data(db_path)
    trainer.train(raw_data)