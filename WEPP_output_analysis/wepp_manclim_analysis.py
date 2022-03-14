#%%

from operator import index
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def analyze_soil_loss(wshed,mod_lst,ymin,ymax):
    '''
    Analyze soil loss outputs for all watersheds, management scenarios, and climate 
    models. Data is loaded and prepped in with prep_soil_loss_data function. The
    prepped data is then visualized with the graph_soil_losses function.

    wshed_lst = list of watershed names 
    scen_lst = list of future management scenario IDs
    mod_lst = list of future climate model IDs
    '''


    def prep_soil_loss_data(wepp_out_dir,years):
        '''
        Loads in wepp output data from .ebe and .loss files. Extracts Sediment
        delivery values from .ebe, averages them by hillslope over entire period,
        and then converts the average to a mass/area soil loss value using
        profile width and area values extracted from the .loss files.

        wepp_out_dir = WEPP watershed/scenario/clim model output directory 

        years = total number of years in climate period

        output_lst = output list that will hold average soil loss value for each hillslope
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


        #output list that will hold average soil loss values for each hillslope
        output_lst = []

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


            #get average loss for entire period
            #divide sum by total number of years,
            #multiple by sed delivery value (in kg/m) by profile width to get kg,
            #convert from kg to tons,
            #divide by area to get avg soil loss in tons/ha

            if area > 0:
                avg_loss = (((all_data['Sed-Del'].sum() / years) * width) * 0.00110231) / area
                #append to hillslope
                output_lst.append(avg_loss)

            if area == 0:
                pass


        #Get average soil loss values for entire watershed
        total_loss = sum(output_lst) / len(hillslopes)

        return total_loss

    #set up groups of scenarios. Each group will be plotted into an ecdf
    #for each climate model. Climate models will be combined onto each
    #management scenario plot

    scen_types = [['CC_B', 'CC_10', 'CC_20'],\
                  ['CT_B', 'CT_50', 'CT_100'],\
                  ['Per_0','Per_m20','Per_B','Per_p20']]

    # % Adoption rates for each management scenario 
    adopt_rates = [[1, 10, 20],\
                   [0, 50, 100],\
                   [0,30,50,70]]

    scen_names = ['Cover Croping',\
                  'Conservation Tillage',\
                  'Perennial Integration']


    #Set up a subplot for each watershed that contains plots for each watershed
    fig, axes = plt.subplots(nrows = 1, ncols = 3, figsize = (23,12))

    fig.text(0.08, 0.51,\
             'Average Soil Loss (tons/ha)',\
             va='center',\
             rotation='vertical',\
             fontsize = 20)

    subx_vals = [0,1,2]

    #loop through each scenario and adoption % in scenario type list
    for scen_lst, adopt_lst, subx,scen_name in zip(scen_types,adopt_rates,subx_vals,scen_names):


        #set up output lists for each climate model
        B3_59 = []
        B3_99 = []
        B4_59 = []
        B4_99 = []
        L3_59 = []
        L3_99 = []
        L4_59 = []
        L4_99 = []
        Obs = []

        #create list of lists
        mod_out_lsts = [B3_59, B3_99, B4_59, B4_99,\
                        L3_59, L3_99, L4_59, L4_99,\
                        Obs]

        #Run function for all climate models and scenarios
        for mod, mod_out_lst in zip(mod_lst, mod_out_lsts):

            for scen in scen_lst:
                
                if mod == 'Obs':
                    years = 55

                if mod != 'Obs':
                    years = 40
                
                #define wepp output directory where data is stored
                wepp_out_dir = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/New_Runs/{}/{}/wepp/output/'.format(wshed,mod,scen))

                #run prep_soil_loss_data using defined number of years and wepp output directory
                soil_loss = prep_soil_loss_data(wepp_out_dir, years)

                #append output value to list
                mod_out_lst.append(soil_loss)


        output_df = pd.DataFrame({'gfdl 4.5 2020-59':B3_59,\
                                    'gfdl 4.5 2060-99':B3_99,\
                                    'gfdl 6.0 2020-59':B4_59,\
                                    'gfdl 6.0 2060-99':B4_99,\
                                    'hadgem2 4.5 2020-59':L3_59,\
                                    'hadgem2 4.5 2060-99':L3_99,\
                                    'hadgem2 8.5 2020-59':L4_59,\
                                    'hadgem2 8.5 2060-99':L4_99,\
                                    'Baseline 1965-2019':Obs,
                                    '% Adoption':adopt_lst},\
                                    index = scen_lst)  


        print(output_df)

        mod_names = ['gfdl 4.5 2020-59','gfdl 4.5 2060-99',\
                     'gfdl 6.0 2020-59', 'gfdl 6.0 2060-99',\
                     'hadgem2 4.5 2020-59', 'hadgem2 4.5 2060-99',\
                     'hadgem2 8.5 2020-59', 'hadgem2 8.5 2060-99',\
                     'Baseline 1965-2019']

        colors = ['cornflowerblue', 'mediumblue',\
                 'Gold', 'goldenrod',\
                 'mediumseagreen', 'darkgreen',\
                 'salmon', 'Red',\
                 'black']

        def create_plot(df,mod,color):

            x = df['% Adoption']
            y = df[mod]

            #plot data
            axes[subx].plot(x,y, '-o',label = mod, color = color)

            #standardize y-axis
            axes[subx].set_ylim(bottom = ymin, top = ymax)

            #set axis labels
            axes[subx].set_xlabel('Adoption of Practice (%)', fontsize = 20)

            axes[subx].tick_params(labelsize = 17)

            #set subplot titles
            axes[subx].set_title(scen_name, fontsize = 20)


        #loop through model names and colors, then plot
        for mod_name, color in zip(mod_names,colors):
            create_plot(output_df,mod_name,color)

    #create legend
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, bbox_to_anchor = [1.05,0.92],fontsize=16)

    fig.suptitle('Average WEPP Growing Season Soil Loss for HUC12 Watershed in Stearns County, MN\nwith Varying Management Scenarios and Future Climates',\
                 fontsize = 21)



mod_lst = ['B3_59', 'B3_99', 'B4_59', 'B4_99',\
           'L3_59', 'L3_99', 'L4_59', 'L4_99',\
           'Obs']    

S_ymin = 0.25 #ST1
S_ymax = 2.5 #ST1

G_ymin = 1.5 #GO1
G_ymax = 11 #GO1

D_ymin = 1.5 #GO1
D_ymax = 8 #GO1

analyze_soil_loss('ST1', mod_lst,S_ymin,S_ymax)

#%%
