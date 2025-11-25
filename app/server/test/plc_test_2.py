import snap7

def test_s7_connection(ip, rack=0, slot=2):
    """
    测试 Siemens S7 PLC 连接

    参数:
        ip: PLC 的 IP 地址
        rack: 机架号 (默认为0)
        slot: 插槽号 (默认为1)
    """
    try:
        # 创建客户端实例
        plc = snap7.client.Client()

        # 设置连接超时时间(毫秒)

        # 连接到PLC
        plc.connect(ip, rack, slot)

        # 获取PLC信息
        plc_info = plc.get_cpu_info()
        print(f"连接成功! PLC信息: {plc_info}")

        # 读取一个测试字节 (DB1.DBX0.0)
        data = plc.db_read(1, 0, 1)
        print(f"测试读取数据: {data}")

        return True

    except Exception as e:
        print(f"连接失败: {str(e)}")
        return False
    finally:
        # 确保断开连接
        if 'plc' in locals():
            plc.disconnect()


# 使用示例
if __name__ == "__main__":
    plc_ip = "10.20.28.145"  # 替换为你的PLC IP地址
    if test_s7_connection(plc_ip):
        print("S7连接测试成功!")
    else:
        print("S7连接测试失败!")