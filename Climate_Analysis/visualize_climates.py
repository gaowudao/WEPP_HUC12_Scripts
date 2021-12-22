#%%
def vis_climates(mod_rcps, HUC12_path, dwnsc_type, model_name, out_path, wshed):
    '''
    '''
    
    import os
    import pandas as pd
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

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
                    
                    #group data by month numbers corresponding to the season input and turn into new dataframe
                    df = pd.DataFrame(cli_data[cli_data['Month'].isin(months)])
                    tmax = df['tmax'].mean()
                    tmin = df['tmin'].mean()
                    precip = df['prcp'].sum() / years
                    df_G1 = df['prcp'][df['prcp'].astype(float) >= 1] #series where precip events > 1mm
                    R10 = df_G1[df_G1.astype(float) > 10].count() / years #No. days with prcp above 10mm
                    R25 = df_G1[df_G1.astype(float) > 25].count() / years #No. days with prcp above 20mm
                    q95 = df_G1.astype(float).quantile(0.95) #95th percentile of prcp
                    #Avg seasonal percent of prcp above 95th percentile
                    R95pT = (df_G1[df_G1 > q95].astype(float).sum() / df_G1.sum())*100

                    
                    #Send numbers to dataframes with corresponding col names
                    season = pd.DataFrame({'tmax':tmax, 'tmin':tmin, 'precip':precip,\
                                           'R10':R10, 'R25':R25, 'R95pT':R95pT}, index = [0])
                    return season

                #Combine monthly data by seasons
                fall_dfs[file[:-4]] = group_by_season([9,10,11])
                winter_dfs[file[:-4]] = group_by_season([12,1,2])
                spring_dfs[file[:-4]] = group_by_season([3,4,5])
                summer_dfs[file[:-4]] = group_by_season([6,7,8])

        #Get the average seasonal watershed value for each climate variable
        fall = pd.concat(fall_dfs, axis = 0).mean()
        winter = pd.concat(winter_dfs, axis = 0).mean()
        spring = pd.concat(spring_dfs, axis = 0).mean()
        summer = pd.concat(summer_dfs, axis = 0).mean()
        
        #Separate the variables into different lists and append the corresponding seasonal values
        tmax = []
        tmin = []
        precip = []
        R10 = []
        R25 = []
        R95pT = []

        ##Loop through season dataframes and append each variable average to corresponding list
        for season in [winter, spring, summer,fall]:
            tmax.append(season['tmax'].round(1))
            tmin.append(season['tmin'].round(1))
            precip.append(season['precip'].round(1))
            R10.append(season['R10'].round(1))
            R25.append(season['R25'].round(1))
            R95pT.append(season['R95pT'].round(1))

        #return dictionary of lists for each variable
        return {'tmax':tmax, 'tmin':tmin, 'precip':precip,\
                'R10':R10, 'R25':R25, 'R95pT':R95pT}


    #Run get_cli_dfs for each time period and rcp scenario
    r1_19 = get_cli_dfs('Base', mod_rcps[0], '19', 55)
    r2_19 = get_cli_dfs('Base', mod_rcps[1], '19', 55)
    r1_59 = get_cli_dfs('CC', mod_rcps[0], '59', 40)
    r2_59 = get_cli_dfs('CC', mod_rcps[1], '59', 40)
    r1_99 = get_cli_dfs('CC', mod_rcps[0], '99', 40)
    r2_99 = get_cli_dfs('CC', mod_rcps[1], '99', 40)


    #Define: 
    seasons = ['Winter', 'Spring', 'Summer', 'Fall'] #x-axis labels
    x_len = np.arange(len(seasons)) #x-tick mark locations
    deg_symbol = u"\N{DEGREE SIGN}"  #temperature degree symbol

    ##Define RCP scenario - dependent on which downscaling method is being
    ##depicted in figures
    if dwnsc_type == 'LOCA':
        rcp1_ID = '4.5'
        rcp2_ID = '8.5'

    if dwnsc_type == 'BCCA':
        rcp1_ID = '4.5'
        rcp2_ID = '6.0'


    def create_barplot(var, title, var_y, subx, suby):
        '''
        Creates bar graph of seasonal data for each variable. Each graph 
        is a subplot on coordinate subx,suby

        var = climate variable/statistic being depicted
        title = title of subplot
        subx = x coordinate value of subplot
        suby = y coordinate value of subplot
        '''

        ##Plot bars for each time period and rcp scenario. RCP scenarios have '/' hatch pattern
        f1 = axes[subx,suby].bar(x_len-0.32,r1_19[var],0.1, color='lightsteelblue', edgecolor='black')
        ##label each bar with its value
        axes[subx,suby].bar_label(f1, padding = 2, fontsize = 5)

        f2 = axes[subx,suby].bar(x_len-0.2,r2_19[var],0.1, color = 'lightsteelblue', edgecolor='black', hatch='/')
        axes[subx,suby].bar_label(f2, padding = 2, fontsize = 5)

        f3 = axes[subx,suby].bar(x_len-0.06,r1_59[var],0.1, color = 'royalblue',edgecolor='black')
        axes[subx,suby].bar_label(f3, padding = 2, fontsize = 5)

        f4 = axes[subx,suby].bar(x_len+0.06,r2_59[var],0.1, color = 'royalblue', edgecolor='black', hatch='/')
        axes[subx,suby].bar_label(f4, padding = 2, fontsize = 5)

        f5 = axes[subx,suby].bar(x_len+0.2,r1_99[var],0.1, color = 'skyblue', edgecolor='black')
        axes[subx,suby].bar_label(f5, padding = 2, fontsize = 5)

        f6 = axes[subx,suby].bar(x_len+0.32,r2_99[var],0.1, color = 'skyblue', edgecolor='black', hatch='/')
        axes[subx,suby].bar_label(f6, padding = 2, fontsize = 5)

        ##Set y-axis label, x-tick labels, and title
        axes[subx,suby].set_ylabel(var_y)
        axes[subx,suby].set_xticks(x_len, seasons) #set x-tick labels to seasons
        axes[subx,suby].axhline(0, color='black', linewidth=0.8)
        axes[subx,suby].set_title('{}'.format(title))

        if var == 'R95pT':
            axes[subx,suby].set_ylim(0,100)


    #Set up subplot and have plots share x axis (seasons)
    fig, axes = plt.subplots(nrows = 3, ncols = 2, figsize = (14, 14))
    
    #Set up legend for RCP scenarios and time periods. Use mpatches.Patch to create custom legend
    rcp1 = mpatches.Patch(color = 'black', fill=False, label='RCP {}'.format(rcp1_ID))
    rcp2 = mpatches.Patch(color='black', hatch ='//', fill=False, label='RCP {}'.format(rcp2_ID))
    lab_19 = mpatches.Patch(color = 'lightsteelblue', fill=True, edgecolor = 'black', label='1965-2019')
    lab_59 = mpatches.Patch(color = 'royalblue', fill=True, edgecolor = 'black', label='2020-2059')
    lab_99 = mpatches.Patch(color = 'skyblue', fill=True, edgecolor = 'black', label='2060-2099')
    legend = fig.legend(handles = [lab_19, lab_59, lab_99, rcp1, rcp2], bbox_to_anchor=(1, 0.9), loc = 'lower right')
    fig.add_artist(legend)

    #Run create_barplot to create each subplot
    create_barplot('tmax', 'Average Max Temperature ({}C)'.format(deg_symbol),\
                   'Temperature ({}C)'.format(deg_symbol), 0,0)
    create_barplot('tmin', 'Average Min Temperature ({}C)'.format(deg_symbol),\
                   'Temperature ({}C)'.format(deg_symbol), 1,0)
    create_barplot('precip', 'Average Total Precipitation (mm)', 'Precipitation (mm)', 2,0)
    create_barplot('R10', 'No. Days > 10mm', '# of Days', 0,1)
    create_barplot('R25', 'No. Days > 25mm','# of Days', 1,1)
    create_barplot('R95pT', 'Percent of Precipitation > Seasonal 95th Percentile',\
                   'Percent of Precip (%)', 2,1)



    fig.suptitle('{} {} {}\n'.format(wshed,dwnsc_type, model_name), fontsize = 14)
    fig.tight_layout()

    #Save figure
    fig.savefig(str(HUC12_path + out_path))

LOCA_pairs = [['L1','L2'], ['L3', 'L4'], ['L5', 'L6']]
LOCA_mods = ['csiro_mk3_6_01', 'hadgem2_cc_1', 'giss_e2_h_6']

BCCA_pairs = [['B1','B2'], ['B3', 'B4'], ['B5', 'B6']]
BCCA_mods = ['ccsm4_1', 'gfdl_esm2g_1', 'ipsl_cm5a_mr_1']

wshed_lst = ['BE1', 'DO1', 'RO1', 'ST1']

for wshed in wshed_lst:

    HUC12_path = 'E:/Soil_Erosion_Project/WEPP_PRWs/{}/'.format(wshed)

    for LOCA_pair, mod in zip(LOCA_pairs, LOCA_mods):
        vis_climates(LOCA_pair, HUC12_path, 'LOCA', mod, '{}_LOCA_clim/{}.pdf'.format(wshed, mod), wshed)
    for BCCA_pair, mod in zip(BCCA_pairs, BCCA_mods):
        vis_climates(BCCA_pair, HUC12_path, 'BCCA', mod, '{}_BCCA_clim/{}.pdf'.format(wshed, mod), wshed)


# %%
