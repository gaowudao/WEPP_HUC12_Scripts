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
            file = open(current_path, "r+")

            #read in lines
            lines = file.readlines()

            lines[9] = 'No\n'
            lines[11] = 'No\n'
            
            del lines[10]
            #delete value at index of 12, but because 10 is removed, index
            #is dropped to 11
            del lines[11]

            # move file pointer to the beginning of a file
            file.seek(0)
            # truncate the file
            file.truncate()

            #write new lines
            file.writelines(lines)



wshed_lst = ['BE1','DO1','GO1','RO1','ST1']
scen_lst = ['CC', 'Comb', 'CT', 'NC', 'Per']
mod_labs = ['B3', 'B4', 'L3', 'L4']
periods = ['59', '99']

for wshed in wshed_lst:
    for scen in scen_lst:
        for mod in mod_labs:
            for period in periods:

                parent_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/{}/{}_{}/wepp/runs/'.format(wshed, scen, mod,period)        
                scan_folder_replace_txt(parent_dir, '.run')