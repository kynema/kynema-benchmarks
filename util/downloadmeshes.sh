#!/usr/bin/env bash
#

SCRIPTDIR=$(dirname "$0")
REPODIR=${SCRIPTDIR}/../
REPODIR=$(readlink -f "$REPODIR")
#echo "The script you are running has:"
#echo "basename: [$(basename "$0")]"
#echo "dirname : [$(dirname "$0")]"
#echo "repodir : $REPODIR"
#echo "pwd     : [$(pwd)]"

# Define mesh url and locations 
read -r -d '' meshlist <<'EOF'
https://github.com/Kynema/kynema-benchmarks/releases/download/mesh_assets/du00w212_F.exo.tar.gz		nalu-wind/2D_airfoil_Transition/DU00-W-212/mesh/
https://github.com/Kynema/kynema-benchmarks/releases/download/mesh_assets/naca0021_aoa_30.exo.tar.gz		nalu-wind/3D_airfoil_IDDES/NACA-0021/aoa_30/input_files
https://github.com/Kynema/kynema-benchmarks/releases/download/mesh_assets/naca0021_aoa_45.exo.tar.gz		nalu-wind/3D_airfoil_IDDES/NACA-0021/aoa_45/input_files
https://github.com/Kynema/kynema-benchmarks/releases/download/mesh_assets/naca0021_aoa_60.exo.tar.gz		nalu-wind/3D_airfoil_IDDES/NACA-0021/aoa_60/input_files
https://github.com/Kynema/kynema-benchmarks/releases/download/mesh_assets/naca0021_aoa_90.exo.tar.gz		nalu-wind/3D_airfoil_IDDES/NACA-0021/aoa_90/input_files
https://github.com/Kynema/kynema-benchmarks/releases/download/mesh_assets/nlf0416_F.exo.tar.gz		nalu-wind/2D_airfoil_Transition/NLF1-0416/mesh/
https://github.com/Kynema/kynema-benchmarks/releases/download/mesh_assets/nrelvi_nearbody_mesh.exo.tar.gz	exawind/NREL_Phase_VI_Turbine/mesh/
https://github.com/Kynema/kynema-benchmarks/releases/download/mesh_assets/pazyslip.exo.tar.gz			exawind/Pazy_Wing/mesh
https://github.com/Kynema/kynema-benchmarks/releases/download/mesh_assets/split_tower_and_blades.exo.tar.gz	exawind/NREL_5MW_Turbine/flexible/mesh
EOF

FILTER=""

function dlmesh(){
    url=$1
    dest=$2
    basefile=$(basename "$url")
    filename=`echo "$basefile" | sed -e 's/.gz//g' -e 's/.tar//g' `
    echo "Downloading $url"
    wget "$url"
    tar xvzf $basefile
    rm $basefile
    mv -v $filename ${REPODIR}/${dest}
}

# Help for this script
function help() {
cat <<EOF
Download all meshes for benchmark problems from the repository https://github.com/Kynema/kynema-benchmarks/releases/tag/mesh_assets

Usage: 
  $1 [OPTIONS]

Arguments
  None

Options:
  -f|--filter FILTERSTRING  : Only download and unpack meshes which have FILTERSTRING in the URL
  -r|--repodir REPODIR      : Set the benchmark repository directory to REPODIR (current default: $REPODIR)
  -h|--help                 : This help file

EOF
}

# Parse the arguments and options
# --------------------------
# For arg parsing details/example, see https://medium.com/@Drew_Stokes/bash-argument-parsing-54f3b81a6a8f
PARAMS=""
while (( "$#" )); do
    case "$1" in
	-h|--help)
	    help $0
	    exit
	    ;;
    	-f|--filter)
	    FILTER=$2
	    shift 2
	    break
	    ;;
    	-r|--repodir)
	    REPODIR=$2
	    shift 2
	    break
	    ;;
	--) # end argument parsing
	    shift
	    break
	    ;;
	-*|--*=) # unsupported flags
	    echo "Error: Unsupported flag $1" >&2
	    exit 1
	    ;;
	*) # preserve positional arguments
	    PARAMS="$PARAMS $1"
	    shift
	    ;;
    esac
done # set positional arguments in their proper place
eval set -- "$PARAMS"

# Run through each mesh and download
while IFS= read -r line; do
    #echo "Processing line: $line"
    url=`echo "$line" | awk '{print $1}'`
    loc=`echo "$line" | awk '{print $2}'`
    if [[ "$url" == *"$FILTER"* ]]; then
	echo "Working on $url"
	dlmesh $url $loc
    else
      echo "Skipping $url"
    fi
done <<< "$meshlist"
