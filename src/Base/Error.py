class CoolBedError(Exception):
    def __init__(self,msg="无数据"):
        self.msg = msg
