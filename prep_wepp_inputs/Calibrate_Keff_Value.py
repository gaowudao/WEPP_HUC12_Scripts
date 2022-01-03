#!/usr/bin/env python
# coding: utf-8

# In[4]:


import os
import pandas as pd
import numpy as np


def edit_Keff_val(scale_val, runs_dir):
        '''
        Multiplys the Keff parameter in the .sol input file by a given
        scale value for each overland flow element(OFE)

        'line 4' = Line that includes the Keff parameter for the OFE. 

        Each OFE has its own 'line 4'
        '''
        #loop through all input files in directory
        for file_name in os.listdir(runs_dir):

            #select soil files
            if file_name.endswith('.sol'):
                file = open(str(runs_dir+file_name), "r+") # read in file 
                lines = file.readlines()  #read lines to a list

                #loop through selected lines in each file
                for num, line in enumerate(lines, 0):

                    find_key = '0.750000' # Find 'Line 4' for each OFE

                    if find_key in line:
                        new_line = str(line[:-1] + str(round(float(line[-3::])*scale_val, 6)) + '\n')
                        lines[num] = new_line

                # move file pointer to the beginning of a file
                file.seek(0)
                # truncate the file
                file.truncate()

                #write new lines
                file.writelines(lines)

scen_dir = 'E:/Soil_Erosion_Project/WEPP_PRWs/DO1/Runs/DF_Comp/'
period = '_19'
mod_labs = ['L3', 'L4', 'B1', 'B2', 'B3', 'B4']

for mod in mod_labs:
    runs_dir = str(scen_dir + mod + period + '/wepp/runs/')
    edit_Keff_val(10, runs_dir)


# In[ ]:




