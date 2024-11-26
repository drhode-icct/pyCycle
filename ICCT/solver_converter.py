# solver_converter.py

"""
solver_converter.py

This module provides classes and functions to define solver pairs in a manner similar to NPSS,
and automatically sets up the corresponding PyCycle balance objects. It abstracts the PyCycle
balance setup, allowing for a more intuitive definition of independent and dependent variables.

Usage Example:

    from solver_converter import SolverConverter
    import openmdao.api as om

    prob = om.Problem()
    model = prob.model

    # Add a BalanceComp to the model without promoting its variables
    balance = om.BalanceComp()
    model.add_subsystem('balance', balance)  # No promotion here

    # Initialize the SolverConverter with the balance component and the model
    converter = SolverConverter(balance, model)

    # Define Independent and Dependent Variables
    converter.add_independent(
        name="Burner_FAR",
        var_name="burner_FAR",
        units=None,  # Specify units if needed
        val=0.017  # Initial guess
    )
    converter.add_dependent(
        name="Des_T41",
        eq_lhs="TrbH_FS41_Tt",
        eq_rhs=2750,
        eq_units=None  # Specify equation units if needed
    )

    # Setup the solvers
    converter.setup_solver()

    # Add other components as needed
    # ...

    # Setup and run the problem
    prob.setup()
    prob.run_model()

    # Retrieve and print balance results
    print("\nBalance Results:")
    for balance_name in converter.balance.options['bal_names']:
        value = prob.get_val(f'balance.{balance_name}')
        print(f"{balance_name}: {value}")
"""

import re
from typing import Any, List, Optional
import openmdao.api as om


class IndependentVariable:
    """
    Represents an independent variable for the solver.
    """
    def __init__(self, name: str, var_name: str, units: Optional[str] = None,
                 lower: Optional[float] = None, upper: Optional[float] = None,
                 val: Optional[Any] = None):
        self.name = name
        self.var_name = var_name
        self.units = units
        self.lower = lower
        self.upper = upper
        self.val = val

    def __repr__(self):
        return (f"IndependentVariable(name={self.name}, var_name={self.var_name}, "
                f"units={self.units}, lower={self.lower}, upper={self.upper}, val={self.val})")


class DependentVariable:
    """
    Represents a dependent variable for the solver.
    """
    def __init__(self, name: str, eq_lhs: str, eq_rhs: Any,
                 eq_units: Optional[str] = None, lower: Optional[float] = None,
                 upper: Optional[float] = None, val: Optional[Any] = None):
        self.name = name
        self.eq_lhs = eq_lhs
        self.eq_rhs = eq_rhs
        self.eq_units = eq_units
        self.lower = lower
        self.upper = upper
        self.val = val

    def __repr__(self):
        return (f"DependentVariable(name={self.name}, eq_lhs={self.eq_lhs}, "
                f"eq_rhs={self.eq_rhs}, eq_units={self.eq_units}, lower={self.lower}, "
                f"upper={self.upper}, val={self.val})")


class SolverConverter:
    """
    Converts NPSS-style solver definitions to PyCycle balance setups.
    """
    def __init__(self, balance_component: om.BalanceComp, model: om.Group):
        """
        Initialize the SolverConverter with a PyCycle BalanceComp and the model.

        Parameters:
            balance_component (om.BalanceComp): The balance component to which solvers will be added.
            model (om.Group): The OpenMDAO model or group where connections will be made.
        """
        self.balance = balance_component
        self.model = model
        self.independents: List[IndependentVariable] = []
        self.dependents: List[DependentVariable] = []

    def add_independent(self, name: str, var_name: str, units: Optional[str] = None,
                       lower: Optional[float] = None, upper: Optional[float] = None,
                       val: Optional[Any] = None):
        """
        Add an independent variable.

        Parameters:
            name (str): Unique name for the independent variable.
            var_name (str): The variable name to vary.
            units (Optional[str]): Units of the variable.
            lower (Optional[float]): Lower bound for the variable.
            upper (Optional[float]): Upper bound for the variable.
            val (Optional[Any]): Initial guess or value.
        """
        independent = IndependentVariable(name, var_name, units, lower, upper, val)
        self.independents.append(independent)
        print(f"Added independent variable: {independent}")

    def add_dependent(self, name: str, eq_lhs: str, eq_rhs: Any,
                     eq_units: Optional[str] = None, lower: Optional[float] = None,
                     upper: Optional[float] = None, val: Optional[Any] = None):
        """
        Add a dependent variable.

        Parameters:
            name (str): Unique name for the dependent variable.
            eq_lhs (str): The left-hand side expression.
            eq_rhs (Any): The right-hand side expression or target value.
            eq_units (Optional[str]): Units for the equation.
            lower (Optional[float]): Lower bound for the balance.
            upper (Optional[float]): Upper bound for the balance.
            val (Optional[Any]): Initial guess or value.
        """
        dependent = DependentVariable(name, eq_lhs, eq_rhs, eq_units, lower, upper, val)
        self.dependents.append(dependent)
        print(f"Added dependent variable: {dependent}")

    def _parse_expression(self, expr: str) -> List[str]:
        """
        Parse an expression to extract variable names.

        Parameters:
            expr (str): The expression to parse.

        Returns:
            List[str]: A list of variable names found in the expression.
        """
        # Simple regex to match variable names (e.g., 'burner_FAR', 'TrbH_FS41_Tt')
        pattern = r'[A-Za-z_][A-Za-z0-9_]*'
        return re.findall(pattern, expr)

    def setup_solver(self):
        """
        Set up the PyCycle balance solvers based on the added independent and dependent variables.
        """
        if len(self.independents) != len(self.dependents):
            raise ValueError("The number of independent variables must match the number of dependent variables.")

        for indep, dep in zip(self.independents, self.dependents):
            # Use the independent variable's name as the balance name
            balance_name = indep.name

            # Add a balance to the balance component
            self.balance.add_balance(
                name=balance_name,
                val=indep.val if indep.val is not None else 1.0,
                lower=indep.lower,
                upper=indep.upper,
                units=indep.units  # Use independent variable's units
            )

            # Connect the BalanceComp's output to the independent variable's input
            # balance.balance_name (output) -> independent.var_name (input)
            self.model.connect(f'balance.{balance_name}', indep.var_name)

            # Handle the LHS: connect dep.eq_lhs to balance.lhs:balance_name
            lhs_expr = dep.eq_lhs
            lhs_vars = self._parse_expression(lhs_expr)

            if len(lhs_vars) == 1:
                lhs_var = lhs_vars[0]
                # Connect the single variable to balance.lhs:balance_name
                self.model.connect(lhs_var, f'balance.lhs:{balance_name}')
            else:
                # Create an ExecComp to compute the LHS expression
                exec_comp_name = f'{balance_name}_lhs_comp'
                expr = f'{balance_name}_lhs = {lhs_expr}'
                self.model.add_subsystem(
                    exec_comp_name,
                    om.ExecComp(expr),
                    promotes_outputs=[f'{balance_name}_lhs']
                )
                # Connect all variables in the expression to the ExecComp
                for var in lhs_vars:
                    # Replace dots with underscores for valid variable names in ExecComp
                    var_exec = var.replace('.', '_')
                    self.model.connect(var, f'{exec_comp_name}.{var_exec}')
                # Connect the ExecComp output to balance.lhs:balance_name
                self.model.connect(f'{balance_name}_lhs', f'balance.lhs:{balance_name}')

            # Handle the RHS: connect dep.eq_rhs to balance.rhs:balance_name
            if isinstance(dep.eq_rhs, (int, float, complex)):
                # If eq_rhs is a constant, add an IndepVarComp
                const_comp_name = f'{balance_name}_rhs_const'
                self.model.add_subsystem(
                    const_comp_name,
                    om.IndepVarComp(f'{balance_name}_rhs', val=dep.eq_rhs),
                    promotes_outputs=[f'{balance_name}_rhs']
                )
                # Connect the constant to balance.rhs:balance_name
                self.model.connect(f'{balance_name}_rhs', f'balance.rhs:{balance_name}')
            elif isinstance(dep.eq_rhs, str):
                rhs_expr = dep.eq_rhs
                rhs_vars = self._parse_expression(rhs_expr)
                if len(rhs_vars) == 1:
                    rhs_var = rhs_vars[0]
                    # Connect the single variable to balance.rhs:balance_name
                    self.model.connect(rhs_var, f'balance.rhs:{balance_name}')
                else:
                    # Create an ExecComp to compute the RHS expression
                    exec_comp_name = f'{balance_name}_rhs_comp'
                    expr = f'{balance_name}_rhs = {rhs_expr}'
                    self.model.add_subsystem(
                        exec_comp_name,
                        om.ExecComp(expr),
                        promotes_outputs=[f'{balance_name}_rhs']
                    )
                    # Connect all variables in the expression to the ExecComp
                    for var in rhs_vars:
                        var_exec = var.replace('.', '_')
                        self.model.connect(var, f'{exec_comp_name}.{var_exec}')
                    # Connect the ExecComp output to balance.rhs:balance_name
                    self.model.connect(f'{balance_name}_rhs', f'balance.rhs:{balance_name}')
            else:
                raise TypeError(f"Unsupported type for eq_rhs: {type(dep.eq_rhs)}")

            print(f"Set up balance '{balance_name}' with lhs '{dep.eq_lhs}' and rhs '{dep.eq_rhs}' by varying '{indep.var_name}'.")

# example_usage.py

import openmdao.api as om
from solver_converter import SolverConverter

def main():
    # Create an OpenMDAO problem and model
    prob = om.Problem()
    model = prob.model

    # Add a BalanceComp to the model without promoting its variables
    balance = om.BalanceComp()
    model.add_subsystem('balance', balance)  # No promotion here

    # Initialize the SolverConverter with the balance component and the model
    converter = SolverConverter(balance, model)

    # Define Independent and Dependent Variables

    # Example 1: Vary burner_FAR to match TrbH_FS41_Tt = 2750
    converter.add_independent(
        name="Burner_FAR",
        var_name="burner_FAR",
        units=None,  # Specify units if needed
        val=0.017  # Initial guess
    )
    converter.add_dependent(
        name="Des_T41",
        eq_lhs="TrbH_FS41_Tt",
        eq_rhs=2750,
        eq_units=None  # Specify equation units if needed
    )

    # Example 2: Vary splitter_BPR to match NozSec_Fl_I_Pt / NozPri_Fl_I_Pt = 1.1
    converter.add_independent(
        name="Extraction_Ratio",
        var_name="splitter_BPR",
        units='inch**2',
        val=2.5,
        lower=2.0,
        upper=10.0
    )
    converter.add_dependent(
        name="Des_Extraction_Ratio",
        eq_lhs="NozSec_Fl_I_Pt / NozPri_Fl_I_Pt",
        eq_rhs=1.1,
        eq_units=None  # Specify equation units if needed
    )

    # Add Components to the Model
    # Ensure all promoted outputs have unique names to prevent conflicts

    # Dummy Burner component
    burner = om.IndepVarComp('burner_FAR', val=0.017, units=None)
    model.add_subsystem('burner', burner, promotes_outputs=['burner_FAR'])

    # Dummy TrbH component
    trbH = om.IndepVarComp('TrbH_FS41_Tt', val=3000.0, units=None)
    model.add_subsystem('TrbH', trbH, promotes_outputs=['TrbH_FS41_Tt'])

    # Dummy Splitter component
    splitter = om.IndepVarComp('splitter_BPR', val=2.5, units='inch**2')
    model.add_subsystem('splitter', splitter, promotes_outputs=['splitter_BPR'])

    # Dummy NozSec component
    nozSec = om.IndepVarComp('NozSec_Fl_I_Pt', val=1.1, units=None)
    model.add_subsystem('NozSec', nozSec, promotes_outputs=['NozSec_Fl_I_Pt'])

    # Dummy NozPri component
    nozPri = om.IndepVarComp('NozPri_Fl_I_Pt', val=1.0, units=None)
    model.add_subsystem('NozPri', nozPri, promotes_outputs=['NozPri_Fl_I_Pt'])

    # Setup the solvers
    converter.setup_solver()
    # Setup and run the problem
    prob.setup()
    prob.check_setup(show_browser=False)
    prob.run_model()
    prob.model.list_inputs()
    prob.model.list_outputs()

    # Retrieve and print balance results
    print("\nBalance Results:")
    for balance_name in converter.balance.options['bal_names']:
        value = prob.get_val(f'balance.{balance_name}')
        print(f"{balance_name}: {value}")

if __name__ == "__main__":
    main()