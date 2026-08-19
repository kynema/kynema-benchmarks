#################  IMPORT  ###################

import numpy  as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rc

##################  FONTS  ###################

rc('font',**{'family':'sans-serif','sans-serif':['Computer Modern Roman']})
mpl.rcParams['text.latex.preamble'] = '\n'.join([
       r'\usepackage{sansmath}', r'\sansmath'  
])
rc('text',usetex=True)
mpl.rcParams.update({'font.size': 16})

###############  READ IN DATA  ###############

data = np.loadtxt('expq7.dat')
cloc = data[:, 0]
cval = data[:, 1]
nval = len(cloc)

data = np.loadtxt('expa7.dat')
cloc2 = data[:, 0]
cval2 = data[:, 1]*1000
nval2 = len(cloc2)

data = np.loadtxt('workq7.dat')
cloc3 = data[:, 0]
cval3 = data[:, 1]*1000
nval3 = len(cloc3)
cval4 = data[:, 2]*1000

data = np.loadtxt('nalu7.dat')
cloc5 = data[:, 0]*data[:,0]*1.225*0.5
cval5 = data[:, 1]*1000
nval5 = len(cloc5)

##################  COLORS  ##################

mycolors = {
    'grey25'      : (0.250,   0.250,   0.250),
    'grey50'      : (0.500,   0.500,   0.500),
    'grey75'      : (0.750,   0.750,   0.750),
    'grey80'      : (0.800,   0.800,   0.800),              
    'blue'        : (0.122,   0.471,   0.706),
    'green'       : (0.200,   0.627,   0.173),
    'red'         : (0.890,   0.102,   0.110),
    'orange'      : (1.000,   0.498,   0.000),    
    'black'       : (0.000,   0.000,   0.000),
    'white'       : (1.000,   1.000,   1.000),
    'purple'      : (0.416,   0.239,   0.602),
    'yellow'      : (1.000,   1.000,   0.600),
    'brown'       : (0.690,   0.394,   0.157),    
    'lightpurple' : (0.792,   0.698,   0.839),
    'lightorange' : (0.992,   0.749,   0.043),
    'lightred'    : (0.984,   0.604,   0.600),
    'lightgreen'  : (0.698,   0.875,   0.541),
    'lightblue'   : (0.651,   0.808,   0.890),    
}

################  PLOT SETUP  ################

fig, ax = plt.subplots(figsize=(6,4), tight_layout=True)
plt.fill_between(cloc3/1000, cval3, cval4, color=mycolors['grey80'], alpha=1.0,label='Workshop')
plt.plot(cloc/1000,cval, '-k', linewidth=1,label='Exp. q sweep')
plt.plot(cloc2/1000,cval2, '--k', linewidth=1,label='Exp. AoA sweep')
plt.plot(cloc5/1000,cval5, '-o', color=mycolors['blue'], markersize=3.0, label='Exawind FSI')
ax.tick_params(axis='x', which='major', pad=7)
ax.tick_params(axis='y', which='major', pad=7)
for axis in ['top','bottom','left','right']:
  ax.spines[axis].set_linewidth(1.5)
ax.xaxis.set_tick_params(width=1.5)
ax.yaxis.set_tick_params(width=1.5)
plt.xlabel(r"Dynamic pressure [kPa]")
plt.ylabel(r'Tip deflection [mm]')
plt.xticks(np.arange(0, 1.8, 0.1))
plt.yticks(np.arange(0, 160, 20))
plt.xlim([0.1,0.8])
plt.ylim([0,120])
plt.legend(frameon=False,bbox_to_anchor=(-0.01,1.02),handlelength=1.2,loc='upper left')
ax.text(0.6, 20, r"AoA = $7^\circ$")

##################  OUTPUT  ##################

plt.savefig('aoa7.png', format='png', dpi=200,bbox_inches=0)






