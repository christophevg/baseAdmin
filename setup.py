import os
import re
import setuptools

NAME             = "baseadmin"
AUTHOR           = "Christophe VG"
AUTHOR_EMAIL     = "contact@christophe.vg"
DESCRIPTION      = "A Pythonic base for building administrator tools for distributed (IoT) applications."
LICENSE          = "MIT"
KEYWORDS         = ""
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
  "Programming Language :: Python :: 3.5",
  "Programming Language :: Python :: 3.6",
  "Programming Language :: Python :: 3.7",
]
INSTALL_REQUIRES = [
  "flask",
  "gunicorn",
  "eventlet",
  "flask_restful",
  "Flask-SocketIO",
  "pymongo",
  "py-bcrypt",
  "python-dateutil",
  "python-dotenv==0.8.2",
  "python-bcrypt",
  "requests"
]
ENTRY_POINTS = {}
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
