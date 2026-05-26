import os
import yaml
from pathlib import Path


def rtv_configuration_file(name_conf:str, path_conf:Path=None, save:bool=True, pathout:str='')->dict:
    """
    It reads the configuration file from a .yml file and it gives it as output as a dictionary.
    
    
    :param name_conf: name of configuration file.
    :type name_conf: str
    :param path_conf: full path of the configuration file.
    :type path_conf: Path
    :param save: boolean value to save the configuration inside the results folder.
    :type save: bool
    :param pathout: where to save a copy of configuration file.
    :type pathout: str
    
    
    :return: dictionary with parameters config.
    :rtype: dict
    """
    
    if path_conf is not None:
        config_path = Path(path_conf)
    else:
        
        config_path = Path(r"input_path")
    
    # READING THE CONFIGURATION FILE
    with open(config_path) as file:
        config_parameters = yaml.load(file, Loader=yaml.FullLoader)
        
    if save and pathout!='':
        # pathout = Path.cwd().parent.parent / "wrk" / "Models" / config_parameters["survey_name"] / folder
        if not os.path.exists(pathout):
            os.makedirs(pathout)
        with open(config_path, "r") as source, open(pathout / "conf.txt", "w") as dest:
            dest.write(source.read())

    return config_parameters