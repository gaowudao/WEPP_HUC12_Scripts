#!/usr/bin/env python
# coding: utf-8

# In[27]:


import pandas as pd
import numpy as np
import os
from statistics import mean
import matplotlib.pyplot as plt
from functools import reduce, partial
import math
from sklearn.metrics import mean_squared_error
import statsmodels.api as sm




def analyze_RO(add_years, start_crop1_yrs, start_crop2_yrs, crop1_obs_yrs, crop2_obs_yrs, scen_dir, mod_labels, excel_parent_path, obs_path, scenario):
    '''
    Compares WEPP runoff outputs with observed datasets from the Mn Discovery
    Farms Project.Runoff outputs are split by crop.
    
    start_yrs_ = years in first rotation
    
    add_years = num of years to add onto starting years in each rotation dependent
    on crop rotation
    
    '''
    
    ##### Prepare modeled data #####
    
    #list of years selected for each crop (output for separating the crops in rotation)
    crop1_years = []
    crop2_years = []
    
    #loop through add_years
    for rot_add in add_years:

        def create_crop_yrs(rot_add, start_lst, append_lst):
            '''
            creates list of years for each crop within a rotation
            '''
            #add 
            new_lst = [x+rot_add for x in start_lst]

            for val in new_lst:
                append_lst.append(int(val))

        #run for crops in rotation        
        create_crop_yrs(rot_add, start_crop1_yrs, crop1_years)
        create_crop_yrs(rot_add, start_crop2_yrs, crop2_years)

    def Get_Monthly_WEPP_Data(mod_lab, crop_yrs, crop_name):

        '''
        Daily values from .cli and .ebe files are combined into monthly totals and 
        averaged over all years and hillslopes. The function can be run for individual
        crops within a rotation or for all years in a run (crops not separated). 

        Hillslope runoff event data and climate data are loaded into dataframes and then
        append to a list after the necessary calculations are performed.

        crop_years = a list of the years in which a certain crop is present
        crop_name = name of crop
        '''

        #Set path to hillslope outputs and inputs(runs)
        out_files_dir = str(scen_dir + mod_lab + '_' + '19' + '\\' + 'wepp' + '\\' + 'output' + '\\')
        run_files_dir = str(scen_dir + mod_lab + '_' + '19' + '\\' + 'wepp' + '\\' + 'runs' + '\\')

        #Get file names for each hillslope output
        out_hill_names = [x for x in os.listdir(out_files_dir) if x.endswith('.ebe.dat')]

        #And same for climate inputs
        in_hill_names = [x for x in os.listdir(run_files_dir) if x.endswith('.cli')]


        ebe_col_list = ['Day', 'Month', 'Year', 'Precip', 'RO', 'IR-det',\
                        'Av-det', 'Mx-det', 'Point', 'Av-dep', 'Mx-dep',\
                        'Point_2', 'Sed-Del', 'ER']

        #Create lists for output dataframes
        WEPP_Events_lst = []
        WEPP_cli_lst = []


        #read each csv file into a dataframe. Columns are seperated by
        #uneven number of spaces
        for hill in out_hill_names:
            data = pd.read_csv(str(out_files_dir + hill), skiprows = 3, names = ebe_col_list, sep = '\s+', header=None)

            ind_crop = data[data['Year'].isin(crop_yrs)]

            #Perform groupby on dataframes to calculate total monthly
            # events and RO for the individual hillslope
            HS_month_events = ind_crop.groupby('Month')['RO'].count() / len(crop_yrs)
            HS_month_RO = ind_crop.groupby('Month')['RO'].sum() / len(crop_yrs)

            HS_month_comb = pd.DataFrame({'RO':HS_month_RO, 'Total RO Events':HS_month_events})

            WEPP_Events_lst.append(HS_month_comb)

        for cli_file in in_hill_names:
            #Read cligen file data into dataframe and remove row with units
            cli_data = pd.read_csv(str(run_files_dir + cli_file), skiprows = 13, sep = '\s+| ', engine = 'python')
            cli_data.drop([0,], axis = 0, inplace = True)
            cli_data['Pr'] = cli_data['prcp'].astype(float)
            cli_data['Month'] = cli_data['mo'].astype(int)
            cli_data['year'] = cli_data['year'].astype(int)

            cli_crop = cli_data[cli_data['year'].isin(crop_yrs)]

            # Get mean of monthly data 
            cli_avg = (cli_crop.groupby('Month')[['Pr']].sum()) / len(crop_yrs)
            pr_e_df = cli_crop.groupby('Month').agg(lambda x: x.ne(0).sum()) / len(crop_yrs)
            cli_avg['Pr_e'] = pr_e_df['Pr']

            WEPP_cli_lst.append(cli_avg)


        # Sum .cli data and get average hillslope values
        WEPP_pr_data = sum(WEPP_cli_lst) / 5
        WEPP_Events_data = reduce(lambda x, y: x.add(y, fill_value=0), WEPP_Events_lst) / 5

        #Combine climate and runoff event dataframes
        WEPP_data = pd.concat([WEPP_pr_data, WEPP_Events_data],axis = 1)

        #Select months where soil is not frozen 
        WEPP_data = WEPP_data[WEPP_data.index > 3]
        WEPP_data = WEPP_data[WEPP_data.index < 11]

        print(WEPP_data)

        return WEPP_data

    #Create lists to hold each output list of dataframes for each model
    WEPP_crop1_lst = []
    WEPP_crop2_lst = []

    #Loop through model labels and run Get_Monthly_WEPP_Data
    for mod_lab in mod_labels:

        WEPP_crop1_data = Get_Monthly_WEPP_Data(mod_lab, crop1_years, '_alf')
        WEPP_crop1_lst.append(WEPP_crop1_data) #Append outputs to lists created above

        WEPP_crop2_data = Get_Monthly_WEPP_Data(mod_lab, crop2_years, '_corn')
        WEPP_crop2_lst.append(WEPP_crop2_data)

    #Concat the list of dataframes for transport to excel
    WEPP_crop1_outputs = pd.concat(WEPP_crop1_lst)
    WEPP_crop2_outputs = pd.concat(WEPP_crop2_lst)
    
    # Export outputs to excel files
    out_path = str(excel_parent_path + 'DF_comp_crop1_{}.xlsx'.format(scenario))
    WEPP_crop1_outputs.to_excel(out_path)
    
    out_path = str(excel_parent_path + 'DF_comp_crop2_{}.xlsx'.format(scenario))
    WEPP_crop2_outputs.to_excel(out_path)
    
    
    
    #### Load in MnDNR Obs data #####
    obs_df = pd.read_csv(obs_path, sep = '\t')
    obs_df = obs_df[obs_df['Month'] > 3]
    obs_df = obs_df[obs_df['Month'] < 11]

    def sep_obs_crops(crop_obs_yrs):
        '''
        Separates observed data by crop
        crop_obs_yrs = years in which crop of interest is present
        '''
        crop_df = obs_df[obs_df['Year'].isin(crop_obs_yrs)]
        crop_RO = (crop_df.groupby('Month')['RO (in)'].sum() * 25.4) / len(crop_obs_yrs)
        crop_Events = (crop_df.groupby('Month')['RO (in)'].count()) / len(crop_obs_yrs)
        
        months = [4,5,6,7,8,9,10]
        crop_out = pd.DataFrame({'Total RO (mm)':crop_RO, 'Total RO Events':crop_Events},index = months).fillna(0)
        return crop_out
    
    crop1_obs = sep_obs_crops(crop1_obs_yrs)
    crop2_obs = sep_obs_crops(crop2_obs_yrs)

    print(crop1_obs)
    print(crop2_obs)
    
    ##### Compare modeled and observed data #####
    def comp_mod_obs_RO(WEPP_crop_lst, obs_df):
        '''
        Compares observed and modeled data using RMSE and R2 values
        '''
        #prep output lists for running RMSE and R2 function
        rmse_RO_lst = []
        rmse_RO_e_lst = []
        R2_RO_lst = []
        R2_RO_e_lst = []
        mod_ID_lst = []  
        
        def calc_RMSEs_R2s(wepp_data):
            '''
            Calculates RMSE and R2 values for obs vs mod
            '''
            #Calculate the RMSE values for monthly RO and total number of events per month
            rmse_RO = math.sqrt(mean_squared_error(obs_df['Total RO (mm)'], wepp_data['RO']))
            rmse_RO_lst.append(rmse_RO)
            rmse_RO_e = math.sqrt(mean_squared_error(obs_df['Total RO Events'], wepp_data['Total RO Events']))
            rmse_RO_e_lst.append(rmse_RO_e)

            #Calculate the R2 values for monthly precip and total number of events per month
            R2_RO = sm.OLS(obs_df['Total RO (mm)'], wepp_data['RO']).fit().rsquared_adj
            R2_RO_lst.append(R2_RO)
            R2_RO_e = sm.OLS(obs_df['Total RO Events'], wepp_data['Total RO Events']).fit().rsquared_adj
            R2_RO_e_lst.append(R2_RO_e)

        for crop, mod in zip(WEPP_crop_lst, mod_labels):
            #run calc_RMSEs_R2s for each mod label
            calc_RMSEs_R2s(crop)
            
            #Append dataframe names since they include the ID for each model
            mod_ID_lst.append(mod)

        # Create a dataframe out of the RMSE and R2 values 
        val_values = pd.DataFrame(data = {'Model':mod_ID_lst, 'RMSE_RO':rmse_RO_lst, 'R2_RO':R2_RO_lst,
                                          'RMSE_RO_e':rmse_RO_e_lst, 'R2_RO_e':R2_RO_e_lst})

        return val_values
    
    crop1_comp_vals = comp_mod_obs_RO(WEPP_crop1_lst, crop1_obs)
    crop2_comp_vals = comp_mod_obs_RO(WEPP_crop2_lst, crop2_obs)


#Set up input parameters for analyze_RO function
add_years = [0,6,12,18,24,30,36,42,48,54] 
start_crop1_yrs = [1,2]
start_crop2_yrs = [3,4,5,6]
crop1_obs_yrs = ['2011', '2012']
crop2_obs_yrs = ['2013', '2014', '2015', '2016']
scen_dir = 'C:\\Users\\Garner\\Soil_Erosion_Project\\WEPP_PRWs\\GO1_DEP\\Runs\\DEP_DF_10K\\'
mod_labels = ['L1','L2','L3','L4','L5','L6',\
              'B1','B2','B3','B4','B5','B6']
excel_parent_path = 'C:\\Users\\Garner\\Soil_Erosion_Project\\WEPP_PRWs\\'
obs_path = 'C:\\Users\\Garner\\Soil_Erosion_Project\\WEPP_PRWs\\GO1_DEP\\obs_data\\DF_Obs_Cal.txt'


analyze_RO(add_years, start_crop1_yrs, start_crop2_yrs, crop1_obs_yrs, crop2_obs_yrs,
           scen_dir, mod_labels, excel_parent_path, obs_path, '10K')
