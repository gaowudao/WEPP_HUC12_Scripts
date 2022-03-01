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


            #implement future tillage values specific to hillslopes with kernza
            if 'Kernza' in reading_file.read():

                #replace tandem values with all zeros, do not want tandem in rotation
                replace_string(norm_tan_2, new_tan_2)
                replace_string(norm_tan_1, new_tan_1)

            #implement future tillage values to all other hillslopes
            if 'Kernza' not in reading_file.read():

                #replace tandem values with all zeros, do not want tandem in rotation
                replace_string(norm_tan_2, new_tan_2)
                replace_string(norm_tan_1, new_tan_1)


wshed_lst = ['BE1', 'DO1', 'GO1', 'RO1', 'ST1']

for wshed in wshed_lst:
    parent_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/Base/Obs/wepp/runs/'.format(wshed)        
    scan_folder_replace_txt(parent_dir, '.man')