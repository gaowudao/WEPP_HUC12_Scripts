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


    def get_obs_avgs(combined_df,var):

        #Split data into two different dataframes by crop type
        crop1_df = combined_df[combined_df['Year'].isin(crop1_yrs)]
        crop2_df = combined_df[combined_df['Year'].isin(crop2_yrs)]

        months = [3,4,5,6,7,8,9,10,11]

        months_present = []
        cal_avgs = []
        val_avgs = []

        #loop through months
        for month in months:

            #get events for month
            crop1_month = crop1_df[crop1_df['Month'] == month]
            crop2_month = crop2_df[crop2_df['Month'] == month]

            #randomly shuffle df rows    
            random_crop1 = crop1_month.sample(frac=1)
            random_crop2 = crop2_month.sample(frac=1)

            def split_dfs(df):
                '''
                only split dataframe if value is greater than 1
                '''
                if len(df) > 1:
                    #split into sub_dataframes (returned type is a list)
                    split_df = np.array_split(df, 2)

                elif len(df) == 1:
                    split_df = df

                return split_df

            crop1_split = split_dfs(random_crop1)
            crop2_split = split_dfs(random_crop2)
            

            #combine the first sub-dataframes together and repeat for the second ones
            cal_events = crop1_split[0].append(crop2_split[0], ignore_index = True)
            val_events = crop1_split[1].append(crop2_split[1], ignore_index = True)

            #get average of each df by dividing total sum by half of the 
            # observed years
            cal_avg = cal_events[var].sum() / (len(obs_rot)/2)
            val_avg = val_events[var].sum() / (len(obs_rot)/2)

            #append to lists created above
            months_present.append(month)
            cal_avgs.append(cal_avg)
            val_avgs.append(val_avg)

        output_df = pd.DataFrame({'cal_{}'.format(var):cal_avgs,\
                                 'val_{}'.format(var):val_avgs,\
                                 'month':months_present})


        return output_df

    obs_avgs = get_obs_avgs(obs_data_months, 'RO')

    print(obs_avgs)


    ####### select runoff events that will be used in statistical tests #########
    def get_mod_avgs(yr_selection, input, var):
        '''
        Limits data to specific years required for downstream analysis 
        (validation vs calibration, different crops, etc.) and then selects
        all years greater than 10mm and 25mm into separate dataframes

        '''
        #create empty list for appending
        all_yrs = []

        #select year keys in all_div_mod_yrs that correspond to the year selection
        for year in all_div_mod_yrs:
            if year in yr_selection:
                num_yrs = all_div_mod_yrs[year]
                #extend years to all_yrs
                all_yrs.extend(num_yrs)

        #limit dataframes in dict input to keys that match years in yr_selection
        select_data = input[input['Year'].isin(yr_selection)]

        #get monthly averages for input data
        monthly_df = select_data.groupby('Month')[var].sum() / len(all_yrs)

        #fill in 0mm months with 0 by using merge
        months_df = pd.DataFrame({'Month':[3,4,5,6,7,8,9,10,11]})
        merged_df = months_df.merge(monthly_df.reset_index(), on = ['Month'], how = 'left', validate='one_to_one').fillna(0)
        monthly_avgs = merged_df

        return monthly_avgs
    
    mod_avgs = get_mod_avgs(obs_rot, mod_data_months, 'RO')

    print(mod_avgs)


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

        print(wshed, clim_mod)

        nse = float(he.evaluator(he.nse, mod['RO'], obs['cal_RO']))
        pbias = float(he.evaluator(he.pbias, mod['RO'], obs['cal_RO']))

        nse_lst.append(nse)
        pbias_lst.append(pbias)

        nse_avg = mean(nse_lst)
        pbias_avg = mean(pbias_lst)

        
        output_df = pd.DataFrame({'NSE':[nse_avg], 'PBIAS':[pbias_avg]})


        return output_df

    output_stats = evalulate_mod_outputs(obs_avgs, mod_avgs)

    print(output_stats)



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


cal_dirs = ['DF_Comp']

output_params = []

for wshed, crop1_yrs, crop2_yrs, mod_rot_starters, obs_rot, cal_yrs, val_yrs\
    in zip(wshed_lst, lst_crop1_yrs, lst_crop2_yrs, lst_mod_rot_starts_wshed, obs_rot_yrs,\
           lst_cal_yrs, lst_val_yrs):

    wshed_path = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/'.format(wshed))

    for cal_dir in cal_dirs:

        calibrate_wepp_RO(wshed_path, wshed, 'Obs', cal_dir, crop1_yrs, crop2_yrs, mod_rot_starters,\
                        obs_rot, cal_yrs, val_yrs)