#!/usr/bin/env python2
from __future__ import print_function
from setuptools import setup
from sys import version_info

if version_info < (3, 3):
    requirements = ["pathlib"]
else:
    requirements = []

setup(name="mpd_pydb",
      author="Wieland Hoffmann",
      author_email="themineo@gmail.com",
      packages=["mpd_pydb"],
      package_dir={"mpd_pydb": "mpd_pydb"},
      download_url=["https://github.com/mineo/mpd_pydb/tarball/master"],
      url=["http://github.com/mineo/mpd_pydb"],
      license="MIT",
      classifiers=["Development Status :: 4 - Beta",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.4"],
      description="Module for reading an MPD database",
      long_description=open("README.rst").read(),
      setup_requires=["setuptools_scm"],
      use_scm_version={"write_to": "mpd_pydb/version.py"},
      install_requires=requirements,
      extras_require={
          'docs': ['sphinx']
      }
      )
