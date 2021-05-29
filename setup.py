#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
from codecs import open
from os import path, system
from re import compile as re_compile
try:
    from urllib.request import urlretrieve
except:
    from urllib import urlretrieve

# For convenience.
if sys.argv[-1] == "publish":
    system("python setup.py sdist upload")
    sys.exit()

def read(filename):
    kwds = {"encoding": "utf-8"} if sys.version_info[0] >= 3 else {}
    with open(filename, **kwds) as fp:
        contents = fp.read()
    return contents

# Get the version information.
here = path.abspath(path.dirname(__file__))
vre = re_compile("__version__ = \"(.*?)\"")
version = vre.findall(read(path.join(here, "smhr_session", "__init__.py")))[0]

# External data.
if "--without-models" not in sys.argv:
    data_paths = [
        # Model photospheres:
        # Castelli & Kurucz (2004)
        ("https://zenodo.org/record/14964/files/castelli-kurucz-2004.pkl",
            "smhr_session/photospheres/castelli-kurucz-2004.pkl"),
        # MARCS (2008)
        ("https://zenodo.org/record/14964/files/marcs-2011-standard.pkl",
            "smhr_session/photospheres/marcs-2011-standard.pkl"),
        # Stagger-Grid <3D> (2013)
        ("https://zenodo.org/record/15077/files/stagger-2013-optical.pkl",
            "smhr_session/photospheres/stagger-2013-optical.pkl"),
        ("https://zenodo.org/record/15077/files/stagger-2013-mass-density.pkl",
            "smhr_session/photospheres/stagger-2013-mass-density.pkl"),
        ("https://zenodo.org/record/15077/files/stagger-2013-rosseland.pkl",
            "smhr_session/photospheres/stagger-2013-rosseland.pkl"),
        ("https://zenodo.org/record/15077/files/stagger-2013-height.pkl",
            "smhr_session/photospheres/stagger-2013-height.pkl"),
    ]
    for url, filename in data_paths:
        if path.exists(filename):
            print("Skipping {0} because file already exists".format(filename))
            continue
        print("Downloading {0} to {1}".format(url, filename))
        try:
            urlretrieve(url, filename)
        except IOError:
            raise("Error downloading file {} -- consider installing with flag "
                "--without-models".format(url))
else:
    sys.argv.remove("--without-models")

setup(
    name="smhr-session",
    version=version,
    author="Alex Ji, Andy Casey",
    description="Refactoring SMHR session",
    long_description=read(path.join(here, "README.md")),
    url="https://github.com/alexji/smhr-session",
    license="MIT",
    packages=find_packages(exclude=["documents", "tests"]),
    install_requires=[
        "numpy","astropy","scipy",
        "six","pyyaml"
        ],
    extras_require={
        #"test": ["coverage"]
    },
    package_data={
        "": ["LICENSE"]
    },
    include_package_data=True,
    data_files=None,
    entry_points=None
)
