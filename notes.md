# Notes and additional cases

More information regarding the benchmark cases is provided
below, including downloading the meshes, contributing to the Kynema
Benchmarks project, and the authors of the benchmark cases.


## Additional published cases

Additional simulations have been performed for verification and validation of this CFD tool.
Following publication of the methods paper on Kynema-SGF, this page will provide those cases
to the public, though these are not intended as benchmark cases in the same manner as the
rest of this repository. For now, while the paper is under review, we provide the input
files only:

- See the [verification cases in github repository](https://github.com/Kynema/kynema-benchmarks/tree/main/kynema-sgf/verification)
- See the [validation cases in the github repository](https://github.com/Kynema/kynema-benchmarks/tree/main/kynema-sgf/validation)


## Downloading meshes

The meshes for many of the benchmark cases (Phase VI rotor, NACA 0021 airfoil, etc), are available from the github release page [https://github.com/Kynema/kynema-benchmarks/releases/tag/mesh_assets](https://github.com/Kynema/kynema-benchmarks/releases/tag/mesh_assets).  For convenience, we have included the download script `downloadmeshes.sh` to automatically download the meshes from the release page, uncompress them, and place them in the correct directories.  Use the script in the following manner:

```bash
$ git clone --recursive git@github.com:Kynema/kynema-benchmarks.git
$ cd kynema-benchmarks
$ ./util/downloadmeshes.sh
```

Note that meshes for only a particular subset of cases can be downloaded using the `--filter` option.  For instance, to download only the NACA 0021 airfoil cases, run the following:  

```bash
$ ./util/downloadmeshes.sh --filter naca0021
```

```{admonition} Note
Additional methods for distributing the mesh files are currently being investigated.  Please check back later regarding the use of DVC or other approaches for version-tracking of large binaries.
```

## Contributing to kynema-benchmarks

```{admonition} Note
For now, contributing to this repository is strictly an internal exercise for the DOE HFM project.	
Public contributions from the research community will be sought and incorporated starting in 2025.
```

## Credits

The following people contributed to the development of the Kynema benchmark cases.

|   |   |
|---|---|
| Shreyas Bidadi       | National Renewable Energy Laboratory |
| Lawrence Cheung      | Sandia National Laboratories |
| Nate deVelder        | Sandia National Laboratories |
| Marc Henry de Frahan | National Renewable Energy Laboratory |
| Wyatt Horne          | Sandia National Laboratories |
| Michael Kuhn         | National Renewable Energy Laboratory |
| Bumseok Lee          | National Renewable Energy Laboratory |
| Neil Matula          | Sandia National Laboratories |
| Prakash Mohan        | National Renewable Energy Laboratory |
| Matteo Polimeno      | National Renewable Energy Laboratory |
| Ganesh Vijayakumar   | National Renewable Energy Laboratory |
| Gopal Yalla          | Sandia National Laboratories |
