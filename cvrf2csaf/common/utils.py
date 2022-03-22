# pylint: disable=invalid-name,broad-except
import json
import logging
import os
import re
import sys

from pathlib import Path
from datetime import datetime, timezone

import yaml
import pkg_resources

from .common import SectionHandler


def critical_exit(msg, status_code=1):
    """ A critical error encountered, converter is not able to proceed and exits
     with a status code (default 1) """
    logging.critical(msg)
    sys.exit(status_code)

def handle_boolean_config_values(key, val):
    try:
        if isinstance(val, bool):
            return val
        if val.strip().lower() in {'true', 'yes', '1', 'y'}:
            return True
        if val.strip().lower() in {'false', 'no', '0', 'n'}:
            return False

        raise ValueError("unexpected value")

    except (AttributeError, ValueError) as e:
        critical_exit(f"Reading config.yaml failed. "
                      f"Invalid value for config key {key}: {val} {e}.")


def get_config_from_file() -> dict:
    """ Loads configuration file. Parts of it can be overwritten by CLI arguments. """
    config = {}
    try:
        # TODO: Workaround for now, config file placement is to be discussed
        req = pkg_resources.Requirement.parse('cvrf2csaf')
        path_to_conf = pkg_resources.resource_filename(req, 'cvrf2csaf/config/config.yaml')
        with open(path_to_conf, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        for key in ['force', 'fix_insert_current_version_into_revision_history']:
            if key in config.keys():
                config[key] = handle_boolean_config_values(key=key, val=config[key])

    except Exception as e:
        critical_exit(f"Reading config.yaml failed: {e}.")
    return config


def create_file_name(document_tracking_id, valid_output):
    if document_tracking_id is not None:
        file_name = re.sub(r"([^+\-_a-z0-9]+)", '_', document_tracking_id.lower())
    else:
        file_name = 'out'

    if not valid_output:
        file_name = f'{file_name}_invalid'
    file_name = f'{file_name}.json'
    return file_name


def store_json(json_dict, fpath):
    try:

        path = Path(fpath)
        base_dir = path.parent.absolute()

        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
            print(f"Created output folder {base_dir}.")

        if os.path.exists(fpath):
            logging.warning("Output %s already exists. Overwriting it.", fpath)

        if not fpath.lower().endswith('.json'):
            logging.warning("Given output file %s does not contain valid .json suffix.", fpath)

        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(json_dict, f, ensure_ascii=False, indent=2)
            logging.info("Successfully wrote %s.", fpath)

    except Exception as e:
        critical_exit(f"Writing output file {fpath} failed. {e}")


def get_utc_timestamp(time_stamp='now'):
    if time_stamp == 'now':
        now = datetime.now(timezone.utc)

    else:
        time_stamp = time_stamp.replace('Z', '+00:00')
        try:
            now = datetime.fromisoformat(time_stamp)
        except (ValueError, TypeError) as e:
            logging.error('invalid time stamp provided %s: %s.', time_stamp, e)
            SectionHandler.error_occurred = True
            return None

    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    return now.isoformat(timespec='milliseconds')
