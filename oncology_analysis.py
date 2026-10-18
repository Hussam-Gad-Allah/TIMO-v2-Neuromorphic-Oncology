"""
Oncology Run Analysis & Plotter.
Generates UF100-identical diagnostic plots for oncology runs:
1. plot_timeline.png: Steps vs Unsatisfied Clauses & Drug Interventions
2. plot_3d.png: 3D Trajectory in State Space (Steps x Unsat x Drugs) with Solution Touchdown Star
"""

import json
from pathlib import Path
import numpy as np


def analyze_and_plot_oncology(run_dir: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    run_dir = Path(run_dir)
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
                u = d.get("u", d.get("unsat", 0))
                s = d.get("s", d.get("step", 0))
                h = d.get("h", len(d.get("active_drugs", [])))
                samples.append({"s": s, "u": u, "h": h})
            except Exception:
                pass

    if not samples:
        return None

    s = np.array([r["s"] for r in samples])
    u = np.array([r["u"] for r in samples])
    h = np.array([r["h"] for r in samples])
    best_u = np.minimum.accumulate(u)

    # 1. Timeline Plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    axes[0].plot(s, u, color="steelblue", lw=0.8, alpha=0.8, label="Unsatisfied Biological Clauses")
    axes[0].step(s, best_u, color="crimson", lw=1.5, where="post", label="Best Unsat Clauses")
    axes[0].set_ylabel("Unsatisfied Clauses")
    axes[0].set_title(f"Oncology SNN Simulation Timeline - {run_dir.name}")
    axes[0].grid(True, linestyle=":", alpha=0.6)
    axes[0].legend(loc="upper right")

    axes[1].plot(s, h, color="darkgreen", lw=1.2, label="Active Drug Interventions")
    axes[1].set_ylabel("Active Target Count")
    axes[1].set_xlabel("Simulation Steps (ms)")
    axes[1].grid(True, linestyle=":", alpha=0.6)
    axes[1].legend(loc="upper right")

    fig.tight_layout()
    timeline_path = run_dir / "plot_timeline.png"
    fig.savefig(timeline_path, dpi=130)
    plt.close(fig)

    # 2. 3D State Space Trajectory Plot (Exact UF100 style)
    fig_3d = plt.figure(figsize=(11, 8))
    ax = fig_3d.add_subplot(111, projection="3d")

    ax.plot(s, u, h, color="royalblue", lw=0.9, alpha=0.85, label="Fly Search Trajectory")
    ax.scatter([s[0]], [u[0]], [h[0]], c="forestgreen", s=90, label="Start (Untreated Cancer Attractor)")
    ax.scatter([s[-1]], [u[-1]], [h[-1]], c="crimson", s=90, label="End State")

    if u[-1] == 0:
        ax.scatter([s[-1]], [0], [h[-1]], marker="*", c="lime", s=400, edgecolors="black",
                   label=f"REMISSION TOUCHDOWN (Apoptosis >= 90%, Unsat=0)")
    else:
        ax.scatter([s[-1]], [0], [0], marker="*", c="gold", s=250, edgecolors="black",
                   label="Curative Target Attractor")

    ax.set_xlabel("Simulation Step")
    ax.set_ylabel("Unsatisfied Clauses")
    ax.set_zlabel("Active Drug Targets")
    ax.set_title(f"3D Fly Connectome Trajectory - {run_dir.name}")
    ax.legend(loc="upper right")
    fig_3d.tight_layout()

    plot_3d_path = run_dir / "plot_3d.png"
    fig_3d.savefig(plot_3d_path, dpi=130)
    plt.close(fig_3d)

    print(f"[OncologyAnalysis] Plots saved to {run_dir.name}:")
    print(f"  -> Timeline: {timeline_path.name}")
    print(f"  -> 3D Plot : {plot_3d_path.name}")
    return timeline_path, plot_3d_path
