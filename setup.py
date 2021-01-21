# -*- coding: utf-8 -*-
import re
from setuptools import setup

REQUIRES = [
    'sanic>=0.8.3',
    'webargs>=7.0.1'
]

def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ""
    with open(fname, "r") as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError("Cannot find version information")
    return version

__version__ = find_version("webargs_sanic/__init__.py")

setup(
    name="webargs-sanic",
    version=__version__,
    description="webargs-sanic provides integration of Webargs with Sanic applications",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Endurant Devs",
    author_email="info@endurantdevs.com",
    url="https://github.com/EndurantDevs/webargs-sanic",
    packages=["webargs_sanic"],
    install_requires=REQUIRES,
    license="MIT",
    zip_safe=False,
    keywords="webargs-sanic webargs sanic testing",
    classifiers=[
        "Intended Audience :: Developers",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
)
