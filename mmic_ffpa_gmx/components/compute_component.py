# Import models
from mmelemental.models.util import FileOutput
from mmelemental.util.files import random_file
from ..models import ComputeGmxInput, ComputeGmxOutput

# Import components
from mmic_cmd.components import CmdComponent
from mmic.components.blueprints import GenericComponent

# General utils
import cmselemental
from typing import Any, Dict, List, Tuple, Optional
import os
import shutil

_supported_engines = {"gmx": "pdb2gmx", "gmx_mpi": "pdb2gmx", "pdb2gmx": ...}
_supported_solvents = ("spc", "tip3p", "tip4p")

__all__ = ["ComputeGmxComponent"]


class ComputeGmxComponent(GenericComponent):
    """A component for generating a pramaterized molecule."""

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

        # For now only a single molecule supported ~ hackish
        # TODO: improve this
        ff_name, ff = list(ffs.items()).pop()
        mol_name, mol = list(mols.items()).pop()

        assert ff_name == mol_name, "Each molecule must have an assigned FF!"

        input_model = {"mol": mol, "ff": ff, "proc_input": inputs.proc_input}
        clean_files, cmd_input = self.build_input(input_model)

        print("cmd_input = ", cmd_input["command"])
        rvalue = CmdComponent.compute(cmd_input)

        self.cleanup(clean_files)

        return True, self.parse_output(
            rvalue.dict(),
            inputs.proc_input,
        )

    @staticmethod
    def cleanup(remove: List[str]):
        for item in remove:
            if os.path.isdir(item):
                shutil.rmtree(item)
            elif os.path.isfile(item):
                os.remove(item)

    def build_input(
        self,
        inputs: Dict[str, Any],
        config: Optional["TaskConfig"] = None,
        template: Optional[str] = None,
    ) -> Dict[str, Any]:

        assert (
            inputs["proc_input"].engine in _supported_engines
        ), "Engine must be gmx (Gromacs)!"

        fname = random_file(suffix=".gro")
        clean_files = []

        with FileOutput(path=fname) as fp:
            fp.write(inputs["mol"])
            # input_model["molecule"][mol_name] = fp.abs_path
            mol_fpath = fp.abs_path
            # Assume FF is supplied by name only? i.e. no FF object to create?
            clean_files.append(mol_fpath)

        env = os.environ.copy()

        if config:
            env["MKL_NUM_THREADS"] = str(config.ncores)
            env["OMP_NUM_THREADS"] = str(config.ncores)

        scratch_directory = config.scratch_directory if config else None
        gro_file = random_file(suffix=".gro")
        top_file = random_file(suffix=".top")
        itp_file = random_file(suffix=".itp")

        for eng, subeng in _supported_engines.items():
            if cmselemental.util.importing.which(eng):
                cmd = [eng, subeng] if subeng is not Ellipsis else [eng]
                break

        if inputs["ff"] in _supported_solvents:
            cmd.extend(
                [
                    "-f",
                    mol_fpath,
                    "-ff",
                    "amber99",  # dummy FF because PDB2GMX requires it
                    "-water",
                    inputs["ff"],
                    "-o",
                    gro_file,
                    "-p",
                    top_file,
                ]
            )
            outfiles = [
                gro_file,
                top_file,
            ]  # ext itp file is NOT generated for library-def solvents
        else:
            cmd.extend(
                [
                    "-f",
                    mol_fpath,
                    "-ff",
                    inputs["ff"],
                    "-water",
                    "none",
                    "-o",
                    gro_file,
                    "-p",
                    top_file,
                    "-i",
                    itp_file,
                ]
            )
            outfiles = [gro_file, top_file, itp_file]

        # Additional args to pdb2gmx e.g. -ignh, -dist float, etc. parsed here
        if inputs["proc_input"].keywords:
            for key, val in inputs["proc_input"].keywords.items():
                if val is not None and val is not Ellipsis:
                    cmd.extend([key, val])
                else:
                    cmd.extend([key])

        return clean_files, {
            "command": cmd,
            "infiles": [mol_fpath],
            "outfiles": outfiles,
            "scratch_directory": scratch_directory,
            "environment": env,
        }

    def parse_output(
        self, output: Dict[str, str], inputs: Dict[str, Any]
    ) -> ComputeGmxOutput:
        stdout = output["stdout"]
        stderr = output["stderr"]
        outfiles = output["outfiles"]

        # I think order in util.execute matters. For a more rigorous imp, we need
        # to pass the conf, top, etc. filenames
        if len(outfiles) == 3:
            conf, top, _ = outfiles.values()  # posre = outfiles["posre.itp"]
        elif len(outfiles) == 2:
            conf, top = outfiles.values()
        else:
            raise ValueError(
                "The number of output files should be either 2 (.gro, .top) or 3 (.gro, .top, .itp)"
            )

        return self.output()(
            proc_input=inputs,
            molecule=conf,
            forcefield=top,
            stdout=stdout,
            stderr=stderr,
        )
