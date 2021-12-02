#!/usr/bin/env python
# coding: utf-8

# In[1]:


import shutil, os
import pandas as pd
import numpy as np

def assign_cli_files(coords_path, cli_path, hill_dir, model_labs, wshed):
    '''
    Loads in GPS coordinates from .cli files, matches them with the closest hillslope coordinates,
    and then copies the .cli files to a directory under the name of the matched hillslope's ID. 
    '''
    #Read in hillslope coordinates file to dataframe and rename columns
    hillslope_coords = pd.read_csv(coords_path)
    hillslope_coords = hillslope_coords.rename(columns={'fpath': 'ID', 'LON': 'lon', 'LAT':'lat'})

    def load_cli_latlon():
        '''
        Creates dictionary of latitude and longitude values from .cli files in 
        cli_path directory
        '''
        ### Load in cli files
        os.chdir(cli_path)
        cli_files = [x for x in os.listdir('.') if x.endswith('.cli')]

        ### Read in top files as lines in a list
        cli_lines = {}
        for file_name in cli_files:
            temp_lst = []
            with open (file_name, 'rt') as file:
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

        #Create dictionary of lat and lon values in each file    
        lat_dic = {}
        lon_dic = {}

        create_latlon_dfs(cli_lines, lat_dic, lon_dic)

        ### Create dataframe from dictionaires
        coords = pd.DataFrame({'Labels':lat_dic.keys(),'lat':lat_dic.values(), 'lon': lon_dic.values()})

        ### Get unique coordinate points/areas in dataframe format
        uni_locs = coords.drop_duplicates(subset = ['lat', 'lon']).reset_index().drop('index', axis = 1)
        return uni_locs

    uni_locs = load_cli_latlon(cli_path)


    def assign_files(cli_locs_df):
        '''
        Assign the .cli files to their respective run directory for each hillslope in 
        the watershed. Lat and lon coordinates are used to match hillslopes with the
        climate region/file they are in. 

        hill_dict = dictionary with hillslope info

        cli_locs_df = dataframe with unique lat/lon values for .cli files

        hill_dir and cli_dir = parent directories for where .cli files are placed (hill_dir)
        and where base .cli_files are taken from (cli_dir)

        wshed = name of watershed with WEPP hilsllopes
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


            period_labels = ['19', '59', '99']
            man_labels = ['CC', 'CT', 'Comb', 'Per', 'NC']

            for mod_lab in model_labels:
                for peri_lab in period_labels:

                    if peri_lab == '19':
                        ### Create path to cli file
                        cli_file = str(cli_dir + wshed + '_' + mod_lab + cli_loc_lab + peri_lab + '.cli')

                        ### Create path to hillslope directory
                        new_hill_dir = str(hill_dir + 'Base//' + mod_lab + '_' + peri_lab + '//' + 'wepp//' + 'runs//')

                        ### Create new file name
                        new_hill_file = str(new_hill_dir + 'p' + str(ID) + '.cli')

                        ### Send cli file to hillslope directory
                        shutil.copy(cli_file, new_hill_file)

                    if peri_lab == '59' or peri_lab == '99':
                        for man in man_labels:
                            ### Create path to cli file
                            cli_file = str(cli_dir + wshed + '_' + mod_lab + cli_loc_lab + peri_lab + '.cli')

                            ### Create path to hillslope directory
                            new_hill_dir_f = str(hill_dir + man + '//' + mod_lab + '_' + peri_lab + '//' + 'wepp//' + 'runs//')

                            ### Create new file name
                            new_hill_file_f = str(new_hill_dir_f + 'p' + str(ID) + '.cli')

                            ### Send cli file to hillslope directory
                            shutil.copy(cli_file, new_hill_file_f)
        

        assign_files(uni_locs): 

        
#Set up assign_cli_files inputs                
coords_path = 'C://Users//Garner//Soil_Erosion_Project//WEPP_PRWs//GO1_DEP//Residue_Data//flowpaths.csv'            

LOCA_cli_path = 'C://Users//Garner//Soil_Erosion_Project//WEPP_PRWs//GO1_DEP//PAR//LOCA_1116//'
BCCA_cli_path = 'C://Users//Garner//Soil_Erosion_Project//WEPP_PRWs//GO1_DEP//PAR//LOCA_1116//'

Runs_path = 'C://Users//Garner//Soil_Erosion_Project//WEPP_PRWs//GO1_DEP//Runs//'

LOCA_mod_labels = ['L1','L2','L3','L4','L5','L6']    
BCCA_mod_labels = ['B1','B2','B3','B4','B5','B6']


assign_cli_files(coords_path, LOCA_cli_path, Runs_path, LOCA_mod_labels, 'GO1')
assign_cli_files(coords_path, BCCA_cli_path, Runs_path, BCCA_mod_labels, 'GO1')


# In[ ]:




