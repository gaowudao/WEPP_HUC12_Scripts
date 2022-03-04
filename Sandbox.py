import pandas as pd

mod_lst = ['B1','B2']
scen_lst = ['CC','Comb','CT']

B1 = []
B2 = []

mod_output_lsts = [B1, B2]

for mod, mod_out_lst in zip(mod_lst,mod_output_lsts):

    for scen in scen_lst:

        mod_out_lst.append(scen)

        
test = pd.DataFrame({'B1':B1, 'B2':B2})


print(test)