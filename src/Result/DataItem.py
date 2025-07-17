from Result.DetResult import DetResult
from Result.SteelItem import SteelItemNone


class DataItem:
    def __init__(self,key, steels: DetResult):
        self.key = key
        self.steels = steels

    @property
    def has_error(self):
        return self.steels is None

    @property
    def has_roll_steel_left(self):
        if self.steels is None:
            return False

        for steel in self.steels.roll_steel:
            if steel.in_left:
                return True
        return False

    @property
    def has_roll_steel_right(self):
        if self.steels is None:
            return False

        for steel in self.steels.roll_steel:
            if steel.in_right:
                return True
        return False

    @property
    def has_cool_bed_steel_left(self):
        if self.steels is None:
            return False

        for steel in self.steels.cool_bed_steel:
            if steel.in_left:
                return True
        return False

    @property
    def has_cool_bed_steel_right(self):
        if self.steels is None:
            return False

        for steel in self.steels.cool_bed_steel:
            if steel.in_right:
                return True
        return False


    @property
    def roll_steel(self):
        return self.steels.roll_steel

    @property
    def cool_bed_steel(self):
        return self.steels.cool_bed_steel

    @property
    def left_under_steel(self):
        if self.steels is None:
            return SteelItemNone()

        return self.steels.left_under_steel

    @property
    def left_under_cool_bed_steel(self):
        if self.steels is None:
            return SteelItemNone()
        return self.steels.left_under_cool_bed_steel

    @property
    def right_under_cool_bed_steel(self):
        if self.steels is None:
            return SteelItemNone()
        return self.steels.right_under_cool_bed_steel

    @property
    def left_cool_bed_steel(self):
        if self.steels is None:
            return SteelItemNone()
        return self.steels.left_cool_bed_steel

    @property
    def right_cool_bed_steel(self):
        if self.steels is None:
            return SteelItemNone()
        return self.steels.right_cool_bed_steel

    @property
    def right_under_steel(self):
        if self.steels is None:
            return SteelItemNone()

        return self.steels.right_under_steel

    @property
    def steel_info(self):
        return [[round(i/1000,1) for i in list(steel.mm_rec)] for steel in self.steels.steel_list]

    @property
    def group_key(self):
        return self.steels.map_config.key

    def get_info(self):

        if self.steels is None:
            group_key = ""
            objects = []
        else:
            group_key = self.group_key
            objects = self.steels.infos
        return {
            "left_cool_bed_has_steel":self.has_cool_bed_steel_left,
            "right_cool_bed_has_steel": self.has_cool_bed_steel_right,
            "left_roll_bed_has_steel": self.has_roll_steel_left,
            "right_roll_bed_has_steel": self.has_roll_steel_right,
            "group_key":group_key ,
            "has_error": self.has_error,
            "left_under_steel_to_center": self.left_under_steel.to_roll_center_y,
            "right_under_steel_to_center": self.right_under_steel.to_roll_center_y,
            "left_cool_bed_steel_to_up":self.left_under_cool_bed_steel.to_under_mm,
            "right_cool_bed_steel_to_up": self.right_under_cool_bed_steel.to_under_mm,
            "left_rol_to_center": self.left_cool_bed_steel.to_roll_center_y,
            "right_rol_to_center": self.right_cool_bed_steel.to_roll_center_y,
            "objects" : objects
        }