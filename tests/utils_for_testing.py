"""
Module for auxiliary functions used in testing.
"""

from pathlib import Path
from typing import Any
import yaml


def modify_configuration_file(
    config_path: Path, key_list: list | str = None, value_list: Any = None
) -> dict:
    """
    Modify the input configuration file.

    :param config_path: input configuration file path.
    :type config_path: Path
    :param key_list: key or list of keys to be modified.
    :type key_list: list|str
    :param value_list: value or list of values to be modified.
    :type value_list: Any


    :return: dictionary containing the modified configuration parameters.
    :rtype: dict
    """

    conf = yaml.safe_load(config_path.read_text())

    if key_list is not None:

        if isinstance(key_list, str):
            conf[key_list] = value_list

        else:

            if len(value_list) != len(key_list):
                raise ValueError("Missing keys or values")

            for k, v in zip(key_list, value_list):
                conf[k] = v
    else:
        print("No keys are provided. The configuration file is not modified.")
    return conf
