#%%

from operator import index
import pandas as pd
import os
import numpy as np
import matplotlib as plt

def analyze_soil_loss(wshed_lst,scen_lst,mod_lst,mod_names):
    '''
    Analyze soil loss outputs for all watersheds, management scenarios, and climate 
    models. Data is loaded and prepped in with prep_soil_loss_data function. The
    prepped data is then visualized with the graph_soil_losses function.

    wshed_lst = list of watershed names 
    scen_lst = list of future management scenario IDs
    mod_lst = list of future climate model IDs
    '''


    def prep_soil_loss_data(wepp_out_dir,years,season_start,season_end):
        '''
        Loads in wepp output data from .ebe and .loss files. Extracts Sediment
        delivery values from .ebe, averages them by hillslope over entire period,
        and then converts the average to a mass/area soil loss value using
        profile width and area values extracted from the .loss files.

        wepp_out_dir = WEPP watershed/scenario/clim model output directory 

        years = total number of years in climate period

        season_lst = output list that will hold average seasonal soil loss value for each hillslope
        '''


        ##### Load in .ebe and .loss files ######

        #get ebe files from output directory
        hillslopes = [x for x in os.listdir(wepp_out_dir) if x.endswith('.ebe.dat')]

        #define column names for ebe file load in
        ebe_col_list = ['Day', 'Month', 'Year', 'Precip', 'RO', 'IR-det',\
                        'Av-det', 'Mx-det', 'Point', 'Av-dep', 'Mx-dep',\
                        'Point_2', 'Sed-Del', 'ER']



        #get loss files from output directory
        loss_files = [x for x in os.listdir(wepp_out_dir) if x.endswith('.loss.dat')]


        #output list that will hold average seasonal soil loss value for each hillslope
        season_lst = []


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

            #get average seasonal loss for entire period
            #divide sum by total number of years,
            #multiple by sed delivery value (in kg/m) by profile width to get kg,
            #convert from kg to tons,
            #divide by area to get avg soil loss in tons/ha

            if area > 0:
                avg_loss = (((season_df['Sed-Del'].sum() / years) * width) * 0.00110231) / area
                #append to hillslope
                season_lst.append(avg_loss)

            if area == 0:
                pass


        #Get average seasonal soil loss values for entire watershed
        seasonal_loss = sum(season_lst) / len(hillslopes)

        return seasonal_loss



    ### Run prep_soil_loss_data function for all wshes, scenarios, and clim models ###

    #use to loop through months used for selecting the months corresponding to each season
    season_start_months = [3]
    season_end_months = [6]
    season_names = ['Spring']

    for wshed in wshed_lst:

        for season_start,season_end,season_name in zip(season_start_months,season_end_months,season_names):

            #Only one baseline period, which does not have any scenarios or climate models. Only need to perform
            #function once per watershed
            wepp_out_dir = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/Base/Obs/wepp/output/'.format(wshed))
            #num years in period = 55
            obs_loss = prep_soil_loss_data(wepp_out_dir, 55,season_start,season_end)

            #set up output lists for each climate model
            B3_59 = []
            B3_99 = []
            B4_59 = []
            B4_99 = []
            L3_59 = []
            L3_99 = []
            L4_59 = []
            L4_99 = []

            mod_out_lsts = [B3_59, B3_99, B4_59, B4_99,\
                            L3_59, L3_99, L4_59, L4_99]

            #Run function for all climate models and scenarios
            for mod, mod_out_lst in zip(mod_lst, mod_out_lsts):

                for scen in scen_lst:

                    wepp_out_dir = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/{}/{}/wepp/output/'.format(wshed,scen, mod))
                    season_loss = prep_soil_loss_data(wepp_out_dir, 40,season_start,season_end)
                    mod_out_lst.append(season_loss)

            output_df = pd.DataFrame({'gfdl 4.5 2020-59':B3_59,\
                                      'gfdl 4.5 2060-99':B3_99,\
                                      'gfdl 6.0 2020-59':B4_59,\
                                      'gfdl 6.0 2060-99':B4_99,\
                                      'hadgem2 4.5 2020-59':L3_59,\
                                      'hadgem2 4.5 2060-99':L3_99,\
                                      'hadgem2 8.5 2020-59':L4_59,\
                                      'hadgem2 8.5 2060-99':L4_99},\
                                      index = scen_names)    

            print(season_name, output_df)

            axes = output_df.plot.bar(width = 0.7, rot = 45,\
                                      title = 'Spring',\
                                      color = {'gfdl 4.5 2020-59':'Plum',\
                                                'gfdl 4.5 2060-99':'DarkSlateBlue',\
                                                'gfdl 6.0 2020-59':'SkyBlue',\
                                                'gfdl 6.0 2060-99':'MediumBlue',\
                                                'hadgem2 4.5 2020-59':'PaleGreen',\
                                                'hadgem2 4.5 2060-99':'DarkGreen',\
                                                'hadgem2 8.5 2020-59':'BurlyWood',\
                                                'hadgem2 8.5 2060-99':'DarkGoldenrod'})

            axes.legend(bbox_to_anchor=(1.0, 1.0))

            axes.set_ylabel('Average Hillslope Soil Loss (tons/ha)')


wshed_lst = ['BE1']
scen_lst = ['NC', 'Comb', 'CT', 'CC', 'Per']

mod_lst = ['B3_59', 'B3_99', 'B4_59', 'B4_99',\
           'L3_59', 'L3_99','L4_59', 'L4_99']


scen_names = ['No Change', 'Combined\nManagement', 'Conservation\nTillage',\
              'Cover\nCrop', 'Perennial']

analyze_soil_loss(wshed_lst,scen_lst,mod_lst,scen_names)

#%%
