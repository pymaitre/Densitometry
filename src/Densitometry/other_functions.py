import os
import yaml
from pathlib import Path


def rtv_configuration_file(name_conf, path_conf=None, save=True, pathout=''):
    """
    It reads the configuration file from a .yml file and it gives it as output as a dictionary.
    :param: name_conf: name of configuration file.
    :param: path_conf: full path of the configuration file.
    :param: save: boolean value to save the configuration inside the results folder.
    :param: pathout: where to save a copy of configuration file.
    :return: config_parameters = dictionary with parameters config.
    """
    # TODO: modify parameters read as global params read directly from yml or sql
    if path_conf is not None:
        config_path = Path(path_conf)
    else:
        # config_path = Path("//IHSR.dom/OSRFileServices") / "Ric.FisicaSanitaria" / "Belardo" / "BAROTRAUMA" / "try_exe" / "conf" / f"{name_conf}.yml"
        config_path = Path(r"C:\Users\belardo.alfonso\Desktop\GitHub\Densitometry_Alfo\src\Densitometry\conf\conf_dcm.yml")
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