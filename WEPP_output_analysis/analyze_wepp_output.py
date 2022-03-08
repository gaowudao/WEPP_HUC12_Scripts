#%%

from operator import index
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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
    season_start_months = [3,5,8]
    season_end_months = [6,9,12]
    season_names = ['Spring','Summer', 'Fall']

    #Define x/y axis coordinates for each watershed plot
    subx_vals = [0,1,2]
    suby_vals = [0,1,2,3,4]

    #Set up a subplot for each watershed that contains plots for each watershed
    fig, axes = plt.subplots(nrows = 3, ncols = 5, figsize = (30,22), sharex=True)

    fig.text(0.2, 0.90, 'Blue Earth', ha='center')
    fig.text(0.35, 0.90, 'Dodge', ha='center')
    fig.text(0.51, 0.90, 'Goodhue', ha='center')
    fig.text(0.67, 0.90, 'Rock', ha='center')
    fig.text(0.83, 0.90, 'Sterns', ha='center')

    fig.text(0.08, 0.77, 'Average Spring Soil Loss (tons/ha)', va='center', rotation='vertical')
    fig.text(0.08, 0.51, 'Average Summer Soil Loss (tons/ha)', va='center', rotation='vertical')
    fig.text(0.08, 0.24, 'Average Fall Soil Loss (tons/ha)', va='center', rotation='vertical')

    for wshed,suby in zip(wshed_lst,suby_vals):

        for season_start,season_end,season_name,subx in zip(season_start_months,season_end_months,season_names,subx_vals):

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

            output_df.plot.bar(ax = axes[subx,suby],\
                               width = 0.73,\
                               rot = 45,\
                               legend=False,\
                               edgecolor='white',\
                               color = {'gfdl 4.5 2020-59':'SkyBlue',\
                                        'gfdl 4.5 2060-99':'Blue',\
                                        'gfdl 6.0 2020-59':'Orange',\
                                        'gfdl 6.0 2060-99':'Yellow',\
                                        'hadgem2 4.5 2020-59':'DimGrey',\
                                        'hadgem2 4.5 2060-99':'Silver',\
                                        'hadgem2 8.5 2020-59':'Red',\
                                        'hadgem2 8.5 2060-99':'LightSalmon'})



            axes[subx, suby].axhline(y = obs_loss, color = 'Black')

            axes[subx, suby].tick_params(labelrotation=45)


        #Add title to grouping of subplots
        fig.suptitle('Average Seasonal Soil Loss for WEPP Simulated HUC12 Watersheds\nwith Future Climate and Management Scenarios'.format(season_name), fontsize = 16)

        #Set up figure legend items
        B1 = mpatches.Patch(color='SkyBlue', label='gfdl 4.5 2020-59')
        B2 = mpatches.Patch(color='Blue', label='gfdl 4.5 2060-99')
        B3 = mpatches.Patch(color='Orange', label='gfdl 6.0 2020-59')
        B4 = mpatches.Patch(color='Yellow', label='gfdl 6.0 2060-99')
        Base = mpatches.Patch(color = 'Black', label = 'Baseline Period')
        L1 = mpatches.Patch(color='DimGrey', label='hadgem2 4.5 2020-59')
        L2 = mpatches.Patch(color='Silver', label='hadgem2 4.5 2060-99')
        L3 = mpatches.Patch(color='Red', label='hadgem2 8.5 2020-59')
        L4 = mpatches.Patch(color='LightSalmon', label='hadgem2 8.5 2060-99')

        fig.legend(handles=[B1,B2,B3,B4,Base,L1,L2,L3,L4], mode = "expand", ncol= 2,prop={'size': 11}, bbox_to_anchor = [0.53,0.1])


wshed_lst = ['BE1','DO1','GO1','RO1','ST1']
scen_lst = ['NC', 'Comb', 'CT', 'CC', 'Per']

mod_lst = ['B3_59', 'B3_99', 'B4_59', 'B4_99',\
           'L3_59', 'L3_99','L4_59', 'L4_99']


scen_names = ['No Change', 'Combined\nManagement', 'Conservation\nTillage',\
              'Cover\nCrop', 'Perennial']

analyze_soil_loss(wshed_lst,scen_lst,mod_lst,scen_names)

#%%
