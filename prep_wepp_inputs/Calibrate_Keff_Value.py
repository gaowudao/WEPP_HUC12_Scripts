#!/usr/bin/env python
# coding: utf-8

# In[4]:


import os
import pandas as pd
import numpy as np

scen_dir = 'C:\\Users\\Garner\\Soil_Erosion_Project\\WEPP_PRWs\\GO1_DEP\\Runs\\DEP_DF_10K\\'


def edit_Keff_val(mod_labs, scen_dir, scale_val):

    '''
    Multiplys the Keff parameter in the .sol input file by a given
    scale value for each overland flow element(OFE)

    'line 4' = Line that includes the Keff parameter for the OFE. 

    Each OFE has its own 'line 4'
    '''
    #Create path to run directory
    run_dir = str(scen_dir + mod + '_19' + '\\wepp\\runs\\')

    #loop through all input files in directory
    for file_name in os.listdir(run_dir):

        #select soil files
        if file_name.endswith('.sol'):
            file = open(str(run_dir+file_name), "r+") # read in file 
            lines = file.readlines()  #read lines to a list

            #loop through selected lines in each file
            for num, line in enumerate(lines, 0):

                find_key = '0.750000' # Find 'Line 4' for each OFE

                if find_key in line:
                    new_line = str(line[:-9] + str(round(float(line[-9::])*scale_val, 6)) + '\n')
                    lines[num] = new_line

            # move file pointer to the beginning of a file
            file.seek(0)
            # truncate the file
            file.truncate()

            #write new lines
            file.writelines(lines)
                               
                
scen_dir = 'C:\\Users\\Garner\\Soil_Erosion_Project\\WEPP_PRWs\\GO1_DEP\\Runs\\DEP_DF_10K\\'

edit_Keff_val(scen_dir, 10)


# In[ ]:




