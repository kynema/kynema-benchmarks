import pandas as pd
import numpy as np
import os,sys,importlib
import warnings
import re
from scipy.interpolate import interp1d

import exawind_helpers as eh
importlib.reload(sys.modules['exawind_helpers'])

class exawind_sim:

    def __init__(self,case):

        # Case details
        self.case_label = case['label']
        self.case_dir = case['directory']
        self.case_type = case['type']
        self.case_fsi = case['fsi']

        # Turbine inputs
        self.yawangle = case['yaw_deg']*np.pi/180.0
        self.tiltangle = case['tilt_deg']*np.pi/180.0
        self.coneangle = case['cone_deg']*np.pi/180.0
        self.constant_omega = case['rotor_speed_rpm']*2*np.pi/60.0
        self.blade_radius = case['tip_radius']
        self.hub_radius = case['hub_radius']
        self.geneff = case['generator_eff']

        # Openfast inputs
        self.of_dt = case['openfast_dt_out']
        self.of_outfile_path = case['openfast_outfile_path']

        self.startup_time = case['startup_time']

        if 'aerodyn_bladefile_path' in case:
            self.of_aerodyn_bladefile = case['aerodyn_bladefile_path']
        else:
            self.of_aerodyn_bladefile = None

        # Exawind inputs
        self.force_file_paths = case['force_file_relpaths']
        self.force_data = None
        
        self.result = None
        self.of_result = None

        if self.case_type == "exawind":
            if 'paraview_spanwise_file' in case:
                self.paraview_spanwise_file = case['paraview_spanwise_file']
                self.spanwise_time = case['spanwise_time']
            else:
                self.paraview_spanwise_file = None
                self.spanwise_time = None
        else:
            if 'spanwise_time' in case:
                self.spanwise_time = case['spanwise_time']
            else:
                self.spanwise_time = None

        
        self.spanfx = None
        self.spanfy = None
        self.span_r = None

        self.gravity_force = eh.calc_gravity_rotor(self.tiltangle,self.blade_radius)

        self.populate_data()
        self.get_spanwise_forces()
        self.spanwise_root_moment()

    def populate_data(self):

        if self.case_type == "exawind":
            self.force_data = eh.read_force_files(self.case_dir,self.force_file_paths)
            self.result = eh.calc_forces_cfd(self.force_data,self.yawangle,self.tiltangle,self.constant_omega)
            if self.of_outfile_path:
                self.of_result = eh.process_openfast_outfile(self.of_outfile_path, self.of_dt, self.startup_time, self.gravity_force, self.geneff)
        
        if self.case_type == "alm" or self.case_type == "openfast":
            self.result = eh.process_openfast_outfile(self.of_outfile_path, self.of_dt, 0.0, self.gravity_force, self.geneff)


    def get_spanwise_forces(self):

        if self.case_type == "alm" or self.case_type == "openfast":

            print(self.spanwise_time,self.of_dt)
        
            nm = 2
            timestart = self.spanwise_time - (0.5*nm*self.of_dt)
            timeend = self.spanwise_time + (0.5*nm*self.of_dt)
            ls = ["--","-",":"]

            n_bladenodes = int(eh.read_openfast_input(self.of_aerodyn_bladefile,'NumBlNds',"int"))
            self.span_r = eh.aerodyn_nodelocs(self.of_aerodyn_bladefile,n_bladenodes)

            oftimedata_start = eh.get_closest_row(self.result,'Time',timestart)
            oftimedata_end = eh.get_closest_row(self.result,'Time',timeend)

            uptest = np.array(self.result.Time > oftimedata_start.Time)
            downtest = np.array(self.result.Time < oftimedata_end.Time)
            thistest = np.logical_and(uptest,downtest)
            of_data_slice = self.result.loc[thistest]
            of_data_mean = of_data_slice.mean()

            nodes = np.arange(1,len(self.span_r)+1,1,dtype=int)
            
            self.spanfx = np.empty(0,dtype=float)
            self.spanfy = np.empty(0,dtype=float)

            for i,n in enumerate(nodes):
                nvar = 'AB1N'+ str(n).zfill(3) + 'Fx'
                self.spanfx = np.append(self.spanfx,of_data_mean[nvar])
                
                tvar = 'AB1N'+ str(n).zfill(3) + 'Fy'
                self.spanfy = np.append(self.spanfy,of_data_mean[tvar])

        if self.case_type == "exawind":
            if self.paraview_spanwise_file:
                pf_azimuth = self.constant_omega*self.spanwise_time
                self.span_r,self.spanfx,self.spanfy,afz,pcfx,pcfy,pcfz = eh.spanforces_from_pview(self.paraview_spanwise_file,self.yawangle,self.tiltangle,-pf_azimuth,-self.coneangle)
                self.span_r = self.span_r - 1.5

    def spanwise_root_moment(self):
        if self.case_type == "alm" or self.case_type == "openfast" or self.paraview_spanwise_file:
            dr = np.diff(self.span_r)
            root_moment_y = np.sum(self.spanfy[1:]*dr*self.span_r[1:])
            print(self.case_label,"Fy Integrated Moment",root_moment_y*3/1000)

            root_moment_x = np.sum(self.spanfx[1:]*dr*self.span_r[1:])
            root_force_x = np.sum(self.spanfx[1:]*dr)
            print(dr)
            print(self.spanfx[1:])
            print(self.spanfx[1:]*dr)
            print(self.case_label,"Fx Integrated Moment",root_moment_x*3/1000)
            print(self.case_label,"Fx Integrated Force",root_force_x*3/1000)