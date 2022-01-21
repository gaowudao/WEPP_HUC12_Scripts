#!/usr/bin/env python
# coding: utf-8
def edit_Keff_val(scale_val,runs_dir):
    '''
    Multiplys the Keff parameter in the .sol input file by a given
    scale value for each overland flow element(OFE)

    'line 4' = Line that includes the Keff parameter for the OFE. 

    Each OFE has its own 'line 4'
    '''
    
    import os
    import pandas as pd
    import numpy as np
    
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
                    #Get K-eff value in string with rsplit and multiply it by scale_val
                    Keff = str(round(float(line.rsplit(' ',1)[1])* scale_val, 2))
                    #split line by spaces but dont include the last value (i.e. K-eff)
                    split_line = line.split(' ')[:-1]
                    #rejoin the line together and separate values by spaces (no K-eff included)
                    joined_noKeff = ' '.join(split_line)
                    #create new line with updated K-eff value
                    new_line = str(joined_noKeff + ' ' + Keff + '\n')
                    #assign new line back to lines list
                    lines[num] = new_line

            # move file pointer to the beginning of a file
            file.seek(0)
            # truncate the file
            file.truncate()

            #write new lines
            file.writelines(lines)

wshed_lst = ['BE1', 'DO1', 'GO1', 'RO1', 'ST1']

for wshed in wshed_lst:
    scen_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/DF_Comp10/'.format(wshed)
    period = '_19'
    mod_labs = ['L3', 'L4','B3', 'B4']

    for mod in mod_labs:
        runs_dir = str(scen_dir + mod + period + '/wepp/runs/')
        edit_Keff_val(10, runs_dir)


# In[ ]:




