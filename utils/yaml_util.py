import os

import yaml

from utils.log_util import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load_yaml(path):
    full_path = os.path.join(BASE_DIR, path)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            logger.debug(f'[LOAD_YAML] Loaded yaml file: {full_path}')
            return data
    except FileNotFoundError:
        logger.warning(f'[LOAD_YAML] File not found: {full_path}')
        return {}

if __name__ == '__main__':
    env_data = load_yaml('config/env.yaml')
    print(env_data['dev']['base_url'])