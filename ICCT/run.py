# run_simulation.py
from bokeh.io import output_file
import time
from simulation_core import run_simulations
from generate_outputs import generate_outputs

def main():

    # User specifies the input CSV file and model selection
    engine_parameters_file = 'doe_input.csv'  # Specify your CSV file here
    engine_model_name = 'HBTF'  # Options: 'HBTF', add more as needed
    thermo_method = 'CEA'  # Options: 'CEA', 'TABULAR'
    summary_output_filename='summary_output.csv'


    # Run simulations
    simulation_results = run_simulations(engine_parameters_file, engine_model_name, thermo_method)

    # Generate outputs
    generate_outputs(simulation_results, output_filename=summary_output_filename)

if __name__ == '__main__':
    st = time.time()
    main()

    print()
    print("Run time", time.time() - st)