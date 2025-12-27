import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import subprocess


def _setup_logger() -> logging.Logger:
    log_dir = Path(__file__).resolve().parents[2] / "logs" / "server"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("server_runner")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(log_dir / "runner.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def _restart_delay(restart_times, base_delay=2.0, max_delay=30.0):
    now = time.time()
    restart_times[:] = [t for t in restart_times if now - t < 300]
    if len(restart_times) >= 5:
        return 60.0
    return min(max_delay, base_delay * (2 ** max(0, len(restart_times) - 1)))


def main():
    logger = _setup_logger()
    script_dir = Path(__file__).resolve().parent
    target = script_dir / "main.py"
    if not target.is_file():
        logger.error("main.py not found at %s", target)
        return 1

    restart_times = []
    env = os.environ.copy()

    while True:
        start_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("starting server: %s", start_ts)
        proc = subprocess.Popen(
            [sys.executable, str(target)],
            cwd=str(script_dir),
            env=env,
        )
        code = proc.wait()
        logger.warning("server exited with code=%s", code)
        if code == 0:
            logger.info("server exited cleanly, not restarting")
            return 0
        restart_times.append(time.time())
        delay = _restart_delay(restart_times)
        logger.info("restarting in %.1fs", delay)
        time.sleep(delay)


if __name__ == "__main__":
    raise SystemExit(main())
