# CVRF-CSAF-Converter

<!-- TOC depthfrom:2 depthto:3 -->

- [Introduction](#introduction)
- [Getting started](#getting-started)
- [How to use CVRF-CSAF-converter](#how-to-use-cvrf-csaf-converter)
    - [Usage as CLI tool](#usage-as-cli-tool)
    - [Config](#config)
- [Specifications](#specifications)
- [Developing CVRF-CSAF-converter](#developing-cvrf-csaf-converter)
    - [Developer Guide, Architecture and Technical Design](#developer-guide-architecture-and-technical-design)
    - [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [Project](#project)

<!-- /TOC -->

## Introduction

> CVRF-CSAF-converter is a Python tool for converting [CSAF CVRF 1.2 documents](https://docs.oasis-open.org/csaf/csaf-cvrf/v1.2/cs01/csaf-cvrf-v1.2-cs01.html) in [CSAF 2.0 documents](https://docs.oasis-open.org/csaf/csaf/v2.0/csaf-v2.0.html). It fulfills the conformance target [CVRF CSAF converter](https://docs.oasis-open.org/csaf/csaf/v2.0/csaf-v2.0.html#915-conformance-clause-5-cvrf-csaf-converter).

**Note**: The project is currently still under development. Not all features have been implemented and therefore the conformance goal is not yet fulfilled.

## Getting started

Ensure that you have **Python 3** installed.

Assume your current directory is also avaliable at the environment variable `$ROOT_DIR`.

Check out the repository and navigate to the working directory.

```shell script
   git clone https://github.com/csaf-tools/CVRF-CSAF-Converter.git
   cd CVRF-CSAF-Converter
```

Afterwards, create a virtual environment and install the package there:

```shell script
   python3 -m venv venv
   . venv/bin/activate
   pip install .
```

_Hint: If you would like to get the debugger running, try to install the code as follows: `pip install -e .`_

## How to use CVRF-CSAF-converter

### Usage as CLI tool

To convert the CVRF CSAF 1.2 document `$ROOT_DIR/CVRF-CSAF-Converter/examples/1.2/cvrf_example_a.xml` use the following command:

```shell script
   cvrf2csaf --input-file $ROOT_DIR/CVRF-CSAF-Converter/examples/1.2/cvrf_example_a.xml
```

The default output directory is `./`, it can be set using `--output-dir`. 

The output filename is derived from the CSAF field `/document/tracking/id`.

If there is an ERROR during conversion, the output file will not be written unless `--force` option is used.

The rest of the options can be shown with:

```shell script
   cvrf2csaf -h
```

### Config

The [config file](https://github.com/csaf-tools/CVRF-CSAF-Converter/blob/main/cvrf2csaf/config/config.yaml) is installed inside the Python package (`.../site-packages/cvrf2csaf/config/config.yaml`).
Convertor options can be changed there, or overridden by command line arguments/options.

## Specifications

We follow the official OASIS specifications in order to provide as much acceptance on the user base as possible.

- [Specification CVRF 1.2](http://docs.oasis-open.org/csaf/csaf-cvrf/v1.2/cs01/csaf-cvrf-v1.2-cs01.html)
  - [xsd common](http://docs.oasis-open.org/csaf/ns/csaf-cvrf/v1.2/common)
  - [xsd cvrf](http://docs.oasis-open.org/csaf/ns/csaf-cvrf/v1.2/cvrf)
  - [xsd prod](http://docs.oasis-open.org/csaf/ns/csaf-cvrf/v1.2/prod)
  - [xsd vuln](http://docs.oasis-open.org/csaf/ns/csaf-cvrf/v1.2/vuln)

- [Specification CSAF 2.0](https://docs.oasis-open.org/csaf/csaf/v2.0/csaf-v2.0.html)
  - [JSON spec](https://docs.oasis-open.org/csaf/csaf/v2.0/schemas/csaf_json_schema.json)

## Developing CVRF-CSAF-converter

### Developer Guide, Architecture and Technical Design

``` To Be Published ```

### Security Considerations

## Contributing

Please refer to [`CONTRIBUTING.md`](CONTRIBUTING.md) for details about how to contribute to the development of [CVRF-CSAF-converter](https://github.com/csaf-tools/CVRF-CSAF-converter).

## Project

CVRF-CSAF-Converter is a project between Deutsche Telekom Security GmbH and the Federal Office for Information Security. It aims to provide a CVRF 1.x to CSAF 2.0 converter.

Realization is taking place 100% Open Source. The final delivery will be in Q1/2022.
