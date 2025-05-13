

def get_int_byte(value:int):
    return bytearray(value.to_bytes(2,"little"))