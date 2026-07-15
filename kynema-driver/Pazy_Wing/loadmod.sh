manloc=/path/to/your/build/exawind-manager
envnam=pazy


echo
mydir=${PWD}
echo "Starting here:"
echo $mydir
echo


echo "Going here to activate shortcut:"
echo $manloc
cd $manloc
source shortcut.sh
echo "Done"
echo

echo "Loading this environment:"
echo $manloc/environments/$envnam
quick-activate $manloc/environments/$envnam
echo "Done"
echo

echo "Loading amrwind and exawind"
spack load amr-wind
spack load nalu-wind
spack load exawind
echo "Done"
echo

echo "Going back to this dir:"
echo $mydir
cd $mydir
echo "Done"
echo

echo "Creating ranks_per_node function"
umask 007
function ranks_per_node(){
  threads=$(lscpu | grep -m 1 "CPU(s):" | awk '{print $2}')
  tpcore=$( lscpu | grep -m 1 "Thread(s) per core:" | awk '{print $4}')
  echo $(($threads/$tpcore))
}
echo "Done"
