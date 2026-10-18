"""
Batch Oncology Benchmark Runner (FlyFly Oncology Champions League Phase).
Mirrors batch_benchmark_runner.py from the UF100 benchmarks.

Runs multiple clinical cancer 3-SAT instances sequentially (e.g. 12 patient cohorts).
Per-patient detailed logs go to results/batch_run/runs/<instance>_seed<seed>/
A master summary is updated and flushed to results/batch_run/master_oncology_batch_log.csv.
"""

import argparse
import csv
import json
import time
from pathlib import Path

from flyfly_oncology.fly_oncology_solver import FlyOncologySolver, OncologySolverConfig
from flyfly_oncology.dataset_downloader import get_t_lgl_model, get_aml_model
from flyfly_oncology.telemetry_logger import OncologyTelemetryLogger


def main():
    root = Path(__file__).resolve().parent
    project_root = root.parent
    bench_dir = root / "data" / "benchmarks"
    results_dir = root / "results" / "batch_run"
    results_dir.mkdir(parents=True, exist_ok=True)
    runs_dir = results_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    ap = argparse.ArgumentParser(description="Virtual Fly Oncology Batch Benchmark Runner")
    ap.add_argument("--bench-dir", type=str, default=str(bench_dir), help="Directory containing .cnf benchmarks")
    ap.add_argument("--files", type=str, nargs="+", default=None, help="Specific .cnf files to run")
    ap.add_argument("--limit", type=int, default=0, help="Process only the first N files (0 = all)")
    ap.add_argument("--seed", type=int, default=42, help="Random seed to use")
    ap.add_argument("--vary-seeds", action="store_true", help="Vary seed per instance (seed = base_seed + i)")
    ap.add_argument("--max-steps", type=int, default=5000, help="Max SNN steps per instance")
    ap.add_argument("--flip-ratio", type=float, default=0.20, help="SNN motor flip threshold ratio")
    ap.add_argument("--max-allowed-drugs", type=int, default=3, help="Clinical drug sparsity constraint (max 3)")
    ap.add_argument("--resume", action="store_true", help="Skip already completed runs")
    args = ap.parse_args()

    bench_path = Path(args.bench_dir)
    if args.files:
        cnf_files = []
        for f in args.files:
            p = Path(f)
            if not p.is_absolute():
                cand = bench_path / f
                if cand.exists():
                    p = cand
                elif (bench_path / f"{f}.cnf").exists():
                    p = bench_path / f"{f}.cnf"
            if p.exists():
                cnf_files.append(p)
            else:
                print(f"[warn] Benchmark instance not found: {f}")
    else:
        cnf_files = sorted(bench_path.glob("*.cnf"))

    if not cnf_files:
        print(f"Error: no .cnf files found in {bench_path}")
        return

    if args.limit > 0:
        cnf_files = cnf_files[:args.limit]

    print("=" * 80)
    print(f"VIRTUAL FLY ONCOLOGY BATCH RUNNER | {len(cnf_files)} Patient Instance(s) Queued")
    print(f"Benchmarks Directory: {bench_path}")
    print(f"Results Directory:    {results_dir}")
    print(f"Max Steps: {args.max_steps:,} | Base Seed: {args.seed} | Drug Sparsity Limit: <= {args.max_allowed_drugs}")
    print("=" * 80)

    graph_path = project_root / "flyfly_sat" / "data" / "processed" / "graph_core.pt"
    master_csv = results_dir / "master_oncology_batch_log.csv"
    new_file = not master_csv.exists()

    fields = [
        "instance_id", "patient_title", "cohort", "seed", "n_vars", "n_clauses",
        "status", "steps_taken", "elapsed_seconds", "discovered_drugs", "n_drugs",
        "apoptosis_clean_pct", "apoptosis_noisy_pct", "prolif_suppressed_pct",
        "mean_steps_to_death", "blocking_clauses", "synergy_flips", "wet_lab_matches"
    ]

    t_lgl_base = get_t_lgl_model()
    aml_base = get_aml_model()

    with open(master_csv, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        if new_file:
            writer.writeheader()

        for i, cnf in enumerate(cnf_files, 1):
            seed = (args.seed + i) if args.vary_seeds else args.seed
            inst_id = cnf.stem
            out_run_dir = runs_dir / f"{inst_id}_seed{seed}"

            # Check resume
            if args.resume and (out_run_dir / "05_executive_experiment_report.md").exists():
                print(f"[{i:02d}/{len(cnf_files):02d}] [SKIP] {inst_id} (already completed in {out_run_dir.name})")
                continue

            print(f"\n{'='*80}")
            print(f"[{i:02d}/{len(cnf_files):02d}] >>> Launching Clinical Instance: {inst_id} (Seed {seed}) <<<")
            print(f"{'='*80}")

            # Load patient profile metadata
            profile_file = cnf.with_suffix(".profile.json")
            if profile_file.exists():
                with open(profile_file, "r", encoding="utf-8") as f:
                    profile = json.load(f)
            else:
                profile = {"title": inst_id, "pinned": {}, "description": ""}

            cohort = "T-LGL Leukemia" if "tlgl" in inst_id else "AML Leukemia"
            base_model = t_lgl_base if "tlgl" in inst_id else aml_base
            model_dict = dict(base_model)
            model_dict["name"] = profile.get("title", inst_id)

            # SNN and Logger setup
            logger = OncologyTelemetryLogger(base_log_dir=runs_dir, run_name=f"{inst_id}_seed{seed}")
            cfg = OncologySolverConfig(
                max_steps=args.max_steps,
                flip_ratio=args.flip_ratio,
                max_allowed_drugs=args.max_allowed_drugs,
                seed=seed
            )

            solver = FlyOncologySolver(
                cnf_path=cnf,
                model_dict=model_dict,
                graph_path=graph_path,
                cfg=cfg,
                logger=logger
            )

            s = solver.solve()

            row = {
                "instance_id": inst_id,
                "patient_title": profile.get("title", inst_id),
                "cohort": cohort,
                "seed": seed,
                "n_vars": s.get("n_vars", solver.n_vars),
                "n_clauses": solver.ev.n_clauses,
                "status": s.get("status"),
                "steps_taken": s.get("steps_taken"),
                "elapsed_seconds": s.get("elapsed_seconds"),
                "discovered_drugs": "+".join(s.get("active_drugs", [])) or "NONE",
                "n_drugs": len(s.get("active_drugs", [])),
                "apoptosis_clean_pct": s.get("apoptosis_rate_clean", 0.0),
                "apoptosis_noisy_pct": s.get("apoptosis_rate_noisy", 0.0),
                "prolif_suppressed_pct": s.get("proliferation_suppression_rate", 0.0),
                "mean_steps_to_death": s.get("mean_steps_to_apoptosis", 0.0),
                "blocking_clauses": s.get("blocking_clauses_count", 0),
                "synergy_flips": s.get("synergy_flips_count", 0),
                "wet_lab_matches": "+".join(s.get("wet_lab_matches", [])) or "NONE"
            }
            writer.writerow(row)
            fh.flush()

    print("\n" + "=" * 80)
    print(f"Batch execution finished! Master log saved at:\n  -> {master_csv}")
    print("=" * 80)


if __name__ == "__main__":
    main()
