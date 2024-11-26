import sys
import pycycle.api as pyc

def viewer(prob, pt, file=sys.stdout):
    """
    print a report of all the relevant cycle properties
    """

    if pt == 'DESIGN':
        MN = prob['DESIGN.fc.Fl_O:stat:MN']
        LPT_PR = prob['DESIGN.balance.lpt_PR']
        HPT_PR = prob['DESIGN.balance.hpt_PR']
        FAR = prob['DESIGN.balance.FAR']
    else:
        MN = prob[pt+'.fc.Fl_O:stat:MN']
        LPT_PR = prob[pt+'.lpt.PR']
        HPT_PR = prob[pt+'.hpt.PR']
        FAR = prob[pt+'.balance.FAR']

    summary_data = (MN, prob[pt+'.fc.alt'], prob[pt+'.inlet.Fl_O:stat:W'], prob[pt+'.perf.Fn'],
                        prob[pt+'.perf.Fg'], prob[pt+'.inlet.F_ram'], prob[pt+'.perf.OPR'],
                        prob[pt+'.perf.TSFC'], prob[pt+'.splitter.BPR'])

    print(file=file, flush=True)
    print(file=file, flush=True)
    print(file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                              POINT:", pt, file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                       PERFORMANCE CHARACTERISTICS", file=file, flush=True)
    print("    Mach      Alt       W      Fn      Fg    Fram     OPR     TSFC      BPR ", file=file, flush=True)
    print(" %7.5f  %7.1f %7.3f %7.1f %7.1f %7.1f %7.3f  %7.5f  %7.3f" %summary_data, file=file, flush=True)


    fs_names = ['fc.Fl_O', 'inlet.Fl_O', 'fan.Fl_O', 'splitter.Fl_O1', 'splitter.Fl_O2',
                'duct4.Fl_O', 'lpc.Fl_O', 'duct6.Fl_O', 'hpc.Fl_O', 'bld3.Fl_O', 'burner.Fl_O',
                'hpt.Fl_O', 'duct11.Fl_O', 'lpt.Fl_O', 'duct13.Fl_O', 'core_nozz.Fl_O', 'byp_bld.Fl_O',
                'duct15.Fl_O', 'byp_nozz.Fl_O']
    fs_full_names = [f'{pt}.{fs}' for fs in fs_names]
    pyc.print_flow_station(prob, fs_full_names, file=file)

    comp_names = ['fan', 'lpc', 'hpc']
    comp_full_names = [f'{pt}.{c}' for c in comp_names]
    pyc.print_compressor(prob, comp_full_names, file=file)

    pyc.print_burner(prob, [f'{pt}.burner'], file=file)

    turb_names = ['hpt', 'lpt']
    turb_full_names = [f'{pt}.{t}' for t in turb_names]
    pyc.print_turbine(prob, turb_full_names, file=file)

    noz_names = ['core_nozz', 'byp_nozz']
    noz_full_names = [f'{pt}.{n}' for n in noz_names]
    pyc.print_nozzle(prob, noz_full_names, file=file)

    shaft_names = ['hp_shaft', 'lp_shaft']
    shaft_full_names = [f'{pt}.{s}' for s in shaft_names]
    pyc.print_shaft(prob, shaft_full_names, file=file)

    bleed_names = ['hpc', 'bld3', 'byp_bld']
    bleed_full_names = [f'{pt}.{b}' for b in bleed_names]
    pyc.print_bleed(prob, bleed_full_names, file=file)