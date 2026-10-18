import types
import sys
from pathlib import Path
_cur_dir = Path(__file__).resolve().parent
_root_dir = _cur_dir if (_cur_dir / "data").exists() else _cur_dir.parent
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))
if "flyfly_oncology" not in sys.modules and (_root_dir / "fly_oncology_solver.py").exists():
    _pkg = types.ModuleType("flyfly_oncology")
    _pkg.__path__ = [str(_root_dir)]
    _pkg.__file__ = str(_root_dir / "__init__.py")
    sys.modules["flyfly_oncology"] = _pkg

#!/usr/bin/env python3
"""
Prospective Unsolved & Orphan Cancers Multi-Noise Discovery Runner.
Executes TIMO v2 (23,214-neuron FlyWire SNN + in-loop asynchronous GAUS verification)
across all 12 Prospective Unsolved Cancer benchmarks at 2%, 5%, 10%, and 18% noise.
Saves full telemetry, CSV matrices, and clinical discovery reports directly inside:
  - F:\\Research II - PhD\\flyfly_oncology\\logs\\sweep_unsolved_prospective_<ts>\\
  - F:\\Research II - PhD\\flyfly_oncology\\results\\clinical_reports\\unsolved_12_cancers_prospective_discovery_report.md
  - F:\\Research II - PhD\\flyfly_oncology\\results\\clinical_reports\\unsolved_12_cancers_prospective_discovery_report.csv
"""

import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

_HERE = Path(__file__).resolve().parent
ROOT = _HERE if (_HERE / 'data').exists() else _HERE.parent
sys.path.insert(0, str(ROOT))

from flyfly_oncology.fly_oncology_solver import FlyOncologySolver, OncologySolverConfig
from flyfly_oncology.telemetry_logger import OncologyTelemetryLogger
from flyfly_oncology.dataset_downloader import load_model

NOISE_TIERS = [0.02, 0.05, 0.10, 0.18]


def find_graph_path() -> Path:
    for c in [
        ROOT / "flyfly_sat" / "data" / "processed" / "graph_core.pt",
        ROOT / "data" / "processed" / "graph_core.pt",
    ]:
        if c.exists():
            return c
    raise FileNotFoundError("Could not find graph_core.pt!")


def run_prospective_unsolved_study():
    graph_path = find_graph_path()
    pt_dir = (ROOT / "data" if (ROOT / "data").exists() else ROOT / "flyfly_oncology" / "data") / "benchmarks" / "unsolved_patients"
    cnf_files = sorted(list(pt_dir.glob("unsolved_pt*.cnf")))
    model_dict = load_model("unsolved")

    ledger_path = pt_dir / "UNSOLVED_PATIENTS_CLINICAL_TRUTH_LEDGER.json"
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sweep_dir = (ROOT / "logs" if (ROOT / "logs").exists() else ROOT / "flyfly_oncology" / "logs") / f"sweep_{ts}_unsolved_prospective"
    sweep_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 88)
    print("  TIMO v2 PROSPECTIVE DISCOVERY FRONTIER: 12 UNSOLVED & ORPHAN CANCERS")
    print(f"  Connectome Substrate : {graph_path.name} (23,214 Spiking Neurons, FlyWire v783)")
    print(f"  Noise Perturbation   : {[f'{round(n*100,1)}%' for n in NOISE_TIERS]}")
    print("=" * 88)

    sweep_matrix = {}
    for cnf_path in cnf_files:
        sweep_matrix[cnf_path.name] = {
            "model": model_dict["name"],
            "results": {}
        }

    for n_prob in NOISE_TIERS:
        pct_int = int(round(n_prob * 100))
        tier_dir = sweep_dir / f"noise_{pct_int:02d}pct"
        tier_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n>>> RUNNING NOISE TIER: {n_prob*100:.1f}% ({tier_dir.name})")

        for idx, cnf_path in enumerate(cnf_files, 1):
            map_path = cnf_path.with_suffix(".mapping.json")
            with open(map_path, "r", encoding="utf-8") as f:
                mapping = json.load(f)

            cfg = OncologySolverConfig(
                max_steps=4000,
                seed=42,
                max_allowed_drugs=3,
                target_apoptosis=90.0,
                validation_noise=n_prob
            )
            run_name = f"{cnf_path.stem}_noise{pct_int:02d}_seed42"
            logger = OncologyTelemetryLogger(
                base_log_dir=tier_dir,
                run_name=run_name,
                noise_percent=n_prob * 100.0,
                n_cells=200,
                cell_steps=1500
            )
            t0 = time.time()
            solver = FlyOncologySolver(
                cnf_path=cnf_path,
                mapping_path=map_path,
                model_dict=model_dict,
                graph_path=graph_path,
                cfg=cfg,
                logger=logger,
                pinned_vars=mapping.get("pinned_vars", {})
            )
            summary = solver.solve()
            elapsed = time.time() - t0

            drugs = summary.get("active_drugs", [])
            apop_clean = summary.get("apoptosis_rate_clean", 0.0)
            apop_noisy = summary.get("apoptosis_rate_noisy", 0.0)
            steps = summary.get("steps_taken", 0)

            sweep_matrix[cnf_path.name]["results"][n_prob] = {
                "drugs": drugs,
                "apoptosis_clean": apop_clean,
                "apoptosis_noisy": apop_noisy,
                "steps": steps,
                "time": round(elapsed, 2),
                "status": summary.get("status", "solved")
            }
            print(
                f"  [{idx:02d}/12] {cnf_path.stem:<38} | Drugs: {' + '.join(drugs):<22} | "
                f"Clean: {apop_clean:>5.1f}% | Noisy({pct_int}%): {apop_noisy:>5.1f}% | Steps: {steps:<4} ({elapsed:.2f}s)"
            )

    # Save Prospective Discovery Report (MD & CSV) in clinical_reports and sweep_dir
    reports_dir = (ROOT / "results" if (ROOT / "results").exists() else ROOT / "flyfly_oncology" / "results") / "clinical_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    md_out = reports_dir / "unsolved_12_cancers_prospective_discovery_report.md"
    csv_out = reports_dir / "unsolved_12_cancers_prospective_discovery_report.csv"

    md_lines = [
        "# Prospective Discovery Report: 12 Unsolved & Orphan Cancers (Zero Established Curative Therapy)",
        f"**Experiment Session:** `{sweep_dir.name}`  ",
        "**Computational Architecture:** TIMO v2 — *Drosophila melanogaster* Whole-Brain Connectome SNN (23,214 Neurons, FlyWire v783)  ",
        "**Verification Engine:** In-Loop General Asynchronous Updating Scheme (GAUS; 200 stochastic cells x 1,500 steps per candidate)  ",
        "**Stochastic Perturbation Spectrum:** 2.0% (Baseline), 5.0% (Microenvironment Stress), 10.0% (Transcriptional Drift), 18.0% (Thermal Chaos Boundary)  ",
        "",
        "---",
        "",
        "## Prospective Synthetic Lethal Discovery Ledger",
        "| # | Benchmark ID & Unsolved Cancer Subtype | Oncogenic Driver & Peer-Reviewed Reference | Failed / Palliative Hospital Standard | Clinical Status | Molecular Lock Mechanism | TIMO v2 Proposed Novel Combination | Multi-Noise Apoptosis (2% / 5% / 10% / 18%) | Steps (2%) |",
        "| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |"
    ]

    csv_rows = []
    for idx, (b_name, b_info) in enumerate(sweep_matrix.items(), 1):
        pt_id = b_name.replace(".cnf", "")
        led = ledger.get(pt_id, {})
        ch = led.get("clinical_history", {})

        sub = ch.get("subtype", pt_id)
        drv = ch.get("primary_driver", "")
        rx = ch.get("hospital_treatment", "")
        out = ch.get("real_world_outcome", "")
        res_mech = ch.get("known_resistance_mechanism", "")

        apops = []
        regimens = []
        for n in NOISE_TIERS:
            r = b_info["results"].get(n, {})
            apops.append(f"**{r.get('apoptosis_noisy', 0.0):.1f}%**")
            d_str = " + ".join(r.get("drugs", []))
            if d_str and d_str not in regimens:
                regimens.append(d_str)

        regimen_display = " / ".join(f"`{rg}`" for rg in regimens[:2]) if regimens else "—"
        apop_display = " / ".join(apops)
        steps_2pct = b_info["results"].get(0.02, {}).get("steps", 0)

        md_lines.append(
            f"| **{idx:02d}** | **{pt_id}**<br>*{sub}* | {drv} | {rx} | **{out}** | {res_mech} | {regimen_display} | {apop_display} | {steps_2pct} |"
        )

        csv_rows.append({
            "idx": idx,
            "patient_id": pt_id,
            "subtype": sub,
            "driver_and_reference": drv,
            "palliative_standard_care": rx,
            "clinical_status": out,
            "resistance_lock": res_mech,
            "timo_v2_discovered_regimen": " | ".join(regimens),
            "apop_2pct": b_info["results"].get(0.02, {}).get("apoptosis_noisy", 0.0),
            "apop_5pct": b_info["results"].get(0.05, {}).get("apoptosis_noisy", 0.0),
            "apop_10pct": b_info["results"].get(0.10, {}).get("apoptosis_noisy", 0.0),
            "apop_18pct": b_info["results"].get(0.18, {}).get("apoptosis_noisy", 0.0),
            "steps_2pct": steps_2pct
        })

    md_content = "\n".join(md_lines) + "\n"
    md_out.write_text(md_content, encoding="utf-8")
    (sweep_dir / "UNSOLVED_12_CANCERS_PROSPECTIVE_DISCOVERY_REPORT.md").write_text(md_content, encoding="utf-8")

    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    print("\n" + "=" * 88)
    print(f"  [✓] Prospective Discovery Markdown Saved : {md_out}")
    print(f"  [✓] Prospective Discovery CSV Saved      : {csv_out}")
    print(f"  [✓] Sweep Telemetry Folder               : {sweep_dir}")
    print("=" * 88)


if __name__ == "__main__":
    run_prospective_unsolved_study()
