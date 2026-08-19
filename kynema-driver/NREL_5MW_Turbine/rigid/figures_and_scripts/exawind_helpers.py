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
import netCDF4 as nc


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

def interp_new_time(reftime,time,vals):
    f = interp1d(time, vals, kind='linear')
    return [f(t) for t in reftime]

def read_openfast_output(file_loc, skip_time, dt_out):

    initial_skip_steps = int(skip_time/dt_out)
    
    headskip = [0,1,2,3,4,5,7]

    restart_lines = find_line('#Restarting here',file_loc)
    if len(restart_lines) > 0:
        for s in restart_lines:
            headskip.append(s-1)

    largeskip = list(range(8,initial_skip_steps+8))

    this_data = pd.read_csv(file_loc,sep='\\s+',skiprows=(headskip+largeskip), header=(0),skipinitialspace=True, dtype=float)
    print('Reading',file_loc,sys.getsizeof(this_data),'bytes')

    #this_data['Time'] = this_data['Time']-skip_time
    #print(this_data.Time)

    return this_data

def calc_forces_cfd(all_data,yawangle,tiltangle,omega):

    time = all_data['Time']

    all_data['fx'] = all_data['Fpx']+all_data['Fvx']
    all_data['fy'] = all_data['Fpy']+all_data['Fvy']
    all_data['fz'] = all_data['Fpz']+all_data['Fvz']

    all_data['frot_yaw_x'] = all_data['fx']*np.cos(-yawangle)-all_data['fy']*np.sin(-yawangle)
    all_data['frot_yaw_y'] = all_data['fx']*np.sin(-yawangle)+all_data['fy']*np.cos(-yawangle)
    all_data['frot_yaw_z'] = all_data['fz']       

    all_data['mrot_yaw_x'] = all_data['Mtx']*np.cos(-yawangle)-all_data['Mty']*np.sin(-yawangle)
    all_data['mrot_yaw_y'] = all_data['Mtx']*np.sin(-yawangle)+all_data['Mty']*np.cos(-yawangle)
    all_data['mrot_yaw_z'] = all_data['Mtz']

    all_data['Torque'] = all_data['mrot_yaw_x']*np.cos(-tiltangle)+all_data['mrot_yaw_z']*np.sin(-tiltangle)
    
    all_data['Thrust'] = all_data['frot_yaw_x']*np.cos(-tiltangle)+all_data['frot_yaw_z']*np.sin(-tiltangle)

    all_data['T1'] = all_data['frot_yaw_x']*np.cos(-tiltangle)+all_data['frot_yaw_z']*np.sin(-tiltangle)
    all_data['T2'] = all_data['frot_yaw_y']
    all_data['T3'] = -all_data['frot_yaw_x']*np.sin(-tiltangle)+all_data['frot_yaw_z']*np.cos(-tiltangle)

    all_data['RotorPower'] = all_data['Torque']*omega

    return all_data

def get_nc_var(ncfile,varname,dim=3):

    dataset = nc.Dataset(ncfile, 'r')
    vardata = dataset.variables[varname][:]
    timedata = dataset.variables['time'][:]

    if dim == 3:
        vardata_mag = [float(np.linalg.norm(np.array(vardata[i]))) for i in range(len(vardata))]
    else:
        vardata_mag = vardata

    return np.array(timedata),np.array(vardata),np.array(vardata_mag)

def calc_centrifugal(bld_rad,flap,omega):
    bdpath = "/pscratch/ndeveld/hfm-2025-q1/data/nrel5mw-blade-prop.csv"
    blade_data = pd.read_csv(bdpath,sep='\\s+',skipinitialspace=True)

    span = blade_data.BlFract*bld_rad
    ds = np.diff(span) #len(span)-1

    r = span[1:]+0.5*ds
    dm = blade_data.BMassDen[1:]*ds #single blade sectional mass

    cf = []

    for i,s in enumerate(omega):
        cf.append(3*np.sum(r*np.sin(flap[i])*np.power(s*2*np.pi/60.0,2)*dm))

    return np.array(cf)

def calc_gravity_blades(bld_rad,tilt,azimuth):

    bdpath = "/pscratch/ndeveld/hfm-2025-q1/data/nrel5mw-blade-prop.csv"
    blade_data = pd.read_csv(bdpath,sep='\\s+',skipinitialspace=True)

    span = blade_data.BlFract*bld_rad
    ds = np.diff(span) #len(span)-1

    r = span[1:]+0.5*ds
    dm = blade_data.BMassDen[1:]*ds #single blade sectional mass 

    azb1 = azimuth*np.pi/180.0
    azb2 = (azimuth+120.0)*np.pi/180.0
    azb3 = (azimuth+240.0)*np.pi/180.0

    gb1 = np.sum(9.8*np.cos(azb1)*dm)
    gb2 = np.sum(9.8*np.cos(azb2)*dm)
    gb3 = np.sum(9.8*np.cos(azb3)*dm)

    return np.array((gb1+gb2+gb3)*np.sin(tilt))

def blade_mass(bld_rad):

    bdpath = "/pscratch/ndeveld/hfm-2025-q1/data/nrel5mw-blade-prop.csv"
    blade_data = pd.read_csv(bdpath,sep='\\s+',skipinitialspace=True)

    span = blade_data.BlFract*bld_rad
    ds = np.diff(span) #len(span)-1

    r = span[1:]+0.5*ds
    dm = blade_data.BMassDen[0:-1]*ds #single blade sectional mass 

    return 3.0*np.sum(dm)

def aerodyn_nodelocs(bladefile,nlines):
    headskip = [0,1,2,3,5]
    print("Reading blade file",bladefile, 'lines',nlines)
    blade_data = pd.read_csv(bladefile,sep='\\s+',skiprows=(headskip), header=(0),skipinitialspace=True, nrows=nlines)
    return np.array(blade_data.BlSpn) 

def calc_gravity_rotor(tilt,bld_rad):

    rotor_mass = 56780.0 + blade_mass(bld_rad)
    #print("Rotor mass",rotor_mass,"kg")
    g = 9.8

    return rotor_mass*g*np.sin(tilt)

def spanforces_from_pview(csvfile,yaw,tilt,azimuth,precone):
    data = pd.read_csv(csvfile)
    
    fx = data.pfx + data.vfx
    fy = data.pfy + data.vfy
    fz = data.pfz + data.vfz

    yfx = fx*np.cos(-yaw) - fy*np.sin(-yaw)
    yfy = fx*np.sin(-yaw) + fy*np.cos(-yaw)
    yfz = fz

    tfx = yfx*np.cos(-tilt) + yfz*np.sin(-tilt)
    tfy = yfy
    tfz = -yfx*np.sin(-tilt) + yfz*np.cos(-tilt)

    afx = tfx
    afy = tfy*np.cos(-azimuth) - tfz*np.sin(-azimuth)
    afz = tfy*np.sin(-azimuth) + tfz*np.cos(-azimuth)

    pcfx = afx*np.cos(-precone) + afz*np.sin(-precone)
    pcfy = afy
    pcfz = -afx*np.sin(-precone) + afz*np.cos(-precone)

    return data.span,afx,-afy,afz,pcfx,pcfy,pcfz

def read_force_files(case_dir, force_file_paths):

    this_data = []

    for j in range(len(force_file_paths)):
        fullpath = os.path.join(case_dir,force_file_paths[j])
        this_data.append(pd.read_csv(fullpath,sep='\\s+',skipinitialspace=True))

    return pd.concat(this_data, ignore_index=True)

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

def process_openfast_outfile(openfast_file, dtout, offset_seconds, gravity_force, geneff):

    data = read_openfast_output(openfast_file, offset_seconds, dtout)

    data['AeroThrust'] = data.RotThrust - gravity_force/1000.0 #- centrifugal_force/1000.0
    data['GenPwr'] = data.RotTorq*data.RotSpeed*2*np.pi/60.0*geneff
    data['Time'] = data['Time'] - offset_seconds
    print(offset_seconds)
    print(dtout)
    print(data['Time'])

    return data

def setup_summary_plot(r,c,w,h,inp):

    plt.rcParams.update({'font.size': 18})
    xmin = inp['common']['plot_x_bounds'][0]
    xmax = inp['common']['plot_x_bounds'][1]

    fig, ax = plt.subplots(r,c,figsize=(w,h),gridspec_kw={'height_ratios':[2, 1]})

    #ax[1,2].axis('off')

    ax[0,0].set_title('Gen Power(kW)')
    ax[0,1].set_title('Torque (kN-m)')
    ax[0,2].set_title('Thrust (kN)')
    #ax[1,0].set_title('RotSpeed (rpm)')
    #ax[1,1].set_title('BldPitch1 (deg)')
    #ax[1,2].set_title('B1TipTDxr (m)')
    #ax[2,0].set_title('B1RootMxr (N-m)')
    #ax[2,1].set_title('B1RootMyr (N-m)')

    ax[1,0].set_title('% Diff GR')
    ax[1,1].set_title('% Diff GR')
    ax[1,2].set_title('% Diff GR')

    for i in range(r):
        for j in range(c):
            ax[i,j].minorticks_on()
            ax[i,j].grid(visible=True, which='minor', axis='both',linestyle='-',color="#eee")
            ax[i,j].grid(visible=True, which='major', axis='both',linestyle='-',color="#888")
            ax[i,j].set_axisbelow(True)
            ax[i,j].set_xlim([xmin,xmax])

    return fig,ax

def setup_summary_plot_fsi(r,c,w,h,inp):

    plt.rcParams.update({'font.size': 18})
    xmin = inp['common']['plot_x_bounds'][0]
    xmax = inp['common']['plot_x_bounds'][1]

    fig, ax = plt.subplots(r,c,figsize=(w,h),gridspec_kw={'height_ratios':[2, 1]})

    #ax[1,2].axis('off')

    ax[0,0].set_title('Gen Power(kW)')
    ax[0,1].set_title('Torque (kN-m)')
    ax[0,2].set_title('Thrust (kN)')
    ax[0,3].set_title('RotSpeed (rpm)')
    ax[0,4].set_title('BldPitch1 (deg)')
    ax[0,5].set_title('B1TipTDxr (m)')
    #ax[2,0].set_title('B1RootMxr (N-m)')
    #ax[2,1].set_title('B1RootMyr (N-m)')

    ax[1,0].set_title('% Diff GR')
    ax[1,1].set_title('% Diff GR')
    ax[1,2].set_title('% Diff GR')    
    ax[1,3].set_title('% Diff GR')
    ax[1,4].set_title('% Diff GR')
    ax[1,5].set_title('% Diff GR')

    for i in range(r):
        for j in range(c):
            ax[i,j].minorticks_on()
            ax[i,j].grid(visible=True, which='minor', axis='both',linestyle='-',color="#eee")
            ax[i,j].grid(visible=True, which='major', axis='both',linestyle='-',color="#888")
            ax[i,j].set_axisbelow(True)
            ax[i,j].set_xlim([xmin,xmax])

    return fig,ax

def setup_spanwise_plot(w,h,inp):

    plt.rcParams.update({'font.size': 18})

    fig, ax = plt.subplots(1,2,figsize=(w,h))

    ax[0].set_title('Fx (kN)')
    ax[1].set_title('Fy (kN)')

    for i in range(2):
        ax[i].minorticks_on()
        ax[i].grid(visible=True, which='minor', axis='both',linestyle='-',color="#eee")
        ax[i].grid(visible=True, which='major', axis='both',linestyle='-',color="#888")
        ax[i].set_axisbelow(True)

    return fig,ax
