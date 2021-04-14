from mmic.components.blueprints import SpecificComponent
from mmelemental.models.util import FileOutput, FileInput
from mmelemental.util.files import random_file
from mmic_ffpa.models import AssignInput
from ..models import ComputeGmxInput
from typing import List, Tuple, Optional


__all__ = ["PrepGmxComponent"]


class PrepGmxComponent(SpecificComponent):
    """ A component for converting AssignInput object to ComputeInput. """

    @classmethod
    def input(cls):
        return AssignInput

    @classmethod
    def output(cls):
        return ComputeGmxInput

    def execute(
        self,
        inputs: AssignInput,
        extra_outfiles: Optional[List[str]] = None,
        extra_commands: Optional[List[str]] = None,
        scratch_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, ComputeGmxInput]:

        if isinstance(inputs, dict):
            inputs = self.input()(**inputs)

        mols = {}
        for name, mol in inputs.molecule.items():
            fname = random_file(suffix=".gro")
            mol.to_file(fname)

            with FileInput(path=fname) as fp:
                mols[name] = fp.read()

        if not all(
            [isinstance(ff_name, str) for ff_name in inputs.forcefield.values()]
        ):
            raise NotImplementedError("Only FFs by names supported for now. Sorry!")

        return True, self.output()(
            molecule=mols,
            forcefield=inputs.forcefield,
            engine=inputs.engine,
            proc_input=inputs,
        )
