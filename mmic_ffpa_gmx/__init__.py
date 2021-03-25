"""
mmic_ffpa_gmx
MMIC for force field parameter association with GMX
"""

# Add imports here
from .mmic_ffpa_gmx import *

# Handle versioneer
from ._version import get_versions

versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions
