from dataclasses import replace


def scan_folder_replace_txt(parent, file_type):
    '''
    Function that scans a directory to find a specific file type
    if the file type is not in that directory, it will go into any
    sub-directories and try to find the file type (.man in this case). 
    
    Once the .man file is located, a specific string item (old_string) is searched for
    and replaced by a different string item (new_string)
    
    
    '''

    import os
    import pandas as pd

    for file_name in os.listdir(parent):

        # search for file in directory
        if file_name.endswith(file_type):

            # if found, add file name to end of path
            current_path = ''.join((parent, file_name))
            # read in file
            reading_file = open(current_path, "r")

            def replace_string(old_string, new_string):
                '''
                Replace old_string with new_string
                ''' 

                with open(current_path, "r") as file:

                    # assign blank new file content
                    new_file_content = ""

                    # iterate through all lines in file
                    for line in file:
                        #strip line for editing
                        stripped_line = line.strip() 
                        #replace old string with new string
                        new_line = stripped_line.replace(old_string, new_string) 
                        # add new line to new_file_content
                        new_file_content += new_line +"\n"

                    #close reading file
                    file.close()
                    # open file for writing
                    writing_file = open(current_path, "w")
                    # write new content to file
                    writing_file.write(new_file_content)
                    #close file
                    writing_file.close()

            #set up strings for tandem disk
            norm_tan_1 = '0.5000 0.5000 0'
            norm_tan_2 = '0.0500 0.2300 0.5000 0.5000 0.0260 1.0000 0.1000'

            new_tan_1 = '0.0000 0.0000 0'
            new_tan_2 = '0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000'

            #set up strings for field cultivator
            norm_fc_1 = '0.6000 0.3500 0'
            norm_fc_2 = '0.0250 0.3000 0.6000 0.3500 0.0150 1.0000 0.0500'

            new_fc_1 = '0.5000 0.3500 0'
            new_fc_2 = '0.0250 0.3000 0.5000 0.3500 0.0150 1.0000 0.0500'

            kernza_fc_1 = '0.5000 0.0000 0'
            kernza_fc_2 = '0.0250 0.3000 0.5000 0.0000 0.0150 1.0000 0.0500'


            #set up strings for mid-summer cultivator
            norm_cu_1 = '0.4000 0.2000 0'
            norm_cu_2 = '0.0750 0.7500 0.4000 0.2000 0.0150 0.8500 0.0500'

            new_cu_1 = '0.0000 0.0000 0'
            new_cu_2 = '0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000'


            #set up strings for Chisel plow 

            norm_chis_1 = '0.5000 0.3000 0'
            norm_chis_2 = '0.0500 0.3000 0.5000 0.3000 0.0230 1.0000 0.1500'

            new_chis_1 = '0.0000 0.0000 0'
            new_chis_2 = '0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000'

            kernza_chis_1 = '0.0000 0.3000 0'
            kernza_chis_2 = '0.0500 0.3000 0.0000 0.3000 0.0230 1.0000 0.1500'



            #implement future tillage values specific to hillslopes with kernza
            if 'Kernza' in reading_file.read():

                #replace tandem values with all zeros, do not want tandem in rotation
                replace_string(norm_tan_2, new_tan_2)
                replace_string(norm_tan_1, new_tan_1)

                #replace field cultivator values with future kernza tillage values 
                replace_string(norm_fc_2, kernza_fc_2)
                replace_string(norm_fc_1, kernza_fc_1)

                #replace cultivator values with future tillage values
                replace_string(norm_cu_2, new_cu_2)
                replace_string(norm_cu_1, new_cu_1)

                #replace chisel plow values with future kernza tillage values
                replace_string(norm_chis_2, kernza_chis_2)
                replace_string(norm_chis_1, kernza_chis_1)

            #implement future tillage values to all other hillslopes
            if 'Kernza' not in reading_file.read():

                #replace tandem values with all zeros, do not want tandem in rotation
                replace_string(norm_tan_2, new_tan_2)
                replace_string(norm_tan_1, new_tan_1)

                #replace field cultivator values with future kernza tillage values 
                replace_string(norm_fc_2, new_fc_2)
                replace_string(norm_fc_1, new_fc_1)

                #replace cultivator values with future tillage values
                replace_string(norm_cu_2, new_cu_2)
                replace_string(norm_cu_1, new_cu_1)

                #replace chisel plow values with future kernza tillage values
                replace_string(norm_chis_2, new_chis_2)
                replace_string(norm_chis_1, new_chis_1)

wshed_lst = ['DO1', 'GO1', 'RO1', 'ST1']
scen_lst = ['Comb', 'CT']
mod_labs = ['L3', 'L4','B3', 'B4']
period_lst = ['59','99']

for wshed in wshed_lst:
    for scen in scen_lst:
        for mod in mod_labs:
            for period in period_lst:

                parent_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/{}/{}_{}/wepp/runs/'.format(wshed, scen,mod,period)        
                scan_folder_replace_txt(parent_dir, '.man')