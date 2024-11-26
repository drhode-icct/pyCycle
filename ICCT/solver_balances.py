import openmdao.api as om
from balance_setup import Independent, Dependent, Solver
# Create a balance component
# Balances can be a bit confusing, here's some explanation -
#   State Variables:
#           (W)        Inlet mass flow rate to implictly balance thrust
#                      LHS: perf.Fn  == RHS: Thrust requirement (set when TF is instantiated)
#
#           (FAR)      Fuel-air ratio to balance Tt4
#                      LHS: burner.Fl_O:tot:T  == RHS: Tt4 target (set when TF is instantiated)
#
#           (lpt_PR)   LPT press ratio to balance shaft power on the low spool
#           (hpt_PR)   HPT press ratio to balance shaft power on the high spool
# Ref: look at the XDSM diagrams in the pyCycle paper and this:
# http://openmdao.org/twodocs/versions/latest/features/building_blocks/components/balance_comp.html

def add_design_balances(self):
    """Add balances specific to the design point."""
    # Define the balances using the specified format
    self.add_subsystem('solver', NPSSolver(), promotes=['*'])
    # Dependent: Target_Fnet
    Target_Fnet = Dependent('Target_Fnet', eq_lhs='perf.Fn', eq_rhs='Fn_DES')

    # Independent: W
    W = Independent(varName='fc.W', dxLimit=0.05, dxLimitType='Absolute')

    # Add to solver
    self.solver.addIndependent(W)
    self.solver.addDependent(Target_Fnet)

    # You can define additional Independents and Dependents similarly
    # For example, balancing FAR to achieve T4_MAX
    Target_T4 = Dependent('Target_T4', eq_lhs='burner.Fl_O:tot:T', eq_rhs='T4_MAX')
    Des_FAR = Independent(varName='burner.Fl_I:FAR', dxLimit=0.01, dxLimitType='Absolute')

    self.solver.addIndependent(Des_FAR)
    self.solver.addDependent(Target_T4)
    '''
    # Balancing LPT pressure ratio to match shaft power
    LPT_Pwr_Balance = Dependent('LPT_Pwr_Balance', eq_lhs='lp_shaft.pwr_in_real', eq_rhs='lp_shaft.pwr_out_real')
    LPT_PR = Independent('LPT_PR', varName='lpt.PR', dxLimit=0.5, dxLimitType='Absolute')

    solver.addIndependent(LPT_PR)
    solver.addDependent(LPT_Pwr_Balance)

    # Balancing HPT pressure ratio to match shaft power
    HPT_Pwr_Balance = Dependent('HPT_Pwr_Balance', eq_lhs='hp_shaft.pwr_in_real', eq_rhs='hp_shaft.pwr_out_real')
    HPT_PR = Independent('HPT_PR', varName='hpt.PR', dxLimit=0.5, dxLimitType='Absolute')

    solver.addIndependent(HPT_PR)
    solver.addDependent(HPT_Pwr_Balance)
    '''
def add_off_design_balances(self,solver):
    """Add balances specific to off-design points."""

    # Off-design balances
    throttle_mode = self.options['throttle_mode']

    '''
    if throttle_mode == 'T4':
        # Balance FAR to achieve T4_MAX
        Target_T4 = Dependent('Target_T4', eq_lhs='burner.Fl_O:tot:T', eq_rhs='T4_MAX')
        Des_FAR = Independent('Des_FAR', varName='burner.Fl_I:FAR', dxLimit=0.01, dxLimitType='Absolute')

        solver.addIndependent(Des_FAR)
        solver.addDependent(Target_T4)

    elif throttle_mode == 'percent_thrust':
        # Balance FAR to achieve percentage of maximum thrust
        Des_FAR = Independent(
            name='Des_FAR',
            varName='burner.Fl_I:FAR',
            val=0.017,
            units=None,
            eq_units='lbf',
            use_mult=True,
            mult_val=1.0,  # PC will be used as the multiplicative factor
            dxLimit=0.01,
            dxLimitType='Absolute'
        )

        Target_Fn = Dependent(
            name='Target_Fn',
            eq_lhs='perf.Fn',
            eq_rhs='PC * Fn_max',
            eq_units='lbf'
        )

        solver.addIndependent(Des_FAR)
        solver.addDependent(Target_Fn)
        # Note: You may need to include scaling for 'PC' (percentage command)
    '''

    # Additional off-design balances can be defined similarly
    # For mass flow rate (W) to match core nozzle area
    '''
    Core_Nozzle_Area_Balance = Dependent('Core_Nozzle_Area_Balance', eq_lhs='core_nozz.Throat:stat:area',
                                         eq_rhs='design_core_nozz_area')
    Des_W = Independent('Des_W', varName='fc.W', dxLimit=50.0, dxLimitType='Absolute')

    solver.addIndependent(Des_W)
    solver.addDependent(Core_Nozzle_Area_Balance)

    # For bypass ratio (BPR) to match bypass nozzle area
    Bypass_Nozzle_Area_Balance = Dependent('Bypass_Nozzle_Area_Balance', eq_lhs='byp_nozz.Throat:stat:area',
                                           eq_rhs='design_byp_nozz_area')
    Des_BPR = Independent('Des_BPR', varName='splitter.BPR', dxLimit=0.1, dxLimitType='Absolute')

    solver.addIndependent(Des_BPR)
    solver.addDependent(Bypass_Nozzle_Area_Balance)

    '''
    # For LP shaft speed (LP_Nmech) balance
    LP_Shaft_Pwr_Balance = Dependent('LP_Shaft_Pwr_Balance', eq_lhs='lp_shaft.pwr_in_real',
                                     eq_rhs='lp_shaft.pwr_out_real')
    Des_LP_Nmech = Independent('Des_LP_Nmech', varName='LP_Nmech', dxLimit=500.0, dxLimitType='Absolute')

    solver.addIndependent(Des_LP_Nmech)
    solver.addDependent(LP_Shaft_Pwr_Balance)

    # For HP shaft speed (HP_Nmech) balance
    HP_Shaft_Pwr_Balance = Dependent('HP_Shaft_Pwr_Balance', eq_lhs='hp_shaft.pwr_in_real',
                                     eq_rhs='hp_shaft.pwr_out_real')
    Des_HP_Nmech = Independent('Des_HP_Nmech', varName='HP_Nmech', dxLimit=500.0, dxLimitType='Absolute')

    solver.addIndependent(Des_HP_Nmech)
    solver.addDependent(HP_Shaft_Pwr_Balance)


