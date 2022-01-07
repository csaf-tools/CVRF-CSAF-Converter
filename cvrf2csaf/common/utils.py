import argparse
import yaml
import os, logging, json
import inspect
import pkg_resources
from pathlib import Path
from datetime import datetime, timezone


def critical_exit(msg, status_code=1):
    """ A critical error encountered, converter is not able to proceed and exits with a status code (default 1) """
    logging.critical(msg)
    exit(status_code)


def get_config_from_file() -> dict:
    """ Loads configuration file. Parts of it can be overwritten by CLI arguments. """
    config = dict()
    try:
        # TODO: Workaround for now, config file placement is to be discussed
        req = pkg_resources.Requirement.parse('cvrf2csaf')
        path_to_conf = pkg_resources.resource_filename(req, 'cvrf2csaf/config/config.yaml')
        with open(path_to_conf, 'r') as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        critical_exit(f"Reading config.yaml failed: {e}.")


def store_json(js, fpath):

    try:

        path = Path(fpath)
        base_dir = path.parent.absolute()

        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
            print(f"Created output folder {base_dir}.")

        if os.path.exists(fpath):
            logging.warning(f"Output {fpath} already exists. Overwriting it.")

        if not fpath.lower().endswith('.json'):
            logging.warning(f"Given output file {fpath} does not contain valid .json suffix.")

        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(js, f, ensure_ascii=False, indent=4)
            logging.info(f"Successfully wrote {fpath}.")
    except Exception as e:
        critical_exit(f"Writing output file {fpath} failed. {e}")


def get_utc_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')
