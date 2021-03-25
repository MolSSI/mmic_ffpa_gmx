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

import mmic_ffpa_gmx
import pytest
import sys
import os


def test_mmic_ffpa_gmx_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "mmic_ffpa_gmx" in sys.modules


def test_mmic_ffpa_sub():
    mfile = os.path.join("mmic_ffpa_gmx", "data", "molecules", "dialanine.gro")
    mol = Molecule.from_file(mfile)
    inputs = AssignInput(
        molecule={"mol": mol}, forcefield={"mol": "amber99"}, engine="gmx"
    )
    computeInput = PrepGmxComponent.compute(inputs)
    computeOutput = ComputeGmxComponent.compute(computeInput)
    outp = PostGmxComponent.compute(computeOutput)
    mol, ff = outp.molecule, outp.forcefield


def test_mmic_ffpa_main():
    mfile = os.path.join("mmic_ffpa_gmx", "data", "molecules", "dialanine.gro")
    mol = Molecule.from_file(mfile)
    inputs = AssignInput(
        molecule={"mol": mol}, forcefield={"mol": "amber99"}, engine="gmx"
    )
    outp = AssignGmxComponent.compute(inputs)
    mol, ff = outp.molecule, outp.forcefield
