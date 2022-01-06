#%%

import pandas as pd
import numpy as np
import os
from statistics import mean
import matplotlib.pyplot as plt
from functools import reduce, partial
import statsmodels.api as sm
import matplotlib.patches as mpatches
import matplotlib.axes as axs


def analyze_RO(add_years, start_crop1_yrs, start_crop2_yrs, crop1_obs_yrs, crop2_obs_yrs, \
               crop1_name, crop2_name, scen_dir, mod_labels, obs_path, wshed, excel_parent_path,\
               cal_ID, num_hills):
    '''
    Compares WEPP runoff outputs with observed datasets from the Mn Discovery
    Farms Project.Runoff outputs are split by crop.
    
    start_crop1/2_yrs_ = years in first rotation

    crop1/2_obs_yrs = years where a specific crop is present in observed data
    
    add_years = num of years to add onto starting years in each rotation dependent
    on crop rotation
    
    crop1/2_name = name of crop

    scen_dir = parent directory for wepp runs file (i.e. scenario folder)

    mod_labels = labels of climate models

    obs_path = path to obs data

    excel_parent_path = directory for excel outputs

    cal_ID = Specifies the type of calibration performed

    num_hills = number of WEPP hillslopes being compared to observed data
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
        out_files_dir = str(scen_dir + mod_lab + '_' + '19' + '/' + 'wepp' + '/' + 'output' + '/')
        run_files_dir = str(scen_dir + mod_lab + '_' + '19' + '/' + 'wepp' + '/' + 'runs' + '/')

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
        WEPP_pr_data = sum(WEPP_cli_lst) / num_hills
        WEPP_Events_data = reduce(lambda x, y: x.add(y, fill_value=0), WEPP_Events_lst) / num_hills

        #Combine climate and runoff event dataframes
        WEPP_data = pd.concat([WEPP_pr_data, WEPP_Events_data],axis = 1)

        #Select months where soil is not frozen 
        WEPP_data = WEPP_data[WEPP_data.index > 2]
        WEPP_data = WEPP_data[WEPP_data.index < 12]

        return WEPP_data

    #Create lists to hold each output list of dataframes for each model
    WEPP_crop1_lst = []
    WEPP_crop2_lst = []

    #Loop through model labels and run Get_Monthly_WEPP_Data
    for mod_lab in mod_labels:

        #Run function for every climate model
        WEPP_crop1_data = Get_Monthly_WEPP_Data(mod_lab, crop1_years, crop1_name)
        #Append outputs to list created above
        WEPP_crop1_lst.append(WEPP_crop1_data.fillna(0))
        #Assign outputs to dict created outisde function
        WEPP_RO_dic[str(wshed + '_' + crop1_name + '_' + mod_lab)] = WEPP_crop1_data.fillna(0)

        #repeat for second crop
        WEPP_crop2_data = Get_Monthly_WEPP_Data(mod_lab, crop2_years, crop2_name)
        WEPP_crop2_lst.append(WEPP_crop2_data.fillna(0))
        WEPP_RO_dic[str(wshed + '_' + crop2_name + '_' + mod_lab)] = WEPP_crop2_data.fillna(0)

    #Concat the list of dataframes for transport to excel
    WEPP_crop1_outputs = pd.concat(WEPP_crop1_lst)
    WEPP_crop2_outputs = pd.concat(WEPP_crop2_lst)
    
    # Export outputs to excel files
    out_path = str(excel_parent_path + 'RG_Comp_{}_{}_{}.xlsx'.format(wshed, cal_ID, crop1_name))
    WEPP_crop1_outputs.to_excel(out_path)
    
    out_path = str(excel_parent_path + 'RG_Comp_{}_{}_{}.xlsx'.format(wshed,cal_ID, crop2_name))
    WEPP_crop2_outputs.to_excel(out_path)
    
    
    #### Load in MnDNR Obs data #####
    obs_df = pd.read_excel(obs_path)
    obs_df = obs_df[obs_df['Month'].astype(int) > 2]
    obs_df = obs_df[obs_df['Month'].astype(int) < 12]

    print(obs_df.tail())

    def sep_obs_crops(crop_obs_yrs):
        '''
        Separates observed data by crop
        crop_obs_yrs = years where crop of interest is present
        '''
        print(crop_obs_yrs)

        crop_df = obs_df[obs_df['Year'].astype(int).isin(crop_obs_yrs)]

        #Group avg number of runoff events per month
        num_events = crop_df.groupby('Month')['RO (in)'].count() / len(crop_obs_yrs)

        #get average monthly total runoff 
        crop_RO = (crop_df.groupby('Month')['RO (in)'].sum() / len(crop_obs_yrs)) * 25.4
        
        months = [3,4,5,6,7,8,9,10,11]
        #create dataframe of RO values for each month
        crop_out = pd.DataFrame({'Total RO (mm)':crop_RO, 'Avg # Events':num_events},index = months).fillna(0)
        return crop_out
    

    crop1_obs = sep_obs_crops(crop1_obs_yrs)
    crop2_obs = sep_obs_crops(crop2_obs_yrs)

    #Send obs data to excel spreadsheets
    out_path = str(excel_parent_path + 'DF_obs_{}_{}_{}.xlsx'.format(wshed, cal_ID, crop1_name))
    crop1_obs.to_excel(out_path)
    
    out_path = str(excel_parent_path + 'DF_obs_{}_{}_{}.xlsx'.format(wshed,cal_ID, crop2_name))
    crop2_obs.to_excel(out_path)
    
    #Assign obs dataframes to dict keys
    obs_RO_dic[str(wshed + '_' + crop1_name)] = crop1_obs
    obs_RO_dic[str(wshed + '_' + crop2_name)] = crop2_obs

###Set up input parameters for analyze_RO function###

#List of watershed names
wshed_lst = ['BE1','DO1','GO1', 'RO1', 'ST1']

#Years in first rotation for each crop (starts at 1)
start_crop1_yrs = [[1], [1], [1,2,3], [1,2,3,4,5,6,8,9,10,11,12,13,14,15],\
                   [1,2,3]]
start_crop2_yrs = [[2], [2], [4,5,6], [7], [4,5,6]]

#List of lists that add integers to the starting years
add_years = [list(range(0,59,2)), list(range(0,59,2)),\
             list(range(0,59,6)), list(range(0,59,15)),\
             list(range(0,59,6))]

#observed crop years
crop1_obs_yrs = [[2013,2015],[2013,2015,2017,2019],\
                 [2011,2012], [2015,2016,2017,2019],\
                 [2011,2012,2013]]
crop2_obs_yrs = [[2012,2014,2016],[2014,2016,2018],\
                 [2013,2014,2015,2016], [2014,2018],\
                 [2014,2015,2016,2017]]

#Number of modeled hillslopes being used for comparison
num_hills = [2,2,1,1,2]

#lists of crop names
crop1_names = ['Corn', 'Corn', 'Alfalfa', 'Corn', 'Corn']
crop2_names = ['Soy', 'Soy', 'Corn', 'Soy', 'Alfalfa']

#Climate model short IDs
mod_labels = ['L3','L4','B3','B4']

#Output dictionaries
obs_RO_dic = {}
WEPP_RO_dic = {}

for wshed, addyr, start1, start2, obs1, obs2, name1, name2, hills\
     in zip(wshed_lst, add_years, start_crop1_yrs, start_crop2_yrs, crop1_obs_yrs,\
            crop2_obs_yrs, crop1_names, crop2_names, num_hills):

    print('Analyzing runoff for {} watershed...'.format(wshed))

    #Define paths to scenario parent directory and observed data path
    scen_dir = 'E:/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/RG_Comp/'.format(wshed)
    obs_path = 'E:/Soil_Erosion_Project/WEPP_PRWs/{}/obs_data/{}_Obs_RO.xlsx'.format(wshed, wshed)
    excel_path = 'E:/Soil_Erosion_Project/WEPP_PRWs/{}/Comparisons/'.format(wshed)

    analyze_RO(addyr, start1, start2, obs1, obs2, name1, name2,\
               scen_dir, mod_labels, obs_path, wshed, excel_path, '10xK_RG', hills)


def create_scatter_plots(wshed, mod_lab, mod_name, crop1, color1, crop2, color2, subx, suby):
    '''
    Creates a scatter plot of observed and modeled runoff data for each month

    Scatter plots are separated by climate models (mod_lab)

    mod_lab = model short label
    
    mod_name = full model name
    '''


    #loop through dataframes in dict with modeled data
    for mod_df in WEPP_RO_dic:
        
        #define watershed and crop name for each iteration
        crop_name = str(mod_df[:-3])
        crop_name = crop_name[4::]

        #Define colors and plot names for each crop
        if crop_name == crop1:
            color = color1
            crop_lab = crop1
        if crop_name == crop2:
            color = color2
            crop_lab = crop2

        #specify which modeled data to use based on climate model short ID
        if mod_df.startswith(wshed) and mod_df.endswith(mod_lab):
            axes[subx,suby].plot(WEPP_RO_dic[mod_df].index.values, WEPP_RO_dic[mod_df]['RO'],\
                                marker = 'o', label = 'WEPP Runoff - {}'.format(crop_lab), color = color,\
                                alpha = 1)

    #loop through dataframes in observed dict
    for obs_df in obs_RO_dic:

        #repeat above for observed data
        crop_name = str(obs_df[4::])

        #Define colors and crop names to use in scatter plots for each crop
        if crop_name == crop1:
            color = color1
            crop_lab = crop1
        if crop_name == crop2:
            color = color2
            crop_lab = crop2
        
        if obs_df.startswith(wshed):
            axes[subx,suby].plot(obs_RO_dic[obs_df].index.values, obs_RO_dic[obs_df]['Total RO (mm)'],\
                                marker = '^', label = 'Observed Data - {}'.format(crop_lab), color = color,\
                                linestyle = 'dashed' ,alpha = 0.7)

                
    #Add labels
    axes[subx,suby].set_xlabel('Month')
    axes[subx,suby].set_ylabel('Average Total Runoff (mm)')

    #Add sub-title
    axes[subx,suby].set_title(mod_name)


#set up colors for crops in each watershed
crop_colors1 = ['orange', 'orange', 'purple', 'orange', 'orange']
crop_colors2 = ['green', 'green', 'orange', 'green', 'purple']

#define full climate model names
mod_names = ['hadgem2-cc.1 RCP 4.5','hadgem2-cc.1 RCP 8.5',\
             'gfdl_esm2g.1 RCP 4.5', 'gfdl_esm2g.1 RCP 8.5']

for wshed,crop1, color1, crop2, color2 in \
    zip(wshed_lst, crop1_names, crop_colors1, crop2_names, crop_colors2):

    #Set up a subplot for each watershed that contains scatter plots for each climate model
    fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize = (14, 14))

    #Define x/y axis coordinates for each plot
    subx_vals = [0,1,0,1]
    suby_vals = [0,0,1,1]

    for mod, mod_name, subx, suby in zip(mod_labels, mod_names, subx_vals, suby_vals):
        create_scatter_plots(wshed, mod, mod_name, crop1, color1, crop2, color2, subx, suby)

    #Add title to grouping of subplots
    fig.suptitle('WEPP Outputs with Calibrated K-eff and Rain Gauge Precip vs {} DF Site Data:\n Average Total Monthly Runoff'.format(wshed), fontsize = 14)

    #Create single legend for all plots
    handles, labels = fig.axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc = 'upper right')

    #save figure to comparisons folder
    fig_path = 'E:/Soil_Erosion_Project/WEPP_PRWs/{}/Comparisons/{}_RO_10xK_RG.png'.format(wshed,wshed)
    fig.savefig(fig_path)

    
#%%