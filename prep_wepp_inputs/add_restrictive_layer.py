def restrictive_layer(runs_dir):
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

                find_key = '0 0.000000 0' # Find 'line with restrive layer input options' for soil file

                if find_key in line:
                    #create new line with updated K-eff value
                    new_line = str('1 13 2.000000 0.005 \n')
                    #assign new line back to lines list
                    lines[num] = new_line

            # move file pointer to the beginning of a file
            file.seek(0)
            # truncate the file
            file.truncate()

            #write new lines
            file.writelines(lines)


wshed_lst = ['ST1']

for wshed in wshed_lst:
    scen_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/DF_Comp/'.format(wshed)
    period = '_19'
    mod_labs = ['L3', 'L4', 'B3', 'B4']

    for mod in mod_labs:
        runs_dir = str(scen_dir + mod + period + '/wepp/runs/')
        restrictive_layer(runs_dir)