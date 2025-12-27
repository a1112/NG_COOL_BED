import os

DEFAULT_L1_PORT = 8011
DEFAULT_L2_PORT = 8012

CAPTURE_BIND_HOST = os.getenv("CAPTURE_BIND_HOST", "0.0.0.0")

L1_PORT = int(os.getenv("CAPTURE_L1_PORT", str(DEFAULT_L1_PORT)))
L2_PORT = int(os.getenv("CAPTURE_L2_PORT", str(DEFAULT_L2_PORT)))

L1_URL = os.getenv("CAPTURE_L1_URL", f"http://127.0.0.1:{L1_PORT}")
L2_URL = os.getenv("CAPTURE_L2_URL", f"http://127.0.0.1:{L2_PORT}")

CAPTURE_URLS = {
    "L1": L1_URL,
    "L2": L2_URL,
}
CAPTURE_PORTS = {
    "L1": L1_PORT,
    "L2": L2_PORT,
}
