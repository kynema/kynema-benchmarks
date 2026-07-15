################  IMPORT  ###################

import numpy  as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from   matplotlib.legend_handler import HandlerErrorbar
from   matplotlib.container import ErrorbarContainer
from   matplotlib import rc

################  FONTS  ###################

rc('font',**{'family':'sans-serif','sans-serif':['Computer Modern Roman']})
mpl.rcParams['text.latex.preamble'] = '\n'.join([
       r'\usepackage{sansmath}', r'\sansmath'  
])
rc('text',usetex=True)
mpl.rcParams.update({'font.size': 16})

##############  READ IN DATA  ##############

data = np.loadtxt('expflut.dat')
aoaexp   = data[:, 0]
qonexp   = data[:, 1]
qoffexp  = data[:, 2]
qonwork  = data[:, 3]
qonworkl = data[:, 4]

data = np.loadtxt('nalustable.dat')
aoanalus   = data[:, 0]
qnalus   = data[:, 1]

data = np.loadtxt('naluunstable.dat')
aoanaluu     = data[:, 0]
qnaluu   = data[:, 1]

data = np.loadtxt('naluflut.dat')
aoanaluf     = data[:, 0]
qnaluf   = data[:, 1]

###############  COLORS  #################

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

############  PLOT SETUP  ###############

mpl.rcParams['hatch.linewidth'] = 0.5
mark = 5.0
fig, ax = plt.subplots(figsize=(6,4), tight_layout=True)
plt.fill_betweenx(aoaexp,qonexp,qoffexp, linewidth=0.0,color=mycolors['grey80'],label="Exp. Flutter Region")
plt.plot(qonexp,aoaexp, '-', color=mycolors['black'],linewidth=1,markersize=mark,label='Exp. Onset')
bar2 = plt.errorbar(qonwork, aoaexp, xerr=qonwork-qonworkl, capsize=4, fmt="o", markersize=0,ecolor = mycolors["green"],color = mycolors["green"], label="WS Onset")
plt.plot(qnalus,aoanalus, '>', color=mycolors['blue'],linewidth=1,markersize=mark,label='EW Stable')
plt.plot(qnaluu,aoanaluu, 'o', color=mycolors['blue'],linewidth=1,markersize=mark,label='EW Unstable')
plt.plot(qnaluf,aoanaluf, '<', color=mycolors['blue'],linewidth=1,markersize=mark,label='EW Flutter')
ax.tick_params(axis='x', which='major', pad=7)
ax.tick_params(axis='y', which='major', pad=7)
for axis in ['top','bottom','left','right']:
  ax.spines[axis].set_linewidth(1.5)
ax.xaxis.set_tick_params(width=1.5)
ax.yaxis.set_tick_params(width=1.5)
plt.xlabel(r"Wind speed [m/s]")
plt.ylabel(r'Angle of attack [deg]')
plt.xticks(np.arange(0, 100, 5))
plt.yticks(np.arange(3, 9, 2))
plt.xlim([30,55])
plt.ylim([2.7,7.3])
plt.legend(prop={'size': 12})
phan, plab = plt.gca().get_legend_handles_labels()
pord = [2,3,4,5,1,0]
plt.legend([phan[ii] for ii in pord],[plab[ii] for ii in pord],frameon=False,bbox_to_anchor=(-0.02,-0.02),handlelength=0.9,loc='lower left',handler_map={type(bar2): HandlerErrorbar(xerr_size=0.45)},handletextpad=0.5)

#############  OUTPUT  #############

plt.savefig('flut.png', format='png', dpi=200,bbox_inches=0)






