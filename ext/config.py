from typing import Union, Optional

import yaml


with open('config.yml') as f:
    config_data = yaml.load(f, Loader=yaml.FullLoader)  # loads config file


def get_nested_dict(data, path: list):  # get value in nested dictionary
    for i in path:
        data = data.get(i, None)
    return data


def config(query: Optional[str] = None) -> Union[str, int, dict, list]:
    if not query:
        return config_data
    else:
        return get_nested_dict(config_data, query.split('.'))
