mmic_ffpa_gmx
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/MolSSI/mmic_ffpa_gmx/workflows/CI/badge.svg)](https://github.com/MolSSI/mmic_ffpa_gmx/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/MolSSI/mmic_ffpa_gmx/branch/main/graph/badge.svg)](https://codecov.io/gh/MolSSI/mmic_ffpa_gmx/branch/main)


MMIC for force field parameter association with GMX

# Snippet
```python

# Import MMIC schema for FFPA
from mmic_ffpa.models import AssignInput

# Import MMSchema Molecule
from mmelemental.models import Molecule

# Import FFPA component with GMX
from mmic_ffpa_gmx.components import AssignGmxComponent

# Prepare input model
mol = Molecule.from_file(path_to_file)
inputs = AssignInput(
    molecule={"mol": mol}, forcefield={"mol": "amber99"}, engine="gmx"
)

# Run FF parameter assignment
outp = AssignGmxComponent.compute(inputs)

# Extract molecule, forcefield (MMSchema) objects
mol, ff = outp.molecule, outp.forcefield
```

### Copyright

Copyright (c) 2021, Andrew Abi-Mansour


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.5.
