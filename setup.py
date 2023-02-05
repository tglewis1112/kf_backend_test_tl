"""
Setup for the outages_processor project
"""
from setuptools import find_packages, setup

from outages_processor.constants import VERSION

REQUIREMENTS = [
    "iso8601",
    "requests",
]

EXTRA_REQUIREMENTS = {
    "test": [
        "httpretty",
        "pylint",
        "pytest",
        "pytest-cov",
        "tox",
    ],
}

setup(
    name="outages_processor",
    version=VERSION,
    python_requires=">=3.10.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    extras_require=EXTRA_REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "process_outages=outages_processor.scripts.outages:process_outages",
        ]
    },
)
