from mmelemental.models import ProcOutput
from mmic_ffpa.models import AssignInput
from pydantic import Field
from typing import Optional

__all__ = ["ComputeGmxOutput"]


class ComputeGmxOutput(ProcOutput):
    proc_input: AssignInput = Field(
        None, description="Procedure input schema."
    )  # must become required field, eventually
    forcefield: str = Field(..., description="Force field params file string object.")
    molecule: str = Field(..., description="Molecule file string object.")
