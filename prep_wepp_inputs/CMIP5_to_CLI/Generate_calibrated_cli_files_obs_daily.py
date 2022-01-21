#!/usr/bin/env python
# coding: utf-8

# In[1]:


def gen_cli_file(top_path, site_name,par_path):
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
    
    par_path = directory where .par and .cli files will be sent to after creation
    '''
    
    import shutil, os
    import pandas as pd
    
    
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

    print('Creating initial .top files from GDS inputs...')
    gds_to_top()

 
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

    print('Creating .par files from calibrated .top files')
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

    print('Generating .cli file from .par file...')
    par_to_cli(par_path,par_files)

top_path = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/ST1/GDS/Obs/obs_sub/'
par_path = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/ST1/PAR/Obs/obs_sub/'

gen_cli_file(top_path, 'ST1', par_path)