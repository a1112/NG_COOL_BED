
class Result:
    def __init__(self):
        pass

    @property
    def can_get_data(self):
        return False


class YoloModel:


    def predict(self,join_image):
        return Result()