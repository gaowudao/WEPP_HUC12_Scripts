def run_wepp(wepppy_win_dir, mod_dir, scen_lst):
    '''
    Runs wepp using the run_project.py script in rogderlew's wepppy 
    repository. This allows all hillslopes within each scenario directory
    to be run without need of the GUI.
    '''

    import os

    os.chdir(wepppy_win_dir)

    #Run for all management scenarios in a given climate model directory
    for scen in scen_lst:
        cli_scen_dir = str(mod_dir + scen)
        os.system('python3 run_project.py {}'.format(cli_scen_dir))

wepppy_win_dir = 'C:/Users/Garner/Soil_Erosion_Project/wepppy-win-bootstrap-master/scripts'

wshed_lst = ['DO1']

scen_lst = ['CC_10/','CC_20/','CC_B/',\
            'CT_50/', 'CT_100/', 'CT_B/',\
            'Per_0/','Per_B/','Per_m20/','Per_p20/']

mod_lst = ['B3_59', 'B3_99', 'B4_59', 'B4_99',\
           'L3_59', 'L3_99', 'L4_59', 'L4_99',\
           'Obs']

for wshed in wshed_lst:
    for mod in mod_lst:
        mod_dir = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/New_Runs/{}/'.format(wshed,mod))
        run_wepp(wepppy_win_dir, mod_dir, scen_lst)