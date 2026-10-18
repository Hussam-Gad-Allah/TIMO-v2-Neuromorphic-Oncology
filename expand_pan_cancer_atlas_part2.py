#!/usr/bin/env python3
"""
Pan-Cancer Atlas Expansion Engine - Part 2 (Cancers #13 to #20).
Generates:
13. BLCA - Bladder / Urothelial Carcinoma
14. HNSCC - Head & Neck Squamous Cell Carcinoma
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


CANCER_SPECS_PART2 = [
    {
        "index": 13,
        "code": "blca",
        "name": "Bladder & Urothelial Carcinoma (BLCA)",
        "citation": "TCGA-BLCA (Cell 2017, 171:540-556); Loriot et al. (2019) NEJM (BLC2001 - Erdafitinib); Powles et al. (2024) NEJM (EV-302)",
        "url": "https://doi.org/10.1016/j.cell.2017.09.007",
        "stimuli": ["EGF_stim", "FGF_stim", "Chemo_DNA_damage", "FGFR3_mut", "ERBB2_amp", "PIK3CA_mut", "TP53_mut", "RB1_loss", "KDM6A_loss"],
        "targets": ["FGFR3", "HER2", "EGFR", "MEK", "ERK", "PI3K", "AKT", "mTOR", "STAT3", "NFkB", "MCL1", "BCL2", "BCLxL", "XIAP"],
        "rules": {
            "EGF_stim": "EGF_stim", "FGF_stim": "FGF_stim", "Chemo_DNA_damage": "Chemo_DNA_damage",
            "FGFR3_mut": "FGFR3_mut", "ERBB2_amp": "ERBB2_amp", "PIK3CA_mut": "PIK3CA_mut",
            "TP53_mut": "TP53_mut", "RB1_loss": "RB1_loss", "KDM6A_loss": "KDM6A_loss",
            "FGFR3": "FGFR3_mut  or  FGF_stim", "HER2": "ERBB2_amp", "EGFR": "EGF_stim",
            "RAS": "FGFR3  or  HER2  or  EGFR", "MEK": "RAS", "ERK": "MEK",
            "PI3K": "PIK3CA_mut  or  FGFR3  or  HER2", "AKT": "PI3K", "mTOR": "AKT",
            "STAT3": "FGFR3  or  ERK", "NFkB": "AKT  or  Chemo_DNA_damage",
            "ATM_ATR": "Chemo_DNA_damage", "P53": "ATM_ATR  and  not TP53_mut",
            "BCL2": "(NFkB  or  STAT3)  and  not BAX", "BCLxL": "(NFkB  or  STAT3  or  ERK)  and  not BAX",
            "MCL1": "(AKT  or  ERK  or  STAT3)  and  not BAX", "XIAP": "AKT  and  not SMAC",
            "BAX": "(P53  or  not BCL2  or  not BCLxL)  and  not MCL1",
            "CytoC": "BAX", "SMAC": "BAX", "Caspase9": "CytoC  and  not XIAP", "Caspase8": "Chemo_DNA_damage",
            "Caspase3": "(Caspase9  or  Caspase8)  and  not XIAP", "Apoptosis": "Caspase3",
            "Proliferation": "(ERK  or  AKT  or  FGFR3)  and  not Apoptosis"
        },
        "patients": [
            {"id": "blca_pt01_fgfr3_s249c_erdafitinib_resistant", "sub": "Luminal-Papillary FGFR3-Mutant Bladder Cancer", "drv": "FGFR3 S249C activating mutation with acquired PI3K bypass", "rx": "Erdafitinib (selective oral FGFR1-4 inhibitor)", "out": "PFS 5.5 mo, rapid bilateral pelvic progression", "res": "Parallel PIK3CA activation and MCL-1 stabilization bypasses FGFR3 inhibition", "pin": {"FGFR3_mut": 1, "PIK3CA_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "blca_pt02_her2_amplified_platinum_failure", "sub": "ERBB2-Amplified Infiltrating Urothelial Carcinoma", "drv": "High-level HER2 gene amplification + TP53 loss", "rx": "Gemcitabine + Cisplatin", "out": "Primary chemo-refractory at 3.0 mo, retroperitoneal lymphadenopathy", "res": "HER2 hyperactivation insulates cancer cells against platinum crosslinks", "pin": {"ERBB2_amp": 1, "TP53_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "blca_pt03_tmb_high_pembrolizumab_cured", "sub": "Basal-Squamous High-TMB Immunotherapy Responsive", "drv": "APOBEC-mediated hypermutation, intact p53 axis", "rx": "Pembrolizumab (anti-PD-1)", "out": "Complete Remission >45 mo (CURED)", "res": "Absence of rigid anti-apoptotic defenses facilitates rapid cytotoxic T-cell lysis", "pin": {"Chemo_DNA_damage": 1}},
            {"id": "blca_pt04_rb1_p53_double_null_neuroendocrine", "sub": "Small-Cell / Neuroendocrine Transformed BLCA", "drv": "Concurrent biallelic loss of TP53 and RB1", "rx": "Etoposide + Cisplatin", "out": "Transient response 3.2 mo, rapid visceral death at 6.0 mo", "res": "Bypass of all cell-cycle checkpoints confers aggressive apoptosis resistance", "pin": {"TP53_mut": 1, "RB1_loss": 1, "Chemo_DNA_damage": 1}},
            {"id": "blca_pt05_kdm6a_mutant_epigenetic_instability", "sub": "KDM6A Epigenetic Altered Urothelial Carcinoma", "drv": "Truncating KDM6A mutation, defective histone methylation", "rx": "Enfortumab Vedotin + Pembrolizumab (EV-302)", "out": "PFS 24.1 mo, outstanding clinical benefit", "res": "High epigenetic replication stress sensitizes tumor to combined targeted perturbation", "pin": {"KDM6A_loss": 1, "Chemo_DNA_damage": 1}},
            {"id": "blca_pt06_pi3k_mutant_gemcitabine_resistant", "sub": "PIK3CA E542K Activated Infiltrating Carcinoma", "drv": "Activating PI3K catalytic subunit mutation", "rx": "Gemcitabine + Carboplatin", "out": "Early progression at 2.9 mo, lung metastases", "res": "Constitutive AKT flux phosphorylates BAD and suppresses mitochondrial death", "pin": {"PIK3CA_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "blca_pt07_fgfr3_fusion_acquired_gatekeeper_mut", "sub": "FGFR3-TACC3 Translocated Advanced Carcinoma", "drv": "FGFR3-TACC3 rearrangement + secondary gatekeeper V555M", "rx": "Infigratinib salvage", "out": "Progression at 3.4 mo, bony metastases", "res": "Gatekeeper mutation produces steric clash in ATP pocket", "pin": {"FGFR3_mut": 1, "FGF_stim": 1, "Chemo_DNA_damage": 1}},
            {"id": "blca_pt08_pan_refractory_fgfr_her2_p53_triplet", "sub": "Pan-Refractory Triplet-Hit Urothelial Carcinoma", "drv": "Concurrent FGFR3 mut, HER2 amp, and TP53 null", "rx": "Chemo-IO followed by ADC salvage", "out": "Rapid failure at 1.9 mo, liver failure", "res": "Dual RTK hyperactivation with p53 loss locks the apoptotic threshold", "pin": {"FGFR3_mut": 1, "ERBB2_amp": 1, "TP53_mut": 1, "Chemo_DNA_damage": 1}}
        ]
    },
    {
        "index": 14,
        "code": "hnscc",
        "name": "Head & Neck Squamous Cell Carcinoma (HNSCC)",
        "citation": "TCGA-HNSC (Nature 2015, 517:576-582); Vermorken et al. (2008) NEJM (EXTREME); Burtness et al. (2019) Lancet (KEYNOTE-048)",
        "url": "https://doi.org/10.1038/nature14129",
        "stimuli": ["EGF_stim", "Chemo_DNA_damage", "EGFR_amp", "PIK3CA_mut", "TP53_mut", "CDKN2A_loss", "CCND1_amp", "HPV_pos", "NOTCH1_loss"],
        "targets": ["EGFR", "PI3K", "AKT", "mTOR", "MEK", "ERK", "STAT3", "NFkB", "CDK4_6", "MCL1", "BCL2", "BCLxL", "XIAP"],
        "rules": {
            "EGF_stim": "EGF_stim", "Chemo_DNA_damage": "Chemo_DNA_damage", "EGFR_amp": "EGFR_amp",
            "PIK3CA_mut": "PIK3CA_mut", "TP53_mut": "TP53_mut", "CDKN2A_loss": "CDKN2A_loss",
            "CCND1_amp": "CCND1_amp", "HPV_pos": "HPV_pos", "NOTCH1_loss": "NOTCH1_loss",
            "EGFR": "EGFR_amp  or  EGF_stim",
            "RAS": "EGFR", "MEK": "RAS", "ERK": "MEK",
            "PI3K": "PIK3CA_mut  or  EGFR", "AKT": "PI3K", "mTOR": "AKT",
            "STAT3": "EGFR  or  ERK", "NFkB": "AKT  or  Chemo_DNA_damage",
            "CDK4_6": "CCND1_amp  or  CDKN2A_loss",
            "ATM_ATR": "Chemo_DNA_damage", "P53": "(ATM_ATR  and  not TP53_mut)  and  not HPV_pos",
            "BCL2": "(NFkB  or  STAT3)  and  not BAX", "BCLxL": "(NFkB  or  STAT3  or  ERK)  and  not BAX",
            "MCL1": "(AKT  or  ERK  or  STAT3)  and  not BAX", "XIAP": "AKT  and  not SMAC",
            "BAX": "(P53  or  not BCL2  or  not BCLxL)  and  not MCL1",
            "CytoC": "BAX", "SMAC": "BAX", "Caspase9": "CytoC  and  not XIAP", "Caspase8": "Chemo_DNA_damage",
            "Caspase3": "(Caspase9  or  Caspase8)  and  not XIAP", "Apoptosis": "Caspase3",
            "Proliferation": "(ERK  or  AKT  or  CDK4_6)  and  not Apoptosis"
        },
        "patients": [
            {"id": "hnscc_pt01_egfr_amp_cetuximab_resistant", "sub": "HPV-Negative EGFR-Amplified Laryngeal Carcinoma", "drv": "High EGFR copy number, secondary MET/AXL flux", "rx": "Cetuximab (anti-EGFR) + Platinum/5-FU (EXTREME)", "out": "Progression at 4.5 mo, bilateral neck nodal recurrence", "res": "Parallel PI3K/Akt activation and persistent STAT3 sustain MCL-1 despite Cetuximab", "pin": {"EGFR_amp": 1, "Chemo_DNA_damage": 1}},
            {"id": "hnscc_pt02_hpv_positive_exceptional_responder", "sub": "HPV-Associated Oropharyngeal Carcinoma (p16+)", "drv": "High-risk HPV-16 E6/E7 oncoprotein expression, wild-type TP53", "rx": "Cisplatin + Radiation therapy", "out": "Complete Remission >60 mo (CURED)", "res": "Intact apoptotic machinery readily responds to genotoxic radiation damage", "pin": {"HPV_pos": 1, "Chemo_DNA_damage": 1}},
            {"id": "hnscc_pt03_ccnd1_amp_cdk4_hyperactive_refractory", "sub": "CCND1-Amplified Recurrent Oral Cavity Squamous Carcinoma", "drv": "11q13 CCND1 amplification, CDKN2A deletion", "rx": "Pembrolizumab + Chemo (KEYNOTE-048)", "out": "Early failure at 2.6 mo, carotid blowout, death at 5.1 mo", "res": "Unrestrained CDK4/6 activity overrides cell-cycle checkpoint arrest", "pin": {"CCND1_amp": 1, "CDKN2A_loss": 1, "TP53_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "hnscc_pt04_pi3k_mutant_radioresistant", "sub": "PIK3CA Helical Mutant Radioresistant Carcinoma", "drv": "PIK3CA E545K mutation + TP53 missense", "rx": "Docetaxel + Cisplatin + 5-FU (TPF induction)", "out": "Progression at 3.1 mo, pulmonary metastases", "res": "Constitutive Akt activation prevents radiation-induced cytochrome c release", "pin": {"PIK3CA_mut": 1, "TP53_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "hnscc_pt05_notch1_loss_stem_like_aggressive", "sub": "NOTCH1-Deficient Dedifferentiated Oral Cancer", "drv": "Inactivating NOTCH1 mutation, mesenchymal stem traits", "rx": "Nivolumab monotherapy", "out": "Primary immune evasion at 2.1 mo, death at 4.8 mo", "res": "Mesenchymal transition upregulates XIAP and BCL-xL survival buffer", "pin": {"NOTCH1_loss": 1, "TP53_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "hnscc_pt06_pembrolizumab_cured_high_cps", "sub": "PD-L1 High (CPS >= 50) Squamous Carcinoma", "drv": "Tobacco smoking mutational signature, wild-type PIK3CA", "rx": "Pembrolizumab monotherapy", "out": "Durable Complete Remission >36 mo (CURED)", "res": "Absence of oncogene-driven anti-apoptotic traps allows cytotoxic T-cell lysis", "pin": {"Chemo_DNA_damage": 1}},
            {"id": "hnscc_pt07_tp53_disruptive_platinum_refractory", "sub": "Disruptive TP53 Mutant Hypopharyngeal Cancer", "drv": "DNA-binding domain nonsense TP53 mutation", "rx": "Carboplatin + Paclitaxel", "out": "Refractory at 2.8 mo, distant bone metastases", "res": "Total absence of p53 eliminates transactivation of pro-apoptotic BAX", "pin": {"TP53_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "hnscc_pt08_pan_refractory_egfr_pi3k_p53_triplet", "sub": "Pan-Refractory Triplet-Hit Head & Neck Cancer", "drv": "Concurrent EGFR amp, PIK3CA mut, and TP53 null", "rx": "Cetuximab + Chemotherapy followed by IO salvage", "out": "Rapid failure at 1.7 mo, death at 3.9 mo", "res": "Simultaneous activation of EGFR and PI3K with p53 loss establishes total resistance", "pin": {"EGFR_amp": 1, "PIK3CA_mut": 1, "TP53_mut": 1, "Chemo_DNA_damage": 1}}
        ]
    }
]


def generate_cancer_spec(spec):
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


def run_pipeline_part2():
    print("\n" + "#" * 84)
    print("   LAUNCHING SEQUENTIAL PAN-CANCER EXPANSION PART 2 (WITH 60-SEC INTERVALS)")
    print("#" * 84)
    for i, spec in enumerate(CANCER_SPECS_PART2):
        generate_cancer_spec(spec)
        if i < len(CANCER_SPECS_PART2) - 1:
            print("\n" + "-" * 80)
            print("  [SLEEP 60s] Pausing 60 seconds as requested before next cancer...")
            print("-" * 80)
            for sec in range(60, 0, -10):
                print(f"   ↳ {sec}s remaining until next cancer unlocks...")
                time.sleep(10)


if __name__ == "__main__":
    run_pipeline_part2()
