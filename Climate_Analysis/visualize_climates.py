#%%
def vis_climates(mod_rcps, HUC12_path, dwnsc_type, model_name, out_path):
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
                    tmax = round(df['tmax'].mean(), 1)
                    tmin = round(df['tmin'].mean(), 1)
                    precip = round(df['prcp'].sum() / years,1)
                    df_G1 = df['prcp'][df['prcp'].astype(float) >= 1] #series where precip events > 1mm
                    R10 = round(df_G1[df_G1.astype(float) > 10].count() / years, 1) #No. days with prcp above 10mm
                    R25 = round(df_G1[df_G1.astype(float) > 25].count() / years, 1) #No. days with prcp above 20mm
                    q95 = df_G1.astype(float).quantile(0.95) #95th percentile of prcp
                    #Avg seasonal percent of prcp above 95th percentile
                    R95pT = round((df_G1[df_G1 > q95].astype(float).sum() / df_G1.sum())*100, 1)

                    
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
            tmax.append(season['tmax'])
            tmin.append(season['tmin'])
            precip.append(season['precip'])
            R10.append(season['R10'])
            R25.append(season['R25'])
            R95pT.append(season['R95pT'])

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


    def create_barplot(var, var_title, var_y, plot_name):
        #Create bar graph of seasonal data for each variable

        ##Plot bars for each time period and rcp scenario. RCP scenarios have '/' hatch pattern
        f1 = plot_name.bar(x_len-0.3,r1_19[var],0.1, color='lightsteelblue', edgecolor='black')
        ##label each bar with its value
        plot_name.bar_label(f1, padding = 3, fontsize = 6)
        f2 = plot_name.bar(x_len-0.2,r2_19[var],0.1, color = 'lightsteelblue', edgecolor='black', hatch='/')
        plot_name.bar_label(f2, padding = 1, fontsize = 6)
        f3 = plot_name.bar(x_len-0.05,r1_59[var],0.1, color = 'royalblue',edgecolor='black')
        plot_name.bar_label(f3, padding = 3, fontsize = 6)
        f4 = plot_name.bar(x_len+0.05,r2_59[var],0.1, color = 'royalblue', edgecolor='black', hatch='/')
        plot_name.bar_label(f4, padding = 1, fontsize = 6)
        f5 = plot_name.bar(x_len+0.2,r1_99[var],0.1, color = 'skyblue', edgecolor='black')
        plot_name.bar_label(f5, padding = 3, fontsize = 6)
        f6 = plot_name.bar(x_len+0.3,r2_99[var],0.1, color = 'skyblue', edgecolor='black', hatch='/')
        plot_name.bar_label(f6, padding = 1, fontsize = 6)

        ##Set y-axis label, x-tick labels, and title
        plot_name.set_ylabel(var_y)
        plot_name.set_xticks(x_len, seasons) #set x-tick labels to seasons
        plot_name.axhline(0, color='black', linewidth=0.8)
        plot_name.set_title('{}'.format(var_title))


    #Set up subplot and have plots share x axis (seasons)
    fig, (cli1,cli2,cli3,cli4,cli5,cli6) = plt.subplots(nrows = 6, ncols = 1, figsize = (8, 12))
    
    #Set up legend for RCP scenarios and time periods. Use mpatches.Patch to create custom legend
    rcp1 = mpatches.Patch(color = 'black', fill=False, label='RCP {}'.format(rcp1_ID))
    rcp2 = mpatches.Patch(color='black', hatch ='//', fill=False, label='RCP {}'.format(rcp2_ID))
    lab_19 = mpatches.Patch(color = 'lightsteelblue', fill=True, edgecolor = 'black', label='1965-2019')
    lab_59 = mpatches.Patch(color = 'royalblue', fill=True, edgecolor = 'black', label='2020-2059')
    lab_99 = mpatches.Patch(color = 'skyblue', fill=True, edgecolor = 'black', label='2060-2099')
    legend = fig.legend(handles = [lab_19, lab_59, lab_99, rcp1, rcp2], bbox_to_anchor=(1, 0.93), loc = 'lower right')
    fig.add_artist(legend)

    #Run create_barplot to create each subplot
    create_barplot('tmax', 'Average Max Temperature ({}C)'.format(deg_symbol),\
                   'Temperature ({}C)'.format(deg_symbol), cli1)
    create_barplot('tmin', 'Average Min Temperature ({}C)'.format(deg_symbol),\
                   'Temperature ({}C)'.format(deg_symbol), cli2)
    create_barplot('precip', 'Average Total Precipitation (mm)', 'Precipitation (mm)', cli3)
    create_barplot('R10', 'No. Days > 10mm', '# of Days', cli4)
    create_barplot('R25', 'No. Days > 25mm','# of Days', cli5)
    create_barplot('R95pT', 'Percent of Precipitation > Seasonal 95th Percentile',\
                   'Percent of Precip (%)', cli6)



    fig.suptitle('{} {}\n'.format(dwnsc_type, model_name), fontsize = 14)
    fig.tight_layout()

    #Save figure
    fig.savefig(str(HUC12_path + out_path))

        

HUC12_path = 'E:/Soil_Erosion_Project/WEPP_PRWs/DO1/'

vis_climates(['L1', 'L2'], HUC12_path, 'LOCA', 'csiro-mk3-6-0.1', 'DO1_LOCA_clim/csiro_mk3_6_0_1.pdf')

# %%
