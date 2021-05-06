# Import schema models for FF assignment
from mmic_ffpa.models import AssignInput, AssignOutput

# Import subcomponents for FF assignment with GMX
from .prep_component import PrepGmxComponent
from .compute_component import ComputeGmxComponent
from .post_component import PostGmxComponent

from mmic.components.blueprints import TacticComponent
from typing import Optional, Tuple, List, Any

__all__ = ["AssignGmxComponent"]


class AssignGmxComponent(TacticComponent):
    """Main entry component for running FF assignment."""

    @classmethod
    def input(cls):
        return AssignInput

    @classmethod
    def output(cls):
        return AssignOutput

    def execute(
        self,
        inputs: AssignInput,
        extra_outfiles: Optional[List[str]] = None,
        extra_commands: Optional[List[str]] = None,
        scratch_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, AssignOutput]:

        computeInput = PrepGmxComponent.compute(inputs)
        computeOutput = ComputeGmxComponent.compute(computeInput)
        assignOutput = PostGmxComponent.compute(computeOutput)
        return True, assignOutput

    def get_version(cls) -> str:
        """Finds program, extracts version, returns normalized version string.
        Returns
        -------
        str
            Return a valid, safe python version string.
        """
        raise NotImplementedError

    @classmethod
    def strategy_comp(cls) -> Any:
        """Returns the strategy component this (tactic) component belongs to.
        Returns
        -------
        Any
        """
        return set(mmic_ffpa.components.AssignComponent)
