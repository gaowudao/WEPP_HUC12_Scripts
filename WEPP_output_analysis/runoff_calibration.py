def calibrate_wepp_RO(wshed_path, wshed_name, clim_mod, cal_dir, crop1_yrs, crop2_yrs,\
                      mod_rot_starters, obs_rot, cal_yrs, val_yrs):
    '''
    cal_dir = name of directory that matches the calibration scenario 
    '''

    import pandas as pd
    import os
    import numpy as np
    import hydroeval as he

    

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

    # Create lists of years in the model data that match observed years within
    # the observed site crop rotation. Then groupby month within each list of years
    # and get the monthly mean RO event. The monthly mean values represent modeled RO 
    # events in each month for the modeled years that match a year within the observed crop 
    # rotation. End result is a dataframe identical in length to the observed monthly means 
    
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

    #create empty dictionary to assign dataframes with mod RO data that matches each year list
    #in all_div_mod_yrs
    #
    #   i.e. key of 2012 would correspond to a dataframe with modeled years that match the observed
    #   crop in 2012 for the current watershed
    #
    matched_mod_yrs = {}

    for obs_yr_key in all_div_mod_yrs:

        mod_yrs = all_div_mod_yrs[obs_yr_key]
        matched_mod_yrs[obs_yr_key] = mod_data_months[mod_data_months['Year'].isin(mod_yrs)]




    ####### prep data #########
    def prep_data(yr_selection, input, type):
        '''
        Limits data to specific years required for downstream analysis 
        (validation vs calibration, different crops, etc.)


        '''

        #limit dataframe to year selection
        if type == 'mod':

            #limit dataframes in dict input to year selection (assign to new dict)
            select_dfs = {key: input[key] for key in yr_selection}

            output_dic = {}

            #loop through selected dfs
            for df in select_dfs:
                #get average total monthly runoff for each month in dataframe
                monthly_avgs = select_dfs[df].groupby('Month')['RO'].mean()


                #fill in 0mm months with 0 by using merge
                months_df = pd.DataFrame({'Month':[3,4,5,6,7,8,9,10,11]})
                merged_df = months_df.merge(monthly_avgs.reset_index(), on = ['Month'], how = 'left', validate='one_to_one').fillna(0)
                output_dic[df] = merged_df

            sep_by_year = pd.concat(output_dic).reset_index(level=0).rename({'level_0':'Year'}, axis=1)

            output = sep_by_year.groupby('Month')['RO'].mean()
            output = output.reset_index()

        if type == 'obs':

            #select by year
            select_yrs = input[input['Year'].isin(yr_selection)]

            #get total runoff for each month
            grouped_df = select_yrs.groupby('Month')['RO'].mean()

            #Create a dictionary that has all months from list and the corresponding year repeated in
            # separate column (used for merging and creating equal datframes)
            months = pd.DataFrame({'Month':[3,4,5,6,7,8,9,10,11]})
            output = months.merge(grouped_df, on = 'Month',\
                                       how='left', validate="one_to_one").fillna(0)
            


        
        return output
    
    obs_crop1_avgs = prep_data(crop1_yrs,obs_data_months, 'obs')
    obs_crop2_avgs = prep_data(crop2_yrs,obs_data_months, 'obs')
    df_obs_cal = prep_data(obs_rot,obs_data_months, 'obs')
    df_obs_val = prep_data(val_yrs,obs_data_months, 'obs')
    mod_crop1_avgs = prep_data(crop1_yrs, matched_mod_yrs, 'mod')
    mod_crop2_avgs = prep_data(crop2_yrs, matched_mod_yrs, 'mod')
    df_mod_cal = prep_data(obs_rot, matched_mod_yrs, 'mod')
    df_mod_val = prep_data(val_yrs, matched_mod_yrs, 'mod')

    def evalulate_mod_outputs(obs_df, mod_df):
        '''
        Compare observed data and modeled data via NSE statistical analysis

        Returns NSE parameter for obs vs mod dataset for each month (in dataframe format)

        NSE param = 1 - (sum((obs - mod)^2) / sum((obs - obs_mean)^2))
            where obs and mod are the individual observed and modeled values in a dataset
        '''


        #create list of months for looping
        seasons = [[3,4,5],[6,7,8],[9,10,11]]
        season_names = ['Spring', 'Summer', 'Fall']

        #Monthly_NSEs list
        seasonal_NSEs = []
        seasonal_pbias = []
        seasonal_rmse = []

        #loop through months
        for season in seasons:
            
            #select data for month
            obs_vals = obs_df[obs_df['Month'].isin(season)]
            mod_vals = mod_df[mod_df['Month'].isin(season)]

            nse = he.evaluator(he.nse, mod_vals['RO'], obs_vals['RO'])
            pbias = he.evaluator(he.pbias, mod_vals['RO'], obs_vals['RO'])
            rmse = he.evaluator(he.rmse, mod_vals['RO'], obs_vals['RO'])

            seasonal_NSEs.append(nse)
            seasonal_pbias.append(pbias)
            seasonal_rmse.append(rmse)
        
        output_df = pd.DataFrame({'Season':season_names, 'NSE':seasonal_NSEs, 'PBIAS':seasonal_pbias, 'RMSE':seasonal_rmse})


        return output_df

    print(wshed,clim_mod)
    params = evalulate_mod_outputs(df_obs_cal,df_mod_cal)

    print(params)
    


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