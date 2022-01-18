def calibrate_wepp_RO(wshed_path, wshed_name, clim_mod, cal_dir, crop1_yrs, crop2_yrs,\
                      mod_rot_starters, obs_rot, cal_yrs, val_yrs):
    '''
    cal_dir = name of directory that matches the calibration scenario 
    '''

    import pandas as pd
    import os
    import numpy as np
    import hydroeval as he
    from statistics import mean

    

    ###### Load in data ######

    #Load in observed data (whole dataset)
    obs_data_whole = pd.read_excel(str(wshed_path + 'obs_data/{}_Obs_RO.xlsx'.format(wshed_name)))

    #select data for March-November
    obs_data_months = obs_data_whole[obs_data_whole['Month'].astype(int) > 2]
    obs_data_months = obs_data_months[obs_data_months['Month'].astype(int) < 12]

    #trim down data column to only include day, month, and year
    obs_data_months['Date'] = obs_data_months['Date'].astype(str).str[0:10]

    #observed data occasionally has multiple events on same day. Combine these into daily values
    aggregation_functions = {'Date': 'first', 'Year': 'first', 'Month': 'first',\
                             'Day':'first', 'RO (in)':'sum', 'TSS (lbs/ac)':'sum'}

    obs_data_months = obs_data_months.groupby(obs_data_months['Date']).aggregate(aggregation_functions)

    #convert runoff from in to mm in observed data
    obs_data_months['RO'] = obs_data_months['RO (in)'] * 25.4


    #Read in data from ebe WEPP output file for a specified calibration scenario

    #set path to directory with output files
    output_file_dir = str(wshed_path + 'Runs/{}/{}/wepp/output/'.format(cal_dir, clim_mod))

    #get ebe file from output directory
    hillslopes = [x for x in os.listdir(output_file_dir) if x.endswith('.ebe.dat')]

    #only one hillslope in DF simulations so just select first file in list
    hill = hillslopes[0]

    #define column names for ebe file load in
    ebe_col_list = ['Day', 'Month', 'Year', 'Precip', 'RO', 'IR-det',\
                    'Av-det', 'Mx-det', 'Point', 'Av-dep', 'Mx-dep',\
                    'Point_2', 'Sed-Del', 'ER']

    #read in ebe file to dataframe
    all_data = pd.read_csv(str(output_file_dir+hill), skiprows = 3,\
                        names = ebe_col_list, sep = '\s+', header=None)

    #select data for March-November
    sel_mod_data = all_data[all_data['Month'] > 2] 
    mod_data_months = sel_mod_data[sel_mod_data['Month'] < 12]


    #create list to hold all "corresponding_mod_yrs" lists
    all_div_mod_yrs = {}

    #loop through mod start years (equivalent to obs year length)
    for mod_starter_yr,obs_yr in zip(mod_rot_starters,obs_rot):
        
        #create list that holds all mods years corresponding to the given observed year
        corresponding_mod_yrs = []
        
        #loop through a multiplier so that all model years that match an obs year are
        #created and add to the corresponding_mod_yrs list
        for n in range(0,11):
            if n == 0:
                mod_yr = mod_starter_yr
            if n > 0:
                mod_yr = mod_starter_yr + (len(obs_rot) * n)
                
            corresponding_mod_yrs.append(mod_yr)
            
        #append list of all matching mod years to a new list so that there is a list of
        #matching mod years for each observed year
        all_div_mod_yrs[obs_yr] = corresponding_mod_yrs

    #change years in WEPP ebe format (1,2,3,4,5, etc) to years corresponding to obs data (ex: 2012, 2013, etc)
    for year,key in zip(all_div_mod_yrs, all_div_mod_yrs.keys()):
        mod_data_months['Year'].replace(all_div_mod_yrs[year], key, inplace = True)


    ####### select runoff events that will be used in statistical tests #########
    def select_events(yr_selection, input):
        '''
        Limits data to specific years required for downstream analysis 
        (validation vs calibration, different crops, etc.) and then selects
        all years greater than 10mm and 25mm into separate dataframes

        '''

        #limit dataframes in dict input to keys that match years in yr_selection
        select_data = input[input['Year'].isin(yr_selection)]

        #loop through selected dfs
        events_5mm = select_data[select_data['RO'] >= 5]
        events_25mm = select_data[select_data['RO'] >= 25]
        
        return events_5mm, events_25mm
    
    obs_crop1_5, obs_crop1_25 = select_events(crop1_yrs,obs_data_months)
    obs_crop2_5, obs_crop2_25 = select_events(crop2_yrs,obs_data_months)
    obs_cal_5, obs_cal_25 = select_events(cal_yrs,obs_data_months)
    obs_val_5, obs_val_25 = select_events(val_yrs,obs_data_months)
    mod_crop1_5, mod_crop1_25 = select_events(crop1_yrs, mod_data_months)
    mod_crop2_5, mod_crop2_25 = select_events(crop2_yrs, mod_data_months)
    mod_cal_5, mod_cal_25 = select_events(cal_yrs, mod_data_months)
    mod_val_5, mod_cal_25 = select_events(val_yrs, mod_data_months)


    def evalulate_mod_outputs(obs, mod):
        '''
        The number of events from the observed and modeled data are uneven,
        so events are randomly selected from whichever dataset is longer in
        order for the length of the observed and modeled data to be even.

        Compare observed data and modeled data via NSE statistical analysis

        Returns NSE parameter for obs vs mod dataset for each month (in dataframe format)

        NSE param = 1 - (sum((obs - mod)^2) / sum((obs - obs_mean)^2))
            where obs and mod are the individual observed and modeled values in a dataset
        '''

        nse_lst = []
        pbias_lst = []
        rmse_lst = []

        #get number of events in each dataset
        obs_len = len(obs['RO'])
        mod_len = len(mod['RO'])

        for n in range(0,4000):

            #randomly sample mod data and assign dataframe 
            if mod_len > obs_len:
                mod_subset = mod.sample(n = obs_len)

                mod_out = mod_subset
                obs_out = obs

            if obs_len > mod_len:
                obs_subset = obs.sample(n = mod_len)

                obs_out = obs_subset
                mod_out = mod
            
            mod_out.sort_values(by=['RO'], inplace = True)
            obs_out.sort_values(by=['RO'], inplace = True)

            
            nse = float(he.evaluator(he.nse, mod_out['RO'], obs_out['RO']))
            pbias = float(he.evaluator(he.pbias, mod_out['RO'], obs_out['RO']))

            nse_lst.append(nse)
            pbias_lst.append(pbias)

        nse_avg = mean(nse_lst)
        pbias_avg = mean(pbias_lst)

        
        output_df = pd.DataFrame({'NSE':[nse_avg], 'PBIAS':[pbias_avg]})


        return output_df

    stat_param = evalulate_mod_outputs(obs_cal_5, mod_cal_5)
    print(wshed, clim_mod)
    print(stat_param)



###### Prepare function parameters and run calibrate_wepp_RO #######

wshed_lst = ['BE1', 'DO1', 'GO1', 'RO1', 'ST1']

crop1_names = ['Corn', 'Corn', 'Alfalfa', 'Corn', 'Corn']
crop2_names = ['Soy', 'Soy', 'Corn', 'Soy', 'Alfalfa']


lst_mod_crop1_starts = [[2,4], [1,3,5,7], [1,2],\
                        [2,3,4,6], [1,2,3]]

lst_mod_crop2_starts = [[1,3,5], [2,4,6], [3,4,5,6],\
                         [1,5], [4,5,6,7]]

lst_mod_rot_starts_wshed = [[1,2,3,4,5], [1,2,3,4,5,6,7], [1,2,3,4,5,6],\
                      [1,2,3,4,5,6], [1,2,3,4,5,6,7]]

obs_rot_yrs = [[2012,2013,2014,2015,2016],\
                [2013,2014,2015,2016,2017,2018,2019],\
                [2011,2012,2013,2014,2015,2016],\
                [2014,2015,2016,2017,2018,2019],\
                [2011,2012,2013,2014,2015,2016,2017]]

lst_crop1_yrs = [[2013,2015], [2013,2015,2017,2019],\
                     [2011,2012],[2015,2016,2017,2019],\
                     [2011,2012,2013]]

lst_crop2_yrs = [[2012,2014,2016],[2014,2016,2018],\
                     [2013,2014,2015,2016],[2014,2018],\
                     [2014,2015,2016,2017]]

lst_cal_yrs = [[2012,2013,2014],\
               [2013,2014,2015,2016],\
               [2011,2013,2015],\
               [2014,2015,2016],\
               [2011,2012,2014,2015]]

lst_val_yrs = [[2015,2016],\
               [2017,2018,2019],\
               [2012,2014,2016],\
               [2017,2018,2019],\
               [2013,2016,2017]]


cal_dirs = ['DF_Comp10']

for wshed, crop1_yrs, crop2_yrs, mod_rot_starters, obs_rot, cal_yrs, val_yrs\
    in zip(wshed_lst, lst_crop1_yrs, lst_crop2_yrs, lst_mod_rot_starts_wshed, obs_rot_yrs,\
           lst_cal_yrs, lst_val_yrs):

    wshed_path = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/'.format(wshed))

    for cal_dir in cal_dirs:

        for clim_mod in ['L3_19','L4_19','B3_19','B4_19']:

            calibrate_wepp_RO(wshed_path, wshed, clim_mod, cal_dir, crop1_yrs, crop2_yrs, mod_rot_starters,\
                              obs_rot, cal_yrs, val_yrs)