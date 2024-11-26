# collect_outputs.py

def collect_outputs(prob, case_number):
    """
    Collects outputs from the model after running the simulation.

    Parameters:
    prob (om.Problem): The OpenMDAO problem instance.

    Returns:
    dict: A dictionary of output values.
    """
    outputs = {
        'CASE': case_number,
        'Fn_DESIGN': prob.get_val('DESIGN.perf.Fn', units='lbf'),
        'TSFC_DESIGN': prob.get_val('DESIGN.perf.TSFC', units='lbm/(lbf*h)'),
        'OPR_DESIGN': prob.get_val('DESIGN.perf.OPR')
        # Add more outputs as needed
    }

    return outputs