#!/usr/bin/env python3
"""server.py — manage the ComfyUI HTTP server as a detached background process.
Usage:
  python server.py start    # launch on :8188 (detached, survives cell exit)
  python server.py stop
  python server.py status
  python server.py log [N]  # tail last N lines (default 30)
"""
import sys, os, subprocess, time, signal

COMFY = "/content/ComfyUI"
PORT = 8188
PIDFILE = "/content/comfy.pid"
LOGFILE = "/content/comfy.log"

def alive(pid):
    try:
        os.kill(pid, 0); return True
    except (ProcessLookupError, PermissionError):
        return False
    except Exception:
        return False

def read_pid():
    if os.path.exists(PIDFILE):
        try: return int(open(PIDFILE).read().strip())
        except: return None
    return None

def start():
    if (pid := read_pid()) and alive(pid):
        print(f"already running, pid={pid}")
        return
    log = open(LOGFILE, "w")
    p = subprocess.Popen(
        ["python", "main.py", "--listen", "0.0.0.0", "--port", str(PORT),
         "--output-directory", os.path.join(COMFY, "output")],
        cwd=COMFY, stdout=log, stderr=subprocess.STDOUT,
        start_new_session=True)
    open(PIDFILE, "w").write(str(p.pid))
    print(f"launched pid={p.pid}, waiting for boot...", flush=True)
    import urllib.request
    for _ in range(60):
        time.sleep(1)
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=1)
            print(f"READY on http://127.0.0.1:{PORT}  (HTTP 200)")
            return
        except Exception:
            pass
    print("TIMEOUT — server did not respond in 60s. Check: python server.py log")

def stop():
    pid = read_pid()
    if pid and alive(pid):
        os.kill(pid, signal.SIGTERM)
        print(f"stopped pid={pid}")
    else:
        print("not running")
    if os.path.exists(PIDFILE): os.remove(PIDFILE)

def status():
    pid = read_pid()
    if pid and alive(pid):
        print(f"RUNNING pid={pid} port={PORT}")
    else:
        print("STOPPED")

def show_log(n=30):
    if os.path.exists(LOGFILE):
        lines = open(LOGFILE).read().splitlines()
        print("\n".join(lines[-n:]))
    else:
        print("no log file yet")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "start": start()
    elif cmd == "stop": stop()
    elif cmd == "status": status()
    elif cmd == "log": show_log(int(sys.argv[2]) if len(sys.argv) > 2 else 30)
    else:
        print(__doc__); sys.exit(1)
