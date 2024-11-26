# get_engine_model.py

def get_engine_model(model_name):
    """
    Returns the engine model class based on the model name.

    Parameters:
    model_name (str): The name of the engine model.

    Returns:
    class: The engine model class.
    """
    if model_name == 'HBTF':
        from HBTF_engine_model import HBTFEngineModel
        return HBTFEngineModel
    else:
        raise ValueError(f"Engine model '{model_name}' is not recognized.")