"""
    Installation script for densitometry analysis
"""

from pathlib import Path
from sys import version_info
import re
import os
from setuptools import setup, find_packages

package_name = "Densitometry"
package_root = "src"
repository_root = Path(__file__).parent
requirements = (repository_root / "Requirements.txt").read_text()

description = "Package for Radiomic Features extraction"
long_description = (repository_root / "README.md").read_text()


def get_version():
    """Gets the version from the package's __init__ file
    if there is some problem, let it happily fail"""
    version_file = repository_root / f"{package_root}/{package_name}/__init__.py"
    initfile_lines = version_file.open("rt").readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    return "unknown"


setup(
    name=package_name,
    version=get_version(),
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="None",
    author="A. Belardo",
    author_email="belardo.alfonso@hsr.it",
    url="https://github.com/AlfonsoBelardo/Densitometry_Alfo.git",
    package_dir={"": package_root},
    packages=find_packages(package_root),
    zip_safe=False,
    classifiers=[],
    package_data={
        "": ["*.yaml"],
    },
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={"test": ["prospector", "pytest"]},
    entry_points={
        "console_scripts": [
            "autospaarc = autospaarc.scripts.autospaarc_script:main",
        ]
    },
)
