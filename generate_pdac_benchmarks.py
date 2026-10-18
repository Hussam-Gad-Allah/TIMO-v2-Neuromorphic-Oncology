#!/usr/bin/env python3
"""
Generator for Pancreatic Ductal Adenocarcinoma (PDAC) KRAS-G12D Benchmarks.
Based on published systems biology models:
- Eduati et al. (2020), Mol. Syst. Biol. 16:e8664
- Briones-Andrade et al. (2024), Royal Society Open Science

Exports 3-CNF DIMACS benchmarks with Tseitin transformation and auxiliary variable mappings.
"""

import json
import sys
from pathlib import Path

# Fix UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

from flyfly_oncology.dataset_downloader import get_pdac_model
from flyfly_oncology.tseitin_cnf_encoder import TseitinCNFEncoder
BENCHMARK_DIR = ROOT / "data" / "benchmarks" / "ground_truth_19"
PDAC_DIR = ROOT / "data" / "benchmarks" / "pdac"
BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
PDAC_DIR.mkdir(parents=True, exist_ok=True)

PDAC_COHORT = [
    {
        "id": "pdac01_kras_G12D_pancreatic",
        "title": "PDAC Cohort 01: KRAS-G12D Inflammatory Desmoplastic Pancreatic Carcinoma",
        "pinned": {
            "KRAS_mut": 1,
            "P53_mut": 1,
            "EGFR_stim": 1,
            "TGFB_stim": 1,
            "Hypoxia_stim": 1,
            "TNF_stim": 1,
            "Proliferation": 0,
            "Apoptosis": 1
        },
        "description": "Standard aggressive PDAC tumor microenvironment with constitutive KRAS activation, TP53 loss, and dense hypoxic stroma."
    },
    {
        "id": "pdac02_kras_G12D_hypoxic_core",
        "title": "PDAC Cohort 02: KRAS-G12D Hypoxic Desmoplastic Avascular Core",
        "pinned": {
            "KRAS_mut": 1,
            "P53_mut": 1,
            "EGFR_stim": 1,
            "Hypoxia_stim": 1,
            "TGFB_stim": 0,
            "TNF_stim": 0,
            "Proliferation": 0,
            "Apoptosis": 1
        },
        "description": "Inner avascular tumor core characterized by extreme hypoxia, metabolic reprogramming, and intrinsic apoptosis evasion."
    },
    {
        "id": "pdac03_kras_G12D_cytokine_storm",
        "title": "PDAC Cohort 03: KRAS-G12D High Inflammatory Cytokine Storm",
        "pinned": {
            "KRAS_mut": 1,
            "P53_mut": 1,
            "EGFR_stim": 1,
            "TGFB_stim": 1,
            "TNF_stim": 1,
            "Hypoxia_stim": 0,
            "Proliferation": 0,
            "Apoptosis": 1
        },
        "description": "Highly inflammatory invasive border with strong TNF-alpha and TGF-beta signaling driving profound NFkB/STAT3 survival shielding."
    }
]


def generate_benchmarks():
    base_model = get_pdac_model()
    print("=" * 72)
    print("  GENERATING PANCREATIC CANCER (PDAC) BENCHMARK CNFs")
    print("  Model: Eduati et al. (2020) & Briones-Andrade et al. (2024)")
    print("=" * 72)

    for bench in PDAC_COHORT:
        b_id = bench["id"]
        # Custom copy of model dict for this benchmark
        m_copy = dict(base_model)
        m_copy["stimuli"] = [k for k, v in bench["pinned"].items() if v == 1 and k not in ("Apoptosis", "Proliferation")]
        m_copy["phenotypes"] = {
            "cancer_state": {"Proliferation": 1, "Apoptosis": 0},
            "curative_state": {k: v for k, v in bench["pinned"].items() if k in ("Apoptosis", "Proliferation")}
        }

        encoder = TseitinCNFEncoder(m_copy)
        
        # Export to both ground_truth_19 (for immediate GUI picker visibility) and pdac/
        out_cnf = BENCHMARK_DIR / f"{b_id}.cnf"
        out_map = BENCHMARK_DIR / f"{b_id}.mapping.json"
        encoder.export_dimacs(out_cnf, out_map)

        pdac_cnf = PDAC_DIR / f"{b_id}.cnf"
        pdac_map = PDAC_DIR / f"{b_id}.mapping.json"
        encoder.export_dimacs(pdac_cnf, pdac_map)

        print(f"  [✓] Benchmark Created: {b_id}.cnf")

    print("\n[✓] All PDAC benchmarks successfully generated and verified!\n")


if __name__ == "__main__":
    generate_benchmarks()
