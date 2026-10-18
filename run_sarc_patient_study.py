import types
import sys
from pathlib import Path
_cur_dir = Path(__file__).resolve().parent
if str(_cur_dir) not in sys.path:
    sys.path.insert(0, str(_cur_dir))
if "flyfly_oncology" not in sys.modules:
    _pkg = types.ModuleType("flyfly_oncology")
    _pkg.__path__ = [str(_cur_dir)]
    _pkg.__file__ = str(_cur_dir / "__init__.py")
    sys.modules["flyfly_oncology"] = _pkg

#!/usr/bin/env python3
import csv, json, os, sys, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from flyfly_oncology.fly_oncology_solver import FlyOncologySolver, OncologySolverConfig
from flyfly_oncology.telemetry_logger import OncologyTelemetryLogger
from flyfly_oncology.dataset_downloader import load_model

def run_sarc_study():
    candidates_graph = [
        Path(__file__).resolve().parent / "data" / "processed" / "graph_core.pt",
        ROOT / "data" / "processed" / "graph_core.pt",
        ROOT / "flyfly_sat" / "data" / "processed" / "graph_core.pt"
    ]
    graph_path = next((p for p in candidates_graph if p.exists()), candidates_graph[0])
    candidates_pdir = [Path(__file__).resolve().parent / "data" / "benchmarks" / "sarc_patients", ROOT / "data" / "benchmarks" / "sarc_patients", ROOT / "flyfly_oncology" / "data" / "benchmarks" / "sarc_patients"]
    patient_dir = next((p for p in candidates_pdir if p.exists()), candidates_pdir[0])
    patient_cnfs = sorted(list(patient_dir.glob("sarc_pt*.cnf")))
    ledger_path = patient_dir / "SARC_PATIENTS_CLINICAL_TRUTH_LEDGER.json"
    clinical_ledger = {}
    if ledger_path.exists():
        with open(ledger_path, "r", encoding="utf-8") as f:
            clinical_ledger = json.load(f)
    model_dict = load_model("sarc")
    log_base = Path(__file__).resolve().parent / "logs" / f"sarc_8_patient_study_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_base.mkdir(parents=True, exist_ok=True)
    print("=" * 84)
    print("      VIRTUAL DROSOPHILA SNN DISCOVERY: 8 REAL SOFT TISSUE SARCOMA & GIST (SARC) PATIENTS")
    print("=" * 84)
    for idx, cnf_path in enumerate(patient_cnfs, 1):
        b_id = cnf_path.stem
        map_path = cnf_path.with_suffix(".mapping.json")
        with open(map_path, "r", encoding="utf-8") as f:
            mapping = json.load(f)
        cfg = OncologySolverConfig(max_steps=5000, seed=42, max_allowed_drugs=3, target_apoptosis=90.0, validation_noise=0.02)
        logger = OncologyTelemetryLogger(base_log_dir=log_base, run_name=f"{b_id}_s42", noise_percent=2.0)
        solver = FlyOncologySolver(cnf_path=cnf_path, mapping_path=map_path, model_dict=model_dict, graph_path=graph_path, cfg=cfg, logger=logger, pinned_vars=mapping.get("pinned_variables", {}))
        res = solver.solve()
        print(f"  [✓] {b_id}: Active Regimen: {' + '.join(res.get('active_drugs', []))} | Apoptosis: {res.get('apoptosis_rate_noisy', 0.0):.1f}%")

if __name__ == "__main__":
    run_sarc_study()
