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
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Operating System :: POSIX :: Linux
""".strip().split('\n')

setup(name='card-live-dashboard',
      version=__version__,
      description='A dashboard to display antimicrobial resistance data from CARD:Live',
      author='Aaron Petkau',
      author_email='aaron.petkau@gmail.com',
      url='https://github.com/arpcard/card-live-dashboard/',
      license='Apache v2.0',
      classifiers=classifiers,
      install_requires=[
          'ete3>=3.1.2',
          'apscheduler',
          'pandas',
          'geopandas',
          'numpy',
          'dash',
          'upsetplot',
          'flask',
          'dash-bootstrap-components',
          'plotly',
          'shapely',
          'gunicorn',
          'pytest',
          'pyyaml',
          'requests',
          'setproctitle',
          'zipstream-new',
      ],
      packages=find_packages(),
      include_package_data=True,
      scripts=['bin/card-live-dash-dev',
               'bin/card-live-dash-prod',
               'bin/card-live-dash-profiler',
               'bin/card-live-dash-init'],
      )
