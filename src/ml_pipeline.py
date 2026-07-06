import pandas as pd
import sqlite3
from sklearn.linear_model import LinearRegression

def load_data_for_training(db_name = 'car_data.db'):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    
    # Load data into a pandas DataFrame
    df = pd.read_sql_query("SELECT * FROM cars", conn)
    
    # Close the connection
    conn.close()
    
    return df

def process_data(df):
    # First we need to drop noise
    df.drop(columns=['id'])

    # Here we use one-hopt encoding for categorical variables
    df = pd.get_dummies(df, columns=['make', 'model'],  drop_first=True) # We drop the first category to avoid multicollinearity (multicollinearity occurs when one feature can be linearly predicted from the others with a substantial degree of accuracy)
    
    return df

def train_model(df):
    # Separate features and target variable
    X = df.drop('price', axis=1)
    y = df['price']
    
    # Initialize and train the model
    model = LinearRegression()
    model.fit(X, y)
    
    return model

# --- RUN THE FULL ARCHITECTURE ---
if __name__ == "__main__":
    print("1. Extracting data from SQLite...")
    raw_df = load_data_for_training()
    
    print("2. Preprocessing and encoding features...")
    clean_df = process_data(raw_df)
    
    print("3. Training the Linear Regression Model...")
    final_model = train_model(clean_df)
    
    print("\nSUCCESS: End-to-End Pipeline Complete.")