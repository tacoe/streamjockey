from setuptools import setup, find_packages
import sys, os

version = '0.1'


setup(name='clubfeud',
      version=version,
      description="The coolest mixing platform Ever",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      py_modules=["spotysuck",],
      package_dir = {'': 'src'},
      entry_points={
          'console_scripts': [
              'spotysuck = spotysuck:main',
              ]},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "argparse"
      	])