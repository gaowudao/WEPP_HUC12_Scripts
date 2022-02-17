#!/usr/bin/env python
# coding: utf-8

# In[1]:
def gen_cli_file(site_name,par_path):

    import os
    import pandas as pd
    import numpy as np
 
    ###### Create .CLI files ########

    ### Read in .PAR files
    os.chdir(par_path)
    par_files = [x for x in os.listdir(par_path) if x.startswith(site_name) and x.endswith(".par")]


    def par_to_cli(path,file_lst):
        '''
        Generate .CLI files from .PAR station files. cli files
        are the final input file used for WEPP project.

        -b = start year
        -y = end year
        -i = input file
        -o = output file (.cli added to end of each file)
        -t = simulation type (5 = simulation for WEPP input)
        '''
        os.chdir(path)
        for file in file_lst:

            if file.endswith('_19.par'):
                years = 55
            if file.endswith(('_59.par', '_99.par')):
                years = 40

            os.system("cligen53.exe -b1 -y{} -i{} -o{}.cli -t5".format(years,file,str(file)[:-4]))


    print('Generating .cli file from .par file...')
    par_to_cli(par_path,par_files)

top_path = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/GO1/GDS/Obs/obs_sub/'
par_path = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/GO1/PAR/Obs/obs_sub/'
site_name = 'GO1'

gen_cli_file(site_name,par_path)