# sauce : https://realpython.com/pypi-publish-python-package/

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# The text of the LICENSE file
#LICENSE = (HERE / "LICENSE").read_text()

# This call to setup() does all the work
setup(
    name="betterCamera",
    version="1.0.2",
    description="Turn camera into black/white board.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/kacpertopol/betterCam",
    author="Kacper Topolnicki",
    author_email="kacpertopol@gmail.com",
    license="GPL-3.0",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    packages=["bcam"],
    include_package_data=True,
    install_requires=["numpy", "opencv-python" , "opencv-contrib-python"],
    scripts=["betterCamera"]
)
