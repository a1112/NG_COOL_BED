from Configs.MappingConfig import MappingConfig


class DetResult:
    def __init__(self,rec_list,map_config):
        self.map_config:MappingConfig = map_config
        self.rec_list = rec_list

    @property
    def can_get_data(self):
        return False

    def draw_steel(self):
        pass