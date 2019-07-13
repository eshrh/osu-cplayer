# -*- coding: utf-8 -*-
 
 
"""setup.py: setuptools control."""
 
 
import re
from setuptools import setup, find_packages

projectName="osu-cplayer"
scriptFile="%s/%s.py" % (projectName,projectName)
description="Setuptools setup.py for osu-cplayer."


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open(scriptFile).read(),
    re.M
    ).group(1)
 
 
with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")
 
 
setup(
    name = projectName,
    packages = find_packages(),
    #add required packages to install_requires list
    #install_requires=["package","package2"]
    entry_points = {
        "console_scripts": ['%s = %s.%s:main' % (projectName,projectName,projectName)]
        },
    version = version,
    description = description,
    long_description = long_descr,
    author = "Your Name",
    author_email = "Your Email",
    url = "http://Project.url.here",
    license='MIT',
#list of classifiers: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=['Development Status :: 1 - Planning',
 'License :: OSI Approved :: MIT License',
 'Environment :: Console',
 'Natural Language :: English',
 'Operating System :: OS Independent',
 'Programming Language :: Python :: 3.4',
 'Programming Language :: Python :: 3.5',
 'Programming Language :: Python :: 3 :: Only'],
    )
