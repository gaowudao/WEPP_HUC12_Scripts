
def calibrate_wepp_RO(wshed_path, wshed_name, clim_mod, cal_dir, mod_crop1_yrs, mod_crop2_yrs,/
                      mod_yrs_timeform, obs_crop1_yrs, obs_crop2_yrs, cal_yrs, val_yrs):

    import pandas as pd
    import os
    import numpy as np


    ###### Load in data and prepare for graphing and ######

    #Load in observed data (whole dataset)
    obs_data_whole = pd.read_excel(str(wshed_path + 'obs_data/{}_Obs_RO.xlsx'.format(wshed_name)))

    def prep_obs_data(yr_selection):
        '''
        Limits data to specific years and selects months required for downstream analysis
        '''

        #limit dataframe to year selection
        select_years = obs_data_whole[obs_data_whole['Year'].astype(int).isin(yr_selection)]

        #select data for march-november
        select_months = select_years[select_years['Month'].astype(int) > 2]
        select_months = select_months[select_years['Month'].astype(int) < 12]

        return select_months
    
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

        #define column names for ebe file load in
        ebe_col_list = ['Day', 'Month', 'Year', 'Precip', 'RO', 'IR-det',\
                        'Av-det', 'Mx-det', 'Point', 'Av-dep', 'Mx-dep',\
                        'Point_2', 'Sed-Del', 'ER']

        #read in ebe file to dataframe
        data = pd.read_csv(str(output_file_dir), skiprows = 3,\
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

            return sel_mod_data, monthly_total_avgs, monthly_means

        #run prep_df_by_crop for each crop (with mod_crop*_yrs)
        mod_crop1_avgs, mod_crop1_means= prep_df_by_crop(mod_crop1_yrs)
        mod_crop2_avgs, mod_crop2_means = prep_df_by_crop(mod_crop2_yrs)


        #get all mod data for downstream statistical analyses. The above dataframes are 
        # only for graphing purposes
        all_years = mod_crop1_yrs.append(mod_crop2_yrs)
        #only choose modeled years that correspond to the observed dataset
        mod_data = data[data['Year'].isin(all_years)]

        #select data for march-november
        mod_data_stat = mod_data[mod_data['Month'] > 2]
        mod_data_stat = mod_data_stat[mod_data_stat['Month'] < 12]

        #change years in WEPP ebe format (1,2,3,4,5, etc) to years corresponding to obs data (ex: 2012, 2013, etc)
        mod_data_stat['year_timeform'] = mod_yrs_timeform
        
        #Join year, month, and day for each RO event into a string and assign to 'Date' column
        #separate year, month, and day with "-"
        mod_data_stat['Date'] = mod_data_stat[['year_timeform', 'Month', 'Day']].astype(str).agg('-'.join, axis=1)

        return mod_data_stat, mod_crop1_avgs, mod_crop1_means, mod_crop2_avgs, mod_crop2_means

    mod_df, mod1_avgs, mod1_means, mod2_avgs, mod2_means = prep_mod_data(cal_dir)


    #prepare data for statistical analysis
    def upsample_RO_data(yr_selection, input_df):
        '''
        Runoff data is loaded in as isolated events throughout a given timeframe,
        so in order to run various statistical analyses, it must be transformed into
        daily data. 

        A time series of dates corresponding to the selection of years is created
        and the runoff events are merged into a new column within this time series. If there
        is no runoff event for a given day, then it is set to 0 mm. 
        '''

        #get number of years in the year selection
        num_yrs = len(yr_selection)

        #create dataframe with a daily time series in the first column
        daily_df = pd.DataFrame({'Date' : pd.period_range(yr_selection[0], periods=(num_yrs*365.5), freq='D')})

        #merge runoff data into the daily timeseries df
        upsampled_df = daily_df.astype(str).merge(input_df, on = 'Date', how='left').fillna(0)

        return upsampled_df

    upsample_RO_data(cal_yrs, df_for_cal)
    upsample_RO_data(val_yrs, df_for_val)
    upsample_RO_data(mod_yrs_timeform, mod_df)



    #Uncalibrated outputs
    uncal_crop1, uncal_crop2 = read_mod_data('DF_Comp')

    #Ke x 3 outputs
    cal3_crop1, cal3_crop2 = read_mod_data('DF_Comp3')

    #Ke x 5 outputs
    cal5_crop1, cal5_crop2 = read_mod_data('DF_Comp5')

    #Ke x 10 outputs
    cal10_crop1, cal10_crop2 = read_mod_data('DF_Comp10')


    #Split crop dataframes into halves (half of all daily values - not by year)

    #Assign halves to dataframes and write to new excel files


###### Prepare function parameters and run calibrate_wepp_RO #######

wshed_lst = ['BE1', 'DO1', 'GO1', 'RO1', 'ST1']
cal_dirs = ['DF_Comp', 'DF_Comp3', 'DF_Comp5', 'DF_Comp10']

for wshed in wshed_lst:

    wshed_path = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/'.format(wshed))

    for cal_dir in cal_dirs:

        for clim_mod in ['L3','L4','B3','B4']:

            calibrate_wepp_RO(wshed_path, wshed, clim_mod, cal_dir, mod_crop1_yrs, mod_crop2_yrs,/
                      mod_yrs_timeform, obs_crop1_yrs, obs_crop2_yrs, cal_yrs, val_yrs)