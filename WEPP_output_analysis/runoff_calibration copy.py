
def calibrate_wepp_RO(wshed_path, wshed_name, clim_mod, cal_dir, mod_crop1_yrs, mod_crop2_yrs,\
                      all_mod_yrs, actual_yrs, obs_crop1_yrs, obs_crop2_yrs, cal_yrs, val_yrs):

    import pandas as pd
    import os
    import numpy as np
    import hydroeval as he

    

    ###### Load in data and prepare for graphing and ######

    #Load in observed data (whole dataset)
    obs_data_whole = pd.read_excel(str(wshed_path + 'obs_data/{}_Obs_RO.xlsx'.format(wshed_name)))

    #select data for March-November
    obs_data_months = obs_data_whole[obs_data_whole['Month'].astype(int) > 2]
    obs_data_months = obs_data_months[obs_data_months['Month'].astype(int) < 12]

    #trim down data column to only include day, month, and year
    obs_data_months['Date'] = obs_data_months['Date'].astype(str).str[0:10]

    #observed data occasionally has multiple events on same day. Combine these into daily values
    obs_data_months = obs_data_months.groupby('Date').sum().reset_index()

    def prep_obs_data(yr_selection):
        '''
        Limits data to specific years and selects months required for downstream analysis
        '''
        #limit dataframe to year selection
        select_years = obs_data_months[obs_data_months['Year'].astype(int).isin(yr_selection)]
        
        return select_years
    
    obs_crop1 = prep_obs_data(obs_crop1_yrs)
    obs_crop2 = prep_obs_data(obs_crop2_yrs)
    df_for_cal = prep_obs_data(cal_yrs)
    df_for_val = prep_obs_data(val_yrs)


    #Load in outputs for uncalibrated and calibrated data, split by crop, and select needed data
    def prep_mod_data(cal_dir):
        '''
        Reads in data from ebe WEPP output file for a specified calibration scenario and
        then splits the data by crop and selects the monthly data needed for downstream 
        analysis

        cal_dir = name of directory that matches the calibration scenario 
        '''
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
        data = pd.read_csv(str(output_file_dir+hill), skiprows = 3,\
                           names = ebe_col_list, sep = '\s+', header=None)
        

        def prep_df_by_crop(mod_crop_yrs):
            #split data by crop
            all_data = data[data['Year'].isin(mod_crop_yrs)]

            #select data for march-november
            sel_mod_data = all_data[all_data['Month'] > 2] 
            sel_mod_data = sel_mod_data[sel_mod_data['Month'] < 12]

            #get monthly average total runoff
            monthly_total_avgs = sel_mod_data.groupby('Month')['RO'].sum() / len(mod_crop_yrs)
            
            #get mean of all runoff events in each month
            monthly_means = sel_mod_data.groupby('Month')['RO'].mean()

            return monthly_total_avgs, monthly_means

        #run prep_df_by_crop for each crop (with mod_crop*_yrs)
        mod_crop1_avgs, mod_crop1_means= prep_df_by_crop(mod_crop1_yrs)
        mod_crop2_avgs, mod_crop2_means = prep_df_by_crop(mod_crop2_yrs)


        #only choose modeled years that correspond to the observed dataset
        mod_data = data[data['Year'].isin(all_mod_yrs)]

        #select data for march-november
        mod_data_stat = mod_data[mod_data['Month'] > 2]
        mod_data_stat = mod_data_stat[mod_data_stat['Month'] < 12]

        #change years in WEPP ebe format (1,2,3,4,5, etc) to years corresponding to obs data (ex: 2012, 2013, etc)
        for (mod_count, mod_yr),(actual_count, actual_yr) in zip(enumerate(all_mod_yrs, start = 0), enumerate(actual_yrs, start = 0)):
            mod_data_stat['Year'].replace(all_mod_yrs[mod_count], actual_yrs[actual_count], inplace = True)
        
        #Fill in month and day values with leading zeros up to 2 digits
        mod_data_stat['Month'] = mod_data_stat['Month'].astype(str).str.zfill(2)
        mod_data_stat['Day'] = mod_data_stat['Day'].astype(str).str.zfill(2)

        #Join year, month, and day for each RO event into a string and assign to 'Date' column
        #separate year, month, and day with "-"
        mod_data_stat['Date'] = mod_data_stat[['Year', 'Month', 'Day']].astype(str).agg('-'.join, axis=1)

        return mod_data_stat, mod_crop1_avgs, mod_crop1_means, mod_crop2_avgs, mod_crop2_means

    mod_df, mod1_avgs, mod1_means, mod2_avgs, mod2_means = prep_mod_data(cal_dir)


    #prepare data for statistical analysis
    def upsample_RO_data(yr_selection, input_df, RO):
        '''
        Runoff data is loaded in as isolated events throughout a given timeframe,
        so in order to run various statistical analyses, it must be transformed into
        daily data. 

        A time series of dates corresponding to the selection of years is created
        and the runoff events are merged into a new column within this time series. If there
        is no runoff event for a given day, then it is set to 0 mm. 

        yr_selection = years corresponding to input dataframe

        input_df = input dataframe holding ebe or cal/val obs data

        RO = runoff column name (different for mod and obs data)
        '''

        #get number of years in the year selection
        num_yrs = len(yr_selection)

        #create dataframe with a daily time series in the first column
        daily_df = pd.DataFrame({'Date' : pd.period_range(yr_selection[0], periods=(num_yrs*365), freq='D')})

        #merge runoff data into the daily timeseries df
        upsampled_df = daily_df.astype(str).merge(input_df[['Date', RO]], on = 'Date', how='left', validate="one_to_one").fillna(0)
        upsampled_df['Month'] = upsampled_df['Date'].astype(str).str[5:7]
        upsampled_df[RO] = upsampled_df[RO].astype(float)

        return upsampled_df

    full_obs_df = upsample_RO_data(actual_yrs, obs_data_months, 'RO (in)')
    full_mod_df = upsample_RO_data(actual_yrs, mod_df, 'RO')


    def NSE(obs_df, mod_df):
        '''
        Compare observed data and modeled data via NSE statistical analysis

        Returns NSE parameter for obs vs mod dataset for each month (in dataframe format)

        NSE param = 1 - (sum((obs - mod)^2) / sum((obs - obs_mean)^2))
            where obs and mod are the individual observed and modeled values in a dataset
        '''

        #convert RO from in to mm
        obs_df['RO'] = obs_df['RO (in)'] * 25.4

        #create list of months for looping
        months = ['03','04','05','06','07','08','09','10','11']

        #get mean of monthly runoff values
        O_means = obs_df.groupby('Month')['RO'].mean()

        #Monthly_NSEs list
        monthly_NSEs = []

        #loop through months
        for month in months:

            all_numerator = []
            all_denominator = []
            
            #select data for month
            obs_vals = obs_df[obs_df['Month'] == month]
            mod_vals = mod_df[mod_df['Month'] == month]

            nse = he.evaluator(he.nse, mod_vals['RO'].astype(float), obs_vals['RO'].astype(float))

            monthly_NSEs.append(nse)
        
        nse_df = pd.DataFrame({'Month':months, 'NSE Param':monthly_NSEs})

        return nse_df
    
    NSE_params = NSE(full_obs_df, full_mod_df)

    print(wshed, cal_dir, clim_mod)
    print(NSE_params)
        

    


###### Prepare function parameters and run calibrate_wepp_RO #######

wshed_lst = ['BE1', 'DO1', 'GO1', 'RO1', 'ST1']

crop1_names = ['Corn', 'Corn', 'Alfalfa', 'Corn', 'Corn']
crop2_names = ['Soy', 'Soy', 'Corn', 'Soy', 'Alfalfa']

lst_mod_crop1_yrs = [[2,4], [1,3,5,7], [1,2],\
                     [2,3,4,6], [1,2,3]]

lst_mod_crop2_yrs = [[1,3,5], [2,4,6], [3,4,5,6],\
                     [1,5], [4,5,6,7]]

lst_all_mod_yrs = [[1,2,3,4,5], [1,2,3,4,5,6,7], [1,2,3,4,5,6],\
                   [1,2,3,4,5,6], [1,2,3,4,5,6,7]]

lst_actual_yrs = [[2012,2013,2014,2015,2016],\
                  [2013,2014,2015,2016,2017,2018,2019],\
                  [2011,2012,2013,2014,2015,2016],\
                  [2014,2015,2016,2017,2018,2019],\
                  [2011,2012,2013,2014,2015,2016,2017]]

lst_obs_crop1_yrs = [[2013,2015], [2013,2015,2017,2019],\
                     [2011,2012],[2015,2016,2017,2019],\
                     [2011,2012,2013]]

lst_obs_crop2_yrs = [[2012,2014,2016],[2014,2016,2018],\
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


cal_dirs = ['DF_Comp', 'DF_Comp3', 'DF_Comp5', 'DF_Comp10']

for wshed, mod_crop1_yrs, mod_crop2_yrs, all_mod_yrs, actual_yrs, obs_crop1_yrs, obs_crop2_yrs, cal_yrs, val_yrs\
    in zip(wshed_lst, lst_mod_crop1_yrs, lst_mod_crop2_yrs, lst_all_mod_yrs, lst_actual_yrs,\
           lst_obs_crop1_yrs, lst_obs_crop2_yrs, lst_cal_yrs, lst_val_yrs):

    wshed_path = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/'.format(wshed))

    for cal_dir in cal_dirs:

        for clim_mod in ['L3_19','L4_19','B3_19','B4_19']:

            calibrate_wepp_RO(wshed_path, wshed, clim_mod, cal_dir, mod_crop1_yrs, mod_crop2_yrs, all_mod_yrs,\
                              actual_yrs, obs_crop1_yrs, obs_crop2_yrs, cal_yrs, val_yrs)