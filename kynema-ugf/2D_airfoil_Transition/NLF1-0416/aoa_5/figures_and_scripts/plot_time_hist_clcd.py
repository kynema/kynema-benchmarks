import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import glob, pathlib
import pandas as pd
import math
from mpl_toolkits.mplot3d import Axes3D


# Figure size format
size=15
params = {'legend.fontsize': size-2,
          'axes.labelsize': size,
          'axes.titlesize': size,
          'xtick.labelsize': size,
          'ytick.labelsize': size}
plt.rcParams.update(params)

# Forc outpute file from Nalu-Wind
force_dir='../performance/forces.dat'

# Flow conditions 
u_infty = 341*0.1
rho     = 1.225
dt      = 1/(u_infty*2.0)
alpha   = 5.0


# Read the force file
data = pd.read_csv(force_dir,sep="\s+",skiprows=1,
    names=[
        "Time",
        "Fpx",
        "Fpy",
        "Fpz",
        "Fvx",
        "Fvy",
        "Fvz",
        "Mtx",
        "Mty",
        "Mtz",
        "Y+min",
        "Y+max",
    ],
)

# Non-dimensionalization
dyn_pres = 0.5 * rho * (u_infty ** 2)
cfz = (data["Fpy"] + data["Fvy"]) / dyn_pres
cfx = (data["Fpx"] + data["Fvx"]) / dyn_pres

cos_aoa=math.cos(math.radians(alpha))
sin_aoa=math.sin(math.radians(alpha))

cl = cfz*cos_aoa - cfx*sin_aoa
cd = cfz*sin_aoa + cfx*cos_aoa

# Plot time time history
fig, ax1 = plt.subplots(1)

# Adjust plot legend
cl_l=cl.iloc[-1]*0.985
cl_u=cl.iloc[-1]*1.015

cd_l=cd.iloc[-1]*0.99
cd_u=cd.iloc[-1]*1.01

x= data['Time']/dt
ax2 = ax1.twinx()
ax1.plot(x, cl, 'g')
ax2.plot(x, cd, 'b')
ax1.set_xlabel('Iteration')
ax1.set_ylabel('Lift coefficient, $C_{l}$', color='g')
ax2.set_ylabel('Drag coefficient, $C_{d}$', color='b')
ax1.set_xlim(0, 10000)
ax1.set_ylim(cl_l, cl_u)
ax2.set_ylim(cd_l, cd_u)
ax2.set_ylim(0.0075,0.0082)
ax1.tick_params(axis='y', colors='g')
ax2.tick_params(axis='y', colors='b')
plt.tight_layout()
plt.savefig("time_clcd_nlf0416_F_aoa_5.png",dpi=300)
plt.show()

