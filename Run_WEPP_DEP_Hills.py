#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pandas
import numpy
import scipy
import subprocess

os.chdir('C:\\Users\\Garner\\Soil_Erosion_Project\\wepppy-win-bootstrap-master\\scripts')

model_labels = ['L1','L2','L3','L4','L5','L6',                'B1','B2','B3','B4','B5','B6']

parent_dir = 'C:\\Users\\Garner\\Soil_Erosion_Project\\WEPP_PRWs\\GO1_DEP\\Runs\\DEP_DF_10K\\'

for mod_lab in model_labels:
    wshed_dir = str(parent_dir + mod_lab + '_19\\')
    os.system('python run_project.py {}'.format(wshed_dir))

