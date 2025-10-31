from setuptools import setup, find_packages

setup(
    name="send_mail",
    version="0.1.0",
    description="Small SMTP email sender utility",
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.8",
    include_package_data=True,
)
