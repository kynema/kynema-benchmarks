import matplotlib.pyplot as plt
import numpy as np

icase = 0
whichblade = 1

if (icase == 0):
  # X-deflection (streamwise)
  idata = 8
elif (icase == 1):
  # Y-deflection (flapwise)
  idata = 9
else:
  # Z-deflection (spanwise)
  idata = 10

if whichblade == 1:
  offset = 0
elif whichblade == 2:
  offset = 3
elif whichblade == 3:
  offset = 6
else:
  print("failed in whichblade")
  exit()
  
idata = idata + offset
data  = np.loadtxt('data.dat')
tval  = data[:, 0]
sval  = -data[:, idata]
n     = sval.shape[0]


dt = (tval[n-1]-tval[0])/n
for i in range(1,n):
  tval[i] = tval[i-1]+dt


# To avoid problems with recently written lines
n = n - 2

tend = tval[n]
T = 0.22
tstart = tend - 2*T
if (tstart < tval[0]):
  tstart = tval[0]

myav = 0.0
counter = 0
for i in range(0,n):
  if (tval[i] > tstart):
    myav = myav + sval[i]
    counter = counter + 1
myav = myav / counter
print("tstart  : ",tval[0])
print("tend    : ",tval[n-1])
print("periods : ",(tval[n-1]-tval[0])/T)
print("Average : ",myav)
print("Curve   : ",sval[n-1]-2*sval[n-2]+sval[n-3])
svalc = np.zeros([len(tval)]) + myav



plt.plot(tval,sval)
plt.plot(tval,svalc)
plt.show()

  

