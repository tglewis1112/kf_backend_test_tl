# Outages Processor Package
## Prerequisites
* Python 3.10 or above with pip

## Installation
It is recommended to create a new virtual environment (venv) for the project and install the package into that.
For details covering setup of a new venv, please see [here](https://docs.python.org/3/tutorial/venv.html).
* Open a terminal/command prompt window and cd to the directory containing this readme
* Install the package using `pip install .`
  * For development, install the package in editable mode and test/dev dependencies by running `pip install -e .[test]`

## Running the Tool
* A command line entry point is exposed by the package. Simply run `process_outages` from your terminal to launch the tool.

## Development Tools
* Run the unit tests for development with `pytest`, coverage is enabled by default and will output a HTML report to the "htmlcov" directory
* Run pylint with `pylint outages_processor`
* Run `tox` to run the unit tests, coverage report and pylint in a repeatable manner across Python versions. This could be useful for CI.

## Contributing
* All code changes should be PEP8 compliant with a clean tox run
