from CONFIG import SOFT_FOLDER

def get_app_url(name):
    if not SOFT_FOLDER.exists():
        return ""
    return SOFT_FOLDER / name

class AppConfigs:
    def __init__(self):
        self.info = {
            "labelimg":get_app_url("labelImg-master/labelImg.exe"),
            "labelme": get_app_url("labelme.exe"),
        }


app_configs = AppConfigs()


print(app_configs.info)