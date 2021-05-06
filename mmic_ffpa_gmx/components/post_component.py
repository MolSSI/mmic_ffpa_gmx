# Import components
from mmic.components.blueprints import GenericComponent

# Import models
from mmelemental.models.util.output import FileOutput
from mmelemental.models import Molecule, ForceField
from mmelemental.util.files import random_file
from mmic_ffpa.models import AssignOutput
from ..models import ComputeGmxOutput

import cmselemental
from typing import Dict, Any, List, Tuple, Optional


__all__ = ["PostGmxComponent"]


class PostGmxComponent(GenericComponent):
    @classmethod
    def input(cls):
        return ComputeGmxOutput

    @classmethod
    def output(cls):
        return AssignOutput

    def execute(
        self,
        inputs: Dict[str, Any],
        extra_outfiles: Optional[List[str]] = None,
        extra_commands: Optional[List[str]] = None,
        scratch_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, Dict[str, Any]]:

        if isinstance(inputs, dict):
            inputs = self.input()(**inputs)

        ff, mol = inputs.forcefield, inputs.molecule

        mol_name = random_file(suffix=".gro")
        ff_name = random_file(suffix=".top")

        with FileOutput(path=mol_name, clean=True) as fp:
            fp.write(mol)
            with FileOutput(path=ff_name, clean=True) as fp:
                fp.write(ff)
                mol = Molecule.from_file(mol_name, ff_name)
                ff = ForceField.from_file(ff_name)

        mol_name = list(inputs.proc_input.molecule.keys())
        if len(mol_name) > 1:
            raise NotImplementedError("Only a single molecule supported for now")
        mol_name = mol_name.pop()
        output = self.output()(
            proc_input=inputs.proc_input,
            molecule={mol_name: mol},
            forcefield={mol_name: ff},
            success=True,
            provenance=cmselemental.extras.provenance_stamp(
                routine=__name__, creator="mmic_ffpa_gmx"
            ),
        )
        return output.success, output
