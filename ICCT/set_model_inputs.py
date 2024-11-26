# set_model_inputs.py

import pandas as pd
def set_model_inputs(prob, row):
    """
    Sets the model inputs from the row data.
    Parameters:
    prob (om.Problem): The OpenMDAO problem instance.
    row (pd.Series): The row data from the input DataFrame.
    """
    # Define a mapping from CSV columns to model variables
    variable_definitions = {

        'MN_DES':
            {'actual_variable': 'DESIGN.fc.MN',
             'default': 0.8,
             'unit': None,
             'description': 'Design point Mach number'},

        'alt_DES':
            {'actual_variable': 'DESIGN.fc.alt',
             'default': 35000.0,
             'unit': 'ft',
             'description': 'Design point altitude'},

        'Fn_DES':
            {'actual_variable': 'DESIGN.Fn_DES',
             'default': 50000,
             'unit': 'lbf',
             'description': 'Design point thrust'},

        'T4_max_DES':
            {'actual_variable': 'DESIGN.T4_MAX',
             'default': 2800,
             'unit': 'degR',
             'description': 'Maxmimum T4 design point temperature'},

        'LP_Nmech_DES':
            {'actual_variable': 'DESIGN.LP_Nmech',
             'default': 5000,
             'unit': 'rpm',
             'description': 'Design LP shaft speed'},

        'HP_Nmech_DES':
            {'actual_variable': 'DESIGN.HP_Nmech',
             'default': 15000,
             'unit': 'rpm',
             'description': 'Design HP shaft speed'},

        # Component efficiencies and PRs at design point
        'fan_PR_DES':
            {'actual_variable': 'DESIGN.fan.PR',
             'default': 1.3,
             'unit': None,
             'description': 'Design point fan pressure ratio'},

        'fan_eff_DES':
            {'actual_variable': 'DESIGN.fan.eff',
             'default': 1.0,
             'unit': None,
             'description': 'Design point fan efficiency'},

        'lpc_PR_DES':
            {'actual_variable': 'DESIGN.lpc.PR',
             'default': 3.0,
             'unit': None,
             'description': 'Design point lpc pressure ratio'},

        'lpc_eff_DES':
            {'actual_variable': 'DESIGN.lpc.eff',
             'default': 1.0,
             'unit': None,
             'description': 'Design point lpc efficiency'},

        'hpc_PR_DES':
            {'actual_variable': 'DESIGN.hpc.PR',
             'default': 10.0,
             'unit': None,
             'description': 'Design point hpc pressure ratio'},

        'hpc_eff_DES':
            {'actual_variable': 'DESIGN.hpc.eff',
             'default': 1.0,
             'unit': None,
             'description': 'Design point hpc efficiency'},

        'hpt_eff_DES':
            {'actual_variable': 'DESIGN.hpt.eff',
             'default': 1.0,
             'unit': None,
             'description': 'Design point hpt efficiency'},

        'lpt_eff_DES':
            {'actual_variable': 'DESIGN.lpt.eff',
             'default': 1.0,
             'unit': None,
             'description': 'Design point lpt efficiency'},

        # Initial guesses
        'FAR_DES':
            {'actual_variable': 'DESIGN.balance.FAR',
             'default': 0.025,
             'unit': None,
             'description': 'Guess for design point fuel-to-air ratio'},

        'W_DES':
            {'actual_variable': 'DESIGN.balance.W',
             'default': 100.0,
             'unit': 'lbm/s',
             'description': 'Guess for design point air flow rate'
            },

        'lpt_PR_DES':
            {'actual_variable': 'DESIGN.balance.lpt_PR',
             'default': 1.5,
             'unit': None,
             'description': 'Guess for design point lpt pressure ratio'
             },

        'hpt_PR_DES':
            {'actual_variable': 'DESIGN.balance.hpt_PR',
            'default': 3.0,
             'unit': None,
             'description': 'Guess for design point hpt pressure ratio'
            },

        # Default assumptions
        'inlet_ram_recovery':
            {'actual_variable': 'inlet.ram_recovery',
             'default': 0.9990,
             'unit': None,
             'description': 'Inlet ram recovery'},

        'duct4_dPqP':
            {'actual_variable': 'duct4.dPqP',
             'default': 0.0048,
             'unit': None,
             'description': 'Pressure drop ratio in duct4'},

        'duct6_dPqP':
            {'actual_variable': 'duct6.dPqP',
             'default': 0.0101,
             'unit': None,
             'description': 'Pressure drop ratio in duct6'},

        'burner_dPqP':
            {'actual_variable': 'burner.dPqP',
             'default': 0.0540,
             'unit': None,
             'description': 'Pressure drop ratio in burner'},

        'duct11_dPqP':
            {'actual_variable': 'duct11.dPqP',
             'default': 0.0051,
             'unit': None,
             'description': 'Pressure drop ratio in duct11'},

        'duct13_dPqP':
            {'actual_variable': 'duct13.dPqP',
             'default': 0.0107,
             'unit': None,
             'description': 'Pressure drop ratio in duct13'},

        'duct15_dPqP':
            {'actual_variable': 'duct15.dPqP',
             'default': 0.0149,
             'unit': None,
             'description': 'Pressure drop ratio in duct15'},

        'core_nozz_Cv':
            {'actual_variable': 'core_nozz.Cv',
             'default': 0.9933,
             'unit': None,
             'description': 'Core nozzle coefficient of velocity'},

        'byp_bld_frac_W':
            {'actual_variable': 'byp_bld.bypBld:frac_W',
             'default': 0.005,
             'unit': None,
             'description': 'Bypass bleed fraction'},

        'byp_nozz_Cv':
            {'actual_variable': 'byp_nozz.Cv',
             'default': 0.9939,
             'unit': None,
             'description': 'Bypass nozzle coefficient of velocity'},

        'hpc_cool1_frac_W':
            {'actual_variable': 'hpc.cool1:frac_W',
             'default': 0.050708,
             'unit': None,
             'description': 'HPC cooling 1 fraction of air flow rate'},

        'hpc_cool1_frac_P':
            {'actual_variable': 'hpc.cool1:frac_P',
             'default': 0.5,
             'unit': None,
             'description': 'HPC cooling 1 fraction of pressure'},

        'hpc_cool1_frac_work':
            {'actual_variable': 'hpc.cool1:frac_work',
             'default': 0.5,
             'unit': None,
             'description': 'HPC cooling 1 fraction of work'},

        'hpc_cool2_frac_W':
            {'actual_variable': 'hpc.cool2:frac_W',
             'default': 0.020274,
             'unit': None,
             'description': 'HPC cooling 2 fraction of air flow rate'},

        'hpc_cool2_frac_P':
            {'actual_variable': 'hpc.cool2:frac_P',
             'default': 0.55,
             'unit': None,
             'description': 'HPC cooling 2 fraction of pressure'},

        'hpc_cool2_frac_work':
            {'actual_variable': 'hpc.cool2:frac_work',
             'default': 0.5,
             'unit': None,
             'description': 'HPC cooling 2 fraction of work'},

        'bld3_cool3_frac_W':
            {'actual_variable': 'bld3.cool3:frac_W',
             'default': 0.067214,
             'unit': None,
             'description': 'Bleed 3 cooling 3 fraction of air flow rate'},

        'bld3_cool4_frac_W':
            {'actual_variable': 'bld3.cool4:frac_W',
             'default': 0.101256,
             'unit': None,
             'description': 'Bleed 3 cooling 4 fraction of air flow rate'},

        'hpc_cust_frac_P':
            {'actual_variable': 'hpc.cust:frac_P',
             'default': 0.5,
             'unit': None,
             'description': 'HPC custom fraction of pressure'},

        'hpc_cust_frac_work':
            {'actual_variable': 'hpc.cust:frac_work',
             'default': 0.5,
             'unit': None,
             'description': 'HPC custom fraction of work'},

        'hpc_cust_frac_W':
            {'actual_variable': 'hpc.cust:frac_W',
             'default': 0.0445,
             'unit': None,
             'description': 'HPC custom fraction of air flow rate'},

        'hpt_cool3_frac_P':
            {'actual_variable': 'hpt.cool3:frac_P',
             'default': 1.0,
             'unit': None,
             'description': 'HPT cooling 3 fraction of pressure'},

        'hpt_cool4_frac_P':
            {'actual_variable': 'hpt.cool4:frac_P',
             'default': 0.0,
             'unit': None,
             'description': 'HPT cooling 4 fraction of pressure'},

        'lpt_cool1_frac_P':
            {'actual_variable': 'lpt.cool1:frac_P',
             'default': 1.0,
             'unit': None,
             'description': 'LPT cooling 1 fraction of pressure'},

        'lpt_cool2_frac_P':
            {'actual_variable': 'lpt.cool2:frac_P',
             'default': 0.0,
             'unit': None,
             'description': 'LPT cooling 2 fraction of pressure'},

        'hp_shaft_HPX':
            {'actual_variable': 'hp_shaft.HPX',
             'default': 250.0,
             'unit': 'hp',
             'description': 'HP Shaft power in horsepower'},

        'inlet_MN_DES':
            {
                'actual_variable': 'DESIGN.inlet.MN',
                'default': 0.751,
                'unit': None,
                'description': 'Inlet Mach number at design'
            },

        'fan_MN_DES':
            {
                'actual_variable': 'DESIGN.fan.MN',
                'default': 0.4578,
                'unit': None,
                'description': 'Fan Mach number at design'
            },

        'splitter_BPR_DES':
            {
                'actual_variable': 'DESIGN.splitter.BPR',
                'default': 5.105,
                'unit': None,
                'description': 'Splitter Bypass ratio at design'
            },
        'splitter_MN1_DES':
            {
                'actual_variable': 'DESIGN.splitter.MN1',
                'default': 0.3104,
                'unit': None,
                'description': 'Splitter Mach number 1 at design'
            },
        'splitter_MN2_DES':
            {
                'actual_variable': 'DESIGN.splitter.MN2',
                'default': 0.4518,
                'unit': None,
                'description': 'Splitter Mach number 2 at design'
            },
        'duct4_MN_DES':
            {
                'actual_variable': 'DESIGN.duct4.MN',
                'default': 0.3121,
                'unit': None,
                'description': 'Duct 4 Mach number at design'
            },
        'lpc_MN_DES':
            {
                'actual_variable': 'DESIGN.lpc.MN',
                'default': 0.3059,
                'unit': None,
                'description': 'Low-pressure compressor Mach number at design'
            },
        'duct6_MN_DES':
            {
                'actual_variable': 'DESIGN.duct6.MN',
                'default': 0.3563,
                'unit': None,
                'description': 'Duct 6 Mach number at design'
            },
        'hpc_MN_DES':
            {
                'actual_variable': 'DESIGN.hpc.MN',
                'default': 0.2442,
                'unit': None,
                'description': 'High-pressure compressor Mach number at design'
            },
        'bld3_MN_DES':
            {
                'actual_variable': 'DESIGN.bld3.MN',
                'default': 0.3000,
                'unit': None,
                'description': 'Bleed 3 Mach number at design'
            },
        'burner_MN_DES':
            {
                'actual_variable': 'DESIGN.burner.MN',
                'default': 0.1025,
                'unit': None,
                'description': 'Burner Mach number at design'
            },
        'hpt_MN_DES':
            {
                'actual_variable': 'DESIGN.hpt.MN',
                'default': 0.3650,
                'unit': None,
                'description': 'High-pressure turbine Mach number at design'
            },
        'duct11_MN_DES':
            {
                'actual_variable': 'DESIGN.duct11.MN',
                'default': 0.3063,
                'unit': None,
                'description': 'Duct 11 Mach number at design'
            },
        'lpt_MN_DES':
            {
                'actual_variable': 'DESIGN.lpt.MN',
                'default': 0.4127,
                'unit': None,
                'description': 'Low-pressure turbine Mach number at design'
            },
        'duct13_MN_DES':
            {
                'actual_variable': 'DESIGN.duct13.MN',
                'default': 0.4463,
                'unit': None,
                'description': 'Duct 13 Mach number at design'
            },
        'byp_bld_MN_DES':
            {
                'actual_variable': 'DESIGN.byp_bld.MN',
                'default': 0.4489,
                'unit': None,
                'description': 'Bypass bleed Mach number at design'
            },
        'duct15_MN_DES':
            {
                'actual_variable': 'DESIGN.duct15.MN',
                'default': 0.4589,
                'unit': None,
                'description': 'Duct 15 Mach number at design'
            },
        'lp_power_diff_DES':
            {'actual_variable': 'DESIGN.lp_power_diff',
             'default': 0.0,
             'unit': 'hp',
             'description': 'Design point lpt power difference'},

        'hp_power_diff_DES':
            {'actual_variable': 'DESIGN.hp_power_diff',
             'default': 0.0,
             'unit': 'hp',
             'description': 'Design point hpt power difference'},

        # Off-design point inputs
        'T4_MAX_OD_full_pwr':
            {'actual_variable': 'OD_full_pwr.T4_MAX',
             'default': 2800,
             'unit': 'degR',
             'description': 'Maximum T4 off-design point temperature'},

        'Fn_Target_OD_part_pwr':
        {'actual_variable': 'OD_part_pwr.Fn_Target',
         'default': 5300,
         'unit': 'lbf',
         'description': 'Maximum off-design point thrust'},

    }

    # Set each input value
    for col_name, info in variable_definitions.items():
        var_name = info['actual_variable']
        unit = info['unit']
        default = info['default']
        try:
            value = row[col_name]
            if col_name in row and not pd.isnull(row[col_name]):
                try:
                    if unit:
                        prob.set_val(var_name, value, units=unit)
                    else:
                        prob.set_val(var_name, value)
                except Exception as e:
                    print(f"Error setting value for {var_name}: {e}")
        except KeyError:
            try:
                if unit:
                    prob.set_val(var_name, default, units=unit)
                else:
                    prob.set_val(var_name, default)
            except Exception as e:
                print(f"Error setting value for {var_name}: {e}")
            continue

