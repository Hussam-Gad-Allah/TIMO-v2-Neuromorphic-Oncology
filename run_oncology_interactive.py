#!/usr/bin/env python3
"""
Interactive Virtual Fly Oncology Discovery Engine.
Run this script directly from terminal or PyCharm:
    python run_oncology_interactive.py

Couples the Drosophila FlyWire Connectome SNN (23,214 cells)
with Biomedical Cancer Boolean Networks (T-LGL Leukemia & AML)
and In-Loop Asynchronous Temporal Cell Validation.

Supports Single Benchmark Runs & Multi-File Sequential Batch Queues.
"""

import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
    from flyfly_oncology.fly_oncology_solver import FlyOncologySolver, OncologySolverConfig
    from flyfly_oncology.telemetry_logger import OncologyTelemetryLogger
    from flyfly_oncology.oncology_analysis import analyze_and_plot_oncology
    from flyfly_oncology.master_ledger import record_experiment_result
except ImportError as err:
    print(f"[!] Error importing flyfly_oncology: {err}")
    sys.exit(1)


def is_port_in_use(port: int = 8765, host: str = "127.0.0.1") -> bool:
    """Check if 3D Visualizer local HTTP server is already running."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False


def generate_sweep_comparison_report(sweep_dir: Path, sweep_matrix: dict, noise_tiers: list):
    """Generates Markdown and CSV Master Comparison Reports across all tested noise tiers."""
    md_path = sweep_dir / "NOISE_ROBUSTNESS_COMPARISON_REPORT.md"
    csv_path = sweep_dir / "NOISE_ROBUSTNESS_COMPARISON_REPORT.csv"

    tier_labels = [f"Noise {round(n*100, 1)}%" for n in noise_tiers]

    md_lines = [
        "# Master Multi-Noise Robustness Report: Virtual Drosophila Connectome SNN",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        "**Connectome Model:** Drosophila Melanogaster Whole-Brain Connectome (23,214 cells, FlyWire)  ",
        "**Theoretical Framework:** Asynchronous Boolean Attractor In-Loop Verification (Garg 2008 / Saadatpour 2011 / Palma 2021)  ",
        f"**Evaluated Noise Tiers:** {', '.join(tier_labels)}  ",
        f"**Total Benchmarks Evaluated:** {len(sweep_matrix)}  ",
        "",
        "---",
        "",
        "## Multi-Tier Robustness Matrix",
        "| # | Benchmark | Model | " + " | ".join(tier_labels) + " | Resilience Verdict |",
        "| :---: | :--- | :---: | " + " | ".join(":---:" for _ in tier_labels) + " | :--- |"
    ]

    csv_rows = []

    for idx, (b_name, b_info) in enumerate(sweep_matrix.items(), 1):
        row_cells = []
        apop_vals = []
        for n in noise_tiers:
            res = b_info["results"].get(n, {})
            apop = res.get("apoptosis_noisy", 0.0)
            apop_vals.append(apop)
            drugs = res.get("drugs", [])
            drugs_str = "+".join(drugs) if drugs else "None"
            cell_str = f"**{apop:.1f}%** (`{drugs_str}`)"
            row_cells.append(cell_str)

        # Scientific Verdict classification based on attractor stability
        if len(apop_vals) >= 4 and all(a >= 90.0 for a in apop_vals):
            verdict = "💎 INVINCIBLE ATTRACTOR (Survives all tiers up to 18%)"
        elif len(apop_vals) >= 3 and all(a >= 90.0 for a in apop_vals[:3]):
            verdict = "⭐ HIGH ROBUSTNESS (Survives up to 10% stress)"
        elif len(apop_vals) >= 2 and all(a >= 90.0 for a in apop_vals[:2]):
            verdict = "🛡️ MODERATE ROBUSTNESS (Survives up to 5% volatility)"
        elif apop_vals and apop_vals[0] >= 90.0:
            verdict = "⚠️ SENSITIVE BASIN (Standard 2% baseline only)"
        else:
            verdict = "❌ INEFFECTIVE / SUB-THRESHOLD"

        md_lines.append(
            f"| **{idx:02d}** | `{b_name}` | {b_info.get('model', 'Oncology')} | " + " | ".join(row_cells) + f" | {verdict} |"
        )

        csv_row = {
            "idx": idx,
            "benchmark": b_name,
            "model": b_info.get("model", "Oncology"),
            "verdict": verdict
        }
        for n in noise_tiers:
            res = b_info["results"].get(n, {})
            pct_tag = f"noise_{int(round(n*100)):02d}pct"
            csv_row[f"{pct_tag}_apoptosis"] = res.get("apoptosis_noisy", 0.0)
            csv_row[f"{pct_tag}_drugs"] = "+".join(res.get("drugs", []))
            csv_row[f"{pct_tag}_steps"] = res.get("steps", 0)
        csv_rows.append(csv_row)

    md_lines.extend([
        "",
        "---",
        "",
        "## Scientific Interpretation of Noise Tiers",
        "1. **Tier 1 (2.0% Noise - Standard Literature):** Baseline physiological thermal fluctuation in living mammalian cells (Garg 2008 / Saadatpour 2011).",
        "2. **Tier 2 (5.0% Noise - High Volatility):** Emulates severe cytokine storm, chemotherapy-induced genotoxic stress, and inflammatory tumor microenvironments.",
        "3. **Tier 3 (10.0% Noise - Hyper-Perturbation):** Maximum resilience stress test; tests whether the drug synergy maintains apoptosis under aggressive mutational drift.",
        "4. **Tier 4 (18.0% Noise - Critical Boundary):** Critical phase transition boundary approaching thermal chaos (15%~20%); isolates unbreakable master therapeutic attractors."
    ])

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

    print("\n" + "=" * 80)
    print("      MULTI-NOISE ROBUSTNESS SWEEP MATRIX (ALL BENCHMARKS x 4 TIERS)")
    print("=" * 80)
    tier_header = " ".join(f"{f'{round(n*100,1)}%':<10}" for n in noise_tiers)
    print(f"{'#':<3} {'Benchmark':<28} {tier_header} Verdict")
    print("-" * 80)
    for idx, (b_name, b_info) in enumerate(sweep_matrix.items(), 1):
        tier_strs = []
        for n in noise_tiers:
            res = b_info["results"].get(n, {})
            apop = res.get("apoptosis_noisy", 0.0)
            tier_strs.append(f"{apop:>5.1f}%")
        print(f"{idx:<3} {b_name[:28]:<28} " + " ".join(f"{s:<10}" for s in tier_strs))
    print("=" * 80)
    print(f"  [✓] Master Comparison Report: {md_path}")
    print(f"  [✓] Master CSV Data Table   : {csv_path}\n")


def find_graph_path():
    candidates = [
        ROOT / "flyfly_sat" / "data" / "processed" / "graph_core.pt",
        ROOT / "data" / "processed" / "graph_core.pt",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError("Could not find biological connectome (graph_core.pt)!")


def open_gui_file_picker(initial_dir) -> List[Path]:
    """Open graphical file dialog allowing single or multi-file selection for Queue."""
    print("    [+] Opening graphical file picker dialog...")
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        files = filedialog.askopenfilenames(
            title="Select Cancer Benchmark CNF File(s) [Ctrl/Shift+Click or Ctrl+A for Queue]",
            initialdir=str(initial_dir),
            filetypes=[("DIMACS CNF files", "*.cnf"), ("All files", "*.*")]
        )
        root.destroy()
        if files:
            return [Path(f) for f in files]
    except Exception as e:
        print(f"    [!] GUI picker unavailable: {e}")
    return []


def synthesize_checkpoint_if_missing(run_dir: Path) -> Path:
    """Synthesizes a checkpoint.json from logs if an older or interrupted run lacks one."""
    ck_json = run_dir / "checkpoint.json"
    if ck_json.exists():
        return ck_json

    manifest_file = run_dir / "01_inputs_and_config_manifest.json"
    tele_file = run_dir / "02_brain_state_timeseries.jsonl"
    verif_file = run_dir / "03_asynchronous_temporal_verification.json"

    manifest = {}
    if manifest_file.exists():
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            pass

    last_step = 0
    best_u = 9999
    active_drugs = []
    if tele_file.exists() and tele_file.stat().st_size > 0:
        try:
            with open(tele_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        s = d.get("step", 0)
                        if s >= last_step:
                            last_step = s
                            active_drugs = d.get("active_drugs", [])
                        u = d.get("unsat", 9999)
                        bu = d.get("best_unsat", u)
                        if bu < best_u:
                            best_u = bu
                    except Exception:
                        pass
        except Exception:
            pass

    evaluated_drug_sets = []
    blocking_clauses = []
    if verif_file.exists():
        try:
            with open(verif_file, "r", encoding="utf-8") as f:
                verifs = json.load(f)
                for v in verifs:
                    cd = v.get("candidate_drugs", [])
                    if cd:
                        evaluated_drug_sets.append(cd)
        except Exception:
            pass

    cnf_path = manifest.get("cnf_path", "")
    mapping_path = Path(cnf_path).with_suffix(".mapping.json") if cnf_path else None
    if mapping_path and mapping_path.exists():
        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                mapping = json.load(f)
            var_to_id = mapping.get("var_to_id", {})
            for cd in evaluated_drug_sets:
                lits = [-var_to_id[f"DRUG_INHIB_{d}"] for d in cd if f"DRUG_INHIB_{d}" in var_to_id]
                if lits:
                    blocking_clauses.append(lits)
        except Exception:
            pass

    ck_data = {
        "step": last_step,
        "status": "interrupted",
        "best_unsat": best_u if best_u != 9999 else 2,
        "cur_unsat": best_u if best_u != 9999 else 2,
        "last_best_step": last_step,
        "failures": 0,
        "blocking_clauses_count": len(blocking_clauses),
        "synergies_count": 0,
        "active_drugs": active_drugs,
        "blocking_clauses": blocking_clauses,
        "evaluated_drug_sets": evaluated_drug_sets,
        "blocking_history": [],
        "synergy_history": [],
        "cnf_path": str(cnf_path),
        "mapping_path": str(mapping_path) if mapping_path and mapping_path.exists() else None,
        "model_name": manifest.get("model_name", "Oncology Network"),
        "seed": manifest.get("config", {}).get("seed", 42),
        "noise_percent": 2.0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open(ck_json, "w", encoding="utf-8") as f:
            json.dump(ck_data, f, indent=2)
    except Exception:
        pass
    return ck_json


def find_resumable_oncology_runs() -> List[Dict]:
    """Scan flyfly_oncology/logs (including sweep subfolders) and results/runs for resumable runs."""
    search_dirs = [
        ROOT / "flyfly_oncology" / "logs",
        ROOT / "flyfly_sat" / "results" / "runs",
        ROOT / "results" / "runs"
    ]
    resumable = []
    seen_paths = set()

    for s_dir in search_dirs:
        if not s_dir.exists():
            continue
        candidates = list(s_dir.glob("**/01_inputs_and_config_manifest.json")) + list(s_dir.glob("**/checkpoint.json")) + list(s_dir.glob("**/checkpoint.pt"))
        for cand in candidates:
            run_dir = cand.parent
            if run_dir in seen_paths or not run_dir.is_dir():
                continue
            seen_paths.add(run_dir)

            manifest_path = run_dir / "01_inputs_and_config_manifest.json"
            tele_path = run_dir / "02_brain_state_timeseries.jsonl"
            ck_json_path = run_dir / "checkpoint.json"
            summary_path = run_dir / "summary.json"

            manifest = {}
            if manifest_path.exists():
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                except Exception:
                    pass

            cnf_name = Path(manifest.get("cnf_path", "")).name if manifest.get("cnf_path") else "?"
            model_name = manifest.get("model_name", "Oncology Network")
            steps = 0
            best_unsat = "?"
            active_drugs = []
            status = "IN_PROGRESS"

            if ck_json_path.exists():
                try:
                    with open(ck_json_path, "r", encoding="utf-8") as f:
                        ck_data = json.load(f)
                        steps = ck_data.get("step", 0)
                        best_unsat = ck_data.get("best_unsat", "?")
                        active_drugs = ck_data.get("active_drugs", [])
                        status = ck_data.get("status", "running").upper()
                        if cnf_name == "?" and ck_data.get("cnf_path"):
                            cnf_name = Path(ck_data["cnf_path"]).name
                except Exception:
                    pass
            elif tele_path.exists() and tele_path.stat().st_size > 0:
                try:
                    with open(tele_path, "rb") as f:
                        f.seek(max(0, tele_path.stat().st_size - 4096))
                        lines = f.read().decode("utf-8", errors="ignore").strip().splitlines()
                        if lines:
                            last_d = json.loads(lines[-1])
                            steps = last_d.get("step", 0)
                            best_unsat = last_d.get("best_unsat", last_d.get("unsat", "?"))
                            active_drugs = last_d.get("active_drugs", [])
                except Exception:
                    pass

            if summary_path.exists():
                try:
                    with open(summary_path, "r", encoding="utf-8") as f:
                        s_data = json.load(f)
                        if s_data.get("solved"):
                            status = "SOLVED"
                        else:
                            status = s_data.get("status", "TIMEOUT").upper()
                except Exception:
                    pass

            # Ignore empty zero-step runs
            if steps == 0 and not ck_json_path.exists() and not (run_dir / "checkpoint.pt").exists():
                continue

            mtime = run_dir.stat().st_mtime
            resumable.append({
                "path": run_dir,
                "name": run_dir.name,
                "mtime": mtime,
                "mtime_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)),
                "cnf": cnf_name,
                "cnf_path": Path(manifest.get("cnf_path")) if manifest.get("cnf_path") else (run_dir / cnf_name),
                "model_name": model_name,
                "steps": steps,
                "best_unsat": best_unsat,
                "active_drugs": active_drugs,
                "status": status,
                "manifest": manifest
            })

    resumable.sort(key=lambda r: r["mtime"], reverse=True)
    return resumable


def select_benchmarks_interactive() -> List[Path]:
    gt_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "ground_truth_19"
    cohort_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks"
    default_dir = gt_dir if gt_dir.exists() else cohort_dir

    print("\n[1] Select Cancer Benchmark CNF File(s):")
    print("    1) Open Graphical File Picker (Select 1 or MULTIPLE files for Queue) [DEFAULT]")
    print("       * Tip: Hold Ctrl or Shift (or Ctrl+A) to select multiple files for Sequential Queue!")
    print("    2) Run all 19 Published Ground-Truth Benchmarks (T-LGL + AML)")
    print("    3) Run Pancreatic Cancer (PDAC KRAS-G12D) Benchmarks (3 Cohorts + 10 Patients)")
    print("    4) Run Glioblastoma Multiforme (GBM) Patient Cohort (8 Real Patients)")
    print("    5) Run Triple-Negative Breast Cancer (TNBC) Patient Cohort (8 Real Patients)")
    print("    6) Run Metastatic Colorectal Cancer (mCRC) Patient Cohort (8 Real Patients)")
    print("    7) Run Non-Small Cell Lung Cancer (NSCLC) Patient Cohort (8 Real Patients)")
    print("    8) Run Cutaneous & Metastatic Melanoma (SKCM) Patient Cohort (8 Real Patients)")
    print("    9) Run Castration-Resistant Prostate Cancer (CRPC) Patient Cohort (8 Real Patients)")
    print("    10) Run High-Grade Serous Ovarian Cancer (HGSOC) Patient Cohort (8 Real Patients)")
    print("    11) Run Hepatocellular Carcinoma (HCC - Liver) Patient Cohort (8 Real Patients) [NEW]")
    print("    12) Run Clear Cell Renal Cell Carcinoma (ccRCC - Kidney) Patient Cohort (8 Real Patients) [NEW]")
    print("    13) Run Gastric Adenocarcinoma (STAD - Stomach) Patient Cohort (8 Real Patients) [NEW]")
    print("    14) Run Bladder / Urothelial Carcinoma (BLCA) Patient Cohort (8 Real Patients) [NEW]")
    print("    15) Run Head & Neck Squamous Carcinoma (HNSCC) Patient Cohort (8 Real Patients) [NEW]")
    print("    16) Run Esophageal Carcinoma (ESCA) Patient Cohort (8 Real Patients) [NEW]")
    print("    17) Run Thyroid Carcinoma (THCA) Patient Cohort (8 Real Patients) [NEW]")
    print("    18) Run Soft Tissue Sarcoma & GIST (SARC) Patient Cohort (8 Real Patients) [NEW]")
    print("    19) Run Chronic Lymphocytic Leukemia (CLL) Patient Cohort (8 Real Patients) [NEW]")
    print("    20) Run Multiple Myeloma (MM) Patient Cohort (8 Real Patients) [NEW]")
    print("    21) Run Small Cell Lung Cancer (SCLC) Patient Cohort (8 Real Patients) [NEW]")
    print("    22) Run Prospective Unsolved & Orphan Cancers Cohort (12 Unsolved Cancers) [PROSPECTIVE FRONTIER]")
    print("    23) Run ALL Combined Cancer Benchmarks across all lineages")
    print("    24) Enter manual .cnf file path in console")

    choice = input("    Your choice [Press Enter for Graphical Window]: ").strip()

    if choice == "" or choice == "1":
        picked = open_gui_file_picker(default_dir)
        if picked:
            if len(picked) == 1:
                print(f"    -> Selected single benchmark: {picked[0].name}")
            else:
                print(f"\n    [+] Selected {len(picked)} benchmarks for Sequential Execution Queue:")
                for idx, p in enumerate(picked, 1):
                    print(f"        [{idx:2d}] {p.name}")
            return picked
        else:
            print("    [!] No file selected in dialog. Defaulting to all 19 ground-truth benchmarks.")
            return sorted(list(gt_dir.glob("gt*.cnf")))
    elif choice == "2":
        all_19 = sorted(list(gt_dir.glob("gt*.cnf")))
        print(f"    -> Queued all {len(all_19)} published ground-truth benchmarks.")
        return all_19
    elif choice == "3":
        pdac_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "pdac_patients"
        pdac_benchmarks = sorted(list(pdac_dir.glob("pdac*.cnf"))) if pdac_dir.exists() else sorted(list(gt_dir.glob("pdac*.cnf")))
        print(f"\n    [+] Queued {len(pdac_benchmarks)} Pancreatic Cancer (PDAC) Benchmarks:")
        for idx, p in enumerate(pdac_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return pdac_benchmarks
    elif choice == "4":
        gbm_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "gbm_patients"
        gbm_benchmarks = sorted(list(gbm_dir.glob("gbm*.cnf"))) if gbm_dir.exists() else sorted(list(gt_dir.glob("gbm*.cnf")))
        print(f"\n    [+] Queued {len(gbm_benchmarks)} Glioblastoma (GBM) Patient Benchmarks:")
        for idx, p in enumerate(gbm_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return gbm_benchmarks
    elif choice == "5":
        tnbc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "tnbc_patients"
        tnbc_benchmarks = sorted(list(tnbc_dir.glob("tnbc*.cnf"))) if tnbc_dir.exists() else sorted(list(gt_dir.glob("tnbc*.cnf")))
        print(f"\n    [+] Queued {len(tnbc_benchmarks)} Triple-Negative Breast Cancer (TNBC) Patient Benchmarks:")
        for idx, p in enumerate(tnbc_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return tnbc_benchmarks
    elif choice == "6":
        mcrc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "mcrc_patients"
        mcrc_benchmarks = sorted(list(mcrc_dir.glob("mcrc*.cnf"))) if mcrc_dir.exists() else sorted(list(gt_dir.glob("mcrc*.cnf")))
        print(f"\n    [+] Queued {len(mcrc_benchmarks)} Metastatic Colorectal Cancer (mCRC) Patient Benchmarks:")
        for idx, p in enumerate(mcrc_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return mcrc_benchmarks
    elif choice == "7":
        nsclc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "nsclc_patients"
        nsclc_benchmarks = sorted(list(nsclc_dir.glob("nsclc*.cnf"))) if nsclc_dir.exists() else sorted(list(gt_dir.glob("nsclc*.cnf")))
        print(f"\n    [+] Queued {len(nsclc_benchmarks)} Non-Small Cell Lung Cancer (NSCLC) Patient Benchmarks:")
        for idx, p in enumerate(nsclc_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return nsclc_benchmarks
    elif choice == "8":
        skcm_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "melanoma_patients"
        skcm_benchmarks = sorted(list(skcm_dir.glob("skcm*.cnf"))) if skcm_dir.exists() else sorted(list(gt_dir.glob("skcm*.cnf")))
        print(f"\n    [+] Queued {len(skcm_benchmarks)} Cutaneous Melanoma (SKCM) Patient Benchmarks:")
        for idx, p in enumerate(skcm_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return skcm_benchmarks
    elif choice == "9":
        crpc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "crpc_patients"
        crpc_benchmarks = sorted(list(crpc_dir.glob("crpc*.cnf"))) if crpc_dir.exists() else sorted(list(gt_dir.glob("crpc*.cnf")))
        print(f"\n    [+] Queued {len(crpc_benchmarks)} Castration-Resistant Prostate Cancer (CRPC) Patient Benchmarks:")
        for idx, p in enumerate(crpc_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return crpc_benchmarks
    elif choice == "10":
        hgsoc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "hgsoc_patients"
        hgsoc_benchmarks = sorted(list(hgsoc_dir.glob("hgsoc*.cnf"))) if hgsoc_dir.exists() else sorted(list(gt_dir.glob("hgsoc*.cnf")))
        print(f"\n    [+] Queued {len(hgsoc_benchmarks)} High-Grade Serous Ovarian Cancer (HGSOC) Patient Benchmarks:")
        for idx, p in enumerate(hgsoc_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return hgsoc_benchmarks
    elif choice == "11":
        hcc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "hcc_patients"
        hcc_benchmarks = sorted(list(hcc_dir.glob("hcc*.cnf"))) if hcc_dir.exists() else sorted(list(gt_dir.glob("hcc*.cnf")))
        print(f"\n    [+] Queued {len(hcc_benchmarks)} Hepatocellular Carcinoma (HCC - Liver) Patient Benchmarks:")
        for idx, p in enumerate(hcc_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return hcc_benchmarks
    elif choice == "12":
        ccrcc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "ccrcc_patients"
        ccrcc_benchmarks = sorted(list(ccrcc_dir.glob("ccrcc*.cnf"))) if ccrcc_dir.exists() else sorted(list(gt_dir.glob("ccrcc*.cnf")))
        print(f"\n    [+] Queued {len(ccrcc_benchmarks)} Clear Cell Renal Cell Carcinoma (ccRCC - Kidney) Patient Benchmarks:")
        for idx, p in enumerate(ccrcc_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return ccrcc_benchmarks
    elif choice == "13":
        stad_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "stad_patients"
        stad_benchmarks = sorted(list(stad_dir.glob("stad*.cnf"))) if stad_dir.exists() else sorted(list(gt_dir.glob("stad*.cnf")))
        print(f"\n    [+] Queued {len(stad_benchmarks)} Gastric Adenocarcinoma (STAD - Stomach) Patient Benchmarks:")
        for idx, p in enumerate(stad_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return stad_benchmarks
    elif choice == "14":
        blca_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "blca_patients"
        blca_benchmarks = sorted(list(blca_dir.glob("blca*.cnf"))) if blca_dir.exists() else sorted(list(gt_dir.glob("blca*.cnf")))
        print(f"\n    [+] Queued {len(blca_benchmarks)} Bladder / Urothelial Carcinoma (BLCA) Patient Benchmarks:")
        for idx, p in enumerate(blca_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return blca_benchmarks
    elif choice == "15":
        hnscc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "hnscc_patients"
        hnscc_benchmarks = sorted(list(hnscc_dir.glob("hnscc*.cnf"))) if hnscc_dir.exists() else sorted(list(gt_dir.glob("hnscc*.cnf")))
        print(f"\n    [+] Queued {len(hnscc_benchmarks)} Head & Neck Squamous Carcinoma (HNSCC) Patient Benchmarks:")
        for idx, p in enumerate(hnscc_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return hnscc_benchmarks
    elif choice == "16":
        esca_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "esca_patients"
        esca_benchmarks = sorted(list(esca_dir.glob("esca*.cnf"))) if esca_dir.exists() else sorted(list(gt_dir.glob("esca*.cnf")))
        print(f"\n    [+] Queued {len(esca_benchmarks)} Esophageal Carcinoma (ESCA) Patient Benchmarks:")
        for idx, p in enumerate(esca_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return esca_benchmarks
    elif choice == "17":
        thca_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "thca_patients"
        thca_benchmarks = sorted(list(thca_dir.glob("thca*.cnf"))) if thca_dir.exists() else sorted(list(gt_dir.glob("thca*.cnf")))
        print(f"\n    [+] Queued {len(thca_benchmarks)} Thyroid Carcinoma (THCA) Patient Benchmarks:")
        for idx, p in enumerate(thca_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return thca_benchmarks
    elif choice == "18":
        sarc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "sarc_patients"
        sarc_benchmarks = sorted(list(sarc_dir.glob("sarc*.cnf"))) if sarc_dir.exists() else sorted(list(gt_dir.glob("sarc*.cnf")))
        print(f"\n    [+] Queued {len(sarc_benchmarks)} Soft Tissue Sarcoma & GIST (SARC) Patient Benchmarks:")
        for idx, p in enumerate(sarc_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return sarc_benchmarks
    elif choice == "19":
        cll_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "cll_patients"
        cll_benchmarks = sorted(list(cll_dir.glob("cll*.cnf"))) if cll_dir.exists() else sorted(list(gt_dir.glob("cll*.cnf")))
        print(f"\n    [+] Queued {len(cll_benchmarks)} Chronic Lymphocytic Leukemia (CLL) Patient Benchmarks:")
        for idx, p in enumerate(cll_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return cll_benchmarks
    elif choice == "20":
        mm_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "mm_patients"
        mm_benchmarks = sorted(list(mm_dir.glob("mm*.cnf"))) if mm_dir.exists() else sorted(list(gt_dir.glob("mm*.cnf")))
        print(f"\n    [+] Queued {len(mm_benchmarks)} Multiple Myeloma (MM) Patient Benchmarks:")
        for idx, p in enumerate(mm_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return mm_benchmarks
    elif choice == "21":
        sclc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "sclc_patients"
        sclc_benchmarks = sorted(list(sclc_dir.glob("sclc*.cnf"))) if sclc_dir.exists() else sorted(list(gt_dir.glob("sclc*.cnf")))
        print(f"\n    [+] Queued {len(sclc_benchmarks)} Small Cell Lung Cancer (SCLC) Patient Benchmarks:")
        for idx, p in enumerate(sclc_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return sclc_benchmarks
    elif choice == "22":
        unsolved_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "unsolved_patients"
        unsolved_benchmarks = sorted(list(unsolved_dir.glob("unsolved*.cnf"))) if unsolved_dir.exists() else sorted(list(gt_dir.glob("unsolved*.cnf")))
        print(f"\n    [+] Queued {len(unsolved_benchmarks)} Prospective Unsolved & Orphan Cancer Benchmarks:")
        for idx, p in enumerate(unsolved_benchmarks, 1):
            print(f"        [{idx:2d}] {p.name}")
        return unsolved_benchmarks
    elif choice == "23":
        all_benchmarks = sorted(list(gt_dir.glob("*.cnf")))
        print(f"    -> Queued all {len(all_benchmarks)} benchmarks across all cancer lineages.")
        return all_benchmarks
    elif choice == "24":
        raw = input("    Enter path to .cnf file: ").strip()
        p = Path(raw)
        if p.exists():
            return [p]
        print("    [!] File not found. Falling back to mCRC benchmarks.")
        mcrc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "mcrc_patients"
        return sorted(list(mcrc_dir.glob("mcrc*.cnf")))
    else:
        mcrc_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "mcrc_patients"
        return sorted(list(mcrc_dir.glob("mcrc*.cnf")))


def main():
    print("\n" + "=" * 72)
    print("      VIRTUAL DROSOPHILA ONCOLOGY DISCOVERY ENGINE (CHAMPIONS LEAGUE)")
    print("      Drosophila FlyWire Connectome + Cancer Boolean Networks (3-SAT)")
    print("=" * 72)

    # [0] Execution Mode: Fresh vs Resume
    print("\n[0] Execution Mode:")
    print("    1) Start a fresh new run / queue [DEFAULT]")
    print("    2) Resume from a previous run / checkpoint (Warm-Restart)")
    choice_mode = input("    Your choice [Press Enter for Fresh Run]: ").strip()

    if choice_mode == "2":
        resumable = find_resumable_oncology_runs()
        if not resumable:
            print("\n    [!] No previous runs found. Falling back to fresh run.\n")
        else:
            print(f"\n    Found {len(resumable)} resumable run(s) [Sorted latest first]:")
            for idx, r in enumerate(resumable[:10], 1):
                latest_tag = " (LATEST)" if idx == 1 else ""
                drugs_str = f" | Drugs: {r['active_drugs']}" if r['active_drugs'] else ""
                steps_display = f"{r['steps']:,}" if isinstance(r['steps'], int) else str(r['steps'])
                print(f"    [{idx:2d}] {r['name']}{latest_tag}")
                print(f"         CNF: {r['cnf']} | Steps: {steps_display} | Best Unsat: {r['best_unsat']}{drugs_str} | Status: {r['status']} | Date: {r['mtime_str']}")

            choice_run = input(f"\n    Select run to resume [1-{min(10, len(resumable))}] [Press Enter for 1]: ").strip()
            try:
                selected_idx = int(choice_run) - 1 if choice_run else 0
                if selected_idx < 0 or selected_idx >= len(resumable):
                    selected_idx = 0
            except ValueError:
                selected_idx = 0

            chosen_run = resumable[selected_idx]
            run_path = chosen_run["path"]
            ck_file = synthesize_checkpoint_if_missing(run_path)

            with open(ck_file, "r", encoding="utf-8") as f:
                ck_data = json.load(f)

            current_step = ck_data.get("step", 0)
            print(f"\n    -> Selected: {chosen_run['name']}")
            print(f"    -> Steps completed so far: {current_step:,}")
            print(f"    -> Best Unsat: {ck_data.get('best_unsat')} | Active Drugs: {ck_data.get('active_drugs', [])}")

            print("\n    How many ADDITIONAL simulation steps to add?")
            print("    Recommended: 30,000 steps (or 100,000 steps)")
            choice_add = input("    Additional steps [Press Enter for 30000]: ").strip()
            try:
                add_steps = int(choice_add) if choice_add else 30000
            except ValueError:
                add_steps = 30000

            print("\n    Continuation Destination:")
            print("    1) In-place (Append to existing run and update plots) [DEFAULT]")
            print("    2) Branch into new timestamped folder (Preserve original run)")
            choice_branch = input("    Your choice [Press Enter for in-place]: ").strip()
            is_branch = (choice_branch == "2")

            # Check 3D Visualizer
            print("\n    Real-Time 3D Holographic Fly Visualizer:")
            print("    Launch 3D Visualizer window now? [Y/n] [DEFAULT: Y]")
            choice_3d = input("    Your choice [Press Enter for Yes]: ").strip().lower()
            if choice_3d in ("", "y", "yes"):
                viewer_script = ROOT / "view_fly_3d.py"
                if is_port_in_use(8765):
                    print("    [✓] 3D Visualizer server is already active on port 8765. Real-time stream connected!")
                elif viewer_script.exists():
                    try:
                        flags = subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                        subprocess.Popen([sys.executable, str(viewer_script)], creationflags=flags)
                        time.sleep(1.8)
                        print("    [✓] Dedicated 3D Holographic window launched!")
                    except Exception as e:
                        print(f"    [!] Could not launch 3D window: {e}")

            # Destination directory
            if is_branch:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_dir = run_path.parent / f"{run_path.name}_resumed_{timestamp}"
                out_dir.mkdir(parents=True, exist_ok=True)
                for item in run_path.iterdir():
                    if item.is_file():
                        import shutil
                        shutil.copy2(item, out_dir / item.name)
                print(f"    [+] Branched run directory created: {out_dir.name}")
            else:
                out_dir = run_path
                print(f"    [+] Continuing in-place in: {out_dir.name}")

            # CNF and model path
            raw_cnf = ck_data.get("cnf_path")
            cnf_path = Path(raw_cnf) if raw_cnf and Path(raw_cnf).exists() else chosen_run["cnf_path"]
            raw_map = ck_data.get("mapping_path")
            mapping_path = Path(raw_map) if raw_map and Path(raw_map).exists() else (cnf_path.with_suffix(".mapping.json") if cnf_path and cnf_path.with_suffix(".mapping.json").exists() else None)

            # Resolve model
            model_dict = None
            if cnf_path:
                is_unsolved = "unsolved" in cnf_path.name.lower()
                is_tlgl = "tlgl" in cnf_path.name.lower() or "t-lgl" in cnf_path.name.lower()
                is_pdac = "pdac" in cnf_path.name.lower() or "pancrea" in cnf_path.name.lower()
                is_gbm = "gbm" in cnf_path.name.lower() or "glio" in cnf_path.name.lower() or "brain" in cnf_path.name.lower()
                is_tnbc = "tnbc" in cnf_path.name.lower() or "breast" in cnf_path.name.lower() or "brca" in cnf_path.name.lower()
                is_mcrc = "mcrc" in cnf_path.name.lower() or "colon" in cnf_path.name.lower() or "colorectal" in cnf_path.name.lower() or "crc" in cnf_path.name.lower()
                is_nsclc = "nsclc" in cnf_path.name.lower() or "lung" in cnf_path.name.lower() or "luad" in cnf_path.name.lower() or "lusc" in cnf_path.name.lower()
                is_skcm = "skcm" in cnf_path.name.lower() or "melanoma" in cnf_path.name.lower() or "skin" in cnf_path.name.lower()
                is_crpc = "crpc" in cnf_path.name.lower() or "prostate" in cnf_path.name.lower() or "prad" in cnf_path.name.lower()
                is_hgsoc = "hgsoc" in cnf_path.name.lower() or "ovarian" in cnf_path.name.lower() or "ovary" in cnf_path.name.lower()
                is_hcc = "hcc" in cnf_path.name.lower() or "liver" in cnf_path.name.lower() or "lihc" in cnf_path.name.lower()
                is_ccrcc = "ccrcc" in cnf_path.name.lower() or "kidney" in cnf_path.name.lower() or "kirc" in cnf_path.name.lower()
                is_stad = "stad" in cnf_path.name.lower() or "gastric" in cnf_path.name.lower() or "stomach" in cnf_path.name.lower()
                is_blca = "blca" in cnf_path.name.lower() or "bladder" in cnf_path.name.lower()
                is_hnscc = "hnscc" in cnf_path.name.lower() or "head" in cnf_path.name.lower()
                if is_unsolved:
                    raw_json_name = "unsolved_model.json"
                elif is_tlgl:
                    raw_json_name = "t_lgl_leukemia_zhang2008.json"
                elif is_pdac:
                    raw_json_name = "pdac_kras_model.json"
                elif is_gbm:
                    raw_json_name = "gbm_model.json"
                elif is_tnbc:
                    raw_json_name = "tnbc_model.json"
                elif is_mcrc:
                    raw_json_name = "mcrc_model.json"
                elif is_nsclc:
                    raw_json_name = "nsclc_model.json"
                elif is_skcm:
                    raw_json_name = "melanoma_model.json"
                elif is_crpc:
                    raw_json_name = "crpc_model.json"
                elif is_hgsoc:
                    raw_json_name = "hgsoc_model.json"
                elif is_hcc:
                    raw_json_name = "hcc_model.json"
                elif is_ccrcc:
                    raw_json_name = "ccrcc_model.json"
                elif is_stad:
                    raw_json_name = "stad_model.json"
                elif is_blca:
                    raw_json_name = "blca_model.json"
                elif is_hnscc:
                    raw_json_name = "hnscc_model.json"
                elif "aml" in cnf_path.name.lower() or "gt" in cnf_path.name.lower():
                    raw_json_name = "aml_palma2021.json"
                else:
                    raw_json_name = None
                if not raw_json_name:
                    prefix = cnf_path.name.split("_")[0].lower()
                    for cand_name in [f"{prefix}_model.json", f"{prefix}.json"]:
                        if (ROOT / "flyfly_oncology" / "data" / "raw_published" / cand_name).exists():
                            raw_json_name = cand_name
                            break
                if raw_json_name:
                    rp = ROOT / "flyfly_oncology" / "data" / "raw_published" / raw_json_name
                    if rp.exists():
                        with open(rp, "r", encoding="utf-8") as f:
                            model_dict = json.load(f)

            graph_path = find_graph_path()
            noise_prob = ck_data.get("noise_percent", 2.0) / 100.0

            cfg = OncologySolverConfig(
                max_steps=add_steps,
                seed=ck_data.get("seed", 42),
                max_allowed_drugs=3,
                target_apoptosis=100.0,
                validation_noise=noise_prob
            )

            logger = OncologyTelemetryLogger(
                explicit_run_dir=out_dir,
                append=True,
                noise_percent=ck_data.get("noise_percent", 2.0)
            )

            solver = FlyOncologySolver(
                cnf_path=cnf_path,
                mapping_path=mapping_path,
                model_dict=model_dict,
                graph_path=graph_path,
                cfg=cfg,
                logger=logger,
                resume_checkpoint=ck_data
            )

            t0 = time.time()
            try:
                summary = solver.solve()
            except KeyboardInterrupt:
                print(f"\n[!] Benchmark {cnf_path.name} interrupted by user.")
                summary = {"status": "interrupted", "steps_taken": solver.last_best_step}
            elapsed = time.time() - t0

            analyze_and_plot_oncology(logger.run_dir)

            is_solved = (summary.get("status") in ("biomedical_verified", "sat_solved", "solved"))
            uf100_summary = {
                "status": "solved" if is_solved else summary.get("status", "TIMEOUT"),
                "solved": is_solved,
                "best_unsat": solver.best_unsat,
                "steps_taken": summary.get("steps_taken", current_step + add_steps),
                "time_seconds": round(elapsed, 2),
                "seed": ck_data.get("seed", 42),
                "cnf": cnf_path.name if cnf_path else "benchmark.cnf",
                "n_vars": solver.n_vars,
                "n_clauses": solver.ev.n_clauses,
                "active_drugs": summary.get("active_drugs", []),
                "validation_noise": noise_prob,
                "apoptosis_rate_clean": summary.get("apoptosis_rate_clean", 0.0),
                "apoptosis_rate_noisy": summary.get("apoptosis_rate_noisy", 0.0),
                "wet_lab_match": summary.get("wet_lab_matches", [])
            }
            with open(logger.run_dir / "summary.json", "w", encoding="utf-8") as f:
                json.dump(uf100_summary, f, indent=2)

            # Record experiment in master ledger
            try:
                record_experiment_result(cnf_path.name if cnf_path else "benchmark.cnf", uf100_summary, logger.run_dir)
            except Exception as e:
                print(f"[!] Warning updating master ledger: {e}")

            # Print clinical summary
            print("\n" + "=" * 70)
            print(f"        RESULTS & CLINICAL SUMMARY: {cnf_path.name if cnf_path else 'Resumed Run'}")
            print("=" * 70)
            status_str = "SOLVED & VERIFIED! (All biological clauses satisfied + Apoptosis >= 90%)" if is_solved else f"STATUS: {summary.get('status', 'TIMEOUT').upper()}"
            print(f"  Status             : {status_str}")
            print(f"  Discovered Drug(s) : {summary.get('active_drugs', [])}")
            print(f"  Wet-Lab Alignment  : {summary.get('wet_lab_matches', []) or 'Novel Synergistic Combination'}")
            print(f"  Apoptosis Rate     : Clean={summary.get('apoptosis_rate_clean', 0.0)}% | Noisy={summary.get('apoptosis_rate_noisy', 0.0)}%")
            print(f"  Steps Taken        : {summary.get('steps_taken', current_step + add_steps):,}")
            print(f"  Elapsed Time       : {elapsed:.2f} seconds")
            print(f"  UF100 Plots & Logs : {logger.run_dir}")
            print("=" * 70 + "\n")
            return

    # Fresh Run: Proceed with benchmark selection
    cnf_paths = select_benchmarks_interactive()
    if not cnf_paths:
        print("[!] No valid benchmark files selected.")
        return

    # [2] Max simulation steps
    print("\n[2] Max simulation steps per benchmark:")
    print("    Recommended: 30,000 steps (SNN automatically stops upon verified clinical cure).")
    steps_input = input("    Enter max steps [Press Enter for 30000]: ").strip()
    try:
        max_steps = int(steps_input) if steps_input else 30000
    except ValueError:
        max_steps = 30000

    # [3] Random seed
    print("\n[3] Random Seed:")
    print("    Controls stochastic neural pool initialization & initial variable states.")
    seed_input = input("    Enter random seed [Press Enter for 42]: ").strip()
    try:
        seed = int(seed_input) if seed_input else 42
    except ValueError:
        seed = 42

    # [4] Clinical Max Allowed Drug Targets
    print("\n[4] Clinical Maximum Allowed Drug Targets:")
    print("    Recommended: 3 drugs (enforces clinical sparsity & minimizes patient toxicity).")
    drugs_input = input("    Enter max allowed drugs [Press Enter for 3]: ").strip()
    try:
        max_drugs = int(drugs_input) if drugs_input else 3
    except ValueError:
        max_drugs = 3

    # [5] Target Apoptosis Eradication Level
    print("\n[5] Target Apoptosis Eradication Criterion:")
    print("    1) 100% COMPLETE ERADICATION (Keeps exploring past 90% until total cell death is found) [DEFAULT]")
    print("    2) 90% Clinical Remission (Stops as soon as initial >=90% threshold is passed)")
    choice_apop = input("    Your choice [Press Enter for 100% Complete Eradication]: ").strip()
    target_apop = 90.0 if choice_apop == "2" else 100.0

    # [6] Biological Noise Level & Experimental Mode
    print("\n[6] Biological Noise Level & Experimental Mode:")
    print("    1) 2.0% Standard Literature Baseline (Garg 2008 / Saadatpour 2011 / Palma 2021) [DEFAULT]")
    print("       * Realistic physiological thermal noise in mammalian cancer cells.")
    print("    2) 5.0% High Transcriptional Volatility (Cytokine Storm / Deep Basin Stress Test)")
    print("       * Rigorous test: Filters out fragile targets; verifies deep apoptotic sinks.")
    print("    3) 10.0% Extreme Hyper-Perturbation (Maximum Resilience Stress Test)")
    print("       * Validates whether drug synergy is virtually unbreakable against extreme noise.")
    print("    4) 18.0% Critical Transition Boundary (15%~20% Near Chaos Stress Test)")
    print("       * Probes edge of cellular collapse to discover absolute survival limit.")
    print("    5) MULTI-NOISE SWEEP COHORT: All 4 Tiers (2%, 5%, 10%, 18%) [FULL SCIENTIFIC COMPARISON]")
    print("       * Runs each benchmark across all 4 noise tiers sequentially.")
    print("       * Creates a dedicated master session folder with isolated subfolders per noise tier.")
    print("       * Generates Master Noise Robustness Comparison Report (MD & CSV).")
    print("    6) Custom Noise Level (Enter percentage, e.g. 4.0)")
    choice_noise = input("    Your choice [Press Enter for 2.0% Standard Literature]: ").strip()
    if choice_noise == "" or choice_noise == "1":
        noise_tiers = [0.02]
    elif choice_noise == "2":
        noise_tiers = [0.05]
    elif choice_noise == "3":
        noise_tiers = [0.10]
    elif choice_noise == "4":
        noise_tiers = [0.18]
    elif choice_noise == "5":
        noise_tiers = [0.02, 0.05, 0.10, 0.18]
    else:
        try:
            val = float(choice_noise.replace("%", "").strip())
            noise_tiers = [val / 100.0 if val >= 1.0 else val]
        except ValueError:
            noise_tiers = [0.02]

    is_sweep = len(noise_tiers) > 1
    session_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if is_sweep:
        sweep_dir = ROOT / "flyfly_oncology" / "logs" / f"sweep_{session_ts}_multi_noise"
        sweep_dir.mkdir(parents=True, exist_ok=True)
        tier_names = ", ".join(f"{round(n*100, 1)}%" for n in noise_tiers)
        print(f"\n    [+] Multi-Noise Sweep Cohort Active: 4 Tiers ({tier_names})")
        print(f"    [+] Master Sweep Directory Created: {sweep_dir.name}")
    else:
        sweep_dir = ROOT / "flyfly_oncology" / "logs"

    # [7] Real-Time 3D Holographic Fly Visualizer
    print("\n[7] Real-Time 3D Holographic Fly Visualizer:")
    print("    Launch 3D Visualizer window now before simulation starts? [Y/n] [DEFAULT: Y]")
    choice_3d = input("    Your choice [Press Enter for Yes]: ").strip().lower()
    visualizer_launched = False
    if choice_3d in ("", "y", "yes"):
        print("    [+] Checking 3D Holographic Visualizer status...")
        viewer_script = ROOT / "view_fly_3d.py"
        if is_port_in_use(8765):
            print("    [✓] 3D Visualizer server is already active on port 8765. Real-time stream connected!")
            visualizer_launched = True
        elif viewer_script.exists():
            try:
                flags = subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                subprocess.Popen([sys.executable, str(viewer_script)], creationflags=flags)
                time.sleep(1.8)
                print("    [✓] Dedicated 3D Holographic window launched! Real-time telemetry will stream from step 1.")
                visualizer_launched = True
            except Exception as e:
                print(f"    [!] Could not launch 3D window automatically: {e}")

    graph_path = find_graph_path()
    total_benchmarks = len(cnf_paths)
    sweep_matrix = {}
    master_queue_results = []
    last_run_dir = None

    if total_benchmarks > 1 and not is_sweep:
        print("\n" + "=" * 72)
        print(f"      BATCH QUEUE ACTIVE: {total_benchmarks} ONCOLOGY BENCHMARKS SCHEDULED")
        print("=" * 72)
        for i, p in enumerate(cnf_paths, 1):
            print(f"  [{i:2d}/{total_benchmarks}] {p.name}")
        print("=" * 72)

    for tier_idx, noise_prob in enumerate(noise_tiers, 1):
        noise_pct_label = round(noise_prob * 100.0, 1)
        if is_sweep:
            tier_dir = sweep_dir / f"noise_{int(round(noise_prob * 100)):02d}pct"
            tier_dir.mkdir(parents=True, exist_ok=True)
            print("\n" + "=" * 78)
            print(f"  >>> SWEEP TIER [{tier_idx}/{len(noise_tiers)}]: NOISE LEVEL = {noise_pct_label}% ({tier_dir.name})")
            print("=" * 78)
        else:
            tier_dir = sweep_dir

        for q_idx, cnf_path in enumerate(cnf_paths, 1):
            mapping_path = cnf_path.with_suffix(".mapping.json")
            mapping = {}
            if mapping_path.exists():
                with open(mapping_path, "r", encoding="utf-8") as f:
                    mapping = json.load(f)

            # Determine underlying model
            is_unsolved = "unsolved" in cnf_path.name.lower()
            is_tlgl = "tlgl" in cnf_path.name.lower() or "t-lgl" in cnf_path.name.lower()
            is_pdac = "pdac" in cnf_path.name.lower() or "pancrea" in cnf_path.name.lower()
            is_gbm = "gbm" in cnf_path.name.lower() or "glio" in cnf_path.name.lower() or "brain" in cnf_path.name.lower()
            is_tnbc = "tnbc" in cnf_path.name.lower() or "breast" in cnf_path.name.lower() or "brca" in cnf_path.name.lower()
            is_mcrc = "mcrc" in cnf_path.name.lower() or "colon" in cnf_path.name.lower() or "colorectal" in cnf_path.name.lower() or "crc" in cnf_path.name.lower()
            is_nsclc = "nsclc" in cnf_path.name.lower() or "lung" in cnf_path.name.lower() or "luad" in cnf_path.name.lower() or "lusc" in cnf_path.name.lower()
            is_skcm = "skcm" in cnf_path.name.lower() or "melanoma" in cnf_path.name.lower() or "skin" in cnf_path.name.lower()
            is_crpc = "crpc" in cnf_path.name.lower() or "prostate" in cnf_path.name.lower() or "prad" in cnf_path.name.lower()
            is_hgsoc = "hgsoc" in cnf_path.name.lower() or "ovarian" in cnf_path.name.lower() or "ovary" in cnf_path.name.lower()
            is_hcc = "hcc" in cnf_path.name.lower() or "liver" in cnf_path.name.lower() or "lihc" in cnf_path.name.lower()
            is_ccrcc = "ccrcc" in cnf_path.name.lower() or "kidney" in cnf_path.name.lower() or "kirc" in cnf_path.name.lower()
            is_stad = "stad" in cnf_path.name.lower() or "gastric" in cnf_path.name.lower() or "stomach" in cnf_path.name.lower()
            is_blca = "blca" in cnf_path.name.lower() or "bladder" in cnf_path.name.lower()
            is_hnscc = "hnscc" in cnf_path.name.lower() or "head" in cnf_path.name.lower()
            if is_unsolved:
                raw_json_name = "unsolved_model.json"
            elif is_tlgl:
                raw_json_name = "t_lgl_leukemia_zhang2008.json"
            elif is_pdac:
                raw_json_name = "pdac_kras_model.json"
            elif is_gbm:
                raw_json_name = "gbm_model.json"
            elif is_tnbc:
                raw_json_name = "tnbc_model.json"
            elif is_mcrc:
                raw_json_name = "mcrc_model.json"
            elif is_nsclc:
                raw_json_name = "nsclc_model.json"
            elif is_skcm:
                raw_json_name = "melanoma_model.json"
            elif is_crpc:
                raw_json_name = "crpc_model.json"
            elif is_hgsoc:
                raw_json_name = "hgsoc_model.json"
            elif is_hcc:
                raw_json_name = "hcc_model.json"
            elif is_ccrcc:
                raw_json_name = "ccrcc_model.json"
            elif is_stad:
                raw_json_name = "stad_model.json"
            elif is_blca:
                raw_json_name = "blca_model.json"
            elif is_hnscc:
                raw_json_name = "hnscc_model.json"
            elif "aml" in cnf_path.name.lower() or "gt" in cnf_path.name.lower():
                raw_json_name = "aml_palma2021.json"
            else:
                raw_json_name = None
            if not raw_json_name:
                prefix = cnf_path.name.split("_")[0].lower()
                for cand_name in [f"{prefix}_model.json", f"{prefix}.json"]:
                    if (ROOT / "flyfly_oncology" / "data" / "raw_published" / cand_name).exists():
                        raw_json_name = cand_name
                        break
            model_dict = None
            if raw_json_name:
                raw_path = ROOT / "flyfly_oncology" / "data" / "raw_published" / raw_json_name
                if raw_path.exists():
                    with open(raw_path, "r", encoding="utf-8") as f:
                        model_dict = json.load(f)

            print("\n" + "#" * 72)
            tier_prefix = f"[Tier {tier_idx}/{len(noise_tiers)} - Noise {noise_pct_label}%] " if is_sweep else ""
            if total_benchmarks > 1:
                print(f"  >>> {tier_prefix}QUEUE [{q_idx}/{total_benchmarks}]: {cnf_path.name}")
            else:
                print(f"  >>> {tier_prefix}RUNNING ONCOLOGY BENCHMARK: {cnf_path.name}")
            print(f"  Connectome Graph: {graph_path.name} (Drosophila FlyWire Read-Only)")
            print(f"  Underlying Model: {model_dict.get('name') if model_dict else 'Oncology Network'}")
            print(f"  Max Steps       : {max_steps:,} (Target Apoptosis: {target_apop}%)")
            print(f"  Biological Noise: {noise_pct_label}% stochastic fluctuation (GAUS)")
            print(f"  Random Seed     : {seed} | Max Drugs: {max_drugs}")
            print("#" * 72 + "\n")

            cfg = OncologySolverConfig(
                max_steps=max_steps,
                seed=seed,
                max_allowed_drugs=max_drugs,
                target_apoptosis=target_apop,
                validation_noise=noise_prob
            )

            run_name = f"{cnf_path.stem}_noise{int(round(noise_prob * 100)):02d}_seed{seed}"
            logger = OncologyTelemetryLogger(
                base_log_dir=tier_dir,
                run_name=run_name,
                noise_percent=noise_prob * 100.0,
                n_cells=200,
                cell_steps=1500
            )
            last_run_dir = logger.run_dir

            solver = FlyOncologySolver(
                cnf_path=cnf_path,
                mapping_path=mapping_path if mapping_path.exists() else None,
                model_dict=model_dict,
                graph_path=graph_path,
                cfg=cfg,
                logger=logger,
                pinned_vars=mapping.get("pinned_vars", {})
            )

            t0 = time.time()
            try:
                summary = solver.solve()
            except KeyboardInterrupt:
                print(f"\n[!] Benchmark {cnf_path.name} interrupted by user.")
                summary = {"status": "interrupted", "steps_taken": solver.last_best_step}
            elapsed = time.time() - t0

            # Generate UF100-identical plots (plot_timeline.png and plot_3d.png)
            analyze_and_plot_oncology(logger.run_dir)

            # Save summary.json & run_meta.json (Exact UF100 format)
            is_solved = (summary.get("status") in ("biomedical_verified", "sat_solved", "solved"))
            uf100_summary = {
                "status": "solved" if is_solved else summary.get("status", "TIMEOUT"),
                "solved": is_solved,
                "best_unsat": solver.best_unsat,
                "steps_taken": summary.get("steps_taken", max_steps),
                "time_seconds": round(elapsed, 2),
                "seed": seed,
                "cnf": cnf_path.name,
                "n_vars": mapping.get("n_vars", solver.n_vars),
                "n_clauses": mapping.get("n_clauses", solver.ev.n_clauses),
                "active_drugs": summary.get("active_drugs", []),
                "validation_noise": noise_prob,
                "apoptosis_rate_clean": summary.get("apoptosis_rate_clean", 0.0),
                "apoptosis_rate_noisy": summary.get("apoptosis_rate_noisy", 0.0),
                "wet_lab_match": summary.get("wet_lab_matches", [])
            }
            with open(logger.run_dir / "summary.json", "w", encoding="utf-8") as f:
                json.dump(uf100_summary, f, indent=2)

            run_meta = {
                "cnf": str(cnf_path),
                "n_vars": mapping.get("n_vars", solver.n_vars),
                "n_clauses": mapping.get("n_clauses", solver.ev.n_clauses),
                "config": {
                    "mode": "full",
                    "seed": seed,
                    "max_steps": max_steps,
                    "max_allowed_drugs": max_drugs,
                    "validation_noise": noise_prob,
                    "target_apoptosis": target_apop
                },
                "flags": {"snn": True, "oncology": True}
            }
            with open(logger.run_dir / "run_meta.json", "w", encoding="utf-8") as f:
                json.dump(run_meta, f, indent=2)

            # Automatically update master scientific ledger for 19 benchmarks
            try:
                record_experiment_result(cnf_path.name, uf100_summary, logger.run_dir)
            except Exception as e:
                print(f"[!] Warning updating master ledger: {e}")

            # Display Single Clinical Summary
            print("\n" + "=" * 70)
            print(f"        RESULTS & CLINICAL SUMMARY: {cnf_path.name} (Noise: {noise_pct_label}%)")
            print("=" * 70)
            status_str = "SOLVED & VERIFIED! (All biological clauses satisfied + Apoptosis >= 90%)" if is_solved else f"STATUS: {summary.get('status', 'TIMEOUT').upper()}"
            print(f"  Status             : {status_str}")
            print(f"  Discovered Drug(s) : {summary.get('active_drugs', [])}")
            print(f"  Wet-Lab Alignment  : {summary.get('wet_lab_matches', []) or 'Novel Synergistic Combination'}")
            print(f"  Apoptosis Rate     : Clean={summary.get('apoptosis_rate_clean', 0.0)}% | Noisy({noise_pct_label}%)={summary.get('apoptosis_rate_noisy', 0.0)}%")
            print(f"  Steps Taken        : {summary.get('steps_taken', max_steps):,}")
            print(f"  Elapsed Time       : {elapsed:.2f} seconds")
            print(f"  Dynamic Blocks     : {summary.get('blocking_clauses_count', 0)} invalid states blocked via GABA")
            print(f"  UF100 Plots & Logs : {logger.run_dir}")
            print("=" * 70 + "\n")

            # Collect into sweep_matrix
            if cnf_path.name not in sweep_matrix:
                sweep_matrix[cnf_path.name] = {
                    "model": model_dict.get("name", "Oncology Network") if model_dict else "Oncology Network",
                    "results": {}
                }
            sweep_matrix[cnf_path.name]["results"][noise_prob] = {
                "status": "SOLVED" if is_solved else summary.get("status", "TIMEOUT"),
                "solved": is_solved,
                "drugs": summary.get("active_drugs", []),
                "apoptosis_noisy": summary.get("apoptosis_rate_noisy", 0.0),
                "apoptosis_clean": summary.get("apoptosis_rate_clean", 0.0),
                "steps": summary.get("steps_taken", max_steps),
                "time": elapsed
            }

            master_queue_results.append({
                "cnf": cnf_path.name,
                "noise": noise_pct_label,
                "status": "SOLVED" if is_solved else summary.get("status", "TIMEOUT").upper(),
                "solved": is_solved,
                "drugs": summary.get("active_drugs", []),
                "apoptosis": summary.get("apoptosis_rate_noisy", 0.0),
                "steps": summary.get("steps_taken", max_steps),
                "time": elapsed,
                "run_dir": logger.run_dir
            })

    # Master Multi-Noise Sweep Comparison Report
    if is_sweep:
        generate_sweep_comparison_report(sweep_dir, sweep_matrix, noise_tiers)

    # Master Queue Final Summary Table (if multiple runs occurred)
    if len(master_queue_results) > 1:
        print("\n" + "=" * 82)
        print("                   BATCH QUEUE FINAL MASTER SUMMARY")
        print("=" * 82)
        print(f"{'#':<3} {'Benchmark':<28} {'Noise':<8} {'Status':<10} {'Discovered Drugs':<18} {'Apoptosis':<10} {'Time':<7}")
        print("-" * 82)
        for i, r in enumerate(master_queue_results, 1):
            drugs_str = str(r['drugs']) if r['drugs'] else "—"
            print(f"{i:<3} {r['cnf'][:28]:<28} {r['noise']:>4.1f}%   {r['status']:<10} {drugs_str:<18} {r['apoptosis']:>5.1f}%    {r['time']:>5.2f}s")
        print("=" * 82)
        solved_cnt = sum(1 for r in master_queue_results if r["solved"])
        print(f"  Total Solved: {solved_cnt}/{len(master_queue_results)} runs | Master Ledger Updated!\n")

    # 3D Trajectory Artifacts Notification
    print(f"  [✓] 3D Flight Trajectory exported: trajectory.jsonl")
    print(f"  [✓] Trajectory Plots generated   : plot_3d.png & plot_timeline.png")

    if visualizer_launched:
        print("\n  [✓] Real-Time 3D Holographic Visualizer is actively running.")
        print("      (You can keep the 3D window open to inspect state-space navigation or close it anytime).")
    else:
        open_3d = input("\n    Launch 3D Holographic Fly Visualizer now? [Y/n]: ").strip().lower()
        if open_3d in ("", "y", "yes"):
            print("\n  [+] Launching 3D Cyber-Space Visualizer in background...")
            viewer_script = ROOT / "view_fly_3d.py"
            if viewer_script.exists():
                try:
                    subprocess.Popen([sys.executable, str(viewer_script)], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
                    print("  [✓] 3D Visualizer launched in new window! (View fly flight in 3D)")
                except Exception as e:
                    print(f"  [!] Could not launch window automatically: {e}")
                    print(f"  -> You can launch it anytime in a new terminal: python view_fly_3d.py")
        else:
            print("  -> You can view the 3D trajectory anytime via: python view_fly_3d.py")


if __name__ == "__main__":
    main()
