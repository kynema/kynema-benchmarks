# Case selection
aoa=93
windspeed=30
# Simulation parameters, expert users only
dtshort=0.00002
dtlong=0.00006
density=1.225
visc=0.000018
tkein=1.0
sdrin=250.0
amrnx=128
cfdplotinterval=1000
cfdcheckpointinterval=10000


source loadmod.sh

apargs="aoa=$aoa windspeed=$windspeed dtlong=$dtlong dtshort=$dtshort density=$density tkein=$tkein sdrin=$sdrin amrnx=$amrnx cfdplotinterval=$cfdplotinterval cfdcheckpointinterval=$cfdcheckpointinterval visc=$visc "
myloc=$(pwd)
dirname="a${aoa}v${windspeed}"
rm -rf $dirname
cp -Rp base $dirname
ls
cd $dirname

pwd

aprepro -e -q $apargs template/run                          run
aprepro -e -q $apargs template/amr.inp                      amr.inp
aprepro -e -q $apargs template/pazy.fst                     pazy.fst
aprepro -e -q $apargs template/nalu.yaml                    nalu.yaml
aprepro -e -q $apargs template/pazy_InflowWind.dat          pazy_InflowWind.dat
aprepro -e -q $apargs template/pazy_ElastoDyn_BDoutputs.dat pazy_ElastoDyn_BDoutputs.dat
aprepro -e -q $apargs template/inp.yaml                     inp.yaml

cp static/* .



