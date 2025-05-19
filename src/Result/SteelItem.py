from Configs.MappingConfig import MappingConfig
from Result import format_mm


class SteelItem:
    """
    单独的 item
    """
    def __init__(self,rec,map_config):
        self.rec=rec
        self.map_config:MappingConfig = map_config
        x,y,w,h, self.type_ = self.rec
        self.px_x = x
        self.px_y = y
        self.px_w = w
        self.px_h = h
        self.mm_rec = self.map_config.get_rect(self.rec[:4])

    @property
    def x_mm(self):
        return self.mm_rec[0]

    @property
    def y_mm(self):
        return self.mm_rec[1]

    @property
    def w_mm(self):
        return self.mm_rec[2]

    @property
    def h_mm(self):
        return self.mm_rec[3]

    @property
    def to_roll_mm(self):
        return self.y_mm - self.h_mm

    @property
    def left_mm(self):
        return self.x_mm

    @property
    def right_mm(self):
        return self.x_mm + self.w_mm

    @property
    def top_mm(self):
        return self.y_mm

    @property
    def bottom_mm(self):
        return self.y_mm - self.h_mm

    @property
    def mm_str(self):
        x_mm, y_mm, w_mm, h_mm = self.mm_rec
        return f"x: {format_mm(x_mm)} y: {format_mm(y_mm)} w: {format_mm(w_mm)} h: {format_mm(h_mm)}"

    @property
    def name(self):
        if self.type_ == 0:
            return "steel" + self.mm_str
        return "t_car"

    @property
    def color(self):
        return 200, 0, 0


    @property
    def rect_px(self):
        return self.rec[:4]

    @property
    def in_roll(self):
        return self.bottom_mm < self.map_config.up_seat_d

    @property
    def in_cool_bed(self):
        return self.top_mm >= self.map_config.up_seat_u
