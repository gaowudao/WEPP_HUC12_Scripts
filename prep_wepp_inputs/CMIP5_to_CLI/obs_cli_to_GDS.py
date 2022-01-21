from matplotlib.pyplot import fill
import pandas as pd
import numpy as np
import os
import statistics

#load in daily precipitation data
daily_inputs = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/ST1/obs_data/ST1_obs_19.xlsx'
daily_data = pd.read_excel(daily_inputs)

#Create path to monthly data
monthly_data = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/ST1/obs_data/ST1_MnDNR_Obs.xlsx'

def read_excel_sheets(output_dic, monthly_data):
    """
    Read all sheets of observed precip excel file and return as dataframes
    in a dictionary

    Observed monthly pr averages should be in one sheet labeled "Monthly_pr"

    Observed monthly number of pr events should be in a separate sheet labeled
    "Monthly_pr_e"  ... _e stands for events

    Observed temperature data should be in daily format and have a separate column for 
    the month ID number (i.e. 1, 2, 3, 4...)
    """
    #Read in excel file
    xl = pd.ExcelFile(monthly_data)
    columns = None
    #loop through sheets
    for idx, name in enumerate(xl.sheet_names):

        #define excel sheet
        sheet = xl.parse(name)

        # Assume index of existing data frame when appended
        df = pd.DataFrame(sheet)

        #select sheets with monthly data
        if 'Monthly' in name:
            #set year as index
            df.set_index('Year', inplace = True)
            output_dic[name] = df

obs_monthly_data = {}
read_excel_sheets(obs_monthly_data, monthly_data)

#Fill in missing monthly data with monthly average across all years
#loop through dataframes in dictionary
for df in obs_monthly_data:
    #loop through month columns
    for month in obs_monthly_data[df]:

        #replace 'M' with monthly average across all years
        obs_monthly_data[df][month].replace('M', pd.to_numeric(obs_monthly_data[df][month], errors='coerce').mean(), inplace = True)


def fill_precip_values(var,monthly_data,monthly_var):
    '''
    fills in missing daily values with monthly averages from the entire
    time period 

    var = variable (pr, Tmax, Tmin)
    monthly_data = observed monthly averages for each var
    monthly_var = key of df in monthly dictionary that corresponds to var
    '''
    #loop through all values in daily dataframe
    for n, val in enumerate(daily_data[var]):

        #if daily value is missing...
        if val in ['M', 'T', 'S']:
            
            year = daily_data['Year'].iloc[n]
            month = daily_data['Month'].iloc[n]
            
            #replace with monthly value
            daily_data[var].iloc[n] =  monthly_data[monthly_var].loc[year, month]


fill_precip_values('Pr', obs_monthly_data, 'Monthly_pr')
fill_precip_values('Tmax', obs_monthly_data, 'Monthly_Tmax')
fill_precip_values('Tmin', obs_monthly_data, 'Monthly_Tmin')

months = [3,4,5,6,7,8,9,10,11]
monthly_stdvs = []


for month in months:
    month_df = daily_data[daily_data['Month'] == month]

    monthly_stdvs.append(statistics.pstdev(month_df['Pr']))

monthly_stdvs_df = pd.DataFrame({'Month':months, 'StDev_Pr':monthly_stdvs})

print(monthly_stdvs_df)


daily_data['Pr'] = daily_data['Pr'] * 25.4
daily_data['Tmax'] = (daily_data['Tmax'] - 32) * 5.0/9.0
daily_data['Tmin'] = (daily_data['Tmin'] - 32) * 5.0/9.0


gds_year = daily_data['Year'].astype(str).str[2::]
gds_month = daily_data['Month'].astype(str).str.zfill(2)
gds_day = daily_data['Day'].astype(str).str.zfill(2)

daily_data['date_gds'] = ['{}{}{}'.format(year, month, day) \
                                        for year, month, day in \
                                        zip(gds_year, gds_month, gds_day)]

df = daily_data

new_lines = ['{}{}  {}  {}'.format(date, str(tmax)[0:5], str(tmin)[0:5], str(pr)[0:5]) \
                                    for date, tmax, tmin, pr in \
                                    zip(df['date_gds'], df['Tmax'], df['Tmin'], df['Pr'])]





