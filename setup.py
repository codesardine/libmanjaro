from setuptools import setup, find_packages

setup(
    name='manjaro-sdk',
    version='0.1.1',
    packages=["Manjaro.SDK"],
    package_dir={"": "src"},
    url='https://github.com/Manjaro-WebDad/libmanjaro.git',
    license='GPL',
    author='Vitor Lopes',
    description='Manjaro library'
)
