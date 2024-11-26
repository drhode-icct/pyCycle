# read_inputs.py

import pandas as pd

def read_input_csv(filename='doe_input.csv'):
    """
    Reads the input CSV file and returns a pandas DataFrame.

    Parameters:
    filename (str): The path to the CSV file.

    Returns:
    pd.DataFrame: The input data.
    """
    try:
        input_data = pd.read_csv(filename)
        print(f"Successfully read input file '{filename}'.")
        return input_data
    except FileNotFoundError:
        print(f"Error: Input file '{filename}' not found.")
        raise

