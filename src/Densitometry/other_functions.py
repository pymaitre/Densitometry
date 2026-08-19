import os
import yaml
from pathlib import Path


def rtv_configuration_file(name_conf:str, path_conf:Path=None, save:bool=True, pathout:str='')->dict:
    """
    Read the configuration file from a .yml file and return it as a dictionary.
    
    
    :param name_conf: name of the configuration file.
    :type name_conf: str
    :param path_conf: full path to the configuration file.
    :type path_conf: Path
    :param save: flag indicating whether to save the configuration inside the results folder.
    :type save: bool
    :param pathout: directory where a copy of the configuration file is saved.
    :type pathout: str
    
    
    :return: dictionary containing the configuration parameters.
    :rtype: dict
    """
    
    if path_conf is not None:
        config_path = Path(path_conf)
    else:
        
        config_path = Path(__file__).parent / "conf" / f"{name_conf}.yml"
    
    with open(config_path) as file:
        config_parameters = yaml.load(file, Loader=yaml.FullLoader)
        
    if save and pathout!='':

        if not os.path.exists(pathout):
            os.makedirs(pathout)
        with open(config_path, "r") as source, open(pathout / "conf.txt", "w") as dest:
            dest.write(source.read())

    return config_parameters
