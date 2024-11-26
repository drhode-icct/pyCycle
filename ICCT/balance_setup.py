# balance_setup.py

import openmdao.api as om
import re
import warnings


def extract_variables(expr):
    """
    Helper function to extract variable names from an expression.
    """
    tokens = re.findall(r'\b[A-Za-z_][A-Za-z0-9_.:]*\b', expr)
    return tokens


class NPSSDependent:
    def __init__(self, eq_lhs, eq_rhs, value_rhs=None, eq_units=None,name='no_name',interconnect_rhs=False, promotion_lhs=None):
        self.eq_lhs = eq_lhs
        self.eq_rhs = eq_rhs
        self.value_rhs = value_rhs
        self.eq_units = eq_units
        self.name = name
        self.interconnect_rhs = interconnect_rhs
        self.promotion_lhs = promotion_lhs

    def create_component(self):
        """
        Creates an OpenMDAO component that computes the residual of the dependent equation.
        """
        # Extract variables from the equations
        lhs_vars = extract_variables(self.eq_lhs)
        rhs_vars = extract_variables(self.eq_rhs)
        all_vars = set(lhs_vars + rhs_vars)

        # Map variable names to valid Python identifiers
        var_map = {var: var.replace('.', '_') for var in all_vars}

        # Replace variable names in the expressions
        eq_lhs_comp = self.eq_lhs
        eq_rhs_comp = self.eq_rhs
        for var in all_vars:
            eq_lhs_comp = eq_lhs_comp.replace(var, f'inputs["{var_map[var]}"]')
            eq_rhs_comp = eq_rhs_comp.replace(var, f'inputs["{var_map[var]}"]')

        # Compute the residual expression
        compute_expression = f'outputs["residual"] = {eq_lhs_comp} - ({eq_rhs_comp})'

        # Define the component class dynamically
        eq_units = self.eq_units  # Capture in closure

        class DependentComponent(om.ExplicitComponent):
            def setup(self_inner):
                # Declare output
                self_inner.add_output('residual', val=0.0, units=eq_units)
                # Declare inputs
                for var in all_vars:
                    var_name = var_map[var]
                    self_inner.add_input(var_name, val=0.0, units=eq_units)
                    # Declare partials (use finite difference)

                    self_inner.declare_partials('residual', var_name, method='fd', form='central', step=1e-6)

            def compute(self_inner, inputs, outputs):
                # Evaluate the residual expression
                exec(compute_expression, {}, {'inputs': inputs, 'outputs': outputs})
        return DependentComponent()


class NPSSIndependent:
    def __init__(self, name, varName, units=None, val=None, lower=None, upper=None):
        self.name = name
        self.varName = varName
        self.units = units
        self.val = val
        self.lower = lower
        self.upper = upper


# Modify your existing Solver class to include the addPair method
def addPair(self, balance, Dependent_obj, Independent_obj):
    """
    Sets up the OpenMDAO model based on the Dependent and Independent objects.
    """
    if Dependent_obj.name == 'no_name':
        warnings.warn(message=f'Set a name for the dependent with eq_rhs: {Dependent_obj.eq_rhs} and eq_lhs: {Dependent_obj.eq_lhs}.', category=UserWarning, stacklevel=2)

    # Create the Dependent component and add it to the model
    dep_comp = Dependent_obj.create_component()
    self.add_subsystem(f'dependent_comp_{Dependent_obj.name}', dep_comp)

    # Add the balance variable
    balance.add_balance(Independent_obj.name, val=Independent_obj.val, lower=Independent_obj.lower,
                        upper=Independent_obj.upper, units=Independent_obj.units,
                        eq_units=Dependent_obj.eq_units)

    # Connect the balance variable to the Independent variable in the model
    self.connect(f'balance.{Independent_obj.name}', Independent_obj.varName)

    # Connect the residual from the Dependent component to the balance component
    self.connect(f'dependent_comp_{Dependent_obj.name}.residual', f'balance.lhs:{Independent_obj.name}')

    # Handle RHS value
    if Dependent_obj.value_rhs != None:
        rhs_name = f'rhs_{Independent_obj.name}'
        balance.add_input(rhs_name, val=Dependent_obj.value_rhs, units=Dependent_obj.eq_units)
        self.connect(f'{rhs_name}', f'balance.rhs:{Independent_obj.name}')
    else:
        pass

    # Map variable names
    all_vars = set(extract_variables(Dependent_obj.eq_lhs) + extract_variables(Dependent_obj.eq_rhs))
    var_map = {var: var.replace('.', '_') for var in all_vars}

    # Connect variables to the Dependent component
    for var in all_vars:
        var_name = var_map[var]
        rhs_vars = [v for v in re.split(r'[*/+\-\s]+', Dependent_obj.eq_rhs.strip()) if v]
        if var in rhs_vars:
            # Create an IndepVarComp for the RHS variable if not already in the model
            if not hasattr(self, f'{var_name}_comp'):
                if Dependent_obj.interconnect_rhs:
                    self.connect(f'{var}', f'dependent_comp_{Dependent_obj.name}.{var_name}')
                else:
                    if Dependent_obj.value_rhs == None:
                        self.add_subsystem(f'{var_name}_comp',
                                           om.IndepVarComp(var_name, val=0.0,
                                                           units=Dependent_obj.eq_units), promotes_outputs=[f'{var_name}'])

                    else:
                        self.add_subsystem(f'{var_name}_comp',
                                           om.IndepVarComp(var_name, val=Dependent_obj.value_rhs,
                                                           units=Dependent_obj.eq_units), promotes_outputs=[f'{var_name}'])
                    self.connect(f'{var_name}', f'dependent_comp_{Dependent_obj.name}.{var_name}')

        else:
            if var == Dependent_obj.promotion_lhs:

                self.connect(var, f'dependent_comp_{Dependent_obj.name}.{var_name}')
            else:
            # Connect existing variables from the model
                self.connect(var, f'dependent_comp_{Dependent_obj.name}.{var_name}')