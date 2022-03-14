from operator import index
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def analyze_wepp_outputs(wshed,mod_pair):
    '''
    Analyze soil loss outputs for all watersheds, management scenarios, and climate 
    models. Data is loaded and prepped in with prep_soil_loss_data function. The
    prepped data is then visualized with the graph_soil_losses function.

    wshed_lst = list of watershed names 
    scen_lst = list of future management scenario IDs
    mod_lst = list of future climate model IDs
    '''


    def prep_data(cli_dir, wepp_out_dir, season_start, season_end):
        '''
        Loads in wepp output data from .ebe and .loss files. Extracts Sediment
        delivery and runoff values from .ebe and then converts sed-del values to 
        a mass/area soil loss value using profile width and area values extracted 
        from the .loss files.

        Also loads in precip data from a .cli cligen file. 1 cligen file per watershed

        wepp_out_dir = WEPP watershed/scenario/clim model output directory 

        cli_dir = directory with cli file (wepp input directory - only one file is loaded in)

        years = total number of years in climate period

        output_lst = output list that will hold average soil loss value for each hillslope
        '''


        ##### Load in .cli files and prep precip data ######

        #get cli files from input/cli directory
        cli_files = [x for x in os.listdir(cli_dir) if x.endswith('.cli')]
        cli_file = str(cli_dir + cli_files[1])

        #read in first cligen file. The .cli files are constant across hillslopes
        cli_df = pd.read_csv(cli_file, skiprows = 13, sep = '\s+| ', engine = 'python')
        cli_df.drop([0,], axis = 0, inplace = True)
        cli_df.reset_index(inplace = True)
        cli_df['cli_pr'] = cli_df['prcp'].astype(float)

        #select months in season
        seasonal_cli = cli_df[cli_df['mo'].astype(int) > season_start] 
        seasonal_cli = seasonal_cli[seasonal_cli['mo'].astype(int) < season_end]

        PR_lst = seasonal_cli['prcp'].to_list()


        ##### Load in .ebe and .loss files ######

        #get ebe files from output directory
        hillslopes = [x for x in os.listdir(wepp_out_dir) if x.endswith('.ebe.dat')]

        #define column names for ebe file load in
        ebe_col_list = ['Day', 'Month', 'Year', 'Precip', 'RO', 'IR-det',\
                        'Av-det', 'Mx-det', 'Point', 'Av-dep', 'Mx-dep',\
                        'Point_2', 'Sed-Del', 'ER']



        #get loss files from output directory
        loss_files = [x for x in os.listdir(wepp_out_dir) if x.endswith('.loss.dat')]


        #output list that will hold all soil loss and runoff values for each hillslope
        SL_lst = []
        RO_lst = []

        ##### Prep data for graphing ######

        #loop through all .loss and .ebe files
        for file, hill in zip(loss_files,hillslopes):

            #open .loss for reading
            with open(str(wepp_out_dir + file), 'r') as loss_data:

                #loop through lines
                for line in loss_data:

                    #select line if it contains this key phrase:
                    if 'kg (based on profile width of' in line:

                        #extract numbers from line
                        nums = []
                        for n in line.split():
                            try:
                                nums.append(float(n))
                            except ValueError:
                                pass
                        
                        #get hillslope profile width in meters
                        width = nums[1]

                    #select line if it contains this key phrase:
                    if 't/ha (assuming contributions from' in line:

                        #extract numbers from line
                        nums = []
                        for n in line.split():
                            try:
                                nums.append(float(n))
                            except ValueError:
                                pass
                        
                        #get hillslope area in hectares
                        area = nums[1]
                        
            
            #read in ebe file to dataframe
            all_data = pd.read_csv(str(wepp_out_dir+hill), skiprows = 3,\
                                    names = ebe_col_list, sep = '\s+', header=None)

            ### select data by season ###

            #select months in season
            season_df = all_data[all_data['Month'] > season_start] 
            season_df = season_df[season_df['Month'] < season_end]

            #extract individual hill loss data
            #multiple sed delivery value (in kg/m) by profile width to get kg,
            #convert from kg to tons,
            #divide by area to get avg soil loss in tons/ha

            if area > 0:
                event_losses = (((all_data['Sed-Del']) * width) * 0.00110231) / area

                #append dataframe column to SL_lst as individual values
                SL_lst.extend(event_losses.tolist())

            if area == 0:
                pass
            
            #append runoff column to RO_lst as individual events
            RO_lst.extend(all_data['RO'].to_list())



        return SL_lst, RO_lst, PR_lst

    ### Run prep_soil_loss_data function for all wshes, scenarios, and clim models ###

    #use to loop through months used for selecting the months corresponding to each season
    season_start_months = [3,5,8]
    season_end_months = [6,9,12]
    season_names = ['Spring','Summer', 'Fall']

    for season_start,season_end,season_name in zip(season_start_months, season_end_months, season_names):


        for mod in mod_pair:

            #define wepp output directory where data is stored
            wepp_out_dir = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/New_Runs/{}/CC_B/wepp/output/'.format(wshed,mod))
            wepp_cli_dir = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/New_Runs/{}/CC_B/wepp/runs/'.format(wshed,mod))

            SL_data, RO_data, PR_data = prep_data(wepp_cli_dir,wepp_out_dir,season_start,season_end)

            print(season_name)
            print(SL_data)
            print(RO_data)
            print(PR_data)


mod_pair = ['B3_59', 'B3_99','Obs']   

analyze_wepp_outputs('ST1', mod_pair)