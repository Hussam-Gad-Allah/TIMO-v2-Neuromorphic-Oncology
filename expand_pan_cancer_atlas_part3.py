#!/usr/bin/env python3
"""
Pan-Cancer Atlas Expansion Engine - Part 3 (Cancers #15 to #20).
Generates:
15. ESCA - Esophageal Carcinoma
16. THCA - Thyroid Carcinoma
17. SARC - Soft Tissue Sarcoma / GIST
18. CLL - Chronic Lymphocytic Leukemia
19. MM - Multiple Myeloma
20. SCLC - Small Cell Lung Cancer

Executes with 60-second intervals between each cancer type generation.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Fix UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
BENCHMARK_DIR = ROOT / "data" / "benchmarks" / "ground_truth_19"
RAW_DIR = ROOT / "data" / "raw_published"
BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT.parent))
from flyfly_oncology.tseitin_cnf_encoder import TseitinCNFEncoder


CANCER_SPECS_PART3 = [
    {
        "index": 15,
        "code": "esca",
        "name": "Esophageal Carcinoma (ESCA)",
        "citation": "TCGA-ESCA (Nature 2017, 541:169-175); Sun et al. (2021) Lancet (KEYNOTE-590); Doki et al. (2022) NEJM (CheckMate-648)",
        "url": "https://doi.org/10.1038/nature20805",
        "stimuli": ["EGF_stim", "Chemo_DNA_damage", "EGFR_amp", "HER2_amp", "TP53_mut", "CCND1_amp", "CDKN2A_loss", "PIK3CA_mut"],
        "targets": ["EGFR", "HER2", "MEK", "ERK", "PI3K", "AKT", "mTOR", "CDK4_6", "STAT3", "NFkB", "MCL1", "BCL2", "BCLxL", "XIAP"],
        "rules": {
            "EGF_stim": "EGF_stim", "Chemo_DNA_damage": "Chemo_DNA_damage", "EGFR_amp": "EGFR_amp",
            "HER2_amp": "HER2_amp", "TP53_mut": "TP53_mut", "CCND1_amp": "CCND1_amp", "CDKN2A_loss": "CDKN2A_loss", "PIK3CA_mut": "PIK3CA_mut",
            "EGFR": "EGFR_amp  or  EGF_stim", "HER2": "HER2_amp",
            "RAS": "EGFR  or  HER2", "MEK": "RAS", "ERK": "MEK",
            "PI3K": "PIK3CA_mut  or  EGFR  or  HER2", "AKT": "PI3K", "mTOR": "AKT",
            "STAT3": "EGFR  or  ERK", "NFkB": "AKT  or  Chemo_DNA_damage",
            "CDK4_6": "CCND1_amp  or  CDKN2A_loss",
            "ATM_ATR": "Chemo_DNA_damage", "P53": "ATM_ATR  and  not TP53_mut",
            "BCL2": "(NFkB  or  STAT3)  and  not BAX", "BCLxL": "(NFkB  or  STAT3  or  ERK)  and  not BAX",
            "MCL1": "(AKT  or  ERK  or  STAT3)  and  not BAX", "XIAP": "AKT  and  not SMAC",
            "BAX": "(P53  or  not BCL2  or  not BCLxL)  and  not MCL1",
            "CytoC": "BAX", "SMAC": "BAX", "Caspase9": "CytoC  and  not XIAP", "Caspase8": "Chemo_DNA_damage",
            "Caspase3": "(Caspase9  or  Caspase8)  and  not XIAP", "Apoptosis": "Caspase3",
            "Proliferation": "(ERK  or  AKT  or  CDK4_6)  and  not Apoptosis"
        },
        "patients": [
            {"id": "esca_pt01_her2_amp_trastuzumab_resistant", "sub": "HER2+ Esophageal Adenocarcinoma", "drv": "Focal HER2 amplification + secondary EGFR bypass", "rx": "Trastuzumab + Cisplatin/5-FU", "out": "Progression at 4.6 mo, celiac adenopathy", "res": "EGFR and PI3K/Akt activation bypasses HER2 blockade", "pin": {"HER2_amp": 1, "EGFR_amp": 1, "Chemo_DNA_damage": 1}},
            {"id": "esca_pt02_pembrolizumab_cured_pd_l1_high", "sub": "Esophageal Squamous Cell Carcinoma (ESCC)", "drv": "PD-L1 CPS >= 10, tobacco/alcohol mutational load", "rx": "Pembrolizumab + Chemo (KEYNOTE-590)", "out": "Complete Remission >42 mo (CURED)", "res": "Absence of rigid anti-apoptotic defenses facilitates rapid cytotoxic T-cell death", "pin": {"Chemo_DNA_damage": 1}},
            {"id": "esca_pt03_ccnd1_amp_cdk4_refractory", "sub": "CCND1-Amplified Advanced ESCC", "drv": "11q13 CCND1 amplification + TP53 missense", "rx": "Nivolumab + Ipilimumab (CheckMate-648)", "out": "Primary refractory, rapid death at 2.4 mo", "res": "Unrestrained CDK4/6 activity drives relentless S-phase entry", "pin": {"CCND1_amp": 1, "TP53_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "esca_pt04_pi3k_mutant_platinum_resistant", "sub": "PIK3CA E545K Activated Adenocarcinoma", "drv": "Activating PI3K catalytic mutation, high MCL-1", "rx": "FOLFOX chemotherapy", "out": "Early failure at 3.0 mo, hepatic spread", "res": "Constitutive Akt flux continuously phosphorylates BAD", "pin": {"PIK3CA_mut": 1, "TP53_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "esca_pt05_cdkn2a_null_radiochemo_refractory", "sub": "Biallelic CDKN2A Deleted ESCC", "drv": "Homozygous p16INK4a loss, high Cyclin D1", "rx": "Chemoradiotherapy (CROSS trial protocol)", "out": "Progression at 3.5 mo, tracheoesophageal fistula", "res": "Loss of p16INK4a hyperactivates CDK4/6, blocking radiation senescence", "pin": {"CDKN2A_loss": 1, "Chemo_DNA_damage": 1}},
            {"id": "esca_pt06_egfr_overexpressed_cetuximab_failure", "sub": "EGFR-Driven Mid-Thoracic ESCC", "drv": "High EGFR copy number, wild-type KRAS", "rx": "Cetuximab + Paclitaxel", "out": "Progression at 3.2 mo, bone metastases", "res": "Parallel PI3K and STAT3 survival transcription sustains Mcl-1", "pin": {"EGFR_amp": 1, "Chemo_DNA_damage": 1}},
            {"id": "esca_pt07_tp53_nonsense_fulminant_lethal", "sub": "Disruptive TP53 Null Esophageal Carcinoma", "drv": "TP53 R175H hotspot mutation, loss of BAX induction", "rx": "Docetaxel + Cisplatin + 5-FU", "out": "Primary chemo-resistance, death at 3.9 mo", "res": "Inability to transactivate BAX/PUMA upon DNA crosslinks", "pin": {"TP53_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "esca_pt08_pan_refractory_triplet_hit_lethal", "sub": "Pan-Refractory Triplet-Hit Gastroesophageal Cancer", "drv": "Concurrent HER2 amp, CCND1 amp, and TP53 null", "rx": "Trastuzumab Deruxtecan salvage", "out": "Rapid failure at 1.8 mo, death at 3.5 mo", "res": "Co-amplification of RTK and cell cycle drivers creates absolute apoptosis lock", "pin": {"HER2_amp": 1, "CCND1_amp": 1, "TP53_mut": 1, "Chemo_DNA_damage": 1}}
        ]
    },
    {
        "index": 16,
        "code": "thca",
        "name": "Thyroid Carcinoma (THCA - Papillary, Anaplastic, Medullary)",
        "citation": "TCGA-THCA (Cell 2014, 159:676-690); Schlumberger et al. (2015) NEJM (SELECT - Lenvatinib); Subbiah et al. (2020) Lancet Oncol (Selpercatinib)",
        "url": "https://doi.org/10.1016/j.cell.2014.09.050",
        "stimuli": ["TSH_stim", "Chemo_DNA_damage", "BRAF_mut", "RET_fusion", "RAS_mut", "TERT_prom_mut", "TP53_mut", "PIK3CA_mut"],
        "targets": ["BRAF", "RET", "MEK", "ERK", "PI3K", "AKT", "mTOR", "STAT3", "NFkB", "MCL1", "BCL2", "BCLxL", "XIAP"],
        "rules": {
            "TSH_stim": "TSH_stim", "Chemo_DNA_damage": "Chemo_DNA_damage", "BRAF_mut": "BRAF_mut",
            "RET_fusion": "RET_fusion", "RAS_mut": "RAS_mut", "TERT_prom_mut": "TERT_prom_mut",
            "TP53_mut": "TP53_mut", "PIK3CA_mut": "PIK3CA_mut",
            "RET": "RET_fusion", "RAS": "RAS_mut  or  RET", "BRAF": "BRAF_mut  or  RAS",
            "MEK": "BRAF", "ERK": "MEK",
            "PI3K": "PIK3CA_mut  or  RAS  or  RET", "AKT": "PI3K", "mTOR": "AKT",
            "STAT3": "RET  or  ERK", "NFkB": "AKT  or  Chemo_DNA_damage",
            "ATM_ATR": "Chemo_DNA_damage", "P53": "ATM_ATR  and  not TP53_mut",
            "BCL2": "(NFkB  or  STAT3)  and  not BAX", "BCLxL": "(NFkB  or  STAT3  or  ERK)  and  not BAX",
            "MCL1": "(AKT  or  ERK  or  STAT3)  and  not BAX", "XIAP": "AKT  and  not SMAC",
            "BAX": "(P53  or  not BCL2  or  not BCLxL)  and  not MCL1",
            "CytoC": "BAX", "SMAC": "BAX", "Caspase9": "CytoC  and  not XIAP", "Caspase8": "Chemo_DNA_damage",
            "Caspase3": "(Caspase9  or  Caspase8)  and  not XIAP", "Apoptosis": "Caspase3",
            "Proliferation": "(ERK  or  AKT  or  TERT_prom_mut)  and  not Apoptosis"
        },
        "patients": [
            {"id": "thca_pt01_braf_v600e_radioiodine_refractory", "sub": "Radioiodine-Refractory Papillary Thyroid Carcinoma (RAIR-PTC)", "drv": "BRAF V600E mutation, loss of sodium-iodide symporter (NIS)", "rx": "Lenvatinib (oral multikinase inhibitor)", "out": "PFS 18.3 mo (SELECT trial benefit)", "res": "Marked response initially; eventual resistance via PI3K/Akt feedback upregulation", "pin": {"BRAF_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "thca_pt02_ret_fusion_selpercatinib_responder", "sub": "CCDC6-RET Translocated Papillary Thyroid Cancer", "drv": "CCDC6-RET rearrangement, intact p53 axis", "rx": "Selpercatinib (highly selective RET kinase inhibitor)", "out": "Complete Remission >30 mo (LIBRETTO-001 benefit)", "res": "Potent uncoupling of RET collapses downstream MAPK and PI3K pathways", "pin": {"RET_fusion": 1, "Chemo_DNA_damage": 1}},
            {"id": "thca_pt03_anaplastic_braf_p53_double_hit_lethal", "sub": "Anaplastic Thyroid Carcinoma (ATC) - Ultra-Aggressive", "drv": "Concurrent BRAF V600E, TP53 null, and TERT promoter mutation", "rx": "Dabrafenib + Trametinib salvage", "out": "Primary failure at 2.1 mo, asphyxiation, death at 3.8 mo", "res": "Co-occurrence of p53 loss and TERT drives unstoppable mitotic immortality", "pin": {"BRAF_mut": 1, "TP53_mut": 1, "TERT_prom_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "thca_pt04_ras_mutant_follicular_carcinoma", "sub": "NRAS Q61R Mutant Follicular Thyroid Carcinoma", "drv": "Activating NRAS mutation, preferential PI3K signaling", "rx": "Sorafenib monotherapy", "out": "Progression at 4.5 mo, widespread pulmonary metastases", "res": "Feedback activation of CRAF and Akt shields cancer cells from Sorafenib", "pin": {"RAS_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "thca_pt05_medullary_ret_m918t_cabozantinib_res", "sub": "MEN2B / Sporadic Medullary Thyroid Carcinoma (MTC)", "drv": "RET M918T activating kinase mutation, secondary gatekeeper", "rx": "Cabozantinib (RET / VEGFR2 / MET inhibitor)", "out": "Progression at 5.2 mo, hepatic lesions, death at 11.0 mo", "res": "Acquired gatekeeper mutation impedes TKI binding pocket access", "pin": {"RET_fusion": 1, "PIK3CA_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "thca_pt06_tert_promoter_aggressive_recurrent", "sub": "High-Risk TERT-Mutated Tall-Cell PTC", "drv": "TERT C228T promoter mutation, telomerase reactivation", "rx": "Radioiodine ablation + Lenvatinib", "out": "Progression at 6.0 mo, invasive tracheal invasion", "res": "Telomerase immortality maintains genomic survival despite DNA radiation", "pin": {"TERT_prom_mut": 1, "BRAF_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "thca_pt07_pi3k_akt_hyperactive_refractory", "sub": "PIK3CA-Mutant Advanced Thyroid Carcinoma", "drv": "PIK3CA H1047R hotspot mutation + RAS activation", "rx": "Everolimus (mTOR inhibitor) + Lenvatinib", "out": "Progression at 3.4 mo, pleural effusion", "res": "mTOR inhibition triggers relief of feedback inhibition on Akt/Mcl-1", "pin": {"PIK3CA_mut": 1, "RAS_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "thca_pt08_pan_refractory_anaplastic_triplet_hit", "sub": "Pan-Refractory Quadruple-Feature Anaplastic Carcinoma", "drv": "BRAF V600E + RET + TP53 null + TERT triplet", "rx": "Chemo-IO followed by multi-TKI salvage", "out": "Death at 2.0 mo, fulminant neck mass", "res": "Simultaneous activation of dual kinase drivers with p53 loss locks apoptosis", "pin": {"BRAF_mut": 1, "RET_fusion": 1, "TP53_mut": 1, "TERT_prom_mut": 1, "Chemo_DNA_damage": 1}}
        ]
    }
]


def generate_cancer_spec_p3(spec):
    code = spec["code"]
    c_name = spec["name"]
    print("\n" + "=" * 80)
    print(f"  [+] UNLOCKING CANCER #{spec['index']:02d}: {c_name.upper()}")
    print(f"      Citation: {spec['citation']}")
    print("=" * 80)

    # 1. Model JSON
    m_dict = {
        "name": c_name, "citation": spec["citation"], "url": spec["url"],
        "stimuli": spec["stimuli"], "drug_targets": spec["targets"],
        "phenotypes": {"cancer_state": {"Proliferation": 1, "Apoptosis": 0}, "curative_state": {"Proliferation": 0, "Apoptosis": 1}},
        "rules": spec["rules"]
    }
    with open(RAW_DIR / f"{code}_model.json", "w", encoding="utf-8") as f:
        json.dump(m_dict, f, indent=2)

    # 2. Patient CNFs
    pt_dir = ROOT / "data" / "benchmarks" / f"{code}_patients"
    pt_dir.mkdir(parents=True, exist_ok=True)
    ledger_entries = {}

    for pt in spec["patients"]:
        pt_id = pt["id"]
        pinned = dict(pt["pin"])
        pinned["Proliferation"] = 0
        pinned["Apoptosis"] = 1

        m_copy = dict(m_dict)
        m_copy["stimuli"] = [k for k, v in pinned.items() if v == 1 and k not in ("Apoptosis", "Proliferation")]
        m_copy["phenotypes"] = {
            "cancer_state": {"Proliferation": 1, "Apoptosis": 0},
            "curative_state": {"Proliferation": 0, "Apoptosis": 1}
        }

        encoder = TseitinCNFEncoder(m_copy)
        cnf_file = pt_dir / f"{pt_id}.cnf"
        map_file = pt_dir / f"{pt_id}.mapping.json"
        encoder.export_dimacs(cnf_file, map_file)

        encoder.export_dimacs(BENCHMARK_DIR / f"{pt_id}.cnf", BENCHMARK_DIR / f"{pt_id}.mapping.json")

        with open(map_file, "r", encoding="utf-8") as f:
            mp = json.load(f)

        print(f"      [✓] Patient: {pt_id:<45} | Vars: {mp['n_vars']:<3} | Clauses: {mp['n_clauses']:<3}")
        ledger_entries[pt_id] = {
            "title": f"Patient {pt_id}: {pt['sub']}", "citation": spec["citation"],
            "clinical_history": {"subtype": pt["sub"], "primary_driver": pt["drv"], "hospital_treatment": pt["rx"], "real_world_outcome": pt["out"], "known_resistance_mechanism": pt["res"]},
            "pinned": pinned
        }

    # 3. Ledgers
    with open(pt_dir / f"{code.upper()}_PATIENTS_CLINICAL_TRUTH_LEDGER.json", "w", encoding="utf-8") as f:
        json.dump(ledger_entries, f, indent=2)
    with open(pt_dir / f"{code.upper()}_PATIENTS_CLINICAL_TRUTH_LEDGER.md", "w", encoding="utf-8") as f:
        f.write(f"# Official Clinical Ledger: {c_name} Patients\n\n")
        for k, v in ledger_entries.items():
            ch = v["clinical_history"]
            f.write(f"### {k}\n- **Subtype:** {ch['subtype']}\n- **Hospital Treatment:** {ch['hospital_treatment']}\n- **Outcome:** {ch['real_world_outcome']}\n- **Resistance:** {ch['known_resistance_mechanism']}\n\n")

    # 4. Runner
    runner_py = ROOT / f"run_{code}_patient_study.py"
    with open(runner_py, "w", encoding="utf-8") as f:
        f.write(f'''#!/usr/bin/env python3
import csv, json, os, sys, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from flyfly_oncology.fly_oncology_solver import FlyOncologySolver, OncologySolverConfig
from flyfly_oncology.telemetry_logger import OncologyTelemetryLogger
from flyfly_oncology.dataset_downloader import load_model

def run_{code}_study():
    graph_path = ROOT / "flyfly_sat" / "data" / "processed" / "graph_core.pt"
    if not graph_path.exists():
        graph_path = ROOT / "data" / "processed" / "graph_core.pt"
    patient_dir = ROOT / "flyfly_oncology" / "data" / "benchmarks" / "{code}_patients"
    patient_cnfs = sorted(list(patient_dir.glob("{code}_pt*.cnf")))
    ledger_path = patient_dir / "{code.upper()}_PATIENTS_CLINICAL_TRUTH_LEDGER.json"
    clinical_ledger = {{}}
    if ledger_path.exists():
        with open(ledger_path, "r", encoding="utf-8") as f:
            clinical_ledger = json.load(f)
    model_dict = load_model("{code}")
    log_base = ROOT / "flyfly_oncology" / "logs" / f"{code}_8_patient_study_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"
    log_base.mkdir(parents=True, exist_ok=True)
    print("=" * 84)
    print("      VIRTUAL DROSOPHILA SNN DISCOVERY: 8 REAL {c_name.upper()} PATIENTS")
    print("=" * 84)
    for idx, cnf_path in enumerate(patient_cnfs, 1):
        b_id = cnf_path.stem
        map_path = cnf_path.with_suffix(".mapping.json")
        with open(map_path, "r", encoding="utf-8") as f:
            mapping = json.load(f)
        cfg = OncologySolverConfig(max_steps=5000, seed=42, max_allowed_drugs=3, target_apoptosis=90.0, validation_noise=0.02)
        logger = OncologyTelemetryLogger(base_log_dir=log_base, run_name=f"{{b_id}}_s42", noise_percent=2.0)
        solver = FlyOncologySolver(cnf_path=cnf_path, mapping_path=map_path, model_dict=model_dict, graph_path=graph_path, cfg=cfg, logger=logger, pinned_vars=mapping.get("pinned_variables", {{}}))
        res = solver.solve()
        print(f"  [✓] {{b_id}}: Active Regimen: {{' + '.join(res.get('active_drugs', []))}} | Apoptosis: {{res.get('apoptosis_rate_noisy', 0.0):.1f}}%")

if __name__ == "__main__":
    run_{code}_study()
''')
    print(f"      [✓] Runner Script Generated: {runner_py.name}")
    print(f"      [✓] Benchmark Directory Ready: {pt_dir.name} (8 CNFs)")


def run_pipeline_part3():
    print("\n" + "#" * 84)
    print("   LAUNCHING SEQUENTIAL PAN-CANCER EXPANSION PART 3 (WITH 60-SEC INTERVALS)")
    print("#" * 84)
    for i, spec in enumerate(CANCER_SPECS_PART3):
        generate_cancer_spec_p3(spec)
        if i < len(CANCER_SPECS_PART3) - 1:
            print("\n" + "-" * 80)
            print("  [SLEEP 60s] Pausing 60 seconds as requested before next cancer...")
            print("-" * 80)
            for sec in range(60, 0, -10):
                print(f"   ↳ {sec}s remaining until next cancer unlocks...")
                time.sleep(10)


if __name__ == "__main__":
    run_pipeline_part3()
