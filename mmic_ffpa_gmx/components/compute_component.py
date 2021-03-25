# Import models
from mmelemental.models.util.output import FileOutput
from ..models import ComputeGmxInput, ComputeGmxOutput

# Import components
from mmic_util.components import CmdComponent
from mmic.components.blueprints import SpecificComponent


from typing import Any, Dict, List, Tuple, Optional
import os


_supported_solvents = ("spc", "tip3p", "tip4p")

__all__ = ["ComputeGmxComponent"]


class ComputeGmxComponent(SpecificComponent):
    """ A component for generating a pramaterized molecule. """

    @classmethod
    def input(cls):
        return ComputeGmxInput

    @classmethod
    def output(cls):
        return ComputeGmxOutput

    def execute(
        self,
        inputs: Dict[str, str],
        extra_outfiles: Optional[List[str]] = None,
        extra_commands: Optional[List[str]] = None,
        scratch_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Writes Molecule as a pdb file.
        """

        if isinstance(inputs, dict):
            inputs = self.input()(**inputs)

        ffs, mols = inputs.forcefield, inputs.molecule

        assert len(ffs) == 1, "Only single FF supported for now."

        if len(mols) > 1:
            raise NotImplementedError("Only a single molecule supported for now.")

        ff_name, ff = list(ffs.items()).pop()
        mol_name, mol = list(mols.items()).pop()

        assert ff_name == mol_name, "Each molecule must have an assigned FF!"

        input_model = {"mol": mol, "ff": ff, "engine": inputs.proc_input.engine}
        cmd_input = self.build_input(input_model)

        rvalue = CmdComponent.compute(cmd_input)
        return True, self.parse_output(rvalue.dict(), inputs.proc_input)

    def build_input(
        self,
        inputs: Dict[str, Any],
        config: Optional["TaskConfig"] = None,
        template: Optional[str] = None,
    ) -> Dict[str, Any]:

        assert inputs["engine"] == "gmx", "Engine must be gmx (Gromacs)!"

        fname = FileOutput.rand_name() + ".pdb"
        clean_files = []

        with FileOutput(path=fname) as fp:
            fp.write(inputs["mol"])
            # input_model["molecule"][mol_name] = fp.abs_path
            mol_fpath = fp.abs_path
            clean_files.append(fp)
            # Assume FF is supplied by name only? i.e. no FF object to create?

        # input_model = self.build_input(input_model)

        env = os.environ.copy()

        if config:
            env["MKL_NUM_THREADS"] = str(config.ncores)
            env["OMP_NUM_THREADS"] = str(config.ncores)

        scratch_directory = config.scratch_directory if config else None

        return {
            "command": [
                inputs["engine"],
                "pdb2gmx",
                "-f",
                mol_fpath,
                "-ff",
                inputs["ff"],
                "-water",
                "none",
            ],
            "infiles": [mol_fpath],
            "outfiles": ["conf.gro", "topol.top", "posre.itp"],
            "scratch_directory": scratch_directory,
            "environment": env,
        }

    def parse_output(
        self, output: Dict[str, str], inputs: Dict[str, Any]
    ) -> ComputeGmxOutput:
        stdout = output["stdout"]
        stderr = output["stderr"]
        outfiles = output["outfiles"]

        if stderr:
            # Supress stderro for now because
            # stupid GMX prints pdb2gmx output to stderr
            # See https://redmine.gromacs.org/issues/2211
            if output.get("Debug"):
                print("Error from {engine}:".format(**inputs))
                print("=========================")
                raise RuntimeError(stderr)

        conf = outfiles["conf.gro"]
        top = outfiles["topol.top"]
        # posre = outfiles['posre.itp']

        return self.output()(proc_input=inputs, molecule=conf, forcefield=top)
