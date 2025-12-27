from __future__ import annotations

import argparse
import time

import torch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GPU load test using torch")
    parser.add_argument("--duration", type=float, default=30.0, help="Test duration in seconds")
    parser.add_argument("--batch", type=int, default=4, help="Batch size for BMM")
    parser.add_argument("--size", type=int, default=1024, help="Matrix size (NxN)")
    parser.add_argument(
        "--dtype",
        type=str,
        default="auto",
        choices=["auto", "float16", "float32", "bfloat16"],
        help="Tensor dtype",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda:0",
        help="Device to run on, e.g. cuda:0",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=5,
        help="Warmup iterations before timing",
    )
    parser.add_argument(
        "--sync-interval",
        type=int,
        default=5,
        help="Synchronize every N iterations (0 to disable)",
    )
    parser.add_argument(
        "--log-interval",
        type=float,
        default=5.0,
        help="Log progress every N seconds (0 to disable)",
    )
    return parser.parse_args()


def resolve_dtype(name: str, device: torch.device) -> torch.dtype:
    if name == "auto":
        return torch.float16 if device.type == "cuda" else torch.float32
    if name == "float16":
        return torch.float16
    if name == "float32":
        return torch.float32
    if name == "bfloat16":
        return torch.bfloat16
    raise ValueError(f"Unsupported dtype: {name}")


def main() -> int:
    args = parse_args()
    device = torch.device(args.device)

    if device.type == "cuda" and not torch.cuda.is_available():
        print("CUDA is not available on this system.")
        return 1

    dtype = resolve_dtype(args.dtype, device)
    if device.type != "cuda" and dtype == torch.float16:
        print("float16 is only supported for CUDA devices in this test.")
        return 1

    torch.manual_seed(0)

    if device.type == "cuda":
        torch.cuda.set_device(device)
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)

    a = torch.randn(args.batch, args.size, args.size, device=device, dtype=dtype)
    b = torch.randn(args.batch, args.size, args.size, device=device, dtype=dtype)

    for _ in range(args.warmup):
        c = torch.bmm(a, b)
        a = torch.relu(c)
        b = torch.tanh(c)

    if device.type == "cuda":
        torch.cuda.synchronize()

    start = time.time()
    last_log = start
    iters = 0

    while True:
        c = torch.bmm(a, b)
        a = torch.relu(c)
        b = torch.tanh(c)
        iters += 1

        if device.type == "cuda" and args.sync_interval > 0 and iters % args.sync_interval == 0:
            torch.cuda.synchronize()

        now = time.time()
        if args.log_interval > 0 and now - last_log >= args.log_interval:
            print(f"elapsed={now - start:.1f}s iters={iters}")
            last_log = now

        if now - start >= args.duration:
            break

    if device.type == "cuda":
        torch.cuda.synchronize()
        max_mem = torch.cuda.max_memory_allocated(device) / (1024 ** 2)
        print(f"max_memory_allocated_mb={max_mem:.1f}")

    elapsed = time.time() - start
    iters_per_s = iters / elapsed if elapsed > 0 else 0.0
    print(f"done elapsed_s={elapsed:.2f} iters={iters} iters_per_s={iters_per_s:.2f}")
    print(f"device={device} dtype={dtype} batch={args.batch} size={args.size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
