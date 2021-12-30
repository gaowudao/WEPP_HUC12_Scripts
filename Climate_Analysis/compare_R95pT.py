
#%%import os
import pandas as pd
import scipy
import scipy.stats
import numpy as np


def compare_models(mod_rcps, HUC12_path):
    '''
    '''

    def get_cli_dfs(scen_dir, mod, period, years):
        '''
        Generate seasonal averages of climate variables across the entire watershed
        and total number of years in each .cli file. Data is returned to four different
        dataframes based on the seasons

        scen_dir = management scenario directory
        mod = climate model
        period = time period ID
        years = number of years modeled in .cli file
        '''

        #Set path to runs directory that includes .cli files being used in WEPP runs
        runs_dir = str(HUC12_path + 'Runs/' + scen_dir + '/' + mod + '_{}'.format(period) +  '/wepp/runs/')

        #Create seasonal lists to append dataframes to once
        fall_dfs = {}
        winter_dfs = {}
        spring_dfs = {}
        summer_dfs = {}

        year_index = range(1,years+1)

        #loop through all files in directory
        for file in os.listdir(runs_dir):
            #only select .cli files
            if file.endswith('.cli'):

                #Read cligen file data into dataframe and remove row with units
                cli_data = pd.read_csv(str(runs_dir + file), skiprows = 13, sep = '\s+| ', engine = 'python')
                cli_data.drop([0,], axis = 0, inplace = True)
                cli_data[['prcp', 'dur', 'tp', 'ip']] = cli_data[['prcp', 'dur', 'tp', 'ip']].where(cli_data['prcp'].astype(float)>0.3, other=0)
                cli_data['tmax'] = cli_data['tmax'].astype(float)
                cli_data['tmin'] = cli_data['tmin'].astype(float)
                cli_data['prcp'] = cli_data['prcp'].astype(float)
                cli_data['dur'] = cli_data['dur'].astype(float)
                cli_data['year'] = cli_data['year'].astype(int)
                cli_data['Month'] = cli_data['mo'].astype(int)

                #rename columns and set them as floats/ints (loaded in as strings)
                def group_by_season(months):
                    '''
                    Returns a dataframe with the seasonal averages of select .cli data

                    months = month numbers as integers
                    '''
                    
                    #Select data in cli_data corresponding to a list of months in each season 
                    df = pd.DataFrame(cli_data[cli_data['Month'].isin(months)])
                    #Get series where precip events > 1mm from 'df'
                    df_G1 = df[df['prcp'].astype(float) >= 1]

                    #95th percentile of prcp for specificed months throughout entire period
                    q95 = df_G1['prcp'].astype(float).quantile(0.95) #95th percentile of prcp
                    #Seasonal percent of prcp above 95th percentile for every year
                    R95pT = (df_G1[df_G1['prcp'] > q95].astype(float).groupby('year')['prcp'].sum() / df_G1.groupby('year')['prcp'].sum())*100

                    
                    #Send numbers to dataframes with corresponding col names
                    season = pd.DataFrame({'R95pT':R95pT}, index = year_index)
                    return season

                #Combine monthly data by seasons
                fall_dfs[file[:-4]] = group_by_season([9,10,11])
                spring_dfs[file[:-4]] = group_by_season([3,4,5])
                summer_dfs[file[:-4]] = group_by_season([6,7,8])
                winter_dfs[file[:-4]] = group_by_season([12,1,2])

        #Get the average seasonal watershed value for each climate variable
        fall = pd.concat(fall_dfs).groupby(level=1).mean()
        spring = pd.concat(spring_dfs).groupby(level=1).mean()
        summer = pd.concat(summer_dfs).groupby(level=1).mean()
        winter = pd.concat(winter_dfs).groupby(level=1).mean()
        
        return fall,spring,summer,winter


    #Run get_cli_dfs for each time period and rcp scenario and assign output dfs to lists
    r1_19 = list(get_cli_dfs('Base', mod_rcps[0], '19', 55))
    r2_19 = list(get_cli_dfs('Base', mod_rcps[1], '19', 55))
    r1_59 = list(get_cli_dfs('CC', mod_rcps[0], '59', 40))
    r2_59 = list(get_cli_dfs('CC', mod_rcps[1], '59', 40))
    r1_99 = list(get_cli_dfs('CC', mod_rcps[0], '99', 40))
    r2_99 = list(get_cli_dfs('CC', mod_rcps[1], '99', 40))

    #create list of season number IDs based on lists created from get_cli_dfs
    #fall = 0, spring = 1, summer = 2, and winter = 3
    season_IDs = [0,1,2,3]

    #create list of variable names (i.e. columns in output dataframes from get_cli_dfs)
    var_lst = ['R95pT']

    #loop through models in mod_rcps
    def analyze_trends(r19, r59, r99):

        #create a list to append trends to for each season
        fall_trends = []
        spring_trends = []
        summer_trends = []
        winter_trends = []

        trend_lsts = [fall_trends, spring_trends, summer_trends, winter_trends]

        #loop through seasons
        for season_ID,trend_lst in zip(season_IDs, trend_lsts):
            #loop through climate analysis variables
            for var in var_lst:

                #get mean value of each variable series in dataframe
                mean19 = r19[season_ID][var].mean()
                mean59 = r59[season_ID][var].mean()
                mean99 = r99[season_ID][var].mean()

                #Perform welch's two sample t-tests to determine if variables are significantly different from
                #one another in the various time periods
                stat, p19v59 = scipy.stats.ttest_ind(r19[season_ID][var], r59[season_ID][var], equal_var=True)
                
                #if difference between periods is significant for a variable, append their difference
                if p19v59 <= 0.051:
                    trend_lst.append(mean59 - mean19)
                #if trend is not significant, append 'NoDiff' to symbolize no difference
                else:
                    trend_lst.append('NoDiff')

                stat1, p19v99 = scipy.stats.ttest_ind(r19[season_ID][var], r99[season_ID][var], equal_var=True)
                if p19v99 <= 0.051:
                    trend_lst.append(mean99 - mean19)
                else:
                    trend_lst.append('NoDiff')

                stat, p59v99 = scipy.stats.ttest_ind(r59[season_ID][var], r99[season_ID][var], equal_var=True)
                if p59v99 <= 0.051:
                    trend_lst.append(mean99 - mean59)
                else:
                    trend_lst.append('NoDiff')

        #Create a dataframe for each season where each column is one of the climate variables 
        trends_df = pd.DataFrame({'fall_R95pT':fall_trends[0:3], 'spring_R95pT':spring_trends[0:3],\
                                  'summer_R95pT':summer_trends[0:3], 'winter_R95pT':winter_trends[0:3]})

        return(trends_df)

    #Assign trends_df output to the trends_dic dictionary
    r1_df = analyze_trends(r1_19, r1_59, r1_99)
    r2_df = analyze_trends(r2_19, r2_59, r2_99)

    return r1_df, r2_df

#Define labels for models and their rcp pairs
LOCA_pairs = [['L1','L2'], ['L3', 'L4'], ['L5', 'L6']]
LOCA_mods = ['csiro_mk3_6_01', 'hadgem2_cc_1', 'giss_e2_h_6']

BCCA_pairs = [['B1','B2'], ['B3', 'B4'], ['B5', 'B6']]
BCCA_mods = ['ccsm4_1', 'gfdl_esm2g_1', 'ipsl_cm5a_mr_1']

wshed_lst = ['BE1']

climate_trends_wshed = {}

for wshed in wshed_lst:

    HUC12_path = 'E:/Soil_Erosion_Project/WEPP_PRWs/{}/'.format(wshed)
    for pair, mod in zip(LOCA_pairs, LOCA_mods):
        climate_trends_wshed[str(wshed+'_'+mod+'_'+pair[0])],\
        climate_trends_wshed[str(wshed+'_'+mod+'_'+pair[1])] = compare_models(pair, HUC12_path)
    for pair,mod in zip(BCCA_pairs, BCCA_mods):
        climate_trends_wshed[str(wshed+'_'+mod+'_'+pair[0])],\
        climate_trends_wshed[str(wshed+'_'+mod+'_'+pair[1])] = compare_models(pair, HUC12_path)

with pd.ExcelWriter('E:/Soil_Erosion_Project/WEPP_PRWs/BE1/BE1_R95pT_trends.xlsx') as writer:
    for df in climate_trends_wshed:
        climate_trends_wshed[df].to_excel(writer, sheet_name=df)
#%%