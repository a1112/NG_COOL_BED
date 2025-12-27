import argparse
import time

from HslCommunication import SiemensPLCS, SiemensS7Net

import app.server.PLC_config as PLC_config


def read_db5_once(client, address, length):
    response = client.Read(address, length)
    if response is None:
        raise RuntimeError("DB5 read: response is None")
    if hasattr(response, "IsSuccess") and not response.IsSuccess:
        msg = getattr(response, "Message", "") or ""
        raise RuntimeError(f"DB5 read failed: {msg}".strip())
    payload = getattr(response, "Content", None)
    if payload is None:
        raise RuntimeError("DB5 read: Content is None")
    data = bytes(payload)
    return data


def main():
    parser = argparse.ArgumentParser(description="PLC DB5 read test")
    parser.add_argument("--ip", default=PLC_config.TMEIC_DB5_IP)
    parser.add_argument("--rack", type=int, default=PLC_config.TMEIC_DB5_RACK)
    parser.add_argument("--slot", type=int, default=PLC_config.TMEIC_DB5_SLOT)
    parser.add_argument("--address", default=PLC_config.TMEIC_DB5_ADDRESS)
    parser.add_argument("--length", type=int, default=PLC_config.TMEIC_DB5_LENGTH)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()

    client = SiemensS7Net(SiemensPLCS.S400, args.ip)
    client.SetSlotAndRack(args.rack, args.slot)

    for i in range(args.count):
        try:
            data = read_db5_once(client, args.address, args.length)
            hex_bytes = " ".join(f"{b:02X}" for b in data)
            print(f"[{i + 1}/{args.count}] {args.address} len={args.length} -> {hex_bytes}")
        except Exception as exc:
            print(f"[{i + 1}/{args.count}] read error: {exc}")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
