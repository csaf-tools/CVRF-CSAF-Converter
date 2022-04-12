# pylint: disable=missing-module-docstring
from .cvrf2csaf import main
# pylint: disable=import-error
from ._version import version

__version__ = version

__all__ = ['main']
