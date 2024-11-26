# simulation_core.py
import openmdao as om
from openmdao.test_suite.components.sellar import SellarNoDerivatives

from openmdao.api import Problem
from get_engine_model import get_engine_model
from read_inputs import read_input_csv
from set_model_inputs import set_model_inputs
from collect_outputs import collect_outputs
from viewout_builder import viewer
from utils import old_files_cleaning
import contextlib
import sys
import logging
import os

def run_simulations(engine_parameters_file, engine_model_name, thermo_method):
    """
    Runs simulations based on the input CSV file and engine model.

    Parameters:
    engine_parameters_file (str): Path to the input CSV file.
    engine_model_name (str): Name of the engine model to use.
    thermo_method (str): Thermodynamic method to use ('CEA' or 'TABULAR').

    Returns:
    list: A list of dictionaries containing simulation outputs.
    """
    
    # Read input data
    input_data = read_input_csv(engine_parameters_file)
    print('DOE is read...')
    print(f'Number of cases: {len(input_data)}')

    old_files_cleaning()


    # Get the engine model class
    EngineModelClass = get_engine_model(engine_model_name)

    # Prepare to collect results
    all_results = []


    # Loop over each row in the input data
    for index, row in input_data.iterrows():
        
        
        print(f"\nCASE {index + 1}")

        # Initialize the problem for each simulation
        prob = Problem()
        prob.model = EngineModelClass(thermo_method=thermo_method)
        prob.setup(check=False)

        prob.set_solver_print(level=-1)
        prob.set_solver_print(level=2, depth=1)

        # Set input variables from the CSV row
        set_model_inputs(prob, row)

        for pt in ['OD_full_pwr', 'OD_part_pwr']:
            # initial guesses
            prob[pt + '.balance.FAR'] = 0.02467
            prob[pt + '.balance.W'] = 300
            prob[pt + '.balance.BPR'] = 5.105
            prob[pt + '.balance.lp_Nmech'] = 5000
            prob[pt + '.balance.hp_Nmech'] = 15000
            prob[pt + '.hpt.PR'] = 3.
            prob[pt + '.lpt.PR'] = 4.
            prob[pt + '.fan.map.RlineMap'] = 2.0
            prob[pt + '.lpc.map.RlineMap'] = 2.0
            prob[pt + '.hpc.map.RlineMap'] = 2.0

        #prob.model.list_inputs(prom_name=False, hierarchical=False, out_stream=sys.stdout)
        #prob.model.list_outputs(prom_name=False, hierarchical=False, out_stream=sys.stdout)
        prob.set_solver_print(level=-1)
        prob.set_solver_print(level=2, depth=1)

        # Check partial derivatives
        #prob.check_partials(compact_print=True)


        # Enable debugging for nonlinear and linear solvers
        #prob.model.nonlinear_solver.options['iprint'] = 2
        #prob.model.linear_solver.options['iprint'] = 2

        #prob.model.list_outputs(prom_name=False,implicit=False, hierarchical=False, out_stream=viewer_file, print_arrays=True)
        first_pass = True
        print(f"Running the model...")

        om.visualization.connection_viewer.viewconns.view_connections(prob, show_values=True, outfile="sellar_connections.html", show_browser=False)

        #print(prob.get_val('DESIGN.lp_shaft.pwr_net_real'))
        #print(prob.get_val('DESIGN.lpt_power_diff'))
        # Run the model
        prob.run_model()

        print(f"Collecting outputs...")
        if first_pass:
            with open(f'\nview{index+1}_DES.out', 'w') as viewout_file:
                viewer(prob, 'DESIGN', file=viewout_file)
            first_pass = False
        with open(f'\nview{index + 1}_100.out', 'w') as viewout_file:
            viewer(prob, 'OD_full_pwr', file=viewout_file)

        std_outputs = open(f'\nstd_outputs{index + 1}.out', 'w')

        OD_Uninstalled_viewer_file = open(f'\nview{index + 1}_part_pwr.out', 'w')
        for PC in [1, 0.9, 0.8, .7]:
            print(f'## PC = {PC}')
            prob['OD_part_pwr.Fn_Target'] = prob['OD_full_pwr.perf.Fn'] * PC
            prob.run_model()
            viewer(prob, 'OD_part_pwr', file=OD_Uninstalled_viewer_file)


        prob.model.list_outputs(prom_name=False,implicit=False, hierarchical=False, out_stream=std_outputs, print_arrays=True)
        # Collect outputs
        outputs = collect_outputs(prob,index+1)
        all_results.append(outputs)
        print('Case ran.')

    return all_results