from Result.DetResult import DetResult


class DataItem:
    def __init__(self,key, steels: DetResult):
        self.key = key
        self.steels = steels
        self.has_roll_steel_left = False  #  辊道存在板子 左侧
        self.has_roll_steel_right = False  # 辊道存在板子 右侧

        self.has_cool_bed_steel_left = False
        self.has_cool_bed_steel_right = False
        self.has_error = False

    @property
    def roll_steel(self):
        return self.steels.roll_steel

    @property
    def cool_bed_steel(self):
        return self.steels.cool_bed_steel

    @property
    def left_under_steel(self):
        return self.steels.left_under_steel

    @property
    def right_under_steel(self):
        return self.steels.right_under_steel

    @property
    def steel_info(self):
        return [[round(i/1000,1) for i in list(steel.mm_rec)] for steel in self.steels.steel_list]

    @property
    def group_key(self):
        return self.steels.map_config.key