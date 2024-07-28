#!/usr/bin/env python
#
from io import open  # required for Python 2
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


PROJECT_NAME = "RESTinstance"
PACKAGE_NAME = "REST"

CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)
Operating System :: OS Independent
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Framework :: Robot Framework
Framework :: Robot Framework :: Library
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Testing
""".strip().splitlines()

CURDIR = dirname(abspath(__file__))
with open(
    join(CURDIR, "src", PACKAGE_NAME, "version.py"), encoding="utf-8"
) as f:
    for line in f:
        if line.startswith("__version__"):
            VERSION = line.strip().split("=")[1].strip(" '\"")
            break
    else:
        VERSION = "0.0.1"
with open(join(CURDIR, "README.md"), encoding="utf-8") as f:
    README = f.read()
with open(join(CURDIR, "requirements.txt"), encoding="utf-8") as f:
    REQUIREMENTS = f.read()

setup(
    name=PROJECT_NAME,
    version=VERSION,
    author="Anssi Syrjäsalo",
    author_email="opensource@syrjasalo.com",
    url="https://github.com/asyrjasalo/RESTinstance",
    download_url="https://pypi.org/pypi/RESTinstance",
    license="LGPLv3",
    description="Robot Framework library for RESTful JSON APIs",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="robotframework library http json api",
    platforms="any",
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    package_dir={"": "src"},
    packages=find_packages("src"),
    zip_safe=False,
)
