def get_hill_info(runs_dir, wshed):
    '''
    Gets crop rotations, average slopes, and soil types for each hillslope

    runs_dir = HUC12_path/Runs/{man scenario}/{cli scenario}/wepp/runs directory

    wshed = Name of HUC12 watershed from DEP project
    '''
    
    import os
    import pandas as pd
    import re
    from statistics import mean

    def find_rotations():
        '''
        Finds all crops in each hillslope .man file. The crops are appended to a separate list
        for each hillslope which is can be interpreted as a crop rotation. Specific years are 
        not known but also not necessary to know for downstream analysis
        
        Returns dataframe with two columns for IDs and rotations in string format
        '''
        
        # Create lists for appending rotations and IDs from all hillslopes
        rot_lst = []
        ID_lst = []
        
        # Loop through all management files in runs_dir
        for file in os.listdir(runs_dir):
            if file.endswith('.man'):
                
                #Create temporary list for appending all crops present in 
                #a management file (resets each iteration)
                temp_lst = []

                #open file for reading
                with open(str(runs_dir + file)) as f:

                    #read lines 
                    lines = f.readlines()

                    #loop through lines
                    for line in lines:
                        #append crops to temp_lst by name

                        if line.startswith('Corn'):
                            temp_lst.append('Corn')

                        if line.startswith('Cor_0967'):
                            temp_lst.append('Corn_2')

                        if line.startswith('ALFALFA'):
                            temp_lst.append('Alf')

                        if line.startswith('Soy_2194'):
                            temp_lst.append('Soy')

                        if line.startswith('`Bromegrass-High'):
                            temp_lst.append('Pasture')

                        if line.startswith('Wheat'):
                            temp_lst.append('Wheat')

                #append temp_lst to rot_lst...each file has separate rotation
                rot_lst.append(temp_lst)
                
                #Append IDs to a list 
                ID_lst.append(file[:-4])

        #remove corn duplicates, two different types of corn in .man files, but 
        #only one is necessary for downstream analysis
        for lst in rot_lst:
            if 'Corn' in lst and 'Corn_2' in lst:
                lst.remove('Corn_2')

        #create new list that combines all crops in a list to a single string
        #separated by a '_'
        new_rot_lst = []
        for rot in rot_lst:
            comb_rot = '_'.join(rot)
            new_rot_lst.append(comb_rot)
            

        #create dataframe of hillslope IDs and the respective rotations
        rotations = pd.DataFrame({'ID':ID_lst, 'Rotation':new_rot_lst})
        
        return rotations
    
    print('Finding crop rotations...')
    
    # Create dataframe for hillslope information
    hillslope_info = find_rotations()
    
    
    def find_slopes():
        '''
        Calculates average slope values for each hillslopes and returns a list
        of the calculated values
        '''
        
        avg_slopes = []

        for file in os.listdir(runs_dir):
            #loop through slope/topography files in runs_dir
            if file.endswith('.slp'):  
                #join path and file
                current_path = ''.join((runs_dir, "/", file))
                
                # read in file
                reading_file = open(current_path, "r")

                lines = reading_file.readlines() 

                #skip first 8 lines - they do not include any relevant data
                core_slope_lines = lines[8::]
                
                #get lines with slope data
                slope_lines = core_slope_lines[0::2]
                
                #get individual data line with slope points
                slope_line = str(''.join(slope_lines))

                #Split line with slope points into individual list items
                split_vals = re.split('\s|[,]', slope_line)

                #Remove blank list items from .split()
                slope_points = [x for x in split_vals if x.strip()]

                #Select the slope values from each point
                slope_vals = slope_points[1::2]

                #change to float values
                slope_vals = [float(i) for i in slope_vals] 

                #get average slope values of hillslope and append to list
                avg_slope = round(mean(slope_vals), 4)
                avg_slopes.append(avg_slope)

        return avg_slopes
    
    print('Finding average slope values...')
    
    avg_slopes = find_slopes()
    
    #Assign avg_slopes to hillslope_info df
    hillslope_info['avg_slopes'] = avg_slopes
    
    
    
    def find_soil_types():
        '''
        Calculates average %sand and %clay content for each hillslope and 
        appends them to separate lists which are returned 
        '''
        sand_vals = []
        clay_vals = []

        for file in os.listdir(runs_dir):
            if file.endswith('.sol'):  # search for file in directory
                current_path = ''.join((runs_dir, "/", file)) # if found, add file name to end of path
                reading_file = open(current_path, "r") # read in file

                lines = reading_file.readlines()  #read lines to a list

                core_soil_lines = lines[4::]  #skip first 4 lines

                data_lines = []

                for line in core_soil_lines:
                    sub_line_1 = '0 0.000000 0\n'
                    sub_line_2 = '0.750000'
                    if sub_line_1 in line:
                        pass
                    elif sub_line_2 in line:
                        pass
                    else:
                        data_lines.append(str(line))

                soil_vals = []

                for line in data_lines:
                    soil_vals.append(line.strip())

                soil_df = pd.DataFrame({'line': soil_vals})

                soil_df[['Depth', '%sand', '%clay', '%OM', 'CEC', '%rock']] = soil_df['line'].str.split(" ", expand=True)

                soil_df.drop(columns = 'line', inplace = True)

                soil_df

                sand = soil_df['%sand'].astype(float).mean()
                clay = soil_df['%clay'].astype(float).mean()

                sand_vals.append(sand)
                clay_vals.append(clay)
                
        return sand_vals, clay_vals
    
    print('Finding soil types...')
    sand_vals, clay_vals = find_soil_types()
    
    hillslope_info['sand%'] = sand_vals
    hillslope_info['clay%'] = clay_vals
    
    print(hillslope_info)

    #Send hillslope_info to excel spreadsheet
    hillslope_info.to_excel('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/{}_info.xlsx'.format(wshed, wshed))

wshed_lst = ['BE1', 'DO1', 'GO1', 'RO1', 'ST1']

for wshed in wshed_lst:
    runs_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/wepp/runs/'.format(wshed)
    get_hill_info(runs_dir, wshed)