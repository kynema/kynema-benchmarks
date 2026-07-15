#!/usr/bin/env python
# coding: utf-8

# # Postprocess OpenFAST results

# In[1]:


# Add any possible locations of amr-wind-frontend here
amrwindfedirs = ['/projects/wind_uq/lcheung/amrwind-frontend/',
                 '/ccs/proj/cfd162/lcheung/amrwind-frontend/']
import sys, os, shutil, io
for x in amrwindfedirs: sys.path.insert(1, x)

import postproamrwindsample_xarray as ppsample
import postproengine as ppeng
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
plt.show(block=False)

# In[2]:


# Load ruamel or pyyaml as needed
try:
    import ruamel.yaml as yaml
    print("# Loaded ruamel.yaml")
    useruamel=True
    loaderkwargs = {'Loader':yaml.RoundTripLoader}
    dumperkwargs = {'Dumper':yaml.RoundTripDumper, 'indent':4, 'default_flow_style':False} 
except:
    import yaml as yaml
    print("# Loaded yaml")
    useruamel=False
    loaderkwargs = {}
    dumperkwargs = {'default_flow_style':False }
    
if useruamel: Loader=yaml.load
else:         Loader=yaml.safe_load


# In[3]:


def stringReplaceDict(s, dreplace):
    outstr = str(s)
    for k, g in dreplace.items():
        outstr=outstr.replace(k, g)
    return outstr


# In[4]:


#rundir='/gpfs/lcheung/HFM/exawind-benchmarks/NREL5MW_ALM_BD_OFv400'
#RESULTSDIR='../results/OpenFAST_v40_out'

replacedict={'RUNDIR':'/tscratch/lcheung/HFM/exawind-benchmarks/NREL5MW_ALM_BD_OFv402_ROSCO',
             'RESULTSDIR':'../results/OpenFAST_v402_out',
             'RESULTSOLDDIR':'../results/OpenFAST_out'
            }


# In[5]:


yamlstring="""
globalattributes:
  verbose: False
  udfmodules: []
  executeorder:
  - openfast
  - plotcsv
  
trange: &trange [300, 900]   # Note: add 15,000 sec to get AMR-Wind time

openfast:
# For FSI case
- name: NREL5MW
  filename: RUNDIR/T0_NREL5MW_v402_ROSCO/openfast-cpp/5MW_Land_DLL_WTurb_cpp/5MW_Land_DLL_WTurb_cpp.out
  #filename: /nscratch/gyalla/HFM/exawind-benchmarks/amr-wind/NREL5MW_ALM_BD/runs/T0_NREL5MW_v402/openfast-cpp/5MW_Land_DLL_WTurb_cpp/5MW_Land_DLL_WTurb_cpp.out
  vars:
  - Time
  - GenPwr
  - RotThrust
  - RotTorq
  - RotSpeed
  - BldPitch1
  output_dir: RESULTSDIR
  csv:  # Store information to CSV files
    individual_files: False
  operate:
    operations: 
    - mean
    trange: *trange

plotcsv:
  - name: Power
    xlabel: 'Time [s]'
    ylabel: 'Power [kW]'
    title: 'Turbine power'
    figsize: [10,4]
    legendopts: {'loc':'upper right'}
    savefile: ../results/images/OpenFAST_T0_GenPwr.png
    csvfiles:
    - {'file':'RESULTSDIR/NREL5MW.csv', 'xcol':'Time', 'ycol':'GenPwr', 'lineopts':{'color':'b', 'lw':1, 'linestyle':'-', 'label':'NREL5MW ALM v4.0.2'}}    
    #- {'file':'RESULTSOLDDIR/NREL5MW.csv', 'xcol':'Time', 'ycol':'GenPwr', 'lineopts':{'color':'r', 'lw':1, 'linestyle':'--', 'label':'NREL5MW ALM v3.5.5'}}    
    
  - name: Thrust
    xlabel: 'Time [s]'
    ylabel: 'RotThrust [kN]'
    title: 'Turbine thrust'
    figsize: [10,4]
    legendopts: {'loc':'upper right'}
    savefile: ../results/images/OpenFAST_T0_RotThrust.png
    csvfiles:
    - {'file':'RESULTSDIR/NREL5MW.csv', 'xcol':'Time', 'ycol':'RotThrust', 'lineopts':{'color':'b', 'lw':1, 'linestyle':'-', 'label':'NREL5MW ALM v4.0.2'}}    
    #- {'file':'RESULTSOLDDIR/NREL5MW.csv', 'xcol':'Time', 'ycol':'RotThrust', 'lineopts':{'color':'r', 'lw':1, 'linestyle':'--', 'label':'NREL5MW ALM v3.5.5'}}    

  - name: RPM
    xlabel: 'Time [s]'
    ylabel: 'RPM [rpm]'
    title: 'Rotor speed'
    figsize: [10,4]
    legendopts: {'loc':'upper right'}
    savefile: ../results/images/OpenFAST_T0_RotSpeed.png
    csvfiles:
    - {'file':'RESULTSDIR/NREL5MW.csv', 'xcol':'Time', 'ycol':'RotSpeed', 'lineopts':{'color':'b', 'lw':1, 'linestyle':'-', 'label':'NREL5MW ALM v4.0.2'}}    
    #- {'file':'RESULTSOLDDIR/NREL5MW.csv', 'xcol':'Time', 'ycol':'RotSpeed', 'lineopts':{'color':'r', 'lw':1, 'linestyle':'--', 'label':'NREL5MW ALM v3.5.5'}}    

  - name: Pitch
    xlabel: 'Time [s]'
    ylabel: 'Pitch [deg]'
    title: 'Blade pitch'
    figsize: [10,4]
    legendopts: {'loc':'upper right'}
    savefile: ../results/images/OpenFAST_T0_BldPitch1.png
    csvfiles:
    - {'file':'RESULTSDIR/NREL5MW.csv', 'xcol':'Time', 'ycol':'BldPitch1', 'lineopts':{'color':'b', 'lw':1, 'linestyle':'-', 'label':'NREL5MW ALM v4.0.2'}}    
    #- {'file':'RESULTSOLDDIR/NREL5MW.csv', 'xcol':'Time', 'ycol':'BldPitch1', 'lineopts':{'color':'r', 'lw':1, 'linestyle':'--', 'label':'NREL5MW ALM v3.5.5'}}    

  - name: RotTorque
    xlabel: 'Time [s]'
    ylabel: 'Torque [kN-m]'
    title: 'Rotor Torque'
    figsize: [10,4]
    legendopts: {'loc':'upper right'}
    savefile: ../results/images/OpenFAST_T0_RotTorq.png
    csvfiles:
    - {'file':'RESULTSDIR/NREL5MW.csv', 'xcol':'Time', 'ycol':'RotTorq', 'lineopts':{'color':'b', 'lw':1, 'linestyle':'-', 'label':'NREL5MW ALM v4.0.2'}}    
    #- {'file':'RESULTSOLDDIR/NREL5MW.csv', 'xcol':'Time', 'ycol':'RotTorq', 'lineopts':{'color':'r', 'lw':1, 'linestyle':'--', 'label':'NREL5MW ALM v3.5.5'}}        

"""
f = io.StringIO(stringReplaceDict(yamlstring, replacedict))
yamldict = Loader(f, **loaderkwargs)


# In[6]:


# Run the driver
ppeng.driver(yamldict, verbose=True)


# In[7]:


# Write out the notebook to a python script
