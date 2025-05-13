
import tool
import CONFIG


class MappingConfig:
    """
    指标转换参数
    """
    def __init__(self, key):
        self.data = tool.load_xml(CONFIG.MappingPath/fr"{key}.xml") # 读取物理坐标标定
        print(self.data)
        # {'up': [8, 1024, 380, 431], 'down': [5, 1020, 738, 768], 'r_0_2': [14, 66, 437, 733], 'coolbed': [3, 1024, 1, 378]}

if __name__ =="__main__":
    MappingConfig("L1_g1_6")