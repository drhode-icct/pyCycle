# generate_outputs.py

import pandas as pd

def generate_outputs(results, output_filename='engine_outputs.csv'):
    """
    Generates outputs from the simulation results.

    Parameters:
    results (list): A list of dictionaries containing simulation outputs.
    output_filename (str): The name of the output CSV file.

    Returns:
    None
    """
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Write to CSV
    results_df.to_csv(output_filename, index=False)

    # Print the results
    print("\nSimulation Results:")
    print(results_df)