#!/usr/bin/env python3

from subprocess import call
import os,sys
import numpy as np 
import json
import ruamel.yaml as yaml
import argparse
import pathlib
from scipy.interpolate import interp1d
import pandas as pd
import re
import matplotlib
import matplotlib.pyplot as plt
import importlib
import time
import glob


def find_line(lookup,filename):
    linelist = []
    with open(filename) as myFile:
        for num, line in enumerate(myFile, 1):
            if lookup in line:
                linelist.append(num)
    return linelist

def get_closest_row(df, column, value):
    """Get the row in a DataFrame that is closest to a given value in a specific column."""

    # Calculate the absolute difference between the column values and the target value
    df['diff'] = abs(df[column] - value)

    # Find the index of the row with the smallest difference
    min_index = df['diff'].idxmin()

    # Return the row with the smallest difference
    return df.loc[min_index]

def read_openfast_output(file_dir, file_name, skip_time, dt_out):

    file_loc = os.path.join(file_dir,file_name)

    initial_skip_steps = int(skip_time/dt_out)
    headskip = [0,1,2,3,4,5,7]
    
    for s in find_line('#Restarting here',file_loc):
        headskip.append(s-1)

    largeskip = list(range(8,initial_skip_steps+8))

    this_data = pd.read_csv(file_loc,sep='\s+',skiprows=(headskip+largeskip), header=(0),skipinitialspace=True, dtype=float)
    print('Reading',file_loc,sys.getsizeof(this_data),'bytes')
    return this_data

def get_of_time_mean(ofdata,ts,tend):

    uptest = np.array(ofdata.Time > ts)
    downtest = np.array(ofdata.Time < tend)
    thistest = np.logical_and(uptest,downtest)
    of_data_slice = ofdata.loc[thistest]
    mean_data = of_data_slice.mean()

    return pd.DataFrame(mean_data)

def main():


    casename='benchfinal_fsi_abl_splitmesh_nrel5mw'
    ofdata = read_openfast_output('/pscratch/ndeveld/hfm-2025-q1/'+casename+'/5MW_Land_BD_DLL_WTurb','5MW_Land_BD_DLL_WTurb.out', 0.0, 0.02)
    #print(list(ofdata.columns))
    
    data_output_cols = ['Time','GenPwr','RotTorq','RotSpeed','RotThrust','B1RootMxr','B1RootMyr','B1TipTDxr','BldPitch1']

    print('Time',ofdata.Time.iloc[-1])

    timeseries_out = ofdata[data_output_cols]
    meanout = get_of_time_mean(timeseries_out,40.0,420.0)
    meanout = meanout.reset_index()
    print(meanout.index)
    meanout.columns=['variable','value']
    print(meanout)

    timeseries_out.to_csv('../performance/timeseries_openfast.csv',index=None)
    meanout.to_csv('../performance/mean_openfast_40_420.csv',index=None)

    almdata_in = pd.read_csv('/pscratch/ndeveld/hfm-2025-q1/exawind-benchmarks-11032025/amr-wind/actuator_line/NREL5MW_ALM_BD/results/OpenFAST_v402_out/NREL5MW.csv')
    almdata = almdata_in[(almdata_in.Time < 420.0)]

    

    ##############################################
    # Plot summary
    ##############################################

    plt.rcParams.update({'font.size': 18})

    fig, ax = plt.subplots(4,2,figsize=(12,9))
    ax[0,0].plot(ofdata.Time,ofdata.GenPwr/1000.0)
    ax[0,1].plot(ofdata.Time,ofdata.RotTorq)
    ax[1,0].plot(ofdata.Time,ofdata.RotSpeed)
    ax[1,1].plot(ofdata.Time,ofdata.B1TipTDxr)
    ax[2,0].plot(ofdata.Time,ofdata.B1RootMxr)
    ax[2,1].plot(ofdata.Time,ofdata.B1RootMyr)
    ax[3,0].plot(ofdata.Time,ofdata.RotThrust)
    ax[3,1].plot(ofdata.Time,ofdata.BldPitch1)


    ax[0,0].set_title('GenPwr (MW)')
    ax[0,1].set_title('RotTorq (kN-m)')
    ax[1,0].set_title('RotSpeed (rpm)')
    ax[1,1].set_title('B1TipTDxr (m)')
    ax[2,0].set_title('B1RootMxr (N-m)')
    ax[2,1].set_title('B1RootMyr (N-m)')
    ax[3,0].set_title('RotThrust (kN)')
    ax[3,1].set_title('BldPitch1 (deg)')
    fig.tight_layout()
    fig.savefig('openfast_summary.png')

    ##############################################
    # Plot spanwise forces
    ##############################################
    
    timestart = 45.0
    timeend = 160.0

    oftimedata_start = get_closest_row(ofdata,'Time',timestart)
    oftimedata_end = get_closest_row(ofdata,'Time',timeend)

    uptest = np.array(ofdata.Time > oftimedata_start.Time)
    downtest = np.array(ofdata.Time < oftimedata_end.Time)
    thistest = np.logical_and(uptest,downtest)
    of_data_slice = ofdata.loc[thistest]
    of_data_mean = of_data_slice.mean()

    nodes = np.arange(1,20,1,dtype=int)
    spanfn = np.empty(0,dtype=float)
    spanft = np.empty(0,dtype=float)

    for i,n in enumerate(nodes):
        nvar = 'AB1N'+ str(n).zfill(3) + 'Fn'
        spanfn = np.append(spanfn,of_data_mean[nvar])
        
        tvar = 'AB1N'+ str(n).zfill(3) + 'Ft'
        spanft = np.append(spanft,of_data_mean[tvar])


    plt.rcParams.update({'font.size': 18})
    fig, ax = plt.subplots(1,2,figsize=(12,4))

    ax[0].plot(nodes,spanfn)
    ax[1].plot(nodes,spanft)

    ax[0].set_title('Aerodyn Fn')
    ax[1].set_title('Aerodyn Ft')

    fig.tight_layout()
    fig.savefig('spanwise_fn_ft_aerodyn.png')


if __name__ == "__main__":
    main()
