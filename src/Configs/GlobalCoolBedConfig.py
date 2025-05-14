

class GlobalCoolBedConfigBase:
    """
    冷床的固定参数
    单位毫米
    """
    def __init__(self,width, height):
        self.roll_width = 1000 # 辊宽
        self.roll_height = 4920 # 棍子高度
        self.up_seat_height = 750 # 轴承座上
        self.down_seat_height = 425 # 轴承座下
        self.roll_count = 45
        self.cool_bed_width = 45000
        self.cool_bed_height = 5810

    @property
    def up_seat_d(self):
        return self.roll_height

    @property
    def up_seat_u(self):
        return self.roll_height+self.up_seat_height

    @property
    def up_cool_bed(self):
        return self.roll_height+self.up_seat_height+self.cool_bed_height

class GlobalCoolBedConfigL1(GlobalCoolBedConfigBase):
    def __init__(self,width, height):
        super().__init__(width, height)
        self.roll_count = 45
        self.cool_bed_width = 45000
        self.cool_bed_height = 5810

class  GlobalCoolBedConfigL2(GlobalCoolBedConfigBase):
    def __init__(self,width, height):
        super().__init__(width, height)
        self.roll_count = 50
        self.cool_bed_width = 50000
        self.cool_bed_height = 5780

def get_config(key, width, height):
    print(f"get_config cool_bed_key {key}")
    if "L1" in key:
        return GlobalCoolBedConfigL1(width, height)
    if "L2" in key:
        return GlobalCoolBedConfigL2(width, height)
    raise KeyError(fr"类型错误！ {key}")