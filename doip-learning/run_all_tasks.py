#!/usr/bin/env python3
"""Start DoIP servers and run Task 1 + Task 2 + Task 3 clients automatically."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASK1 = ROOT / "task1" / "scripts"
TASK2 = ROOT / "task2" / "scripts"
TASK3 = ROOT / "task3" / "scripts"


def start_server(script: Path) -> subprocess.Popen:
    print(f"[RUN_ALL] Starting {script.name} ...")
    return subprocess.Popen(
        [sys.executable, str(script)],
        cwd=str(script.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def run_client(script: Path, extra_args: list[str] | None = None) -> None:
    cmd = [sys.executable, str(script)] + (extra_args or [])
    print(f"\n{'=' * 60}")
    print(f"[RUN_ALL] Running {script.name}")
    print("=" * 60)
    result = subprocess.run(cmd, cwd=str(script.parent))
    if result.returncode != 0:
        raise RuntimeError(f"{script.name} failed with code {result.returncode}")


def stop_processes(processes: list[subprocess.Popen]) -> None:
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all DoIP learning tasks")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--skip-task1", action="store_true")
    parser.add_argument("--skip-task3", action="store_true")
    args = parser.parse_args()

    servers: list[subprocess.Popen] = []
    try:
        servers.append(start_server(TASK1 / "doip_udp_server.py"))
        servers.append(start_server(TASK2 / "doip_tcp_server_uds.py"))
        time.sleep(1.0)

        client_args = ["--host", args.host]

        if not args.skip_task1:
            run_client(TASK1 / "doip_client.py", client_args)

        run_client(TASK2 / "doip_client_uds.py", client_args)

        if not args.skip_task3:
            run_client(TASK3 / "doip_client_faults.py", client_args)

        print("\n" + "=" * 60)
        print("ALL TASKS PASSED")
        print("=" * 60)
        return 0
    except Exception as exc:
        print(f"\n[RUN_ALL] FAILED: {exc}")
        return 1
    finally:
        stop_processes(servers)


if __name__ == "__main__":
    raise SystemExit(main())
