#%%

import pandas as pd

#Read cligen file data into dataframe and remove row with units
cli_data = pd.read_csv(str('E:/Soil_Erosion_Project/WEPP_PRWs/BE1/Runs/CC/L1_99/wepp/runs/p1.cli'), skiprows = 13, sep = '\s+| ', engine = 'python')
cli_data.drop([0,], axis = 0, inplace = True)
cli_data[['prcp', 'dur', 'tp', 'ip']] = cli_data[['prcp', 'dur', 'tp', 'ip']].where(cli_data['prcp'].astype(float)>0.3, other=0)
print(cli_data['prcp'][100:200])

cli_data['tmax'] = cli_data['tmax'].astype(float)
cli_data['tmin'] = cli_data['tmin'].astype(float)
cli_data['prcp'] = cli_data['prcp'].astype(float)
cli_data['dur'] = cli_data['dur'].astype(float)
cli_data['year'] = cli_data['year'].astype(int)
cli_data['Month'] = cli_data['mo'].astype(int)

cli_data['pr_I'] = cli_data['prcp'].div(cli_data['dur']) #precip intensity