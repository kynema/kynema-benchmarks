NREL 5MW Turbine
===================


Two variants of this simulation are provided: one with rigid blades and one with flexible blades modeled using OpenFAST.  Note that both cases use the `convectively unstable ABL <../amr-wind/atmospheric_boundary_layer/convective_abl_nrel5mw/README.html>`__ precursor.


#. `Flexible NREL 5MW turbine <nrel5mw/fsi/README.html>`__: Blade-resolved simulation of the NREL5MW reference turbine, coupled to the OpenFAST BeamDyn aerolastic solver and ROSCO open-source turbine controller.

   * `Simulation setup <nrel5mw/fsi/README.html#simulation-setup>`__
   * `Freestream conditions <nrel5mw/fsi/README.html#freestream-conditions>`__
   * `CFD Mesh <nrel5mw/fsi/README.html#cfd-mesh>`__
   * `Results <nrel5mw/fsi/README.html#results>`__


#. Rigid NREL 5MW turbine: A blade-resolved NREL 5MW with rigid blades, fixed pitch and rotor speed.  This case will be posted in near future.

`View these cases in the github repository
<https://github.com/Exawind/exawind-benchmarks/tree/main/exawind/NREL_5MW_Turbine>`__
