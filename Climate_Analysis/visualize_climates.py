def vis_climates(mod_labs, HUC12_path):
    '''
    '''
    
    import os
    import pandas as pd
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt

    def get_cli_dfs(scen_dir, period, years):
        '''
        '''

        #loop through all climate models
        for mod in mod_labs:

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
                    cli_data['tmax'] = cli_data['tmax'].astype(float)
                    cli_data['tmin'] = cli_data['tmin'].astype(float)
                    cli_data['prcp'] = cli_data['prcp'].astype(float)
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
                        events = df['prcp'].agg(lambda x: x.ne(0).sum()) / years
                        pr_e = precip / events

                        season = pd.DataFrame({'tmax':tmax, 'tmin':tmin, 'precip':precip, 'precip/event':pr_e}, index = [0])
                        return season

                    #Combine monthly data by seasons
                    fall_dfs[file[:-4]] = group_by_season([9,10,11])
                    winter_dfs[file[:-4]] = group_by_season([12,1,2])
                    spring_dfs[file[:-4]] = group_by_season([3,4,5])
                    summer_dfs[file[:-4]] = group_by_season([6,7,8])

            fall = pd.concat(fall_dfs, axis = 0).mean()
            winter = pd.concat(winter_dfs, axis = 0).mean()
            spring = pd.concat(spring_dfs, axis = 0).mean()
            summer = pd.concat(summer_dfs, axis = 0).mean()

            print(summer)



    get_cli_dfs('Base', '19', 55)

HUC12_path = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/BE1/'
vis_climates(['L1'], HUC12_path)


