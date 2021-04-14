"""
Unit and regression test for the mmic_ffpa_gmx package.
"""

# Import package, test suite, and other packages as needed
from mmic_ffpa_gmx.components import (
    PrepGmxComponent,
    ComputeGmxComponent,
    PostGmxComponent,
    AssignGmxComponent,
)
from mmic_ffpa.models import AssignInput
from mmelemental.models import Molecule
import mm_data

import mmic_ffpa_gmx
import pytest
import sys
import os


def test_mmic_ffpa_gmx_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "mmic_ffpa_gmx" in sys.modules


def test_mmic_ffpa_sub():
    mfile = mm_data.mols["dialanine.pdb"]
    mol = Molecule.from_file(mfile)
    inputs = AssignInput(
        molecule={"mol": mol}, forcefield={"mol": "amber99"}, engine="gmx"
    )
    computeInput = PrepGmxComponent.compute(inputs)
    computeOutput = ComputeGmxComponent.compute(computeInput)
    outp = PostGmxComponent.compute(computeOutput)
    mol, ff = outp.molecule, outp.forcefield

@pytest.mark.parametrize("mol_file", ["alanine.gro", "1dzl_fixed.gro"])
def test_mmic_ffpa_main(mol_file):
    mfile = mm_data.mols[mol_file]
    mol = Molecule.from_file(mfile)
    inputs = AssignInput(
        molecule={"mol": mol},
        forcefield={"mol": "amber99"},
        engine="gmx",
        kwargs={"-ignh": ""},
    )
    outp = AssignGmxComponent.compute(inputs)
    mol, ff = outp.molecule, outp.forcefield
