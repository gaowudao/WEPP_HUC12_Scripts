#%%
def vis_climates(mod_rcps, HUC12_path, dwnsc_type, model_name):
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
                cli_data['pr_I'] = cli_data['prcp'].div(cli_data['dur']) #precip intensity

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
                    pr_I = df['pr_I'].mean()
                    

                    season = pd.DataFrame({'tmax':tmax, 'tmin':tmin, 'precip':precip, 'pr_I':pr_I}, index = [0])
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
        pr_I = []

        ##Loop through season dataframes and append each variable average to corresponding list
        for season in [winter, spring, summer,fall]:
            tmax.append(season['tmax'])
            tmin.append(season['tmin'])
            precip.append(season['precip'])
            pr_I.append(season['pr_I'])

        #return dictionary of lists
        return {'tmax':tmax, 'tmin':tmin, 'precip':precip, 'pr_I':pr_I}


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


    def create_barplot(var, var_title, plot_name):
        #Create bar graph of seasonal data for each variable

        ##Plot bars for each time period and rcp scenario. RCP scenarios have '/' hatch pattern
        plot_name.bar(x_len-0.3,r1_19[var],0.1, label='1965-2019', color='lightsteelblue', edgecolor='black')
        plot_name.bar(x_len-0.2,r2_19[var],0.1,color = 'lightsteelblue', edgecolor='black', hatch='/')
        plot_name.bar(x_len-0.05,r1_59[var],0.1, label='2020-2059', color = 'royalblue',edgecolor='black')
        plot_name.bar(x_len+0.05,r2_59[var],0.1, color = 'royalblue', edgecolor='black', hatch='/')
        plot_name.bar(x_len+0.2,r1_99[var],0.1, label='2060-2099', color = 'skyblue', edgecolor='black')
        plot_name.bar(x_len+0.3,r2_99[var],0.1, color = 'skyblue', edgecolor='black', hatch='/')

        ##Create legend for RCP scenarios
        rcp1 = mpatches.Patch(color = 'black', fill=False, label='RCP {}'.format(rcp1_ID))
        rcp2 = mpatches.Patch(color='black', hatch ='//', fill=False, label='RCP {}'.format(rcp2_ID))
        rcp_legend = plot_name.legend(handles = [rcp1, rcp2], loc = 'upper right')
        plot_name.add_artist(rcp_legend)

        ##Create regular legend, set y-axis label, x-tick labels, and title
        plot_name.legend(loc = 'upper left')
        plot_name.set_ylabel(var_title)
        plot_name.set_xticks(x_len, seasons) #set x-tick labels to seasons
        plot_name.axhline(0, color='black', linewidth=0.8)
        plot_name.set_title('{}'.format(var_title))


    #Set up subplot and have plots share x axis (seasons)
    fig, (cli1,cli2,cli3,cli4) = plt.subplots(nrows = 4, ncols = 1, figsize = (8, 14))

    #Run create_barplot to create each subplot
    create_barplot('tmax', 'Average Max Temperature ({}C)'.format(deg_symbol), cli1)
    create_barplot('tmin', 'Average Min Temperature ({}C)'.format(deg_symbol), cli2)
    create_barplot('precip', 'Average Total Precipitation (mm)', cli3)
    create_barplot('pr_I', 'Average Precipitation Intensity  (mm/hr)', cli4)


    fig.suptitle('{} {}\n'.format(dwnsc_type, model_name), fontsize = 14,)
    fig.tight_layout()

    #Save figure
    fig.savefig('test.pdf')

        

HUC12_path = 'E:/Soil_Erosion_Project/WEPP_PRWs/BE1/'

vis_climates(['L5', 'L6'], HUC12_path, 'LOCA', 'giss-e2-h.6')



# %%
