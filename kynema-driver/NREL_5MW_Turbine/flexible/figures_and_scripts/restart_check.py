#!/usr/bin/env python3

import subprocess as sp
import os,sys
import numpy as np 
import json
import ruamel.yaml
import argparse
import pathlib
import pandas as pd
import re
import time
import glob
from collections import OrderedDict
import warnings
import shutil as sh


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

def get_times_netcdf(filepath):
    cmd = 'ncdump -v time_whole ' + filepath + ' | sed -e "1,/data:/d" -e "$d"'
    result = sp.run(cmd, shell=True, capture_output=True, text=True)

    stdout = result.stdout
    retstring = ''

    for line in stdout.splitlines():
        templine = line.strip()
        retstring = retstring + templine
            
    retstring = re.sub(r'\s+', '', retstring)
    retstring = retstring.replace(';}','').replace('time_whole=','').split(',')

    return [float(s) for s in retstring]

def read_openfast_input(offile,ofvariable,vartype):

    # Regex to match any continuous non-whitespace
    allreg = "\\S+"

    # Regex to match any continuous whitespace
    spreg = "\\s+"

    search_text = allreg + spreg + re.escape(str(ofvariable).strip())

    textfile = open(offile, 'r')
    filetext = textfile.read()
    textfile.close()
    matches = re.findall(search_text, filetext)

    if(vartype=="str"):
        return matches[0].split()[0]
    else:
        return float(matches[0].split()[0])


def read_openfast_output(file_dir, file_name, skip_time, dt_out):

    file_loc = os.path.join(file_dir,file_name)

    initial_skip_steps = int(skip_time/dt_out)
    headskip = [0,1,2,3,4,5,7]
    
    for s in find_line('#Restarting here',file_loc):
        headskip.append(s-1)

    largeskip = list(range(8,initial_skip_steps+8))

    this_data = pd.read_csv(file_loc,sep='\\s+',skiprows=(headskip+largeskip), header=(0),skipinitialspace=True, dtype=float)
    print('Reading',file_loc,sys.getsizeof(this_data),'bytes')
    return this_data

def read_yaml(filepath):
    with open(filepath, 'r') as file:
        yaml = ruamel.yaml.YAML()
        data = dict(yaml.load(file))
    return data

def read_amr(filepath):
    returndict = OrderedDict()
    with open(filepath) as f:
        for line in f:
            key, data = processline(line)
            if key is not None: returndict[key] = data
    return returndict

def processline(inputline):
    line = inputline.partition('#')[0]
    line = line.rstrip()
    if len(line)>0:
        line = line.split('=')
        key  = line[0].strip()
        data = line[1].strip()
        return key, data
    return None, None


def main():

    print('Initializing file paths')

    ######################################################
    ### User Input Here ##################################
    ######################################################
    # Script assumes you have created a 
    # restart file
    ######################################################

    casedir = '/pscratch/ndeveld/hfm-2025-q1'
    # casename = 'benchfinal_fsi_abl_splitmesh_nrel5mw'
    # include_openfast = True
    casename = 'benchfinal_rigid_abl_splitmesh_nrel5mw2'
    include_openfast = False
    casepath = os.path.join(casedir,casename)
    n_ranks_nalu = 672
    

    files = {}
    files['nalu_first'] = 'nrel5mw_nalu.yaml'
    files['amr_orig'] = 'nrel5mw_amr.inp'
    files['nalu_orig'] = 'nrel5mw_nalu.yaml'
    files['driver_orig'] = 'nrel5mw.yaml'
    files['amr_restart'] = 'nrel5mw_amr_r1.inp'
    files['nalu_restart'] = 'nrel5mw_nalu_r1.yaml'
    files['driver_restart'] = 'nrel5mw_r1.yaml'
    
    slurm_submit_restart = 'run_case_r1.sh'

    ######################################################

    print('Reading Input Files')

    yamldata = {}

    for k in files.keys():
        #print('Reading',files[k])
        fullpath = os.path.join(casepath,files[k])
        if "amr" not in k:
            yamldata[k] = read_yaml(fullpath)
        else:
            yamldata[k] = read_amr(fullpath) 
            
    print('Reading netcdf restart')

    
    restart_exo_name = str(dict(yamldata['nalu_orig']['realms'][0]['restart'])['restart_data_base_name'])
    restart_exo = os.path.join(casepath,restart_exo_name+'.'+str(n_ranks_nalu)+'.000')
    netcdf_times = get_times_netcdf(restart_exo)

    print('Times available in Nalu-Wind netcdf:',netcdf_times)

    amr_re_starttime = float(yamldata['amr_restart']['time.start_time'])
    nalu_re_starttime = float(yamldata['nalu_restart']['Time_Integrators'][0]['StandardTimeIntegrator']['start_time'])
    
    nalu_restart_check = dict(yamldata['nalu_restart']['realms'][0]['restart']).keys()
    
    # Check for restart_time key in Nalu-Wind
    assert 'restart_time' in nalu_restart_check, "This script needs restart_time flag in Nalu restart file to continue"

    nalu_restart_time = dict(yamldata['nalu_restart']['realms'][0]['restart'])['restart_time']
    print('Nalu restart_time key is present')
    if nalu_restart_time in netcdf_times:
        print('Nalu restart_time exists in the netcdf restart array',nalu_restart_time)
    else:
        print('ERROR: Nalu restart_time is NOT present in netcdf restart exo')
        print('Requsted time:',nalu_restart_time)
        print('Time array:',netcdf_times)

    # Check start times in AMR and Nalu
    if amr_re_starttime in netcdf_times:
        print('AMR start time', amr_re_starttime ,'present in netcdf restart exo')
    else:
        print('ERROR: AMR start time', amr_re_starttime ,'NOT present in restart exo')

    if nalu_re_starttime in netcdf_times:
        print('Nalu start time', nalu_re_starttime ,'present in netcdf restart exo')
    else:
        print('ERROR: Nalu start time', nalu_re_starttime ,'NOT present in restart exo')

    # Openfast checks
    if include_openfast:
        print('Reading OpenFAST restart')

        openfast_timestep = float(dict(yamldata['nalu_orig']['realms'][0]['openfast_fsi'])['dt_FAST'])

        # The following assumes that number of turbines does not change between restarts
        n_turbines_orig = int(dict(yamldata['nalu_orig']['realms'][0]['openfast_fsi'])['n_turbines_glob'])
        for i in range(n_turbines_orig):
            openfast_restart_path_first = str(dict(yamldata['nalu_first']['realms'][0]['openfast_fsi'])['Turbine'+str(i)]['restart_filename'])
            openfast_restart_first_n = int(openfast_restart_path_first.split('.')[-1])
            print('OF Starting N:',openfast_restart_first_n)

            openfast_restart_path = str(dict(yamldata['nalu_restart']['realms'][0]['openfast_fsi'])['Turbine'+str(i)]['restart_filename'])
            openfast_restart_n = int(openfast_restart_path.split('.')[-1])
            print('OF Restart N:',openfast_restart_n)
            print('OF Should Restart At:', openfast_restart_n*openfast_timestep)

            openfast_restart_time = (openfast_restart_n - openfast_restart_first_n)*openfast_timestep
            of_cfd_diff = np.abs(nalu_restart_time-openfast_restart_time)
            print('OF Restart Time:',openfast_restart_time, ' Diff with CFD:',of_cfd_diff)
            assert of_cfd_diff < 1e-9, "OpenFAST restart time does not match your requested CFD restart time"


    # Check that mesh transformation is commented out
    allres = dict(yamldata['nalu_restart']['realms'][0])
    assert "mesh_transformation" not in allres.keys(), "Initial Mesh transformation must be commented on restart"

    # Check that amr-wind is using an updated local checkpoint chkXXXXX
    amr_orig_mesh = str(yamldata['amr_orig']['io.restart_file'])
    amr_res_mesh = str(yamldata['amr_restart']['io.restart_file'])
    print('AMR restart using:',amr_res_mesh)
    assert amr_orig_mesh != amr_res_mesh, "Checkpoint for AMR restart appears to be the same as the original"

    # Check the AMR restart folder exists on disk
    assert os.path.isdir(amr_res_mesh), "AMR restart checkpoint does not exist"

    # Check the amr-wind start time makes sense with checkpoint n
    amr_res_n = int(amr_res_mesh.split('chk')[1])
    amr_start_n = int(str(yamldata['amr_restart']['time.checkpoint_start']))
    amr_dt = float(str(yamldata['amr_restart']['time.fixed_dt']))
    amr_start_time = float(str(yamldata['amr_restart']['time.start_time']))
    amr_chk_start = (amr_res_n - amr_start_n)*amr_dt
    amr_start_diff = amr_chk_start - amr_start_time 
    print('Start diff between AMR-Wind checkpoint and time.start_time',amr_start_diff, amr_res_n,amr_start_n,amr_dt,amr_start_time,amr_chk_start)
    assert amr_start_diff < 1e-10, "AMR-Wind checkpoint time does not match start time"

    # Check that nalu-wind is using an updated local checkpoint/restart
    orig_mesh_name = str(yamldata['nalu_orig']['realms'][0]['mesh'])
    res_mesh_name = str(yamldata['nalu_restart']['realms'][0]['mesh'])
    print('NALU restart using mesh:',res_mesh_name)
    assert orig_mesh_name != res_mesh_name, "Mesh for NALU restart appears to be the same as mesh for original"

    # Make sure restart and out file directories are different
    orig_rst_name = str(yamldata['nalu_orig']['realms'][0]['restart']['restart_data_base_name'])   
    res_rst_name = str(yamldata['nalu_restart']['realms'][0]['restart']['restart_data_base_name']) 
    assert orig_rst_name != res_rst_name, "Output dir for NALU restart appears to be the same as original, these must be different"

    # Make sure driver file uses updated file names
    assert yamldata['driver_restart']['exawind']['nalu_wind_inp'][0] == files['nalu_restart'], "Driver file doesn't used updated nalu restart filename"
    assert yamldata['driver_restart']['exawind']['amr_wind_inp'] == files['amr_restart'], "Driver file doesn't used updated amr restart filename"

    # Make sure driver input was updated
    slurmpath = os.path.join(casepath,slurm_submit_restart)
    with open(slurmpath, 'r') as file:
        content = file.read()
        assert files['driver_restart'] in content, "Slurm submit file appears to not use updated driver file"

    print('Successfully finished restart checks')

    # Make backups of forces files because they get deleted on restart
    nalu_forcefiles = [dict(pp)['output_file_name'] for pp in yamldata['nalu_orig']['realms'][0]['post_processing']]
    for f in nalu_forcefiles:
        fullpath = os.path.join(casepath,f)
        newpath = os.path.join(casepath,f+'.bak')
        if os.path.exists(fullpath):
            print('Making backup of',fullpath)
            sh.copyfile(fullpath,newpath)
        else:
            print('Forces file',fullpath,'has been moved or deleted')



if __name__ == "__main__":
    main()