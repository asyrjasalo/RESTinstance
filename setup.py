#!/usr/bin/env python
# -*- coding: utf-8 -*-


from io import open  # required for Python 2
from os.path import abspath, dirname, join
from setuptools import find_packages, setup

classifiers = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: POSIX
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Topic :: Software Development :: Testing
Framework :: Robot Framework
Framework :: Robot Framework :: Library
""".strip().splitlines()


curdir = dirname(abspath(__file__))
with open(join(curdir, "src", "REST", "version.py"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.strip().split("=")[1].strip(" '\"")
            break
    else:
        version = "0.0.1"
with open(join(curdir, "README.rst"), encoding="utf-8") as f:
    readme = f.read()
with open(join(curdir, "requirements.txt"), encoding="utf-8") as f:
    requirements = f.read()

setup(
    name="RESTinstance",
    version=version,
    description="Robot Framework test library for (RESTful) JSON APIs",
    long_description=readme,
    author="Anssi Syrjäsalo",
    author_email="anssi.syrjasalo@gmail.com",
    url="https://github.com/asyrjasalo/RESTinstance",
    license="Apache License 2.0",
    keywords="robotframework library http json api",
    classifiers=classifiers,
    install_requires=requirements,
    zip_safe=False,
    package_dir={"": "src"},
    packages=find_packages("src"),
)
