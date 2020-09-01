from distutils.core import setup

from setuptools import find_packages

from card_live_dashboard import __version__

classifiers = """
Development Status :: 4 - Beta
Environment :: Web Environment
License :: OSI Approved :: Apache Software License
Intended Audience :: Science/Research
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Bio-Informatics
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Operating System :: POSIX :: Linux
""".strip().split('\n')

setup(name='card-live-dashboard',
      version=__version__,
      description='A dashboard to display data from CARD:Live',
      author='Aaron Petkau',
      author_email='aaron.petkau@gmail.com',
      url='https://devcard.mcmaster.ca:8888/apetkau/card-live-dashboard',
      license='Apache v2.0',
      classifiers=classifiers,
      install_requires=[
          'ete3>=3.1.2',
          'apscheduler',
          'pandas',
          'geopandas',
          'numpy',
          'dash',
          'flask',
          'dash-bootstrap-components',
          'plotly',
          'shapely',
          'gunicorn',
          'pytest',
      ],
      packages=find_packages(),
      include_package_data=True,
      scripts=['bin/cardlive-dash-dev',
               'bin/cardlive-dash-prod',
               'bin/cardlive-dash-profiler',
               'bin/cardlive-dash-init'],
)
