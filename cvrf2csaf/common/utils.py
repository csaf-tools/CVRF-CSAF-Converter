import json
import logging
import os
import pkg_resources
import re
import yaml

from pathlib import Path
from datetime import datetime, timezone
from .common import SectionHandler


def critical_exit(msg, status_code=1):
    """ A critical error encountered, converter is not able to proceed and exits with a status code (default 1) """
    logging.critical(msg)
    exit(status_code)


def handle_boolean_config_values(key, val):
    try:
        if isinstance(val, bool):
            return val
        if val.strip().lower() in {'true', 'yes', '1', 'y'}:
            return True
        if val.strip().lower() in {'false', 'no', '0', 'n'}:
            return False

        critical_exit(f"Reading config.yaml failed. "
                      f"Invalid value for config key {key}: {val}. {e}.")

    except Exception as e:
        critical_exit(f"Reading config.yaml failed. "
                      f"Invalid value for config key {key}: {val} {e}.")


def get_config_from_file() -> dict:
    """ Loads configuration file. Parts of it can be overwritten by CLI arguments. """
    config = dict()
    try:
        # TODO: Workaround for now, config file placement is to be discussed
        req = pkg_resources.Requirement.parse('cvrf2csaf')
        path_to_conf = pkg_resources.resource_filename(req, 'cvrf2csaf/config/config.yaml')
        with open(path_to_conf, 'r') as f:
            config = yaml.safe_load(f)

        for key in ['force', 'fix_insert_current_version_into_revision_history']:
            if key in config.keys():
                config[key] = handle_boolean_config_values(key=key, val=config[key])

    except Exception as e:
        critical_exit(f"Reading config.yaml failed: {e}.")
    finally:
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
            json.dump(js, f, ensure_ascii=False, indent=2)
            logging.info(f"Successfully wrote {fpath}.")
    except Exception as e:
        critical_exit(f"Writing output file {fpath} failed. {e}")


def get_utc_timestamp(time_stamp='now'):
    if time_stamp == 'now':
        dt = datetime.now(timezone.utc)

    else:
        ts = time_stamp.replace('Z', '+00:00')
        try:
            dt = datetime.fromisoformat(ts)
        except Exception as e:
            logging.error(f'invalid time stamp provided {time_stamp}: {e}.')
            SectionHandler.error_occurred = True
            return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.isoformat(timespec='milliseconds')
