"""
Setup script for the send_mail package.
This module defines setuptools configuration used to package and distribute
the 'send_mail' utility — a small SMTP email sender.
Metadata included:
- name: "send_mail"
- version: "0.1.0"
- description: "Small SMTP email sender utility"
- python_requires: ">=3.8"
- packages: discovered via setuptools.find_packages(exclude=("tests",))
- include_package_data: True (expects MANIFEST.in or package_data to include non-code files)
Common tasks:
- Install locally: pip install .
- Install for development: pip install -e .
- Build distributions: python -m build  (requires the 'build' package)
Notes:
- If migrating to PEP 517/518, consider moving metadata to pyproject.toml.
- Add long_description, license, author, and classifiers before publishing to PyPI.
"""

from setuptools import setup, find_packages

setup(
    name="send_mail",
    version="0.1.0",
    description="Small SMTP email sender utility",
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.8",
    include_package_data=True,
)
