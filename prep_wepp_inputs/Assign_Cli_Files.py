#!/usr/bin/env python
# coding: utf-8

# In[1]:
def assign_cli_files(coords_path, cli_path, Run_dir, model_labs, man_labs, periods, HUC12_name):
    '''
    Loads in GPS coordinates from .cli files, matches them with the closest hillslope coordinates,
    and then copies the .cli files to a directory under the name of the matched hillslope's ID. 

    Run_dir and cli_dir = parent directories for where .cli files are placed (Run_dir)
    and where base .cli_files are taken from (cli_dir)
    '''

    import shutil, os
    import pandas as pd
    import numpy as np


    #Read in hillslope coordinates file to dataframe and rename columns
    hillslope_coords = pd.read_excel(coords_path)
    hillslope_coords = hillslope_coords.rename(columns={'fpath': 'ID', 'LON': 'lon', 'LAT':'lat'})

    def load_cli_latlon():
        '''
        Creates dictionary of latitude and longitude values from .cli files in 
        cli_path directory
        '''
        ### Load in cli files and read in as lines in a list
        cli_lines = {}
        for file_name in os.listdir(cli_path):
            if file_name.endswith('.cli'):
                temp_lst = []
                with open (str(cli_path + file_name), 'rt') as file:
                    for line in file:
                        temp_lst.append(line)
                cli_lines[file_name] = temp_lst


        def create_latlon_dfs(cli_dic, lat_dic, lon_dic):
            '''
            Creates dictionaries of lat and lon values from each 
            .cli file that has been read into a list  

            floats are formatted to include 2 decimal places in order
            to keep trailing zeros
            '''
            for key in cli_dic:
                lat_dic[str(key[4:11])] = float(cli_dic[key][4][4:9])
                lon_dic[str(key[4:11])] = float(cli_dic[key][4][12:18])

        #Create empty dictionary for assigning lat and lon values from each file    
        lat_dic = {}
        lon_dic = {}

        create_latlon_dfs(cli_lines, lat_dic, lon_dic)

        ### Create dataframe of labels and lat/lon values from dictionaires
        coords = pd.DataFrame({'Labels':lat_dic.keys(),'lat':lat_dic.values(), 'lon': lon_dic.values()})

        ### Get unique coordinate points/areas in dataframe format
        uni_locs = coords.drop_duplicates(subset = ['lat', 'lon']).reset_index().drop('index', axis = 1)
        return uni_locs

    print('Matching hillslope coordinates to .cli coordinates...')
    uni_locs = load_cli_latlon()


    def assign_files(cli_locs_df):
        '''
        Assign the .cli files to their respective run directory for each hillslope in 
        the watershed. Lat and lon coordinates from the .cli files are matched with the 
        coordinates for each hillslope (hillslope_coords)

        cli_locs_df = dataframe with unique lat/lon values for .cli files
        '''
        
        hill_df = hillslope_coords
        
        for ID, lat, lon in zip(hill_df['ID'], hill_df['lat'], hill_df['lon']):

            ### Find index of lat/lon value in LOCA/BCCA .cli files that 
            ### most closely matches each hillslope's lat/lon values
            lat_index = cli_locs_df[['lat']].sub(lat).abs().idxmin()
            lon_index = cli_locs_df[['lon']].sub(lon).abs().idxmin()

            ### Since idxmin() does not find a single index when given two column
            ### inputs, the values that corresponds with lat_index and lon_index 
            ### must be found in order to look up the single index (CMIP5 location) 
            ### that matches both lat/lon values
            lat_cli = float(cli_locs_df['lat'].loc[lat_index])
            lon_cli = float(cli_locs_df['lon'].loc[lon_index])

            ### Look up single index/row that matches lat_cli and lon_cli then
            ### get numerical location label to help create string that 
            ### will find the correct .cli file
            cli_loc_lab = cli_locs_df.loc[(cli_locs_df['lat'] == lat_cli) & (cli_locs_df['lon'] == lon_cli), 'Labels'].iloc[0][2:5]

            ### Copy .cli file to respective run directory and rename it 
            ### to match the hillslope ID + .cli
            for mod_lab in model_labs:
                for peri_lab in periods:

                    if peri_lab == '19':
                        ### Create new cli file
                        cli_file = str(cli_path + HUC12_name + '_' + mod_lab + cli_loc_lab + peri_lab + '.cli')

                        ### Create path to hillslope directory
                        hill_dir = str(Run_dir + 'Base/' + mod_lab + '_' + peri_lab + '/' + 'wepp/' + 'runs/')

                        ### Create new file name
                        new_cli_file = str(hill_dir + 'p' + str(ID) + '.cli')

                        ### Send cli file to hillslope directory
                        shutil.copy(cli_file, new_cli_file)

                    if peri_lab == '59' or peri_lab == '99':
                        for man in man_labs:
                            ### Create path to cli file
                            cli_file_f = str(cli_path + HUC12_name + '_' + mod_lab + cli_loc_lab + peri_lab + '.cli')

                            ### Create path to hillslope directory
                            hill_dir_f = str(Run_dir + man + '/' + mod_lab + '_' + peri_lab + '/' + 'wepp/' + 'runs/')

                            ### Create new file name
                            new_cli_file_f = str(hill_dir_f + 'p' + str(ID) + '.cli')

                            ### Send cli file to hillslope directory
                            shutil.copy(cli_file_f, new_cli_file_f)
        
    print('Assigning .cli files to directories based on hillslope coordinates...')
    assign_files(uni_locs)
# In[ ]:




