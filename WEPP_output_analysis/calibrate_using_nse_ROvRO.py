#%%

def calibrate_wepp_RO(wshed_path, wshed_name, clim_mod, cal_dir, crop1_yrs, crop2_yrs,\
                      mod_rot_starters, obs_rot, crop1_name, crop2_name):
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
    obs_data_months = obs_data_whole[obs_data_whole['Month'].astype(int) > 3]
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
    sel_mod_data = all_data[all_data['Month'] > 3] 
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


    def get_obs_avgs(combined_df,var,crop_yrs):

        #Split data into two different dataframes by crop type
        crop_df = combined_df[combined_df['Year'].isin(crop_yrs)]

        #set bins and months
        lower_bins = [0, 5, 10, 15, 20]
        upper_bins = [5, 10, 15, 20, 500]
        months = [4,5,6,7,8,9,10,11]

        #create lists that will hold avg values for each month
        months_present = []
        cal_crop = []
        val_crop = []

        for month in months:
            
            #create lists that will hold avg values by bin
            cal_crop_bins = []
            val_crop_bins = []

            for low_bin, high_bin in zip(lower_bins, upper_bins):

                #get data for month
                bin_df = crop_df[(crop_df['RO'] > low_bin) & (crop_df['RO'] < high_bin)]
                month_df = bin_df[bin_df['Month'] == month]


                #split dataframe into two equal dfs if total len is > 1
                if len(month_df) > 1:

                    #split into two sub_dataframes (returned type is a list)
                    split_df = np.array_split(month_df, 2)

                #create list that matches length of split dataframe if len is < 1
                if len(month_df) < 2:

                    month_df['RO'] = month_df['RO'].astype(float) / 2

                    split_df = [month_df,month_df]


                cal_crop_bins.append(split_df[0])
                val_crop_bins.append(split_df[1])

            cal_crop_recomb = pd.concat(cal_crop_bins)
            val_crop_recomb = pd.concat(val_crop_bins)

            #get average of each df by dividing total sum by half of the 
            # observed years
            cal_crop_avg = cal_crop_recomb[var].sum() / (len(crop_yrs) / 2)
            val_crop_avg = val_crop_recomb[var].sum() / (len(crop_yrs) / 2)

            #append to lists created above
            cal_crop.append(cal_crop_avg)
            val_crop.append(val_crop_avg)
            months_present.append(month)

        #Put average monthly totals into dataframe with columns for month, cal vals, and val vals
        output_df = pd.DataFrame({'cal_{}'.format(var):cal_crop,\
                                  'val_{}'.format(var):val_crop,\
                                  'Month':months_present})


        return output_df

    obs_avgs_crop1 = get_obs_avgs(obs_data_months, 'RO', crop1_yrs)
    obs_avgs_crop2 = get_obs_avgs(obs_data_months, 'RO', crop2_yrs)

    obs_dic['{}_{}_obs'.format(wshed,crop1_name)] = obs_avgs_crop1
    obs_dic['{}_{}_obs'.format(wshed,crop2_name)] = obs_avgs_crop2

    print(obs_avgs_crop1)
    print(obs_avgs_crop2)


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
        monthly_df = select_data.groupby('Month')[var].sum() / len(yr_selection)

        #fill in 0mm months with 0 by using merge
        months_df = pd.DataFrame({'Month':[4,5,6,7,8,9,10,11]})
        merged_df = months_df.merge(monthly_df.reset_index(), on = ['Month'], how = 'left', validate='one_to_one').fillna(0)
        monthly_avgs = merged_df

        return monthly_avgs
    
    mod_crop1_avgs = get_mod_avgs(crop1_yrs, mod_data_months, 'RO')
    mod_crop2_avgs = get_mod_avgs(crop2_yrs, mod_data_months, 'RO')

    WEPP_dic['{}_{}'.format(wshed, crop1_name)] = mod_crop1_avgs
    WEPP_dic['{}_{}'.format(wshed, crop2_name)] = mod_crop2_avgs

    print(mod_crop1_avgs)
    print(mod_crop2_avgs)


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

    output_stats_crop1 = evalulate_mod_outputs(obs_avgs_crop1, mod_crop1_avgs)
    output_stats_crop2 = evalulate_mod_outputs(obs_avgs_crop2, mod_crop2_avgs)

    print('crop1',output_stats_crop1)
    print('crop2', output_stats_crop2)

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


cal_dirs = ['DF_Comp','DF_Comp', 'DF_Comp','DF_Comp', 'DF_Comp']

output_params = []
WEPP_dic = {}
obs_dic = {}

for (cal_dir, wshed, crop1_yrs, crop2_yrs, mod_rot_starters, obs_rot, crop1_name, crop2_name)\
    in zip(cal_dirs, wshed_lst, lst_crop1_yrs, lst_crop2_yrs, lst_mod_rot_starts_wshed, obs_rot_yrs,\
           crop1_names, crop2_names):

    wshed_path = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/'.format(wshed))

    calibrate_wepp_RO(wshed_path, wshed, 'Obs', cal_dir, crop1_yrs, crop2_yrs, mod_rot_starters,\
                      obs_rot, crop1_name, crop2_name)


########## GRAPH DATA #############
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

#set up colors for crops in each watershed
crop_colors1 = ['orange', 'orange', 'purple', 'orange', 'orange']
crop_colors2 = ['green', 'green', 'orange', 'green', 'purple']

month_names = ['Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov']

#Define x/y axis coordinates for each plot
subx_vals = [0,0,1,1,0]
suby_vals = [0,1,0,1,2]


#Set up a subplot for each watershed that contains plots for each watershed
fig, axes = plt.subplots(nrows = 2, ncols = 3, figsize = (16, 12))

#loop through watershed, crops, colors for crops, and the subplot x,y coords
for wshed, crop1, color1, crop2, color2, subx, suby in \
    zip(wshed_lst, crop1_names, crop_colors1, crop2_names, crop_colors2, \
        subx_vals, suby_vals):

    #loop through dataframes in dict with modeled data
    for mod_df, obs_df in zip(WEPP_dic, obs_dic):

        #define watershed and crop name for each iteration
        crop_name = str(mod_df[4::])

        #Define colors and plot names for each crop
        if crop_name == crop1:
            color = color1
            crop_lab = crop1
        if crop_name == crop2:
            color = color2
            crop_lab = crop2

        #specify which modeled data to use based on climate model short ID
        if mod_df.startswith(wshed) and obs_df.startswith(wshed):

            x = WEPP_dic[mod_df]['RO']
            y = obs_dic[obs_df]['cal_RO']
            
            axes[subx, suby].scatter(x, y,\
                                marker = 'o', label = 'WEPP vs Observed - {}'.format(crop_lab), color = color,\
                                alpha = 1)

            axes[subx, suby].plot(y,y, color = 'black', label = 'Line for DF Obs = WEPP')

    axes[subx,suby].set_xlabel('Average Total WEPP Runoff (mm)')
    axes[subx,suby].set_ylabel('Average Total Observed Runoff (mm)')

    #Add sub-title
    axes[subx,suby].set_title(wshed)

#remove blank plot that is generated
fig.delaxes(axes[1][2])

#Add title to grouping of subplots
fig.suptitle('WEPP Outputs (1 simulation) vs DF Site Data:\n Average Total Monthly Runoff',\
              fontsize = 14)

corn = mpatches.Patch(color='orange', label='Corn')
soy = mpatches.Patch(color='green', label='Soy')
alf = mpatches.Patch(color='purple', label='Alfalfa')
fit_line = mpatches.Patch(color = 'black', label = 'Line for DF Obs = WEPP', linestyle='-')
fig.legend(handles=[corn,soy,alf,fit_line],bbox_to_anchor = [0.86,0.24], loc = 'lower right')


#save figure to comparisons folder
fig_path = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/Comparisons/WEPPvDF_ROvRO_1sim.png'
fig.savefig(fig_path)

#%%