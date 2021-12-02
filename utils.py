import argparse
import yaml
import os, logging, json
from pathlib import Path

def get_config_from_file():
    """Loads configuration file. Parts of it can be overwritten by CLI arguments."""
    config = dict()
    try:
        f = open('./config.yaml', 'r')
        config = yaml.safe_load(f)
    except Exception as e:
        print(f"Reading config.yaml failed {e}.")
        exit(1)
    finally:
        return config

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
        print(f"Writing output file {fpath} failed. {e}")
        exit(1)

def str2bool(v):
    """For argparse of boolean input, transmitted as string"""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')