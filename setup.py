""" Pypi setup for cheap_pie """
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

setup(
    name='cheap_pie_ral_emu',
    version='0.1.2',
    license='Apache 2.0',
    author="Alon Meirson",
    author_email='ameirson@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    description="A python tool for silicon validation.",
    url='https://github.com/ameirson/cheap_pie_ral_emu/',
    keywords='python silicon validation',
    install_requires=[
          'untangle',
          'hickle',
          # parsers
          'cmsis-svd',
          'ipyxact',
          'python-docx',
          'pyverilator',
          'peakrdl-ipxact',
          'peakrdl-uvm',
          'peakrdl-verilog',
          # transport layers
          #'pylink-square',
          #'pyocd',
          #'esptool',
          #'packaging' # for verilator version check
      ],
)

project_urls={
    "Source": "https://github.com/ameirson/cheap_pie_ral_emu",
    "Tracker": "https://github.com/ameirson/cheap_pie_ral_emu/issues"
}
