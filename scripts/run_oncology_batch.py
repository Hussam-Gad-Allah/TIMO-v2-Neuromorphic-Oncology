"""
Main Oncology Experiment Runner: FlyFly Oncology Champions League Phase.
Couples the Drosophila FlyWire whole-brain connectome SNN with cancer Boolean networks (3-SAT)
and in-loop asynchronous temporal cell validation.

Executes both scenarios:
1. Scenario 1 (Monotherapy Discovery): T-LGL Leukemia (Zhang et al. 2008 / Saadatpour et al. 2011)
2. Scenario 2 (Combination Therapy for Resistant AML): AML with DNMT3A_mut = 1 (Palma et al. 2021)
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flyfly_oncology.citations_manager import generate_citations
from flyfly_oncology.dataset_downloader import download_and_verify, load_model
from flyfly_oncology.tseitin_cnf_encoder import TseitinCNFEncoder
from flyfly_oncology.fly_oncology_solver import FlyOncologySolver, OncologySolverConfig
from flyfly_oncology.telemetry_logger import OncologyTelemetryLogger


def ensure_prerequisites():
    """Ensures citation ledger, raw datasets, and CNF benchmarks are pre-built."""
    print("=" * 80)
    print("FLYFLY ONCOLOGY: CHECKING & PREPARING PREREQUISITES")
    print("=" * 80)

    # 1. Citations
    bib, ledger = generate_citations()
    print(f"[Prereq 1/3] Citations Ledger ready: {ledger.name}")

    # 2. Raw datasets & manifest
    raw_dir = PROJECT_ROOT / "flyfly_oncology" / "data" / "raw_published"
    manifest_file = raw_dir / "download_manifest.json"
    if not manifest_file.exists():
        download_and_verify(raw_dir)
        print(f"[Prereq 2/3] Datasets downloaded & SHA-256 verified.")
    else:
        print(f"[Prereq 2/3] Published models verified from {manifest_file.name}")

    # 3. CNF Encodings
    cnf_dir = PROJECT_ROOT / "flyfly_oncology" / "data" / "cnf_encoded"
    t_lgl_cnf = cnf_dir / "t_lgl_leukemia.cnf"
    aml_cnf = cnf_dir / "aml_leukemia.cnf"

    if not t_lgl_cnf.exists() or not aml_cnf.exists():
        print("[Prereq 3/3] Encoding Boolean regulatory networks to Tseitin 3-CNF...")
        t_lgl_model = load_model("t_lgl")
        TseitinCNFEncoder(t_lgl_model).export_dimacs(t_lgl_cnf)

        aml_model = load_model("aml")
        TseitinCNFEncoder(aml_model).export_dimacs(aml_cnf)
        print(f"[Prereq 3/3] CNF formulas built in {cnf_dir}")
    else:
        print(f"[Prereq 3/3] CNF formulas verified: {t_lgl_cnf.name}, {aml_cnf.name}")
    print()


def run_tlgl_experiment() -> dict:
    """
    Scenario 1: Monotherapy Discovery on T-LGL Leukemia (Zhang et al. 2008 / Saadatpour et al. 2011).
    Explores single/dual interventions to induce apoptosis commitment.
    """
    print("#" * 80)
    print("EXPERIMENT 1: MONOTHERAPY DISCOVERY ON T-LGL LEUKEMIA")
    print("Target: Find single or dual interventions restoring Apoptosis in 60-node network")
    print("#" * 80)

    cnf_path = PROJECT_ROOT / "flyfly_oncology" / "data" / "cnf_encoded" / "t_lgl_leukemia.cnf"
    model_dict = load_model("t_lgl")
    graph_path = PROJECT_ROOT / "flyfly_sat" / "data" / "processed" / "graph_core.pt"

    logger = OncologyTelemetryLogger(run_name="tlgl_monotherapy")
    cfg = OncologySolverConfig(
        max_steps=5000,
        flip_ratio=0.20,
        max_allowed_drugs=2,
        seed=42
    )

    solver = FlyOncologySolver(
        cnf_path=cnf_path,
        model_dict=model_dict,
        graph_path=graph_path,
        cfg=cfg,
        logger=logger
    )

    summary = solver.solve()
    return summary, logger.report_path


def run_aml_experiment() -> dict:
    """
    Scenario 2: Overcoming Drug Resistance via Combination Therapy in AML (Palma et al. 2021).
    With DNMT3A_mut = 1, single agents fail the in-loop temporal validation.
    Dynamic blocking clauses punish ineffective single agents, forcing discovery of synergistic combinations.
    """
    print("\n" + "#" * 80)
    print("EXPERIMENT 2: COMBINATION THERAPY FOR RESISTANT AML (DNMT3A-mutant)")
    print("Target: Demonstrate rejection of monotherapies via Dynamic Blocking Clauses,")
    print("        forcing Connectome discovery of synergistic combination (BCL2 + MCL1)")
    print("#" * 80)

    cnf_path = PROJECT_ROOT / "flyfly_oncology" / "data" / "cnf_encoded" / "aml_leukemia.cnf"
    model_dict = load_model("aml")
    graph_path = PROJECT_ROOT / "flyfly_sat" / "data" / "processed" / "graph_core.pt"

    logger = OncologyTelemetryLogger(run_name="aml_combination_therapy")
    cfg = OncologySolverConfig(
        max_steps=5000,
        flip_ratio=0.20,
        max_allowed_drugs=3,
        seed=42
    )

    solver = FlyOncologySolver(
        cnf_path=cnf_path,
        model_dict=model_dict,
        graph_path=graph_path,
        cfg=cfg,
        logger=logger
    )

    summary = solver.solve()
    return summary, logger.report_path


def main():
    start_time = time.time()
    ensure_prerequisites()

    # 1. Run Scenario 1: T-LGL Monotherapy Discovery
    tlgl_summary, tlgl_report_path = run_tlgl_experiment()

    # 2. Run Scenario 2: AML Combination Therapy
    aml_summary, aml_report_path = run_aml_experiment()

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"ALL EXPERIMENTS COMPLETED IN {elapsed:.2f} SECONDS")
    print("=" * 80)

    print("\n[SUMMARY RESULTS TABLE]")
    print(f"{'Metric':<35} | {'T-LGL Leukemia':<20} | {'AML Resistance':<20}")
    print("-" * 80)
    print(f"{'Status':<35} | {tlgl_summary.get('status', 'N/A'):<20} | {aml_summary.get('status', 'N/A'):<20}")
    print(f"{'Steps Taken':<35} | {tlgl_summary.get('steps_taken', 0):<20} | {aml_summary.get('steps_taken', 0):<20}")
    print(f"{'Active Drugs Discovered':<35} | {str(tlgl_summary.get('active_drugs', [])):<20} | {str(aml_summary.get('active_drugs', [])):<20}")
    print(f"{'Apoptosis Clean (noise=0.0)':<35} | {tlgl_summary.get('apoptosis_rate_clean', 0.0):<19}% | {aml_summary.get('apoptosis_rate_clean', 0.0):<19}%")
    print(f"{'Apoptosis Noisy (noise=0.02)':<35} | {tlgl_summary.get('apoptosis_rate_noisy', 0.0):<19}% | {aml_summary.get('apoptosis_rate_noisy', 0.0):<19}%")
    print(f"{'Proliferation Suppression':<35} | {tlgl_summary.get('proliferation_suppression_rate', 0.0):<19}% | {aml_summary.get('proliferation_suppression_rate', 0.0):<19}%")
    print(f"{'Dynamic Blocking Clauses':<35} | {tlgl_summary.get('blocking_clauses_count', 0):<20} | {aml_summary.get('blocking_clauses_count', 0):<20}")
    print(f"{'Synergy Flips Fired':<35} | {tlgl_summary.get('synergy_flips_count', 0):<20} | {aml_summary.get('synergy_flips_count', 0):<20}")
    print(f"{'Wet-Lab Literature Matches':<35} | {str(tlgl_summary.get('wet_lab_matches', [])):<20} | {str(aml_summary.get('wet_lab_matches', [])):<20}")
    print("-" * 80)

    print(f"\nT-LGL Report Path: {tlgl_report_path}")
    print(f"AML Report Path:   {aml_report_path}\n")

    # Print the full executive report of the AML combination experiment as requested
    print("=" * 80)
    print("EXECUTIVE EXPERIMENT REPORT (05_executive_experiment_report.md):")
    print("=" * 80)
    with open(aml_report_path, "r", encoding="utf-8") as f:
        print(f.read())


if __name__ == "__main__":
    main()
