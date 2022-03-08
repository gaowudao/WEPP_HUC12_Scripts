#%%

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, ax = plt.subplots(nrows=3, ncols=5, sharex=True, sharey=True, figsize=(25, 25))

fig.text(0.2, 0.90, 'common X', ha='center')
fig.text(0.35, 0.90, 'common X', ha='center')
fig.text(0.51, 0.90, 'common X', ha='center')
fig.text(0.67, 0.90, 'common X', ha='center')
fig.text(0.83, 0.90, 'common X', ha='center')

fig.text(0.08, 0.77, 'common Y', va='center', rotation='vertical')
fig.text(0.08, 0.51, 'common Y', va='center', rotation='vertical')
fig.text(0.08, 0.24, 'common Y', va='center', rotation='vertical')

#Set up figure legend items
B1 = mpatches.Patch(color='Plum', label='gfdl 4.5 2020-59')
B2 = mpatches.Patch(color='DarkSlateBlue', label='gfdl 4.5 2060-99')
B3 = mpatches.Patch(color='SkyBlue', label='gfdl 6.0 2020-59')
B4 = mpatches.Patch(color='MediumBlue', label='gfdl 6.0 2060-99')
Base = mpatches.Patch(color = 'Red', label = 'Baseline Period (1965-2019)')
L1 = mpatches.Patch(color='PaleGreen', label='hadgem2 4.5 2020-59')
L2 = mpatches.Patch(color='DarkGreen', label='hadgem2 4.5 2060-99')
L3 = mpatches.Patch(color='BurlyWood', label='hadgem2 8.5 2020-59')
L4 = mpatches.Patch(color='DarkGoldenrod', label='hadgem2 8.5 2060-99')

fig.legend(handles=[B1,B2,B3,B4,Base,L1,L2,L3,L4], mode = "expand", ncol= 2,prop={'size': 15}, bbox_to_anchor = [0.53,0.1])