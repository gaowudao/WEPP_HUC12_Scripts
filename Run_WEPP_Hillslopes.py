def run_wepp(wepppy_win_dir, scen_dir, model_labs):
    '''
    Runs wepp using the run_project.py script in rogderlew's wepppy 
    repository. This allows all hillslopes within each scenario directory
    to be run without need of the GUI.
    '''

    import os

    os.chdir(wepppy_win_dir)

    #Run for all climate scenarios in a given management 'scen_dir'
    for mod_lab in model_labs:
        cli_scen_dir = str(scen_dir + mod_lab + '_19/')
        os.system('python3 run_project.py {}'.format(cli_scen_dir))
