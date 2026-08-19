
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

# experiment
thrust = pd.read_csv('exp_thrust.dat',header=None)
torque = pd.read_csv('exp_torque.dat',header=None)

# Nalu-Wind
nalu_trans= pd.read_csv('nalu_trans.dat')
nalu_turb = pd.read_csv('nalu_turb.dat')

# DTU
dtu_trans  = pd.read_csv('dtu_torque.dat')

# Thrust
uinf    = thrust.iloc[0,:]
th_mean = thrust.iloc[1,:]
th_min  = thrust.iloc[2,:]
th_max  = thrust.iloc[3,:]

# Torque
uinf    = torque.iloc[0,:]
to_mean = torque.iloc[1,:]
to_min  = torque.iloc[2,:]
to_max  = torque.iloc[3,:]


barWidth = 0.2
plt.figure(figsize=(12,5))
plt.subplot(1, 2, 1)

br1 = np.arange(len(th_mean))
br2 = [x + barWidth for x in br1]
br3 = [x + barWidth for x in br2]
br4 = [x + barWidth for x in br3]
#br4 = br4[1]

yerr = [np.subtract(th_mean, th_min), np.subtract(th_max, th_mean)]
plt.bar(br1, th_mean, color ='r', width = barWidth, yerr=yerr,edgecolor ='grey', label ='Experiment')
plt.bar(br2, nalu_turb['thrust'], color ='g', width = barWidth,edgecolor ='grey', label ='Nalu-Wind: Turbulent')
plt.bar(br3, nalu_trans['thrust'], color ='b', width = barWidth,edgecolor ='grey', label ='Nalu-Wind: Transition')


plt.xlabel('Wind Speed [m/s]')
plt.ylim([500, 3000])
plt.ylabel('Thrust [N]')
plt.xticks([r + barWidth for r in range(len(th_mean))],
        ['7', '15'])

plt.legend()

plt.subplot(1, 2, 2)
yerr = [np.subtract(to_mean, to_min), np.subtract(to_max, to_mean)]
plt.bar(br1, to_mean, color ='r', width = barWidth,yerr = yerr, edgecolor ='grey', label ='Experiment')
plt.bar(br2, nalu_turb['torque'], color ='g', width = barWidth,edgecolor ='grey', label ='Nalu-Wind: Turbulent')
plt.bar(br3, nalu_trans['torque'], color ='b', width = barWidth,edgecolor ='grey', label ='Nalu-Wind: Transition')
plt.bar(br4, dtu_trans['torque'], color ='k', width = barWidth,edgecolor ='grey', label ='EllipSys3D: Transition (2009)')

plt.xlabel('Wind Speed [m/s]')
plt.ylim([500, 1700])
plt.ylabel('Torque [Nm]')
plt.xticks([r + barWidth for r in range(len(th_mean))],
        ['7', '15'])

plt.legend()

plt.tight_layout()
plt.savefig("PhaseVi.png",dpi=300)

plt.show()


