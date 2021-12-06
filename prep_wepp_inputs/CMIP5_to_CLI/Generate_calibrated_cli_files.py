#!/usr/bin/env python
# coding: utf-8

# In[1]:


def gen_cli_file(top_path, site_name, uncal_path, obs_path, base_id, fut_id, par_path):
    '''
    Runs a GDS file through GenStPar to create an uncalibrated .TOP file which
    is then calibrated using observed data from the MnDNR. A .PAR file is created
    from the calibrated .TOP file which is sent to the cligen application to create
    a fully calibrated .CLI file. The new .CLI file is ready for input to WEPP.
    
    Calibrated and uncalibrated files should be kept in separate directories 
    so that the uncal files can be used when scaling the calibrations to the 
    future .top files. 
    
    top_path = directory path for calibrated .top files and GDS files, they must
    be in the same directory with the GenStPar.app and WEPP_CountryCodes.txt files
    
    site_name = ID of climate area/site/watershed
    
    uncal_path = path to uncalibrated .TOP files
    
    obs_path = path to observed MnDNR data (precip in monthly averages: total inches
    and number of events, and temperatures in daily format. Should be in three separate
    sheets with the month numbers as column IDs in the precip sheets)
    
    top_path = directory path for calibrated .top files
    
    base_id = Id for baseline time period. Generally set as '19' to indicate the 1965-2019 
    time period
    '''
    
    import shutil, os
    import pandas as pd
    import numpy as np
    
    # Prep functions that are used twice in gen_cli_file function, to be used later in function
    def create_out_string(df, var_name):
        '''
        creates string of calibrated data in .top file format
        '''
        var = list(df)

        if var_name == 'MEAN P  ' or var_name == 'P(W|W)  ':
            new_line = str('{}{:.2f}  {:.2f}  {:.2f}  {:.2f}  {:.2f}  {:.2f}  {:.2f}  {:.2f}  {:.2f}  {:.2f}  {:.2f}  {:.2f}'                           .format(var_name, var[0], var[1], var[2], var[3], var[4], var[5],                                   var[6], var[7], var[8], var[9], var[10], var[11])) 

        else:
            new_line = str('{}{:5.2f} {:5.2f} {:5.2f} {:5.2f} {:5.2f} {:5.2f} {:5.2f} {:5.2f} {:5.2f} {:5.2f} {:5.2f} {:5.2f}'                           .format(var_name, var[0], var[1], var[2], var[3], var[4], var[5],                                   var[6], var[7], var[8], var[9], var[10], var[11]))




        return new_line
    
    ####### Create uncalibrated .top files from exisiting GDS files ########

    def gds_to_top():
        '''
         Sends GDS files to the GenStPar program through os.system

         GenStPar generates the top 12 lines of a .PAR file and saves it as a .TOP
         file
        '''
        ### Load GDS filenames into list
        os.chdir(top_path)
        gds_files = [x for x in os.listdir('.') if x.startswith((site_name))]


        for file in gds_files:
            os.system("ECHO {} |GenStPar.exe".format(file))


    gds_to_top()
    
    
    #Copy uncalibrated .TOP files to uncal_path 
    
    for file in os.listdir(top_path):
        if file.startswith(site_name) and file.endswith('.top'):
            uncal_file = str(uncal_path + file)
            shutil.copy(file, uncal_file)


    ####### Calibrate baseline .top files after moving uncalibrated to seperate folder #######
    def create_cal_top():
        '''
        Combines functions below to generate a calibrated baseline .top file using the
        uncalibrated files generated in the previous function
        '''
        def read_excel_sheets(output_dic):
            """
            Read all sheets of observed precip excel file and return as dataframes
            in a dictionary

            Observed monthly pr averages should be in one sheet labeled "Monthly_pr"

            Observed monthly number of pr events should be in a separate sheet labeled
            "Monthly_pr_e"  ... _e stands for events

            Observed temperature data should be in daily format and have a separate column for 
            the month ID number (i.e. 1, 2, 3, 4...)
            """
            xl = pd.ExcelFile(obs_path)
            columns = None
            for idx, name in enumerate(xl.sheet_names):
                sheet = xl.parse(name)
                # Assume index of existing data frame when appended
                df = pd.DataFrame(sheet)

                if 'pr' in name:
                    df.set_index('Year', inplace = True)
                    output_dic[name] = df

                if 'Temp' in name:
                    output_dic[name] = df

        obs_monthly_data = {}
        read_excel_sheets(obs_monthly_data)

        # Get pr/temp averages and temp stdevs from observed datasets
        Monthly_pr = obs_monthly_data['Monthly_pr'].mean()
        Monthly_pr_e = obs_monthly_data['Monthly_pr_e'].mean()
        Monthly_tmax = obs_monthly_data['Daily_Temp'].groupby('Month')['Tmax'].mean()
        Monthly_tmin = obs_monthly_data['Daily_Temp'].groupby('Month')['Tmin'].mean()
        Monthly_tmax_std = obs_monthly_data['Daily_Temp'].groupby('Month')['Tmax'].std()
        Monthly_tmin_std = obs_monthly_data['Daily_Temp'].groupby('Month')['Tmin'].std()


        # Calculate the mean monthly precip per event for obs_data into a new dataframe 
        mean_pr_e = Monthly_pr / Monthly_pr_e

        #Create df with # of days per month
        Months = [1,2,3,4,5,6,7,8,9,10,11,12]
        days = [31,28,31,30,31,30,31,31,30,31,30,31]
        n_days = pd.DataFrame(data = days, index = Months)

        # Calculate the daily probability of precip for each month in the obs_data
        PW = Monthly_pr / (n_days[0] * mean_pr_e)


        #Read in uncalibrated .top file
        top_files = [x for x in os.listdir(top_path) if x.endswith('{}.top'.format(base_id))]

        def top_to_dic(output_dic):
            '''
            Loops through set of .top files and puts data into a dictionary
            of dataframes
            '''
            for top_file in top_files:
                # Read in .top file
                top_data = pd.read_csv(str(top_path + top_file), skiprows = 3, sep = '\s+', header=None, engine = 'python')
                Months = [1,2,3,4,5,6,7,8,9,10,11,12]
                #Create temporary dataframe that drops NaN columns for the P(W|D) row
                Pw_d_i = top_data.drop([12,13], axis=1)
                #Create dataframe of P(W|D) values by month
                Pw_d = pd.DataFrame(data = {'P(W|D)' : Pw_d_i.loc['P(W|D)'], 'Months':Months})
                Pw_d.set_index('Months', inplace =True)

                output_dic[top_file[:-4]] = Pw_d

        monthly_PWDs = {}   

        top_to_dic(monthly_PWDs)

        
        # Overwrite observed parameters to uncalibrated .TOP files
        for df,top_file in zip(monthly_PWDs, top_files):

            # calculate monthly average probablity of wet days (wet day = precip)
            neg_PWD = monthly_PWDs[df].astype(float).multiply(-1)
            PWD_plus1 = monthly_PWDs[df].astype(float) + 1
            monthly_PWW = abs((neg_PWD.div(PW, axis = 0)) + PWD_plus1)

            #open uncalibrated .top file for reading/writing
            with open(str(top_path + top_file), 'r+') as file:
                #read lines of file
                lines = file.readlines()

                #Turn dataframe back to string and then rewrite to file
                #Create new lines for writing using create_out_string
                new_meanP = create_out_string(mean_pr_e, ' MEAN P  ')
                new_PWW = create_out_string(monthly_PWW['P(W|D)'], ' P(W|W)  ')
                new_tmax = create_out_string(Monthly_tmax, ' TMAX AV ')
                new_tmin = create_out_string(Monthly_tmin, ' TMIN AV ')
                new_sdmax = create_out_string(Monthly_tmax_std, ' SD TMAX ')
                new_sdmin = create_out_string(Monthly_tmin_std, ' SD TMIN ')


                # move file pointer to the beginning of a file
                file.seek(0)
                # truncate the file
                file.truncate()

                #write lines to truncated file
                file.writelines(lines[0:3])
                file.writelines(new_meanP + '\n')
                file.writelines(lines[4:6])
                file.writelines(new_PWW + '\n')
                file.writelines(lines[7])
                file.writelines(new_tmax + '\n')
                file.writelines(new_tmin + '\n')
                file.writelines(new_sdmax + '\n')
                file.writelines(new_sdmax + '\n')
                file.writelines('\n')

                file.close()

        file.close()
        
    #run create_cal_top     
    create_cal_top()
    
    
    
    ########  Calibrate future .top files  #########

    def load_base_top(output_dic, cal_uncal):
        '''
        Loops through set of baseline .top files and puts them into a dictionary
        of dataframes so that the variables are accessible for adjustments/calculations

        cal_uncal = string to guide the process of loading in files (see if
        statements)
        '''

        if cal_uncal == 'cal':
            # Load in calibrated basline files
            top_files = [x for x in os.listdir(top_path) if x.endswith('19.top')]

        if cal_uncal == 'uncal':
            # Load in all uncalibrated files
            top_files = [x for x in os.listdir(uncal_path) if x.endswith('.top')]

        for top_file in top_files:
            Months = [1,2,3,4,5,6,7,8,9,10,11,12]
            # Read in .top file
            if cal_uncal == 'cal':
                top_data = pd.read_csv(str(top_path + top_file), skiprows = 3, sep = '\s+', header=None, engine = 'python')
            if cal_uncal == 'uncal':
                top_data = pd.read_csv(str(uncal_path + top_file), skiprows = 3, sep = '\s+', header=None, engine = 'python')

            #Create temporary dataframes that drop necessary NaN columns for the respective variables
            Pwd_i = top_data.drop([12,13], axis=1)
            Pwd_i.columns = [Months]
            Pww_i = top_data.drop([12,13], axis=1)
            Pww_i.columns = [Months]
            meanP_i = top_data.drop([0,13], axis=1)
            meanP_i.columns = [Months]

            #Create dataframe of variables by month
            df = pd.DataFrame(data = {'P(W|D)':Pwd_i.loc['P(W|D)'], 'P(W|W)':Pww_i.loc['P(W|W)'], 
                                      'Mean_P':meanP_i.loc['MEAN'], 'TMAX':meanP_i.loc['TMAX'],\
                                      'TMIN':meanP_i.loc['TMIN'], 'SD TMAX':meanP_i.iloc[7],\
                                      'SD TMIN':meanP_i.iloc[8], 'Months':Months})
            df.set_index('Months', inplace =True)

            #Calculate P(w)
            one_min_pww = 1 - df['P(W|W)'].astype(float)
            df['P(W)'] = df['P(W|D)'].astype(float) / (one_min_pww + df['P(W|D)'].astype(float))

            #Assign to dictionary with model/location name
            output_dic[top_file[:-4]] = df

    # Set up directories and dictionaries for running top_to_dic function
    uncal_monthly_vars = {}  
    cal_monthly_vars = {}

    #Run top_to_dic for uncalibrated and calibrated .top files
    load_base_top(cal_monthly_vars, 'cal')
    load_base_top(uncal_monthly_vars, 'uncal')

    
    def calibrate_fut_top(mod, base, uncal_base_dic, cal_base_dic, fut_top_path):
        '''
        Calibrate future .top files using uncalibrated and calibrated baseline .top files
        '''

        fut_lab_lst = [str(mod + '59'), str(mod + '99')]

        #Define baseline uncalibrated and calibrated df's
        uncal_base_df = uncal_base_dic[base].astype(float)
        cal_base_df = cal_base_dic[base].astype(float)
        
        for fut_lab in fut_lab_lst:
            #Define uncalibrated future df
            uncal_fut_df = uncal_base_dic[fut_lab].astype(float)

            #Perform calibration calculations

            ##Monthly mean precip per event
            cal_mean_P = abs(uncal_fut_df['Mean_P'] - uncal_base_df['Mean_P']) + cal_base_df['Mean_P']

            ##Monthly mean P(W|W)
            cal_PWW = abs(uncal_fut_df['P(W|W)'] - uncal_base_df['P(W|W)']) + cal_base_df['P(W|W)']

            cal_tmax = abs(uncal_fut_df['TMAX'] - uncal_base_df['TMAX']) + cal_base_df['TMAX']

            cal_tmin = abs(uncal_fut_df['TMIN'] - uncal_base_df['TMIN']) + cal_base_df['TMIN']

            cal_sdmax = abs(uncal_fut_df['SD TMAX'] - uncal_base_df['SD TMAX']) + cal_base_df['SD TMAX']

            cal_sdmin = abs(uncal_fut_df['SD TMIN'] - uncal_base_df['SD TMIN']) + cal_base_df['SD TMIN']


            #Substitute calibrated values into uncalibrated future .top files
            with open(str(fut_top_path+fut_lab+'.top'), 'r+') as file:
                lines = file.readlines()

                #Turn dataframe back to string and then rewrite to file 
                #Using create_out_string function from before
                new_meanP = create_out_string(cal_mean_P, ' MEAN P  ')
                new_PWW = create_out_string(cal_PWW, ' P(W|W)  ')
                new_tmax = create_out_string(cal_tmax, ' TMAX AV ')
                new_tmin = create_out_string(cal_tmin, ' TMIN AV ')
                new_sdmax = create_out_string(cal_sdmax, ' SD TMAX ')
                new_sdmin = create_out_string(cal_sdmin, ' SD TMIN ')
                
                # move file pointer to the beginning of a file
                file.seek(0)
                # truncate the file
                file.truncate()

                file.writelines(lines[0:3])
                file.writelines(new_meanP + '\n')
                file.writelines(lines[4:6])
                file.writelines(new_PWW + '\n')
                file.writelines(lines[7])
                file.writelines(new_tmax + '\n')
                file.writelines(new_tmin + '\n')
                file.writelines(new_sdmax + '\n')
                file.writelines(new_sdmin + '\n')
                file.close()


    # Get list of name/method/location/model label combinations without time period label
    mod_tempor_lst = [x for x in uncal_monthly_vars if x.startswith(site_name) and x.endswith((str(fut_id)))]
    mod_lst = []
    for tempor_mod in mod_tempor_lst:
        mod_lst.append(tempor_mod.replace(fut_id, ''))
        
    # Run calibrate_fut_top for each method/location/model combo
    for mod in mod_lst:  
        calibrate_fut_top(mod, str(mod+'19'), uncal_monthly_vars, cal_monthly_vars, top_path)
        
        
        
    ###### Create .CLI files ########

    ### Load TOP file names to list
    os.chdir(top_path)
    top_files = [x for x in os.listdir('.') if x.endswith('.top')]

    ### Read in TOP files as lines in a list
    top_lines = {}
    for file_name in top_files:
        temp_lst = []
        with open (file_name, 'rt') as file:
            for line in file:
                temp_lst.append(line)
        top_lines[file_name] = temp_lst


    ### Load in Minnesota Climate Station Data as dataframe
    stations = 'E://Soil_Erosion_Project//Discovery_Farms//MN_stations.txt'
    stations = pd.read_csv(stations, sep = ('\t'))

    ### Set up path to station files, station_path contains individual pre-exisiting
    ### .PAR files with climate information for each station.
    station_path = 'E://Soil_Erosion_Project//Discovery_Farms//MN_stations//'

    par_files = {}

    def top_to_par(top_dic, par_dic):
        '''
        Uses .TOP files to locate exisiting climate station files that have similar
        GPS coordinates and climate regimes. Once an existing station is selected,
        the first 12 lines of that file are overwritten by the .TOP file to create
        a new .PAR file.
        '''
        for key in top_dic:
            # Assign lat/lon values from each file
            lat = float(top_dic[key][1][8:13])
            lon = float(top_dic[key][1][21:26])

            # Find index number of the row in each stations dataframe where the
            # latitude and longitude are closest to the TOP input file
            index = stations[['Lat', 'Lon']].sub([lat, lon]).abs().idxmin()

            # Find station file name from stations df using index
            station_name = str(stations.loc[index].File)[6:14]

            #Change dir to station_path
            os.chdir(station_path)

            with open(station_name + '.par', 'r') as station_file:
                # read a station_file lines to a list
                station_lines = station_file.readlines()

                # replace top lines in station file with top lines
                # from .TOP file
                station_lines[0:12] = top_dic[key][0:12]

            # Assign to new_df
            par_dic[key] = station_lines

    top_to_par(top_lines, par_files)

    def write_par(par_dic):
        '''
        Writes .PAR files (in list format) to new file
        '''
        os.chdir(par_path)

        for key in par_dic:
            out_file = open(str(key)[:-4] + '.par', 'w+')
            for line in par_dic[key]:
                out_file.write('%s' % line)

    write_par(par_files)


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

    par_to_cli(par_path,par_files)

    
### Define function inputs
top_path = 'C:\\Users\\Garner\\Soil_Erosion_Project\\WEPP_PRWs\\GO1_DEP\\GDS\\Test_Runs\\'
uncal_path = 'C:\\Users\\Garner\\Soil_Erosion_Project\\WEPP_PRWs\\GO1_DEP\\Uncalibrated\\Test_Runs\\'
obs_path = 'C:\\Users\\Garner\\Soil_Erosion_Project\\WEPP_PRWs\\GO1_DEP\\obs_data\\GO1_MnDNR_Obs.xlsx'
par_path = 'C://Users//Garner//Soil_Erosion_Project//WEPP_PRWs//GO1_DEP//PAR//Test_Runs//'


gen_cli_file(top_path, 'GO1', uncal_path, obs_path, '19', '59', par_path)

