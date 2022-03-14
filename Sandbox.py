#%%

mod_names = ['gfdl 4.5 2020-59','gfdl 4.5 2060-99',\
                     'gfdl 6.0 2020-59', 'gfdl 6.0 2060-99',\
                     'hadgem2 4.5 2020-59', 'hadgem2 4.5 2060-99',\
                     'hadgem2 8.5 2020-59', 'hadgem2 8.5 2060-99',\
                     'Baseline 1965-2019']

        colors = ['cornflowerblue', 'mediumblue',\
                 'Gold', 'goldenrod',\
                 'mediumseagreen', 'green',\
                 'salmon', 'Red',\
                 'black']


fig.suptitle('Average WEPP Growing Season Soil Loss for HUC12 Watershed in Dodge County, MN\nwith Varying Management Scenarios and Future Climates',\
                 fontsize = 21)



 # PDF
df['pdf'] = (df[mod] / sum(df[mod])) * 100

# CDF
df['cdf'] = df['pdf'].cumsum()

print(df)


x = df['% Adoption']
y = df['cdf']