import time

class ImageBuffer:

    def __init__(self):
        self.create_time = time.time()
        self.ret_ = 0
        self.frame_ = None
        self.image_ = None
        self.set_image_time = time.time()
        self.set_frame_time = time.time()

    @property
    def ret(self):
        return self.ret_

    @ret.setter
    def ret(self, value):
        self.ret_ = value

    @property
    def frame(self):
        return self.frame_

    @frame.setter
    def frame(self, value):
        self.set_frame_time = time.time()
        self.frame_ = value

    @property
    def frame_time(self):
        return self.set_frame_time

    @property
    def time_difference(self):
        return self.set_frame_time - self.create_time

    @property
    def image(self):
        return self.image_

    @image.setter
    def image(self, value):
        self.set_image_time = time.time()
        self.image_ = value