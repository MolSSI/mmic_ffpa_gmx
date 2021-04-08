from mmelemental.models import ProcOutput
from mmic_ffpa.models import AssignInput
from pydantic import Field

__all__ = ["ComputeGmxOutput"]


class ComputeGmxOutput(ProcOutput):
    proc_input: AssignInput = Field(
        ..., description="Procedure input schema."
    )
    forcefield: str = Field(..., description="Force field params file string object.")
    molecule: str = Field(..., description="Molecule file string object.")
