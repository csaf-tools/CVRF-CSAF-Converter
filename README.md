# CVRF-CSAF-Converter


> CVRF CSAF converter: A CSAF producer which takes a CVRF document as input and converts it into a valid CSAF document. [OASIS](https://docs.oasis-open.org/csaf/csaf/v2.0/csd01/csaf-v2.0-csd01.html)

## Project

CVRF-CSAF-Converter is a project between Deutsche Telekom Security GmbH and the Federal Office for Information Security. It aims to provide a PoC CVRF 1.x to CSAF 2.0 converter. 

Realization is taking place 100% Open Source. The final delivery will be in Q1/2022.

## Project Team

``` To Be Published ```

## Specifications

We follow the official OASIS specifications in order to provide as much acceptance on the user base as possible.

- [Specification CVRF 1.2](http://docs.oasis-open.org/csaf/csaf-cvrf/v1.2/cs01/csaf-cvrf-v1.2-cs01.html)
   - [xsd common](http://docs.oasis-open.org/csaf/ns/csaf-cvrf/v1.2/common)
   - [xsd cvrf](http://docs.oasis-open.org/csaf/ns/csaf-cvrf/v1.2/cvrf)
   - [xsd prod](http://docs.oasis-open.org/csaf/ns/csaf-cvrf/v1.2/prod)
   - [xsd vuln](http://docs.oasis-open.org/csaf/ns/csaf-cvrf/v1.2/vuln)


- [Specification CSAF 2.0](https://docs.oasis-open.org/csaf/csaf/v2.0/csd01/csaf-v2.0-csd01.html) 
   - [JSON spec](https://docs.oasis-open.org/csaf/csaf/v2.0/csd01/schemas/csaf_json_schema.json)

## Tools around CSAF 2.0

- [BSI Secvisogram CSAF 2.0 Web Editor](https://github.com/secvisogram/secvisogram)


# Installation (with venv)
``` TODO: for now only from source ```

```shell script
ROOT_DIR='/tmp'
cd $ROOT_DIR
git clone https://github.com/csaf-tools/CVRF-CSAF-Converter
cd CVRF-CSAF-Converter
python3 -m venv venv
. venv/bin/activate
pip install .
```

Hint: If you would like to get the debugger running, try to install the code as follows: `pip install -e .`

# Usage (as CLI tool)
```shell script
cvrf2csaf -h
cvrf2csaf --input-file $ROOT_DIR/CVRF-CSAF-Converter/sample_input/sample.xml --output-file sample.json
```
