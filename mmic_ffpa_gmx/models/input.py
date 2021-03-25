from mmelemental.models import ProcInput
from mmic_ffpa.models import AssignInput
from pydantic import Field
from typing import Optional, Dict, Union

__all__ = ["ComputeGmxInput"]


class ComputeGmxInput(ProcInput):
    proc_input: AssignInput = Field(..., description="Procedure input schema.")
    forcefield: Dict[str, str] = Field(
        ..., description="Force field file name e.g. charmm36."
    )
    molecule: Dict[str, str] = Field(..., description="Molecule file contents.")
