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

import exawind_helpers as eh
importlib.reload(sys.modules['exawind_helpers'])

import exawind_sim as es
importlib.reload(sys.modules['exawind_sim'])

def main():

    parser = argparse.ArgumentParser(description="Plot exawind timeseries")

    parser.add_argument(
        "-i",
        "--infile",
        help="Input YAML file (must be present in the current directory)",
        required=True,
        type=str,
    )

    args = parser.parse_args()

    # Load input yaml
    yml = yaml.YAML(typ='safe', pure=True)    
    with open(args.infile, 'r') as stream:
        inp = yml.load(stream)

    # Plot initialization
    plot_dir = inp['common']['plot_out_dir']
    plot_prefix = inp['common']['plot_prefix']
    fig,ax = eh.setup_summary_plot(2,3,18,8,inp)
    fig_sp,ax_sp = eh.setup_spanwise_plot(18,6,inp)

    sims = []

    # Load cases and populate variables
    for case in inp['cases']:
        sims.append(es.exawind_sim(case))

    # Get BR 
    for sim in sims:
        if sim.case_type == "exawind":
            ref_power = sim.geneff*sim.result.RotorPower/1000
            ref_torque = sim.result.Torque/1000.0
            ref_thrust = sim.result.T1/1000.0
            ref_time = sim.result.Time


    # Main plotting loop
    for sim in sims:
        
        if sim.case_type == "exawind":

            print("Min Time:",min(sim.result.Time))
            print("Max Time:",max(sim.result.Time))

            ax[0,0].plot(sim.result.Time,sim.geneff*sim.result.RotorPower/1000)
            ax[0,1].plot(sim.result.Time,sim.result.Torque/1000.0)
            ax[0,2].plot(sim.result.Time,sim.result.T1/1000.0, label=sim.case_label)

            ax[1,0].plot(ref_time,(ref_power-ref_power)/ref_power,label=sim.case_label)
            ax[1,1].plot(ref_time,(ref_torque-ref_torque)/ref_torque,label=sim.case_label)
            ax[1,2].plot(ref_time,(ref_thrust-ref_thrust)/ref_thrust,label=sim.case_label)

            if sim.constant_omega:
                rot_speed = np.ones(len(sim.result.Time))*sim.constant_omega*60.0/(2*np.pi)
                bld_pitch = np.ones(len(sim.result.Time))*0.0
                #ax[1,0].plot(sim.result.Time,rot_speed)
                #ax[1,1].plot(sim.result.Time,bld_pitch)

            if sim.paraview_spanwise_file:
                ax_sp[0].plot(sim.span_r,sim.spanfx)
                ax_sp[1].plot(sim.span_r,sim.spanfy,label=sim.case_label)

        
        if sim.case_type == "alm" or sim.case_type == "openfast":

            print("Max Time:",max(sim.result.Time))

            ax[0,0].plot(sim.result.Time,sim.result['GenPwr'])
            ax[0,1].plot(sim.result.Time,sim.result.RotTorq)
            ax[0,2].plot(sim.result.Time,sim.result['AeroThrust'], label=sim.case_label)

            comp_power = eh.interp_new_time(ref_time,sim.result.Time,sim.result['GenPwr'])
            comp_torque = eh.interp_new_time(ref_time,sim.result.Time,sim.result.RotTorq)
            comp_thrust = eh.interp_new_time(ref_time,sim.result.Time,sim.result['AeroThrust'])

            ax[1,0].plot(ref_time,100*(comp_power-ref_power)/ref_power,label=sim.case_label)
            ax[1,1].plot(ref_time,100*(comp_torque-ref_torque)/ref_torque,label=sim.case_label)
            ax[1,2].plot(ref_time,100*(comp_thrust-ref_thrust)/ref_thrust,label=sim.case_label)

            ax[1,0].set_ylim([-35,35])
            ax[1,1].set_ylim([-35,35])
            ax[1,2].set_ylim([-35,35])

            ax_sp[0].plot(sim.span_r,sim.spanfx)
            ax_sp[1].plot(sim.span_r,sim.spanfy,label=sim.case_label)



        
    fig.tight_layout(pad=2.0)
    ax[1,1].legend(loc='upper center', bbox_to_anchor=(0.3, -0.1),fancybox=False, shadow=False,ncol=len(inp['cases']), frameon=False)
    plotpath = os.path.join(plot_dir,plot_prefix+'_exawind_summary.png')
    fig.savefig(plotpath)


    fig_sp.tight_layout(pad=3.0)
    ax_sp[1].legend(loc='upper center', bbox_to_anchor=(-0.3, -0.1),fancybox=False, shadow=False, ncol=len(inp['cases']), frameon=False)
    plotpath = os.path.join(plot_dir,plot_prefix+'_exawind_spanwise.png')
    fig_sp.savefig(plotpath)



if __name__ == "__main__":
    main()

