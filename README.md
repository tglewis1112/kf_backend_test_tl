# Outages Processor Package
## Overview
The solution implements the outage processing as a Python package, which exposes a command line entry point.
This should make it straight forward for a user to install and work with on the command line.

The package also exposes APIs from `outages_processor.api` which could be used programmatically.

HTTP requests which return a server error/timeout will automatically be retried up to three times with a backoff delay. Client errors are not retried.

Several unit test suites are provided, which can be executed standalone or with tox. Tox has the benefit of cross version testing, and also includes linting in one command.
Unit test coverage is enabled by default. The current average coverage is 96%. I have tested with Python 3.10 and 3.11.

## Directory Structure
```
root
│   README.md
│   .. various config files
│
└───outages_processor       Python package root
    │   constants.py        Constants used throughout the application
    │
    └───api                 API helpers for accessing the various HTTP APIs
    └───scripts             Entrypoint scripts
    └───tests               Unit tests
    │   │   api
    │   │   scripts
    │   │   ... (mirror of top level directory structure)
    │
    └───utils               Miscellaneous shared utilities
```

## Prerequisites
* Python __**3.10**__ or above with pip

## Installation
It is recommended to create a new virtual environment (venv) for the project and install the package into that.
For details covering setup of a new venv, please see [here](https://docs.python.org/3/tutorial/venv.html).
* Open a terminal/command prompt window and cd to the directory containing this readme
* Install the package using `pip install .`
  * For development, install the package in editable mode and test/dev dependencies by running `pip install -e .[test]`. This will also install tools necessary for testing/linting.

## Running the Tool
* Complete installation as per above section.
* A command line entry point is exposed by the package. Simply run `process_outages` from your terminal to launch the tool.
  * Some command line options are available, to list these options run `process_outages --help`

## Configuration
Environment variables can be used to override some settings in the application.
Settings have a default value so the tool will still function without setting these.

| Variable | Description                                                | Default                                  |
|----------|------------------------------------------------------------|------------------------------------------|
| API_KEY  | API key to use for authorisation with the outages API      | EltgJ5G8m44IzwE6UN2Y4B4NjPW77Zk6FJK3lL23 |
| OP_DEBUG | Set to True to enable debug logging across the application | False                                    |


## Development Tools
* Run the unit tests for development with `pytest`, coverage is enabled by default and will output a HTML report to the "htmlcov" directory
* Run pylint with `pylint outages_processor`
* Run `tox` to run the unit tests, coverage report and pylint in a repeatable manner across Python versions. This could be useful for CI.

## Contributing
* Exceptions are used to handle errors, which should be caught by calling functions and handled.
  * Docstrings indicate where this is the case.
* All code changes should be PEP8 compliant with a clean tox run (unit tests and linter).
* Code coverage should always be maintained or improved.

## Future Work/Improvements
* Currently, the API key is held as a constant and can be overridden by an environment variable.
  I was unsure for this task how user friendly the setup/installation process needed to be.
  For a production system I would not default this and force a user to provide a value either as an environment variable or a command line argument, or alternatively fetch from some kind of vault.
