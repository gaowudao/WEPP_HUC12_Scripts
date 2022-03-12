import os,shutil
import pandas as pd


def move_cli_files(wshed,source_scen,clim):

    dest_scen_lst = ['CC_10','CC_20','CC_B',\
                     'CT_50', 'CT_100', 'CT_B',\
                     'Per_0','Per_B','Per_m20','Per_p20']

    for dest_scen in dest_scen_lst:

        source_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/{}/{}/wepp/runs/'.format(wshed,source_scen,clim)
        dest_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/New_Runs/{}/{}/wepp/runs/'.format(wshed,clim,dest_scen)

        for file in os.listdir(source_dir):
            if file.endswith('.cli'):

                source_path = str(source_dir + file)
                dest_path = str(dest_dir + file)

                shutil.copy(source_path,dest_path)


mod_lst = ['B3_59', 'B3_99', 'B4_59', 'B4_99',\
           'L3_59', 'L3_99', 'L4_59', 'L4_99']


for mod in mod_lst:

    move_cli_files('ST1','Comb',mod)