"""
:since:     Wed Dec 02 11:17:09 CET 2015
:author:    Tim Fuehner <tim.fuehner@iisb.fraunhofer.de>
$Id$
"""

import setuptools
from setuptools import setup, find_packages

setup(
        name = "foxbmsflashtool",
        version = "0.1",
        packages = find_packages(),
        author = "Tim Fuehner",
        author_email = "support@foxbms.org",
        package_data={'foxbmsflashtool': ['xrc/*',]},
        zip_safe = False
        )


