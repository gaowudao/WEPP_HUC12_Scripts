import pandas as pd
import os
import numpy as np


def prep_soil_loss_data(wepp_out_dir,years):
    '''
    wepp_out_dir = WEPP watershed/scenario/clim model output directory 

    '''

    ##### Load in .ebe and .loss files ######


    #get ebe files from output directory
    hillslopes = [x for x in os.listdir(wepp_out_dir) if x.endswith('.ebe.dat')]

    #define column names for ebe file load in
    ebe_col_list = ['Day', 'Month', 'Year', 'Precip', 'RO', 'IR-det',\
                    'Av-det', 'Mx-det', 'Point', 'Av-dep', 'Mx-dep',\
                    'Point_2', 'Sed-Del', 'ER']

    #set up output lists for each average seasonal soil loss value
    #lists will hold values from all hillslopes in a watershed
    Spring = []
    Summer = []
    Fall = []


    #get loss files from output directory
    loss_files = [x for x in os.listdir(wepp_out_dir) if x.endswith('.loss.dat')]


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

        #use to loop through months used for selecting the months corresponding to each season
        season_start_months = [3,5,8]
        season_end_months = [6,9,12]

        #put seasonal output lists into a list for looping
        season_lsts = [Spring,Summer,Fall]

        #loop through seasons
        for season_start, season_end,season_lst in zip(season_start_months, season_end_months, season_lsts):

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
    spring_loss = sum(Spring) / len(hillslopes)
    summer_loss = sum(Summer) / len(hillslopes)
    fall_loss = sum(Fall) / len(hillslopes)

    print(spring_loss)



wshed_lst = ['BE1']
scen_lst = ['Comb']
model_labs = ['L4_99/']

for wshed in wshed_lst:
    for scen in scen_lst:
        for mod in model_labs:

            wepp_out_dir = str('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/{}/Runs/{}/{}/wepp/output/'.format(wshed,scen, mod))

            prep_soil_loss_data(wepp_out_dir, 40)
        
