
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob, pathlib
import math


size=13
params = {'legend.fontsize': 'large',
          'axes.labelsize': size,
          'axes.titlesize': size,
          'xtick.labelsize': size,
          'ytick.labelsize': size}
plt.rcParams.update(params)

nalu1 = pd.read_csv('tu_const_aoa_5.dat')
nalu3 = pd.read_csv('tu_sust_aoa_5.dat')

fun3d    = pd.read_csv('fun3d_t_aoa_5.dat')
overf    = pd.read_csv('overflow_aoa_5.dat')

exp      = pd.read_csv('exp.csv')
exp_cl   = exp['cl'][0]
exp_cd   = exp['cd'][0]

plt.figure(figsize=(12,4.5))
plt.subplot(1, 2, 1)
#fig = plt.figure(1)
plt.plot(fun3d['h'],fun3d['cl'],'-o')
plt.plot(overf['h'],overf['cl'],'-o')
plt.plot(nalu3['h'],nalu3['cl'],'-o')
plt.plot(nalu1['h'],nalu1['cl'],'-o')
#plt.axhline(y = exp_cl, color = 'k', linestyle = '--')
plt.xlim([0, 0.01])
plt.ylim([0.95, 1.1])
plt.xlabel('h')
plt.ylabel('Lift coefficient, $C_{l}$')
plt.legend(['SST-$\gamma$: FUN3D','SST-$\gamma$: OVERFLOW','SST-$\gamma$: Nalu-Wind','SST-$\gamma$: Nalu-Wind w/ Const Tu'])

plt.subplot(1, 2, 2)
#fig = plt.figure(2)
plt.plot(fun3d['h'],fun3d['cd'],'-o')
plt.plot(overf['h'],overf['cd'],'-o')
plt.plot(nalu3['h'],nalu3['cd'],'-o')
plt.plot(nalu1['h'],nalu1['cd'],'-o')
#plt.axhline(y = exp_cd, color = 'k', linestyle = '--')
plt.xlim([0, 0.01])
plt.ylim([0.005, 0.02])
plt.xlabel('h')
plt.ylabel('Drag coefficient, $C_{d}$')
plt.legend(['SST-$\gamma$: FUN3D','SST-$\gamma$: OVERFLOW','SST-$\gamma$: Nalu-Wind','SST-$\gamma$: Nalu-Wind w/ Const Tu'])
plt.tight_layout()

plt.savefig("nlf0416_cl_cd.png",dpi=300)

plt.show()

