import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import glob, pathlib
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D


# Plot format
size=15
params = {'legend.fontsize': size-2,
          'axes.labelsize': size,
          'axes.titlesize': size,
          'xtick.labelsize': size,
          'ytick.labelsize': size}
plt.rcParams.update(params)

# Nalu-Wind input
trans   = 1 # transition model on
log_file = "nlf0416_F_aoa_5.0.log" # Nalu-Wind log file


def read_resid(log_file,niter,line_num):

    # Find residual values
    tmp=[]
    file=open(log_file,'r')
    for lines in file:
       tmp += [lines.split()]
    file.close()
    n_line=int(len(tmp))
    
    # Save residuals in arrays
    resid_mom_eqs_x = np.zeros((niter))
    resid_mom_eqs_y = np.zeros((niter))
    resid_mom_eqs_z = np.zeros((niter))
    resid_mom_eqs = np.zeros((niter))
    resid_rho_eqs = np.zeros((niter))
    resid_k_eqs = np.zeros((niter))
    resid_w_eqs = np.zeros((niter))
    it = np.zeros((niter))
    resid_gamma_eqs = np.zeros((niter))

    nlines=9
    if(trans==1):
        nlines=10

    for j in range(niter):
        i0 = line_num[j+2]

        # Read time step count number
        ii = i0+1
        it[j] = tmp[ii][3]

        tmp_lines = 8
        n_solver = 4
        i  =i0+ tmp_lines + (n_solver-1)*nlines
        resid_mom_eqs[j]   = tmp[i+5][3]
        resid_rho_eqs[j]   = tmp[i+6][3]
        resid_k_eqs[j]     = tmp[i+8][3]
        resid_w_eqs[j]     = tmp[i+9][3]
        if(trans==1):
           resid_gamma_eqs[j]     = tmp[i+10][3]

    return it,resid_mom_eqs,resid_rho_eqs,resid_k_eqs,resid_w_eqs,resid_gamma_eqs

def find_index_location(log_file):
    # Find line numbers
    with open(log_file, 'r') as file:
        lines = file.readlines()
    file.close()
    
    n_line=len(lines)
    
    line_num=[]
    for i in range(n_line):
        if(lines[i][0]=="*"):
            line_num.append(i)
    del lines
    
    niter=len(line_num)-4
    print(niter)
 
    return niter, line_num


def create_nalu_hist(niter,line_num,log_file):
    print(log_file)

    [it,resid_mom_eqs,resid_rho_eqs,resid_k_eqs,resid_w_eqs,resid_gamma]=read_resid(log_file,niter,line_num)
    
    plt.figure

    plt.semilogy(it, resid_mom_eqs)
    plt.semilogy(it, resid_k_eqs,'-.')
    plt.semilogy(it, resid_gamma,'--')
    plt.xlabel('Iteration')
    plt.ylabel('Residuals')
    plt.xlim([0, 8000])
    plt.xticks(np.arange(0, 10000.1, 2000))
    plt.ylim([1e-7, 1e-1])
    #plt.legend(["Mean flow","Turbulence model:k","Turbuelnce model: omega","Transition model"])
    plt.legend(["Mean flow","Turbulence model","Transition model"])
    plt.tight_layout()
    plt.savefig("resid_nlf0416_F_aoa_5.png",dpi=300)
    plt.show()

    del it,resid_mom_eqs,resid_rho_eqs,resid_k_eqs,resid_w_eqs

if __name__=="__main__":

    # Nalu-Wind log file
    [niter, line_num] = find_index_location(log_file)
    create_nalu_hist(niter,line_num,log_file)
