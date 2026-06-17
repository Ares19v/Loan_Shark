"""
run_all.py — Launch all 9 Loan Shark agents with a single command.

Usage:
    uv run python run_all.py

Press Ctrl+C to shut down all agents cleanly.
"""

import subprocess
import threading
import sys
import os
import signal
import time

# Windows consoles default to cp1252 and choke on box-drawing/emoji output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ─────────────────────────────────────────────
# AGENT DEFINITIONS
# ─────────────────────────────────────────────

AGENTS = [
    ("INTAKE",         "agents/intake/agent.py",         "\033[94m"),   # Blue
    ("DOCUMENT",       "agents/document/agent.py",        "\033[96m"),   # Cyan
    ("CREDIT",         "agents/credit/agent.py",          "\033[93m"),   # Yellow
    ("FRAUD",          "agents/fraud/agent.py",           "\033[91m"),   # Red
    ("RISK",           "agents/risk/agent.py",            "\033[95m"),   # Magenta
    ("COMPLIANCE",     "agents/compliance/agent.py",      "\033[92m"),   # Green
    ("DECISION",       "agents/decision/agent.py",        "\033[97m"),   # White
    ("PRICING",        "agents/pricing/agent.py",         "\033[33m"),   # Orange
    ("COMMUNICATION",  "agents/communication/agent.py",   "\033[36m"),   # Teal
]

RESET = "\033[0m"
BOLD  = "\033[1m"

processes = []


def stream_output(proc, label, color):
    """Stream stdout and stderr from a subprocess with a colored label prefix."""
    def _read(stream):
        for line in iter(stream.readline, b""):
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                print(f"{color}{BOLD}[{label}]{RESET} {text}")
        stream.close()

    t_out = threading.Thread(target=_read, args=(proc.stdout,), daemon=True)
    t_err = threading.Thread(target=_read, args=(proc.stderr,), daemon=True)
    t_out.start()
    t_err.start()


def shutdown(signum=None, frame=None):
    print(f"\n{BOLD}🛑 Shutting down all agents...{RESET}")
    for proc, name, _ in processes:
        try:
            proc.terminate()
            print(f"  ↳ Terminated {name}")
        except Exception:
            pass
    time.sleep(1)
    for proc, name, _ in processes:
        try:
            proc.kill()
        except Exception:
            pass
    print(f"{BOLD}✅ All agents stopped.{RESET}")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, shutdown)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, shutdown)

    print(f"""
{BOLD}\033[93m
╔═══════════════════════════════════════╗
║       🦈  LOAN SHARK AGENT SWARM      ║
║   9-Agent AI Loan Processing System   ║
╚═══════════════════════════════════════╝
{RESET}""")

    python = sys.executable

    for name, path, color in AGENTS:
        if not os.path.exists(path):
            print(f"{BOLD}\033[91m[ERROR]{RESET} Agent file not found: {path}")
            continue

        proc = subprocess.Popen(
            [python, path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"},
        )
        processes.append((proc, name, color))
        stream_output(proc, name, color)
        print(f"{color}{BOLD}[{name}]{RESET} ✅ Started (PID {proc.pid})")
        time.sleep(0.3)  # Stagger startup slightly to avoid race conditions

    print(f"\n{BOLD}🚀 All 9 agents running. Press Ctrl+C to stop.{RESET}\n")

    # Keep main thread alive, watching for crashed processes
    while True:
        time.sleep(5)
        for proc, name, color in processes:
            ret = proc.poll()
            if ret is not None:
                print(f"{BOLD}\033[91m[{name}]{RESET} ⚠️  Process exited with code {ret}. Check logs above.")


if __name__ == "__main__":
    main()
