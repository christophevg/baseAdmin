import os
import re
import setuptools

NAME             = "baseadmin"
AUTHOR           = "Christophe VG"
AUTHOR_EMAIL     = "contact@christophe.vg"
DESCRIPTION      = "A framework for building distributed IoT applications."
LICENSE          = "MIT"
KEYWORDS         = "A Python base for administrative tools for distributed (IoT) applications."
URL              = "https://github.com/christophevg/" + NAME
README           = ".github/README.md"
CLASSIFIERS      = [
  "Environment :: Console",
  "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Intended Audience :: System Administrators",
  "Topic :: Software Development",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python",
  "Programming Language :: Python :: 2",
  "Programming Language :: Python :: 2.6",
  "Programming Language :: Python :: 2.7",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.3",
  "Programming Language :: Python :: 3.4",
  "Programming Language :: Python :: 3.5",
  "Programming Language :: Python :: 3.6",
]
INSTALL_REQUIRES = [
  "flask",
  "flask_restful",
  "pymongo",
  "py-bcrypt",
  "paho-mqtt"
]
ENTRY_POINTS     = {}
SCRIPTS = []

HERE = os.path.dirname(__file__)

def read(file):
  with open(os.path.join(HERE, file), "r") as fh:
    return fh.read()

VERSION = re.search(
  r'^__version__ = [\'"]([^\'"]*)[\'"]',
  read(NAME.replace("-", "_") + "/__init__.py")
).group(1)

LONG_DESCRIPTION = read(README)

if __name__ == "__main__":
  setuptools.setup(name=NAME,
        version=VERSION,
        packages=setuptools.find_packages(),
        author=AUTHOR,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        license=LICENSE,
        keywords=KEYWORDS,
        url=URL,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        entry_points=ENTRY_POINTS,
        scripts=SCRIPTS,
        include_package_data=True)
