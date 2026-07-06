import pandas as pd
import matplotlib.pyplot as plt # Correct import
import os

def perform_data_analysis(file_path):
    # This function loads the data from the CSV, cleans it, and returns the DataFrame.
    print("Starting data loading and cleaning...")
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    
    print("\n--- Initial DataFrame Info ---")
    print(df.info())
    print("\n--- Initial DataFrame Head ---")
    print(df.head())

    # Now we need to clean the data by identifying and drop columns with placeholder values
    cols_to_drop = ['city_mpg', 'combination_mpg', 'highway_mpg']
    df = df.drop(columns=cols_to_drop, errors='ignore')
    
    # Fill NaN values with 0 before converting to integer
    df[['cylinders', 'displacement']] = df[['cylinders', 'displacement']].fillna(0)
    df['cylinders'] = df['cylinders'].astype(int)

    # Inspect the cleaned data
    print("\n--- Cleaned DataFrame Info ---")
    print(df.info())
    print("\n--- Cleaned DataFrame Head ---")
    print(df.head())

    # Return the cleaned DataFrame for use in other functions
    return df

def generate_cylinders_plot(df, file_path):
    # This function will generate and save a bar chart of the average cylinders per car make
    print("Generating plot...")

    # Here we calculate the average cylinders per car make
    average_cyls = df.groupby('make')['cylinders'].mean()
    
    # Now to create the bar chart
    fig, ax = plt.subplots()
    average_cyls.plot(kind='bar', ax=ax)

    # Set the title and labels for clarity
    ax.set_title('Average Cylinder per Car Make')
    ax.set_xlabel("Car Make")
    ax.set_ylabel("Average Cylinders") # Corrected method name
    
    plt.tight_layout()
    plt.savefig(file_path)

    print(f"Plot saved as {file_path}")

# We only need this block is for testing the script independently
if __name__ == "__main__":
    df = perform_data_analysis("car_data.csv")
    if df is not None:
        generate_cylinders_plot(df, "avg_cylinders_plot.png")