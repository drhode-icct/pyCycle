# HBTF_engine_model.py

import sys
import numpy as np
import openmdao.api as om
from prompt_toolkit.key_binding.bindings.named_commands import self_insert
from soupsieve.util import lower

import pycycle.api as pyc
from balance_setup import NPSSIndependent, NPSSDependent, addPair
import re
import warnings

class HBTFEngineModel(pyc.MPCycle):
    """
    A PyCycle model representing a High Bypass Turbofan (HBTF) engine.
    """

    def initialize(self):
        self.options.declare('thermo_method', default='CEA')
        super().initialize()

    def setup(self):
        thermo_method = self.options['thermo_method']

        # Add the design point
        self.pyc_add_pnt('DESIGN', HBTF(thermo_method=thermo_method))

        ##### THESE VALUES DON'T MEAN ANYTHING - ACTUAL DEFAULT VALUES ARE IN set_model_inputs.py
        ##### These are just to have the model started
        self.set_input_defaults('DESIGN.inlet.MN', 0.751)
        self.set_input_defaults('DESIGN.fan.MN', 0.4578)
        self.set_input_defaults('DESIGN.splitter.BPR', 5.105)
        self.set_input_defaults('DESIGN.splitter.MN1', 0.3104)
        self.set_input_defaults('DESIGN.splitter.MN2', 0.4518)
        self.set_input_defaults('DESIGN.duct4.MN', 0.3121)
        self.set_input_defaults('DESIGN.lpc.MN', 0.3059)
        self.set_input_defaults('DESIGN.duct6.MN', 0.3563)
        self.set_input_defaults('DESIGN.hpc.MN', 0.2442)
        self.set_input_defaults('DESIGN.bld3.MN', 0.3000)
        self.set_input_defaults('DESIGN.burner.MN', 0.1025)
        self.set_input_defaults('DESIGN.hpt.MN', 0.3650)
        self.set_input_defaults('DESIGN.duct11.MN', 0.3063)
        self.set_input_defaults('DESIGN.lpt.MN', 0.4127)
        self.set_input_defaults('DESIGN.duct13.MN', 0.4463)
        self.set_input_defaults('DESIGN.byp_bld.MN', 0.4489)
        self.set_input_defaults('DESIGN.duct15.MN', 0.4589)
        self.set_input_defaults('DESIGN.LP_Nmech', 4666.1, units='rpm')
        self.set_input_defaults('DESIGN.HP_Nmech', 14705.7, units='rpm')




        # --- Set up bleed values -----

        ##### THESE VALUES DON'T MEAN ANYTHING - ACTUAL DEFAULT VALUES ARE IN set_model_inputs.py
        ##### These are just to have the model started
        self.pyc_add_cycle_param('inlet.ram_recovery', 0.9990)
        self.pyc_add_cycle_param('duct4.dPqP', 0.0048)
        self.pyc_add_cycle_param('duct6.dPqP', 0.0101)
        self.pyc_add_cycle_param('burner.dPqP', 0.0540)
        self.pyc_add_cycle_param('duct11.dPqP', 0.0051)
        self.pyc_add_cycle_param('duct13.dPqP', 0.0107)
        self.pyc_add_cycle_param('duct15.dPqP', 0.0149)
        self.pyc_add_cycle_param('core_nozz.Cv', 0.9933)
        self.pyc_add_cycle_param('byp_bld.bypBld:frac_W', 0.005)
        self.pyc_add_cycle_param('byp_nozz.Cv', 0.9939)
        self.pyc_add_cycle_param('hpc.cool1:frac_W', 0.050708)
        self.pyc_add_cycle_param('hpc.cool1:frac_P', 0.5)
        self.pyc_add_cycle_param('hpc.cool1:frac_work', 0.5)
        self.pyc_add_cycle_param('hpc.cool2:frac_W', 0.020274)
        self.pyc_add_cycle_param('hpc.cool2:frac_P', 0.55)
        self.pyc_add_cycle_param('hpc.cool2:frac_work', 0.5)
        self.pyc_add_cycle_param('bld3.cool3:frac_W', 0.067214)
        self.pyc_add_cycle_param('bld3.cool4:frac_W', 0.101256)
        self.pyc_add_cycle_param('hpc.cust:frac_P', 0.5)
        self.pyc_add_cycle_param('hpc.cust:frac_work', 0.5)
        self.pyc_add_cycle_param('hpc.cust:frac_W', 0.0445)
        self.pyc_add_cycle_param('hpt.cool3:frac_P', 1.0)
        self.pyc_add_cycle_param('hpt.cool4:frac_P', 0.0)
        self.pyc_add_cycle_param('lpt.cool1:frac_P', 1.0)
        self.pyc_add_cycle_param('lpt.cool2:frac_P', 0.0)
        self.pyc_add_cycle_param('hp_shaft.HPX', 250.0, units='hp')


        # Add off-design points
        self.od_pts = ['OD_full_pwr', 'OD_part_pwr']

        self.od_MNs = [0.8, 0.8]
        self.od_alts = [35000.0, 35000.0]
        #self.od_Fn_target = [5500.0, 5300]
        self.od_dTs = [0.0, 0.0]

        self.pyc_add_pnt('OD_full_pwr', HBTF(design=False, thermo_method='CEA', throttle_mode='T4'))

        self.set_input_defaults('OD_full_pwr.fc.MN', 0.8)
        self.set_input_defaults('OD_full_pwr.fc.alt', 35000.0, units='ft')
        self.set_input_defaults('OD_full_pwr.fc.dTs', 0., units='degR')

        self.pyc_add_pnt('OD_part_pwr', HBTF(design=False, thermo_method='CEA', throttle_mode='percent_thrust'))

        self.set_input_defaults('OD_part_pwr.fc.MN', 0.8)
        self.set_input_defaults('OD_part_pwr.fc.alt', 35000.0, units='ft')
        self.set_input_defaults('OD_part_pwr.fc.dTs', 0., units='degR')

        #self.connect('OD_full_pwr.perf.Fn', 'Fn_max')

        self.pyc_use_default_des_od_conns()

        # Set up the RHS of the balances!
        self.pyc_connect_des_od('core_nozz.Throat:stat:area', 'balance.rhs:W')
        self.pyc_connect_des_od('byp_nozz.Throat:stat:area', 'balance.rhs:BPR')

        super().setup()

class HBTF(pyc.Cycle):
    def initialize(self):
        self.options.declare('design', default=True)
        self.options.declare('thermo_method', default='CEA')
        self.options.declare('throttle_mode', default='T4', values=['T4', 'percent_thrust'])

        super().initialize()

    def setup(self):
        design = self.options['design']
        thermo_method = self.options['thermo_method']
        throttle_mode = self.options['throttle_mode']

        if thermo_method == 'TABULAR':
            self.options['thermo_method'] = 'TABULAR'
            self.options['thermo_data'] = pyc.AIR_JETA_TAB_SPEC
            FUEL_TYPE = 'FAR'
        else:
            self.options['thermo_method'] = 'CEA'
            self.options['thermo_data'] = pyc.species_data.janaf
            FUEL_TYPE = 'Jet-A(g)'

        # Add components (same as in your provided code)
        # [Add all components and connections here as per your code]

        # Add subsystems to build the engine deck:
        self.add_subsystem('fc', pyc.FlightConditions())
        self.add_subsystem('inlet', pyc.Inlet())

        # Note variable promotion for the fan --
        # the LP spool speed and the fan speed are INPUTS that are promoted:
        # Note here that promotion aliases are used. Here Nmech is being aliased to LP_Nmech
        # check out: http://openmdao.org/twodocs/versions/latest/features/core_features/grouping_components/add_subsystem.html?highlight=alias
        self.add_subsystem('fan', pyc.Compressor(map_data=pyc.FanMap,
                                                 bleed_names=[], map_extrap=True),
                           promotes_inputs=[('Nmech', 'LP_Nmech')])
        self.add_subsystem('splitter', pyc.Splitter())
        self.add_subsystem('duct4', pyc.Duct())
        self.add_subsystem('lpc', pyc.Compressor(map_data=pyc.LPCMap,
                                                 map_extrap=True), promotes_inputs=[('Nmech', 'LP_Nmech')])
        self.add_subsystem('duct6', pyc.Duct())
        self.add_subsystem('hpc', pyc.Compressor(map_data=pyc.HPCMap,
                                                 bleed_names=['cool1', 'cool2', 'cust'], map_extrap=True),
                           promotes_inputs=[('Nmech', 'HP_Nmech')])
        self.add_subsystem('bld3', pyc.BleedOut(bleed_names=['cool3', 'cool4']))
        self.add_subsystem('burner', pyc.Combustor(fuel_type=FUEL_TYPE))
        self.add_subsystem('hpt', pyc.Turbine(map_data=pyc.HPTMap,
                                              bleed_names=['cool3', 'cool4'], map_extrap=True),
                           promotes_inputs=[('Nmech', 'HP_Nmech')])
        self.add_subsystem('duct11', pyc.Duct())
        self.add_subsystem('lpt', pyc.Turbine(map_data=pyc.LPTMap,
                                              bleed_names=['cool1', 'cool2'], map_extrap=True),
                           promotes_inputs=[('Nmech', 'LP_Nmech')])
        self.add_subsystem('duct13', pyc.Duct())
        self.add_subsystem('core_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))

        self.add_subsystem('byp_bld', pyc.BleedOut(bleed_names=['bypBld']))
        self.add_subsystem('duct15', pyc.Duct())
        self.add_subsystem('byp_nozz', pyc.Nozzle(nozzType='CV', lossCoef='Cv'))

        # Create shaft instances. Note that LP shaft has 3 ports! => no gearbox
        self.add_subsystem('lp_shaft', pyc.Shaft(num_ports=3), promotes_inputs=[('Nmech', 'LP_Nmech')])
        self.add_subsystem('hp_shaft', pyc.Shaft(num_ports=2), promotes_inputs=[('Nmech', 'HP_Nmech')])
        self.add_subsystem('perf', pyc.Performance(num_nozzles=2, num_burners=1))

        # Now use the explicit connect method to make connections -- connect(<from>, <to>)

        # Connect the inputs to perf group
        self.connect('inlet.Fl_O:tot:P', 'perf.Pt2')
        self.connect('hpc.Fl_O:tot:P', 'perf.Pt3')
        self.connect('burner.Wfuel', 'perf.Wfuel_0')
        self.connect('inlet.F_ram', 'perf.ram_drag')
        self.connect('core_nozz.Fg', 'perf.Fg_0')
        self.connect('byp_nozz.Fg', 'perf.Fg_1')

        # LP-shaft connections
        self.connect('fan.trq', 'lp_shaft.trq_0')
        self.connect('lpc.trq', 'lp_shaft.trq_1')
        self.connect('lpt.trq', 'lp_shaft.trq_2')
        # HP-shaft connections
        self.connect('hpc.trq', 'hp_shaft.trq_0')
        self.connect('hpt.trq', 'hp_shaft.trq_1')
        # Ideally expanding flow by conneting flight condition static pressure to nozzle exhaust pressure
        self.connect('fc.Fl_O:stat:P', 'core_nozz.Ps_exhaust')
        self.connect('fc.Fl_O:stat:P', 'byp_nozz.Ps_exhaust')

        balance = self.add_subsystem('balance', om.BalanceComp())

        from openmdao.core.explicitcomponent import ExplicitComponent


        if design:

            # Define Dependent and Independent variables using original names
            Dependent_Fn_DES = NPSSDependent(
                name='Fn_DES',
                eq_lhs='perf.Fn',
                eq_rhs='Fn_DES',
                eq_units='lbf'
            )
            Independent_W = NPSSIndependent(
                name='W',
                varName='fc.W',
                units='lbm/s')

            addPair(self,balance,Dependent_Fn_DES, Independent_W)

            # Define Dependent and Independent variables using original names
            Dependent_T4_MAX = NPSSDependent(
                name='T4_MAX',
                eq_lhs='burner.Fl_O:tot:T',
                eq_rhs='T4_MAX',
                eq_units='degR'
            )
            Independent_FAR = NPSSIndependent(
                name='FAR',
                varName='burner.Fl_I:FAR',
                units=None)

            addPair(self,balance,Dependent_T4_MAX, Independent_FAR)

            Dependent_lp_pwr_diff_new = NPSSDependent(
                name='lp_pwr_diff',
                eq_lhs='lp_shaft.pwr_in_real + lp_shaft.pwr_out_real',
                eq_rhs='lp_power_diff',
                eq_units='hp'
            )
            Independent_lpt_PR = NPSSIndependent(
                name='lpt_PR',
                varName='lpt.PR',
                units=None,
                val=1.5,
                lower=1.001,
                upper=16,
                )

            addPair(self,balance,Dependent_lp_pwr_diff_new, Independent_lpt_PR)

            Dependent_hp_pwr_diff_new = NPSSDependent(
                name='hp_pwr_diff',
                eq_lhs='hp_shaft.pwr_in_real + hp_shaft.pwr_out_real',
                eq_rhs='hp_power_diff',
                eq_units='hp'
            )
            Independent_hpt_PR = NPSSIndependent(
                name='hpt_PR',
                varName='hpt.PR',
                units=None,
                val=1.5,
                lower=1.001,
                upper=8,
            )

            addPair(self,balance,Dependent_hp_pwr_diff_new, Independent_hpt_PR)
        else:

            # In OFF-DESIGN mode we need to redefine the balances:
            #   State Variables:
            #           (W)        Inlet mass flow rate to balance core flow area
            #                      LHS: core_nozz.Throat:stat:area == Area from DESIGN calculation
            #
            #           (FAR)      Fuel-air ratio to balance Thrust req.
            #                      LHS: perf.Fn  == RHS: Thrust requirement (set when TF is instantiated)
            #
            #           (BPR)      Bypass ratio to balance byp. noz. area
            #                      LHS: byp_nozz.Throat:stat:area == Area from DESIGN calculation
            #
            #           (lp_Nmech)   LP spool speed to balance shaft power on the low spool
            #           (hp_Nmech)   HP spool speed to balance shaft power on the high spool

            if self.options['throttle_mode'] == 'T4':

                Independent_FAR = NPSSIndependent(
                    name='FAR',
                    varName='burner.Fl_I:FAR',
                    units=None,
                    val=0.017,
                    lower=1e-4,
                    upper=1.0,
                )

                Dependent_T4_MAX_OFFDES = NPSSDependent(
                    name='T4_MAX_OFFDES',
                    eq_lhs='burner.Fl_O:tot:T',
                    eq_rhs='T4_MAX',
                    eq_units='degR',
                )

                addPair(self,balance,Dependent_T4_MAX_OFFDES, Independent_FAR)


            elif self.options['throttle_mode'] == 'percent_thrust':

                Independent_FAR_OFFDES = NPSSIndependent(
                    name='FAR',
                    varName='burner.Fl_I:FAR',
                    units=None,
                    val=0.017,
                    lower=1e-4,
                    upper=1.0,
                )

                Dependent_Fn_OFFDES = NPSSDependent(
                    name='Fn_OFFDES',
                    eq_lhs='perf.Fn',
                    eq_rhs='Fn_Target',
                    eq_units='lbf',
                )

                addPair(self,balance,Dependent_Fn_OFFDES, Independent_FAR_OFFDES)

            Independent_W = NPSSIndependent(
                name='W',
                varName='fc.W',
                units='lbm/s',
                val=100.,
                lower=10.,
                upper=1000.,
            )

            Dependent_core_nozz_Throat_stat_area = NPSSDependent(
                name='core_nozz_Throat_stat_area',
                eq_lhs='core_nozz.Throat:stat:area',
                eq_rhs='rhs_zero_core_nozz_Throat_stat_area',
                eq_units='inch**2',
            )

            addPair(self,balance,Dependent_core_nozz_Throat_stat_area, Independent_W)

            Independent_BPR = NPSSIndependent(
                name='BPR',
                varName='splitter.BPR',
                units=None,
                val=2.0,
                lower=1.0,
                upper=10.0,
            )

            Dependent_byp_nozz_Throat_stat_area = NPSSDependent(
                name='byp_nozz_Throat_stat_area',
                eq_lhs='byp_nozz.Throat:stat:area',
                eq_rhs='rhs_zero_byp_nozz_Throat_stat_area',
                eq_units='inch**2',
            )

            addPair(self,balance,Dependent_byp_nozz_Throat_stat_area, Independent_BPR)

            Independent_lp_Nmech = NPSSIndependent(
                name='lp_Nmech',
                varName='LP_Nmech',
                units='rpm',
                val=1.5,
                lower=500.,
            )

            Dependent_lp_shaft_pwr_net = NPSSDependent(
                name='lp_shaft_pwr_in_real',
                eq_lhs='lp_shaft.pwr_in_real + lp_shaft.pwr_out_real',
                eq_rhs='lp_power_diff',
                eq_units='hp',
            )

            addPair(self,balance,Dependent_lp_shaft_pwr_net, Independent_lp_Nmech)

            Independent_hp_Nmech = NPSSIndependent(
                name='hp_Nmech',
                varName='HP_Nmech',
                units='rpm',
                val=1.5,
                lower=500.,
            )

            Dependent_hp_shaft_pwr_net = NPSSDependent(
                name='hp_shaft_pwr_in_real',
                eq_lhs='hp_shaft.pwr_in_real + hp_shaft.pwr_out_real',
                eq_rhs='hp_power_diff',
                eq_units='hp',
            )

            addPair(self,balance,Dependent_hp_shaft_pwr_net, Independent_hp_Nmech)


        # Set up all the flow connections:
        self.pyc_connect_flow('fc.Fl_O', 'inlet.Fl_I')
        self.pyc_connect_flow('inlet.Fl_O', 'fan.Fl_I')
        self.pyc_connect_flow('fan.Fl_O', 'splitter.Fl_I')
        self.pyc_connect_flow('splitter.Fl_O1', 'duct4.Fl_I')
        self.pyc_connect_flow('duct4.Fl_O', 'lpc.Fl_I')
        self.pyc_connect_flow('lpc.Fl_O', 'duct6.Fl_I')
        self.pyc_connect_flow('duct6.Fl_O', 'hpc.Fl_I')
        self.pyc_connect_flow('hpc.Fl_O', 'bld3.Fl_I')
        self.pyc_connect_flow('bld3.Fl_O', 'burner.Fl_I')
        self.pyc_connect_flow('burner.Fl_O', 'hpt.Fl_I')
        self.pyc_connect_flow('hpt.Fl_O', 'duct11.Fl_I')
        self.pyc_connect_flow('duct11.Fl_O', 'lpt.Fl_I')
        self.pyc_connect_flow('lpt.Fl_O', 'duct13.Fl_I')
        self.pyc_connect_flow('duct13.Fl_O', 'core_nozz.Fl_I')
        self.pyc_connect_flow('splitter.Fl_O2', 'byp_bld.Fl_I')
        self.pyc_connect_flow('byp_bld.Fl_O', 'duct15.Fl_I')
        self.pyc_connect_flow('duct15.Fl_O', 'byp_nozz.Fl_I')

        # Bleed flows:
        self.pyc_connect_flow('hpc.cool1', 'lpt.cool1', connect_stat=False)
        self.pyc_connect_flow('hpc.cool2', 'lpt.cool2', connect_stat=False)
        self.pyc_connect_flow('bld3.cool3', 'hpt.cool3', connect_stat=False)
        self.pyc_connect_flow('bld3.cool4', 'hpt.cool4', connect_stat=False)

        #Specify solver settings:
        newton = self.nonlinear_solver = om.NewtonSolver()
        newton.options['atol'] = 1e-6

        # set this very small, so it never activates and we rely on atol
        newton.options['rtol'] = 1e-99
        newton.options['iprint'] = 1
        newton.options['maxiter'] = 50
        newton.options['solve_subsystems'] = True
        newton.options['max_sub_solves'] = 1000
        newton.options['reraise_child_analysiserror'] = False
        newton.options['err_on_non_converge'] = True

        newton.options['debug_print'] = False #True for Debugging

        # ls = newton.linesearch = BoundsEnforceLS()
        ls = newton.linesearch = om.ArmijoGoldsteinLS()
        ls.options['stall_limit'] = 50
        ls.options['err_on_non_converge'] = True
        ls.options['maxiter'] = 3
        ls.options['rho'] = 0.75
        ls.options['print_bound_enforce'] = True

        self.linear_solver = om.DirectSolver()

        warnings.filterwarnings('ignore', category=om.SolverWarning)

        super().setup()