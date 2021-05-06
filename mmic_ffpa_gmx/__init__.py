"""
mmic_ffpa_gmx
MMIC for force field parameter association with GMX
"""

# Add imports here
from . import models
from . import components

# Handle versioneer
from ._version import get_versions

versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions

# Main component for running FFPA
from .components.ffpa_component import AssignGmxComponent as RunComponent
