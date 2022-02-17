from setuptools import setup
import subprocess


def get_version():
    return subprocess.check_output(["git", "describe", "--always"]).strip().decode()

# The rest of the install configuration lies in setup.cfg
setup(
    version=get_version()
)
