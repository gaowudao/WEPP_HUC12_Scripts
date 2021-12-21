#%%

import pandas as pd

#Read cligen file data into dataframe and remove row with units
cli_data = pd.read_csv(str('E:/Soil_Erosion_Project/WEPP_PRWs/BE1/Runs/CC/L3_59/wepp/runs/p1.cli'), skiprows = 13, sep = '\s+| ', engine = 'python')
cli_data.drop([0,], axis = 0, inplace = True)
cli_data[['prcp', 'dur', 'tp', 'ip']] = cli_data[['prcp', 'dur', 'tp', 'ip']].where(cli_data['prcp'].astype(float)>0.3, other=0)

cli_data['tmax'] = cli_data['tmax'].astype(float)
cli_data['tmin'] = cli_data['tmin'].astype(float)
cli_data['prcp'] = cli_data['prcp'].astype(float)
cli_data['dur'] = cli_data['dur'].astype(float)
cli_data['year'] = cli_data['year'].astype(int)
cli_data['Month'] = cli_data['mo'].astype(int)

months = 7,8,9
years = 40

#group data by month numbers corresponding to the season input and turn into new dataframe
df = pd.DataFrame(cli_data[cli_data['Month'].isin(months)])
tmax = df['tmax'].mean()
tmin = df['tmin'].mean()
precip = df['prcp'].sum() / years
df_G1 = df['prcp'][df['prcp'].astype(float) >= 1] #series where precip events > 1mm
SDII = df_G1.sum() / df_G1.count()
R10 = df_G1[df_G1.astype(float) > 10].count() / years #No. days with prcp above 10mm
R25 = df_G1[df_G1.astype(float) > 25].count() / years #No. days with prcp above 20mm
q95 = df_G1.astype(float).quantile(0.95) #95th percentile of prcp
#Avg seasonal percent of prcp above 95th percentile
R95pT = (df_G1[df_G1 > q95].astype(float).sum() / df_G1.sum())*100

print(df_G1.max())