# coding: utf-8
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MultipleLocator
import matplotlib as mpl 
from cycler import cycler

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
print(colors)


mpl.rcParams['lines.linewidth'] = 2 
mpl.rcParams['axes.titlesize'] = 30
mpl.rcParams['axes.labelsize'] = 34 # 14
mpl.rcParams['xtick.labelsize'] = 16
mpl.rcParams['ytick.labelsize'] = 16
mpl.rcParams['legend.fontsize'] = 12.0
mpl.rcParams['figure.figsize'] = (6.328, 5.328)
mpl.rcParams["figure.autolayout"] = True

###############################################

grids = ['240-257-41', '240-257-96', '240-257-121']


rho = 1.2
u_infty = 50.0
dyn_pres = 0.5 * rho * (u_infty ** 2)
aoa = [30, 45, 60, 90]
case_dirs = ['aoa_{:d}'.format(i) for i in aoa ]



def get_avg_data(home, turb_model, upw, grid):
    """Get average lift and drag data for a given turbulence model, upwinding and grid"""
    case_data = [ pd.read_csv(home + '/' + c +'/raw_data' + '/' + turb_model+'-' + upw + '-' + grid + '_v2_0021.dat', sep="\s+", skiprows=1,header=None, names=[ "Time","Fpx","Fpy","Fpz","Fvx","Fvy","Fvz","Mtx","Mty","Mtz","Y+min","Y+max"],dtype=float).iloc[-4000:] for c in case_dirs]
    case_cl = [ np.average((c["Fpy"] + c["Fvy"])/dyn_pres/4.0) for c in case_data]
    case_cd = [ np.average((c["Fpx"] + c["Fvx"])/dyn_pres/4.0) for c in case_data]
    return case_cl, case_cd

def plots (home):

    exp_data = {
             'cl': pd.read_csv(home + '/experimental_data/cl_exp_data_0021.txt',header=None,names=['aoa','cl']),
             'cd': pd.read_csv(home + '/experimental_data/cd_exp_data_0021.txt',header=None,names=['aoa','cd']), 
    }

    with PdfPages('NACA_0021_cl_240_257_x.pdf') as pfpgs:
        fig = plt.figure()
        for g in grids:
          case_cl, case_cd = get_avg_data(home, 'iddes','sou', g)
          plt.plot(aoa, case_cl, label=g, marker = '^', markersize=10, linestyle = 'None')
        plt.plot(exp_data['cl']['aoa'], exp_data['cl']['cl'],'+-', label='Exp')
        plt.xlabel(r'$\alpha$')
        plt.ylabel('$C_l$')
        plt.xlim([0.0,92.0])
        plt.ylim([0.0,1.75])
        plt.minorticks_on()
        plt.xticks(np.arange(0, 92, 10))
        plt.legend(loc='upper left')
        plt.tight_layout()
        pfpgs.savefig()
        plt.close(fig)
        plt.show()

    with PdfPages('NACA_0021_cd_240_257_x.pdf') as pfpgs:
        fig = plt.figure()
        for g in grids:
          case_cl, case_cd = get_avg_data(home, 'iddes','sou', g)
          plt.plot(aoa, case_cd, label=g, marker = '^', markersize=10, linestyle = 'None')
        plt.plot(exp_data['cd']['aoa'], exp_data['cd']['cd'],'+-', label='Exp')
        plt.xlabel(r'$\alpha$')
        plt.ylabel('$C_d$')
        plt.xlim([0.0,92.0])
        plt.ylim([0.0,3.0]) 
        plt.minorticks_on()
        plt.xticks(np.arange(0, 92, 10)) 
        plt.legend(loc='upper left')
        plt.tight_layout()
        pfpgs.savefig()
        plt.close(fig)

if __name__=="__main__":

    ##################################################
    #      User Specified   
    ##################################################
    # Specify location of the NACA-0021 directory
    home = sys.argv[1] 
    plots(home) 
