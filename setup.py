from setuptools import setup, find_packages
import os

# Usage:
#   [sudo] pip install .
# Note: # These old ways don't work:
#   [sudo] pip install --process-dependency-links .
#   [sudo] python setup.py install
# 2019-Jan process-dependency-links deprecated, see:
# https://pip.pypa.io/en/stable/news/#id4
# It also seems that 'python setup.py install' cannot resolve
# the GitHub URLs (tried several variations).

# Technique below comes from: https://github.com/pypa/pip/issues/4187#issuecomment-452862842

LIBNAME = 'aoulib'

def read_requirements():
    """Parse requirements from requirements.txt."""
    reqs_path = os.path.join('.', 'requirements.txt')
    with open(reqs_path, 'r') as f:
        requirements = [line.rstrip() for line in f]
    return requirements

setup(name=LIBNAME,
      packages=find_packages(),
      install_requires=read_requirements(),
      zip_safe=False)

