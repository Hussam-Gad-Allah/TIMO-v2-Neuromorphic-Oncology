#!/usr/bin/env python3
"""
Virtual Drosophila 3D Cyber-Space Visualizer Launcher.

Run this script to open the 3D holographic state-space visualizer in a dedicated,
sleek research window:
    python view_fly_3d.py

Features:
- Translucent bioluminescent Drosophila melanogaster model with high-frequency flapping wings.
- Cyber-space research environment (Holographic coordinate grid, starfield, attractor orbs).
- Flight trajectory ribbon tracing the search path through state-space.
- Real-time telemetry HUD (Simulation step, unsat clauses, Hamming distance, sensory-motor states).
"""

import http.server
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import webbrowser

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
PORT = 8765
HOST = "127.0.0.1"


def find_latest_run(explicit_dir=None):
    if explicit_dir and Path(explicit_dir).exists():
        p = Path(explicit_dir)
        if (p / "trajectory.jsonl").exists() or (p / "02_brain_state_timeseries.jsonl").exists():
            return p

    search_dirs = [
        ROOT / "logs",
        ROOT / "flyfly_oncology" / "logs",
        ROOT / "flyfly_sat" / "results" / "runs",
        ROOT / "results" / "runs",
    ]
    all_runs = []
    for s_dir in search_dirs:
        if s_dir.exists():
            for traj in s_dir.glob("**/trajectory.jsonl"):
                run_folder = traj.parent
                if run_folder.is_dir() and run_folder not in all_runs:
                    all_runs.append(run_folder)
            for traj in s_dir.glob("**/02_brain_state_timeseries.jsonl"):
                run_folder = traj.parent
                if run_folder.is_dir() and run_folder not in all_runs:
                    all_runs.append(run_folder)
    if not all_runs:
        return None
    all_runs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    return all_runs[0]


class SpatialFlightEngine:
    """Simulates realistic 3D spatial path integration in probability state-space."""
    def __init__(self):
        self.cur_x = 0.0
        self.cur_z = 0.0
        self.heading = 0.0
        self.min_u = 9999
        self.max_u = 0

    def reset(self):
        self.cur_x = 0.0
        self.cur_z = 0.0
        self.heading = 0.0
        self.min_u = 9999
        self.max_u = 0

    def step(self, u, m, step_val, is_uf100=False):
        import math
        fp_thresh = 17 if is_uf100 else 8
        is_fast = (m == "cruise") if m else not (is_uf100 and u <= fp_thresh)

        is_new_best = False
        if u < self.min_u:
            self.min_u = u
            is_new_best = True
        if u > self.max_u:
            self.max_u = u
        is_solution = (u == 0)

        if is_fast:
            # Ballistic Lévy exploration across the cosmic state-space
            speed = 1.85
            turn = 0.045 + 0.16 * math.sin(step_val * 0.028)
        else:
            # Local Area-Restricted Search spiraling tightly inside the local basin
            speed = 0.65
            turn = 0.38 + 0.10 * math.sin(step_val * 0.075)

        self.heading += turn

        # Soft boundary turning within [-70, 70]
        if abs(self.cur_x) > 60.0:
            self.heading += (-0.20 if self.cur_x > 0 else 0.20)
        if abs(self.cur_z) > 60.0:
            self.heading += (-0.20 if self.cur_z > 0 else 0.20)

        self.cur_x += speed * math.cos(self.heading)
        self.cur_z += speed * math.sin(self.heading)
        self.cur_x = max(-72.0, min(72.0, self.cur_x))
        self.cur_z = max(-72.0, min(72.0, self.cur_z))

        # Y position represents energy level (higher unsat = flying higher above grid)
        y_pos = (min(50.0, float(u)) * 0.62) - 9.0 + (math.sin(step_val * 0.12) * 1.4)

        return round(self.cur_x, 2), round(y_pos, 2), round(self.cur_z, 2), is_fast, is_new_best, is_solution


GLOBAL_FLIGHT_ENGINE = SpatialFlightEngine()


def export_trajectory_for_web(run_dir):
    """Downsample and project run trajectory to 3D state-space coordinate funnel."""
    if not run_dir:
        return None
    traj_f = run_dir / "trajectory.jsonl"
    if not traj_f.exists():
        traj_f = run_dir / "02_brain_state_timeseries.jsonl"
    if not traj_f.exists():
        return None

    samples = []
    with open(traj_f, "r", encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
                if "unsat" in d and "u" not in d:
                    d["u"] = d["unsat"]
                if "step" in d and "s" not in d:
                    d["s"] = d["step"]
                if "active_drugs" in d and "h" not in d:
                    d["h"] = len(d["active_drugs"])
                samples.append(d)
            except Exception:
                pass
    if not samples:
        return None

    # Check for verified biomedical attractor to append terminal discovery point with ACTUAL run unsat
    actual_min_u = min((s.get("best_u", s.get("u", 9999)) for s in samples), default=0)
    sol_f = run_dir / "04_final_biomedical_solution.json"
    if sol_f.exists():
        try:
            with open(sol_f, "r", encoding="utf-8") as sf:
                sol_d = json.load(sf)
                if sol_d.get("status") == "biomedical_verified" or sol_d.get("verification_verdict") == "VERIFIED_THERAPEUTIC_ATTRACTOR":
                    d_list = sol_d.get("active_drugs", [])
                    st = sol_d.get("steps_taken", (samples[-1].get("s", 0) + 10))
                    term_u = sol_d.get("best_unsat", actual_min_u)
                    actual_min_u = min(actual_min_u, term_u)
                    samples.append({"s": st, "u": term_u, "best_u": actual_min_u, "h": len(d_list), "drugs": d_list, "m": "solution"})
        except Exception:
            pass

    chk_f = run_dir / "checkpoint.json"
    if chk_f.exists():
        try:
            with open(chk_f, "r", encoding="utf-8") as cf:
                chk_d = json.load(cf)
                if chk_d.get("best_unsat") is not None:
                    actual_min_u = min(actual_min_u, int(chk_d["best_unsat"]))
        except Exception:
            pass

    step_skip = max(1, len(samples) // 700)
    downsampled = samples[::step_skip]
    if samples[-1].get("m") == "solution" and downsampled[-1].get("m") != "solution":
        downsampled.append(samples[-1])

    engine = SpatialFlightEngine()
    web_points = []
    for i, s in enumerate(downsampled):
        u = s.get("u", 20)
        h = s.get("h", -1)
        m = s.get("m")
        step_val = s.get("s", i * 2000)
        is_uf100 = "uf100" in (run_dir.name.lower() if run_dir else "")
        crit_thresh = 8 if is_uf100 else 3
        fp_thresh = 17 if is_uf100 else 8

        x, y_pos, z, is_fast, is_new_best, is_solution = engine.step(u, m, step_val, is_uf100)

        web_points.append({
            "pos": {"x": x, "y": y_pos, "z": z},
            "step": step_val,
            "unsat": u,
            "hamming": h if h >= 0 else 6,
            "phase": "Area-Restricted Foraging (Decelerated)" if u <= crit_thresh else ("Food-Patch Descent" if u <= fp_thresh else "Lévy Casting"),
            "state": "Reflex Chain & Deceleration Active" if u <= crit_thresh else "Connectome Baseline",
            "is_new_best": is_new_best,
            "is_solution": is_solution,
            "drugs": s.get("drugs", [])
        })

    max_u = max((s.get("u", 0) for s in samples), default=0)
    min_u = actual_min_u

    out_p = ROOT / "flyfly_sat" / "assets" / "current_trajectory.json"
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump({"bench": run_dir.name, "max_unsat": max_u, "min_unsat": min_u, "points": web_points}, f)
    return out_p


LIVE_STATE = {
    "run_dir": None,
    "last_pos": 0,
    "latest_step": 0,
    "latest_u": 0,
    "latest_h": -1,
    "max_u": 0,
    "min_u": 9999,
    "solution_logged": False,
    "noise": 2.0,
    "cells": 200,
    "cell_steps": 1500,
    "drugs": []
}


def get_live_stream_data():
    """Extract incremental updates from active simulation with zero GPU/CPU overhead."""
    latest = find_latest_run()
    if not latest:
        return {"active": False, "points": []}

    traj_f = latest / "trajectory.jsonl"
    if not traj_f.exists():
        return {"active": False, "points": []}

    # Reset offset if run changed or initial run (NEVER load stale min_unsat from previous cached run)
    if LIVE_STATE["run_dir"] != latest:
        LIVE_STATE["run_dir"] = latest
        LIVE_STATE["last_pos"] = 0
        LIVE_STATE["max_u"] = 0
        LIVE_STATE["min_u"] = 9999
        LIVE_STATE["solution_logged"] = False
        GLOBAL_FLIGHT_ENGINE.reset()

    new_points = []
    try:
        with open(traj_f, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(LIVE_STATE["last_pos"])
            lines = f.readlines()
            LIVE_STATE["last_pos"] = f.tell()

        if lines:
            # Track true min_u and max_u across ALL lines (even between downsampled display frames)
            for raw_l in lines:
                raw_l = raw_l.strip()
                if not raw_l:
                    continue
                try:
                    rd = json.loads(raw_l)
                    ru = rd.get("u", rd.get("unsat"))
                    rbu = rd.get("best_u", rd.get("best_unsat", ru))
                    if ru is not None:
                        LIVE_STATE["max_u"] = max(LIVE_STATE["max_u"], int(ru))
                        LIVE_STATE["min_u"] = min(LIVE_STATE["min_u"], int(ru))
                    if rbu is not None:
                        LIVE_STATE["min_u"] = min(LIVE_STATE["min_u"], int(rbu))
                except Exception:
                    pass

            stride = max(1, len(lines) // 20)
            sampled = lines[::stride]
            if lines[-1] != sampled[-1]:
                sampled.append(lines[-1])
            for line in sampled:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    if "noise" in d:
                        LIVE_STATE["noise"] = d["noise"]
                    if "cells" in d:
                        LIVE_STATE["cells"] = d["cells"]
                    if "cell_steps" in d:
                        LIVE_STATE["cell_steps"] = d["cell_steps"]
                    if "drugs" in d:
                        LIVE_STATE["drugs"] = d["drugs"]

                    u = d.get("u", 20)
                    best_u = d.get("best_u", u)
                    h = d.get("h", -1)
                    m = d.get("m")
                    step_val = d.get("s", 0)
                    is_uf100 = "uf100" in (latest.name.lower() if latest else "")

                    # Biological progressive 3D spatial path integration
                    x, y_pos, z, is_fast, is_new_best, is_solution = GLOBAL_FLIGHT_ENGINE.step(u, m, step_val, is_uf100)

                    LIVE_STATE["latest_step"] = step_val
                    LIVE_STATE["latest_u"] = u
                    LIVE_STATE["latest_h"] = h
                    LIVE_STATE["max_u"] = max(LIVE_STATE["max_u"], u)
                    LIVE_STATE["min_u"] = min(LIVE_STATE["min_u"], u, best_u)

                    # Bio-electric calculation of Drosophila SNN (Calibrated per tier):
                    import math
                    n_clauses = 430.0 if is_uf100 else 218.0
                    hunger = u / n_clauses
                    base_cpg = 0.8 + 4.2 * min(1.0, hunger * 5.0)
                    bio_current = round(base_cpg * (1.0 + 0.15 * math.sin(step_val * 0.1)), 2)
                    v_norm = 15.0 if is_uf100 else 6.0
                    vm_voltage = round(-65.0 + 22.0 * min(1.0, (u / v_norm)) + 2.0 * math.sin(step_val * 0.25), 1)
                    spike_freq = round(170.0 + 50.0 * min(1.0, hunger * 4.0) + 8.0 * math.cos(step_val * 0.15), 1)
                    u_loss = 2.2 if is_uf100 else 3.8
                    discharge_pct = round(max(10.0, min(100.0, 100.0 - (u * u_loss))), 1)

                    LIVE_STATE["bio_current"] = bio_current
                    LIVE_STATE["vm_voltage"] = vm_voltage
                    LIVE_STATE["spike_freq"] = spike_freq
                    LIVE_STATE["discharge_pct"] = discharge_pct

                    mode_flag = d.get("m")
                    if mode_flag == "slow":
                        phase_label = "🎯 SLOW CASTING (Micro-Basin Focus)"
                        is_fast = False
                    elif mode_flag == "cruise":
                        phase_label = "🚀 FAST CRUISE (Ballistic Search)"
                        is_fast = True
                    else:
                        is_fast = not (is_uf100 and u <= 17)
                        phase_label = "🚀 FAST CRUISE (Ballistic Search)" if is_fast else "🎯 SLOW CASTING (Micro-Basin Focus)"

                    LIVE_STATE["flight_phase"] = phase_label
                    LIVE_STATE["is_fast"] = is_fast

                    new_points.append({
                        "x": x,
                        "y": y_pos,
                        "z": z,
                        "s": step_val,
                        "u": u,
                        "h": h,
                        "electric": bio_current,
                        "voltage": vm_voltage,
                        "freq": spike_freq,
                        "discharge": discharge_pct,
                        "phase": phase_label,
                        "is_fast": is_fast,
                        "is_new_best": is_new_best,
                        "is_solution": is_solution,
                        "drugs": LIVE_STATE.get("drugs", [])
                    })
                except Exception:
                    pass
    except Exception:
        pass

    # Also check checkpoint.json if present for exact best_unsat from solver
    chk_f = latest / "checkpoint.json"
    if chk_f.exists():
        try:
            with open(chk_f, "r", encoding="utf-8") as cf:
                chk_d = json.load(cf)
                if chk_d.get("best_unsat") is not None:
                    LIVE_STATE["min_u"] = min(LIVE_STATE["min_u"], int(chk_d["best_unsat"]))
        except Exception:
            pass

    sol_f = latest / "04_final_biomedical_solution.json"
    if sol_f.exists() and not LIVE_STATE.get("solution_logged", False):
        try:
            with open(sol_f, "r", encoding="utf-8") as sf:
                sol_d = json.load(sf)
                if sol_d.get("status") == "biomedical_verified" or sol_d.get("verification_verdict") == "VERIFIED_THERAPEUTIC_ATTRACTOR":
                    LIVE_STATE["solution_logged"] = True
                    d_list = sol_d.get("active_drugs", [])
                    st = sol_d.get("steps_taken", LIVE_STATE["latest_step"] + 10)
                    real_min_u = sol_d.get("best_unsat", LIVE_STATE["min_u"] if LIVE_STATE["min_u"] < 9999 else LIVE_STATE["latest_u"])
                    real_final_u = sol_d.get("final_unsat", real_min_u)
                    LIVE_STATE["min_u"] = min(LIVE_STATE["min_u"], int(real_min_u))
                    LIVE_STATE["latest_u"] = int(real_final_u)
                    is_uf100 = "uf100" in (latest.name.lower() if latest else "")
                    x, y_pos, z, is_fast, is_new_best, is_solution = GLOBAL_FLIGHT_ENGINE.step(LIVE_STATE["min_u"], "solution", st, is_uf100)
                    LIVE_STATE["latest_step"] = st
                    LIVE_STATE["drugs"] = d_list
                    LIVE_STATE["flight_phase"] = f"🎯 VERIFIED ATTRACTOR ({LIVE_STATE['min_u']} UNSAT)"
                    LIVE_STATE["is_fast"] = False
                    new_points.append({
                        "x": x,
                        "y": y_pos,
                        "z": z,
                        "s": st,
                        "u": LIVE_STATE["min_u"],
                        "h": len(d_list),
                        "electric": 4.85,
                        "voltage": -68.0,
                        "freq": 220.0,
                        "discharge": 100.0,
                        "phase": f"🎯 VERIFIED ATTRACTOR ({LIVE_STATE['min_u']} UNSAT)",
                        "is_fast": False,
                        "is_new_best": True,
                        "is_solution": True,
                        "drugs": d_list
                    })
        except Exception:
            pass

    return {
        "active": True,
        "run_name": latest.name.split("_full")[0],
        "step": LIVE_STATE["latest_step"],
        "unsat": LIVE_STATE["latest_u"],
        "max_unsat": LIVE_STATE["max_u"],
        "min_unsat": (LIVE_STATE["min_u"] if LIVE_STATE["min_u"] < 9999 else LIVE_STATE["latest_u"]),
        "hamming": LIVE_STATE["latest_h"],
        "phase": LIVE_STATE.get("flight_phase", "Area-Restricted Foraging"),
        "is_fast": LIVE_STATE.get("is_fast", False),
        "bio_current": LIVE_STATE.get("bio_current", 2.45),
        "vm_voltage": LIVE_STATE.get("vm_voltage", -52.4),
        "spike_freq": LIVE_STATE.get("spike_freq", 195.0),
        "discharge_pct": LIVE_STATE.get("discharge_pct", 75.0),
        "noise": LIVE_STATE.get("noise", 2.0),
        "cells": LIVE_STATE.get("cells", 200),
        "cell_steps": LIVE_STATE.get("cell_steps", 1500),
        "drugs": LIVE_STATE.get("drugs", []),
        "points": new_points
    }


class VisualizerHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/live"):
            data = get_live_stream_data()
            payload = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def log_message(self, format, *args):
        pass


def launch_server():
    server = http.server.HTTPServer((HOST, PORT), VisualizerHTTPHandler)
    server.serve_forever()


def open_dedicated_window(url):
    """Launch in dedicated application mode (frameless, borderless desktop app look)."""
    edge_paths = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    chrome_paths = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ]

    for exe in edge_paths + chrome_paths:
        if exe.exists():
            try:
                cmd = [
                    str(exe),
                    f"--app={url}",
                    "--window-size=1100,750",
                    "--window-position=120,80"
                ]
                subprocess.Popen(cmd)
                return True
            except Exception:
                pass

    # Fallback to standard system browser
    webbrowser.open(url)
    return False


def main():
    print("=" * 68)
    print("      VIRTUAL DROSOPHILA 3D CYBER-SPACE RESEARCH VISUALIZER")
    print("=" * 68)
    print("  [+] Starting local 3D rendering server on port", PORT, "...")

    server_thread = threading.Thread(target=launch_server, daemon=True)
    server_thread.start()
    time.sleep(0.3)

    explicit = sys.argv[1] if len(sys.argv) > 1 else None
    latest_run = find_latest_run(explicit)
    if latest_run:
        export_trajectory_for_web(latest_run)
    run_param = f"?run={latest_run.name}" if latest_run else ""
    app_url = f"http://{HOST}:{PORT}/fly_3d_visualizer.html{run_param}"

    print(f"  [+] Active benchmark stream: {latest_run.name if latest_run else 'Synthetic Bio-Foraging Mode'}")
    print(f"  [+] Opening dedicated 3D holographic research window...")
    is_app = open_dedicated_window(app_url)

    if is_app:
        print("  [+] Dedicated 3D window launched successfully!")
    else:
        print(f"  [+] Visualizer opened in browser: {app_url}")

    print("\n  Tip: You can use Orbit 3D to rotate/zoom, Chase Cam to follow the fly,")
    print("       and the slider at the bottom to scrub through simulation steps.")
    print("  Press Ctrl+C in this console when you wish to close the server.")
    print("=" * 68)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  [!] 3D Visualizer closed.")


if __name__ == "__main__":
    main()
