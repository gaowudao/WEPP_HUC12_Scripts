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
        cli_scen_dir = str(scen_dir + mod_lab)
        os.system('python3 run_project.py {}'.format(cli_scen_dir))

wepppy_win_dir = 'C:/Users/Garner/Soil_Erosion_Project/wepppy-win-bootstrap-master/scripts'
wshed_lst = ['ST1']
scen_lst = ['CC','Comb','CT','NC','Per']
model_labs = ['B3_59/', 'B3_99/', 'B4_59/', 'B4_99/',\
              'L3_59/', 'L3_99/', 'L4_59/', 'L4_99/']

for wshed in wshed_lst:
    for scen in scen_lst:
        scen_dir = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/{}/'.format(wshed,scen))
        run_wepp(wepppy_win_dir, scen_dir, model_labs)