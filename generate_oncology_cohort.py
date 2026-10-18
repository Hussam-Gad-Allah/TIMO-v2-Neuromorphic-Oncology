"""
Clinical Oncology Cohort Benchmark Generator.
Generates 12 patient-specific cancer Boolean 3-SAT instances (6 T-LGL Leukemia + 6 AML variants)
mirroring the UF100 benchmark methodology (uf100-01 to uf100-12).

Each benchmark instance represents a distinct clinical patient subtype with specific driver mutations,
microenvironment niches, and drug resistance profiles.
"""

import json
from pathlib import Path
from flyfly_oncology.dataset_downloader import get_t_lgl_model, get_aml_model
from flyfly_oncology.tseitin_cnf_encoder import TseitinCNFEncoder

BENCH_DIR = Path(__file__).resolve().parent / "data" / "benchmarks"
BENCH_DIR.mkdir(parents=True, exist_ok=True)

# 1. T-LGL Leukemia Clinical Cohort (6 instances)
TLGL_COHORT = [
    {
        "id": "tlgl_inst01_baseline",
        "title": "T-LGL Patient 01: Standard Autocrine Cytokine Attractor",
        "pinned": {"Stimuli": 1, "IL15": 1, "PDGF": 1, "Proliferation": 0, "Apoptosis": 1},
        "description": "Primary T-LGL patient with dual IL-15 and PDGF autocrine survival loops."
    },
    {
        "id": "tlgl_inst02_hyper_il15",
        "title": "T-LGL Patient 02: Hyper-IL15 Autocrine Attractor",
        "pinned": {"Stimuli": 1, "IL15": 1, "PDGF": 0, "Proliferation": 0, "Apoptosis": 1},
        "description": "Patient with intense IL-15 autocrine loop driving the JAK-STAT3 survival axis."
    },
    {
        "id": "tlgl_inst03_pdgf_sphk1",
        "title": "T-LGL Patient 03: PDGF-Driven SPHK1-S1P Attractor",
        "pinned": {"Stimuli": 0, "IL15": 0, "PDGF": 1, "Proliferation": 0, "Apoptosis": 1},
        "description": "PDGF-predominant patient activating Sphingosine Kinase 1 (SPHK1) and S1P."
    },
    {
        "id": "tlgl_inst04_sfas_decoy",
        "title": "T-LGL Patient 04: Soluble Fas Decoy Receptor Resistance",
        "pinned": {"Stimuli": 1, "IL15": 1, "PDGF": 1, "sFas": 1, "Proliferation": 0, "Apoptosis": 1},
        "description": "Fas-resistant patient overexpressing soluble decoy receptor sFas."
    },
    {
        "id": "tlgl_inst05_cd45_tyrosine",
        "title": "T-LGL Patient 05: CD45 Phosphatase Hyper-activation",
        "pinned": {"Stimuli": 1, "IL15": 1, "CD45": 1, "Proliferation": 0, "Apoptosis": 1},
        "description": "Patient with hyperactive CD45 phosphatase maintaining LCK and FYN tyrosine kinase signaling."
    },
    {
        "id": "tlgl_inst06_tax_oncogene",
        "title": "T-LGL Patient 06: Viral HTLV-1 TAX Oncoprotein Survival",
        "pinned": {"Stimuli": 1, "TAX": 1, "Proliferation": 0, "Apoptosis": 1},
        "description": "Refractory patient driven by viral TAX oncoprotein triggering constitutive TPL2/NF-kB."
    }
]

# 2. AML Leukemia Clinical Cohort (6 instances)
AML_COHORT = [
    {
        "id": "aml_inst01_flt3_itd_std",
        "title": "AML Patient 01: Standard FLT3-ITD Positive",
        "pinned": {"FLT3_ITD": 1, "Microenv": 0, "NPM1_mut": 0, "DNMT3A_mut": 0, "Proliferation": 0, "Apoptosis": 1},
        "description": "Standard FLT3-ITD mutated AML sensitive to targeted kinase/survival inhibition."
    },
    {
        "id": "aml_inst02_dnmt3a_resistant",
        "title": "AML Patient 02: DNMT3A-mutant High-Risk Resistant",
        "pinned": {"FLT3_ITD": 1, "Microenv": 0, "NPM1_mut": 0, "DNMT3A_mut": 1, "Proliferation": 0, "Apoptosis": 1},
        "description": "High-risk resistant patient with DNMT3A epigenetic silencing of P53, resisting monotherapy."
    },
    {
        "id": "aml_inst03_npm1_co_mutant",
        "title": "AML Patient 03: FLT3-ITD + NPM1 Co-mutated",
        "pinned": {"FLT3_ITD": 1, "Microenv": 0, "NPM1_mut": 1, "DNMT3A_mut": 0, "Proliferation": 0, "Apoptosis": 1},
        "description": "Double-mutated patient with FLT3-ITD and NPM1 activating anti-apoptotic BCL-2."
    },
    {
        "id": "aml_inst04_microenv_niche",
        "title": "AML Patient 04: Bone Marrow Microenvironment Protected",
        "pinned": {"FLT3_ITD": 1, "Microenv": 1, "NPM1_mut": 0, "DNMT3A_mut": 0, "Proliferation": 0, "Apoptosis": 1},
        "description": "Stroma-protected niche providing extrinsic microenvironmental survival drive via PI3K/AKT."
    },
    {
        "id": "aml_inst05_pan_resistant",
        "title": "AML Patient 05: Pan-Resistant Triple Mutant",
        "pinned": {"FLT3_ITD": 1, "Microenv": 1, "NPM1_mut": 1, "DNMT3A_mut": 1, "Proliferation": 0, "Apoptosis": 1},
        "description": "Ultra-high-risk patient with FLT3-ITD, NPM1, DNMT3A, and stromal microenvironment protection."
    },
    {
        "id": "aml_inst06_relapsed_refractory",
        "title": "AML Patient 06: Relapsed/Refractory Dual-Axis Dependent",
        "pinned": {"FLT3_ITD": 1, "Microenv": 1, "NPM1_mut": 0, "DNMT3A_mut": 1, "Proliferation": 0, "Apoptosis": 1},
        "description": "Relapsed/refractory patient requiring dual-target BCL2 + MCL1 synthetic lethality."
    }
]


def generate_cohort():
    t_lgl_base = get_t_lgl_model()
    aml_base = get_aml_model()

    print("=" * 80)
    print(f"GENERATING 12 CLINICAL ONCOLOGY 3-SAT BENCHMARKS (UF100 METHODOLOGY)")
    print(f"Output Directory: {BENCH_DIR}")
    print("=" * 80)

    # Generate T-LGL Instances
    for p in TLGL_COHORT:
        model = dict(t_lgl_base)
        model["name"] = p["title"]
        model["phenotypes"]["curative_state"] = {"Proliferation": 0, "Apoptosis": 1}
        # Inject patient-specific pinned stimuli
        model["stimuli"] = [k for k, v in p["pinned"].items() if v == 1 and k not in ("Proliferation", "Apoptosis")]

        encoder = TseitinCNFEncoder(model)
        cnf_file = BENCH_DIR / f"{p['id']}.cnf"
        encoder.export_dimacs(cnf_file)

        # Save clinical profile
        profile_file = BENCH_DIR / f"{p['id']}.profile.json"
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2)

    # Generate AML Instances
    for p in AML_COHORT:
        model = dict(aml_base)
        model["name"] = p["title"]
        model["phenotypes"]["curative_state"] = {"Proliferation": 0, "Apoptosis": 1}
        model["stimuli"] = [k for k, v in p["pinned"].items() if v == 1 and k not in ("Proliferation", "Apoptosis")]

        encoder = TseitinCNFEncoder(model)
        cnf_file = BENCH_DIR / f"{p['id']}.cnf"
        encoder.export_dimacs(cnf_file)

        # Save clinical profile
        profile_file = BENCH_DIR / f"{p['id']}.profile.json"
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2)

    print("=" * 80)
    print(f"Successfully generated 12 Clinical Benchmark Instances in {BENCH_DIR.name}!")
    print("=" * 80)


if __name__ == "__main__":
    generate_cohort()
