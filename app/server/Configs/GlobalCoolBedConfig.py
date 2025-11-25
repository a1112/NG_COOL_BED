

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
        self.roll_count = 48
        self.cool_bed_width = 48000 # 长度
        self.cool_bed_height = 5810  # 识别高度

    @property
    def MAX_T_CAR_HEIGHT(self):
        return self.cool_bed_height

    @property
    def MAX_T_CAR_WIDTH(self):
        return self.cool_bed_width/ 2

    @property
    def up_seat_d(self):
        return self.roll_height

    @property
    def up_seat_u(self):
        return self.roll_height+self.up_seat_height

    @property
    def center_x(self):
        return self.cool_bed_width/2

    @property
    def up_cool_bed(self):
        return self.roll_height+self.up_seat_height+self.cool_bed_height



    @property
    def info(self):
        return {
            "roll_width_mm":self.roll_width,
            "roll_height_mm":self.roll_height,
            "up_seat_height_mm":self.up_seat_height,
            "down_seat_height_mm":self.down_seat_height,
            "roll_count":self.roll_count,
            "cool_bed_width_mm":self.cool_bed_width,
            "cool_bed_height_mm":self.cool_bed_height,
            "up_seat_d_mm":self.up_seat_d,
            "up_seat_u_mm":self.up_seat_u,
            "up_cool_bed_mm":self.up_cool_bed,
            "center_x_mm":self.center_x
        }


class GlobalCoolBedConfigL1(GlobalCoolBedConfigBase):
    def __init__(self,width, height):
        super().__init__(width, height)
        self.roll_count = 48
        self.cool_bed_width = 48000
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