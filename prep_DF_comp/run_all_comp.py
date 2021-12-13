from clip_GDS_files import clip_GDS
from hillslope_subset_sel import select_subset_hs
from prep_wepp_inputs.CMIP5_to_CLI.Generate_calibrated_cli_files import gen_cli_file
from prep_wepp_inputs.Assign_Cli_Files import assign_cli_files

import pandas as pd
import os
import numpy as np


def run_comparsion(HUC12_path, dwnsc_type, subset_ID, years, obs_cli_xlsx, HUC12_name):
    '''
    Sets up input data for subset of WEPP hillslopes, runs the model for them,
    and then compares the runoff and erosion outputs to observed data from the 
    Discovery Farms Project (Minnesota Dept. of Agriculture)
    '''
    #Define paths to GDS, PAR, uncalibrated, and observed directories, and
    #climate model IDs 
    GDS_path_source = str(HUC12_path + '/GDS/{}/'.format(dwnsc_type))
    GDS_path_subset = str(HUC12_path + '/GDS/{}/'.format(str(dwnsc_type + subset_ID)))
    uncal_path = str(HUC12_path + '/Uncalibrated/{}/'.format(dwnsc_type + subset_ID))
    obs_path = str(HUC12_path + '/obs_data/{}'.format(obs_cli_xlsx))
    par_path = str(HUC12_path + '/PAR/{}/'.format(dwnsc_type + subset_ID))

    #Use cli_GDS to create new GDS files that only include years that match the obs data
    clip_GDS(GDS_path_source, GDS_path_subset, '19', years)

    #
    gen_cli_file(GDS_path_subset, HUC12_name, uncal_path, obs_path, '19', '59', par_path)





model_labels = ['L1','L2','L3','L4','L5','L6',\
                'B1','B2','B3','B4','B5','B6']
target_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/GO1_DEP/Runs/wepp/runs/'
source_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/GO1_DEP/Runs/wepp/runs/'

DEP_DF_lst = ['p14', 'p26', 'p66', 'p70', 'p374']


source = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/BE1/GDS/BCCA/'
new = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/BE1/GDS/BCCA_sub/'
years = ['12','13','14','15','16']

clip_GDS(source, new, '19', years)