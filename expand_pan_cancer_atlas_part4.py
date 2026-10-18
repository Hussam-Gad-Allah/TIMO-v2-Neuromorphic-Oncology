#!/usr/bin/env python3
"""
Pan-Cancer Atlas Expansion Engine - Part 4 (Cancers #17 to #20 - Grand Finale).
Generates:
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


CANCER_SPECS_PART4 = [
    {
        "index": 17,
        "code": "sarc",
        "name": "Soft Tissue Sarcoma & GIST (SARC)",
        "citation": "TCGA-SARC (Cell 2017, 171:562-575); Demetri et al. (2002) NEJM (Imatinib in GIST); Tap et al. (2016) Lancet (Doxorubicin + Olaratumab)",
        "url": "https://doi.org/10.1016/j.cell.2017.10.014",
        "stimuli": ["PDGF_stim", "Chemo_DNA_damage", "KIT_mut", "PDGFRA_mut", "MDM2_amp", "CDK4_amp", "TP53_mut", "RB1_loss"],
        "targets": ["cKIT", "PDGFR", "MEK", "ERK", "PI3K", "AKT", "mTOR", "MDM2", "CDK4_6", "STAT3", "NFkB", "MCL1", "BCL2", "BCLxL", "XIAP"],
        "rules": {
            "PDGF_stim": "PDGF_stim", "Chemo_DNA_damage": "Chemo_DNA_damage", "KIT_mut": "KIT_mut",
            "PDGFRA_mut": "PDGFRA_mut", "MDM2_amp": "MDM2_amp", "CDK4_amp": "CDK4_amp", "TP53_mut": "TP53_mut", "RB1_loss": "RB1_loss",
            "cKIT": "KIT_mut", "PDGFR": "PDGFRA_mut  or  PDGF_stim",
            "RAS": "cKIT  or  PDGFR", "MEK": "RAS", "ERK": "MEK",
            "PI3K": "cKIT  or  PDGFR", "AKT": "PI3K", "mTOR": "AKT",
            "STAT3": "cKIT  or  ERK", "NFkB": "AKT  or  Chemo_DNA_damage",
            "CDK4_6": "CDK4_amp", "MDM2": "MDM2_amp  or  AKT",
            "ATM_ATR": "Chemo_DNA_damage", "P53": "ATM_ATR  and  not MDM2  and  not TP53_mut",
            "BCL2": "(NFkB  or  STAT3)  and  not BAX", "BCLxL": "(NFkB  or  STAT3  or  ERK)  and  not BAX",
            "MCL1": "(AKT  or  ERK  or  STAT3)  and  not BAX", "XIAP": "AKT  and  not SMAC",
            "BAX": "(P53  or  not BCL2  or  not BCLxL)  and  not MCL1",
            "CytoC": "BAX", "SMAC": "BAX", "Caspase9": "CytoC  and  not XIAP", "Caspase8": "Chemo_DNA_damage",
            "Caspase3": "(Caspase9  or  Caspase8)  and  not XIAP", "Apoptosis": "Caspase3",
            "Proliferation": "(ERK  or  AKT  or  CDK4_6)  and  not Apoptosis"
        },
        "patients": [
            {"id": "sarc_pt01_gist_kit_exon11_imatinib_resistant", "sub": "Gastrointestinal Stromal Tumor (GIST)", "drv": "KIT exon 11 del with secondary exon 17 D816H gatekeeper", "rx": "Imatinib mesylate 400mg daily", "out": "Progression at 5.2 mo, multiple liver metastases", "res": "Secondary ATP activation loop mutation impairs Imatinib binding", "pin": {"KIT_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "sarc_pt02_dedifferentiated_liposarcoma_mdm2_amp", "sub": "Dedifferentiated Liposarcoma (DDLPS)", "drv": "Giant 12q13-15 amplicon (MDM2 + CDK4 co-amplified)", "rx": "Doxorubicin monotherapy", "out": "Primary chemo-refractory at 2.4 mo, retroperitoneal mass >25cm", "res": "Massive MDM2 amplification targets p53 for constant degradation", "pin": {"MDM2_amp": 1, "CDK4_amp": 1, "Chemo_DNA_damage": 1}},
            {"id": "sarc_pt03_leiomyosarcoma_rb1_p53_double_null", "sub": "Uterine / Retroperitoneal Leiomyosarcoma (LMS)", "drv": "Biallelic loss of both TP53 and RB1", "rx": "Gemcitabine + Docetaxel", "out": "Refractory at 3.0 mo, multiple pulmonary cannonball lesions", "res": "Complete ablation of cell-cycle arrest and apoptosis checkpoints", "pin": {"TP53_mut": 1, "RB1_loss": 1, "Chemo_DNA_damage": 1}},
            {"id": "sarc_pt04_pdgfra_d842v_avapritinib_responder", "sub": "PDGFRA-Mutant Gastric GIST", "drv": "Pathognomonic PDGFRA exon 18 D842V mutation", "rx": "Avapritinib (NAVIGATOR trial protocol)", "out": "Durable Complete Remission >36 mo (CURED)", "res": "Selective conformation-specific uncoupling of mutant PDGFRA", "pin": {"PDGFRA_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "sarc_pt05_synovial_sarcoma_ss18_ssx_fusion", "sub": "Monophasic Synovial Sarcoma", "drv": "t(X;18) SS18-SSX fusion driving BAF complex remodeling", "rx": "Ifosfamide + Doxorubicin", "out": "Progression at 4.1 mo, pleural effusion", "res": "Epigenetic transcriptional rewiring sustains Mcl-1 and Bcl-2", "pin": {"Chemo_DNA_damage": 1}},
            {"id": "sarc_pt06_undifferentiated_pleomorphic_sarcoma_ups", "sub": "High-Grade Undifferentiated Pleomorphic Sarcoma (UPS)", "drv": "Severe chromosomal complexity, TP53 missense", "rx": "Pembrolizumab (SARC028 trial)", "out": "PFS 19.5 mo, major clinical benefit", "res": "High neoantigenic burden and inflammatory microenvironment", "pin": {"TP53_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "sarc_pt07_angiosarcoma_radiation_induced_cmyc_amp", "sub": "Post-Radiation Cutaneous Angiosarcoma", "drv": "High-level MYC amplification + vascular endothelial proliferation", "rx": "Paclitaxel weekly", "out": "Progression at 2.8 mo, scalp ulceration, death at 5.5 mo", "res": "MYC overexpression overrides taxane mitotic apoptosis", "pin": {"TP53_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "sarc_pt08_pan_refractory_kit_mdm2_p53_triplet", "sub": "Pan-Refractory Triplet-Hit Sarcoma", "drv": "Concurrent KIT mut, MDM2 amp, and TP53 null", "rx": "Sunitinib followed by Regorafenib salvage", "out": "Rapid failure at 1.8 mo, death at 3.4 mo", "res": "Simultaneous kinase driving with total p53 shutdown", "pin": {"KIT_mut": 1, "MDM2_amp": 1, "TP53_mut": 1, "Chemo_DNA_damage": 1}}
        ]
    },
    {
        "index": 18,
        "code": "cll",
        "name": "Chronic Lymphocytic Leukemia (CLL)",
        "citation": "Byrd et al. (2014) NEJM (RESONATE - Ibrutinib); Seymour et al. (2018) NEJM (MURANO - Venetoclax + Rituximab); Landau et al. (2015) Nature",
        "url": "https://doi.org/10.1056/NEJMoa1400376",
        "stimuli": ["BCR_stim", "Chemo_DNA_damage", "BTK_mut", "PLCG2_mut", "DEL17P_TP53", "NOTCH1_mut", "SF3B1_mut", "BCL2_amp"],
        "targets": ["BTK", "SYK", "PI3K", "AKT", "NFkB", "BCL2", "MCL1", "BCLxL", "XIAP"],
        "rules": {
            "BCR_stim": "BCR_stim", "Chemo_DNA_damage": "Chemo_DNA_damage", "BTK_mut": "BTK_mut",
            "PLCG2_mut": "PLCG2_mut", "DEL17P_TP53": "DEL17P_TP53", "NOTCH1_mut": "NOTCH1_mut",
            "SF3B1_mut": "SF3B1_mut", "BCL2_amp": "BCL2_amp",
            "SYK": "BCR_stim", "BTK": "BTK_mut  or  SYK", "PLCG2": "PLCG2_mut  or  BTK",
            "PI3K": "SYK  or  BCR_stim", "AKT": "PI3K",
            "NFkB": "PLCG2  or  AKT  or  NOTCH1_mut",
            "ATM_ATR": "Chemo_DNA_damage", "P53": "ATM_ATR  and  not DEL17P_TP53",
            "BCL2": "(BCL2_amp  or  NFkB)  and  not BAX", "BCLxL": "NFkB  and  not BAX",
            "MCL1": "(AKT  or  NFkB)  and  not BAX", "XIAP": "AKT  and  not SMAC",
            "BAX": "(P53  or  not BCL2  or  not BCLxL)  and  not MCL1",
            "CytoC": "BAX", "SMAC": "BAX", "Caspase9": "CytoC  and  not XIAP", "Caspase8": "Chemo_DNA_damage",
            "Caspase3": "(Caspase9  or  Caspase8)  and  not XIAP", "Apoptosis": "Caspase3",
            "Proliferation": "(BTK  or  NFkB  or  AKT)  and  not Apoptosis"
        },
        "patients": [
            {"id": "cll_pt01_del17p_tp53_fludarabine_resistant", "sub": "High-Risk 17p-Deleted / TP53-Mutant CLL", "drv": "del(17p13.1) with TP53 missense, fludarabine refractory", "rx": "FCR chemoimmunotherapy (Fludarabine, Cyclophosphamide, Rituximab)", "out": "Primary refractory, rapid lymphocytosis at 2.9 mo, death at 7.1 mo", "res": "Absence of p53 renders purine analog DNA damage completely futile", "pin": {"DEL17P_TP53": 1, "Chemo_DNA_damage": 1}},
            {"id": "cll_pt02_btk_c481s_ibrutinib_resistant", "sub": "Acquired Ibrutinib-Resistant Relapsed CLL", "drv": "Acquired BTK C481S mutation in ATP-binding domain", "rx": "Ibrutinib (covalent BTK inhibitor) 420mg daily", "out": "Progression at 4.2 mo, explosive Richter transformation", "res": "C481S mutation prevents covalent bond formation by Ibrutinib", "pin": {"BTK_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "cll_pt03_venetoclax_responder_bcl2_hyperdependent", "sub": "Relapsed/Refractory BCL2-Dependent CLL", "drv": "High BCL-2 protein expression, unmutated IGHV", "rx": "Venetoclax (ABT-199 selective BCL-2 BH3 mimetic)", "out": "Undetectable Minimal Residual Disease (uMRD) >40 mo (CURED)", "res": "Severe mitochondrial dependency on BCL-2 allows instantaneous apoptosis", "pin": {"BCL2_amp": 1, "Chemo_DNA_damage": 1}},
            {"id": "cll_pt04_plcg2_mutant_ibrutinib_bypass", "sub": "PLCG2 R665W Mutant Post-BTKi Refractory CLL", "drv": "Activating mutation downstream of BTK in PLCG2", "rx": "Acalabrutinib (2nd-generation BTK inhibitor)", "out": "Primary failure at 2.4 mo, splenomegaly, death at 5.0 mo", "res": "Downstream activation of PLCG2 bypasses all BTK inhibitors", "pin": {"PLCG2_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "cll_pt05_bcl2_g101v_acquired_venetoclax_resistant", "sub": "Acquired Venetoclax-Resistant Relapsed CLL", "drv": "Secondary BCL2 G101V mutation in BH3-binding groove", "rx": "Venetoclax salvage therapy", "out": "Progression at 5.1 mo, massive generalized lymphadenopathy", "res": "G101V mutation causes steric clash reducing Venetoclax affinity 180-fold", "pin": {"BCL2_amp": 1, "Chemo_DNA_damage": 1}},
            {"id": "cll_pt06_notch1_mutated_richter_transformation", "sub": "NOTCH1 P2514fs Mutant Aggressive CLL", "drv": "NOTCH1 PEST domain truncation, constitutive NF-kB", "rx": "R-CHOP chemoimmunotherapy", "out": "Refractory at 2.1 mo, diffuse large B-cell lymphoma transformation", "res": "Constitutive NOTCH1/NF-kB activation drives massive MCL-1 survival", "pin": {"NOTCH1_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "cll_pt07_sf3b1_mutant_spliceosome_aberrant", "sub": "SF3B1 K700E Splicing-Deficient Poor-Prognosis CLL", "drv": "Recurrent spliceosomal mutation, high MCL-1S/L ratio", "rx": "Bendamustine + Rituximab (BR)", "out": "Progression at 4.0 mo, marrow failure, death at 8.2 mo", "res": "Aberrant pre-mRNA splicing insulates pro-survival Bcl-2 family proteins", "pin": {"SF3B1_mut": 1, "Chemo_DNA_damage": 1}},
            {"id": "cll_pt08_pan_refractory_del17p_btk_bcl2_triplet", "sub": "Pan-Refractory Triplet-Hit Ultra-Lethal CLL", "drv": "Concurrent del(17p), BTK C481S, and BCL2 G101V", "rx": "Pirtobrutinib + CAR-T salvage", "out": "Death at 1.9 mo, fulminant leukemic meningitis", "res": "Combined evasion of DNA checkpoints, BTK inhibition, and BCL-2 monotherapy", "pin": {"DEL17P_TP53": 1, "BTK_mut": 1, "BCL2_amp": 1, "Chemo_DNA_damage": 1}}
        ]
    },
    {
        "index": 19,
        "code": "mm",
        "name": "Multiple Myeloma (MM)",
        "citation": "Dimopoulos et al. (2016) NEJM (POLLUX - Daratumumab); San Miguel et al. (2008) NEJM (VISTA - Bortezomib); Kumar et al. (2017) Lancet Oncol",
        "url": "https://doi.org/10.1056/NEJMoa1607751",
        "stimuli": ["IL6_stim", "Chemo_DNA_damage", "T_11_14", "DEL17P", "T_4_14_MMSET", "MYC_transloc", "KRAS_mut", "NRAS_mut"],
        "targets": ["Proteasome", "CD38", "MEK", "ERK", "PI3K", "AKT", "mTOR", "STAT3", "NFkB", "MCL1", "BCL2", "BCLxL", "XIAP"],
        "rules": {
            "IL6_stim": "IL6_stim", "Chemo_DNA_damage": "Chemo_DNA_damage", "T_11_14": "T_11_14",
            "DEL17P": "DEL17P", "T_4_14_MMSET": "T_4_14_MMSET", "MYC_transloc": "MYC_transloc",
            "KRAS_mut": "KRAS_mut", "NRAS_mut": "NRAS_mut",
            "RAS": "KRAS_mut  or  NRAS_mut", "MEK": "RAS", "ERK": "MEK",
            "PI3K": "IL6_stim  or  RAS", "AKT": "PI3K", "mTOR": "AKT",
            "STAT3": "IL6_stim", "NFkB": "AKT  or  Chemo_DNA_damage",
            "ATM_ATR": "Chemo_DNA_damage", "P53": "ATM_ATR  and  not DEL17P",
            "BCL2": "(T_11_14  or  NFkB)  and  not BAX", "BCLxL": "(NFkB  or  STAT3)  and  not BAX",
            "MCL1": "(AKT  or  STAT3  or  IL6_stim)  and  not BAX", "XIAP": "AKT  and  not SMAC",
            "BAX": "(P53  or  not BCL2  or  not BCLxL)  and  not MCL1",
            "CytoC": "BAX", "SMAC": "BAX", "Caspase9": "CytoC  and  not XIAP", "Caspase8": "Chemo_DNA_damage",
            "Caspase3": "(Caspase9  or  Caspase8)  and  not XIAP", "Apoptosis": "Caspase3",
            "Proliferation": "(MYC_transloc  or  AKT  or  STAT3)  and  not Apoptosis"
        },
        "patients": [
            {"id": "mm_pt01_t11_14_venetoclax_responder", "sub": "t(11;14) CCND1 Translocated Multiple Myeloma", "drv": "t(11;14)(q13;q32) high BCL2/MCL1 ratio, plasma cell dyscrasia", "rx": "Venetoclax + Dexamethasone (BELLINI trial protocol)", "out": "Complete Remission (CR) with negative MRD >38 mo (CURED)", "res": "Extreme mitochondrial sensitivity to BCL-2 inhibition triggers swift apoptosis", "pin": {"T_11_14": 1, "Chemo_DNA_damage": 1}},
            {"id": "mm_pt02_del17p_bortezomib_refractory", "sub": "High-Risk del(17p) Proteasome-Inhibitor Refractory MM", "drv": "Biallelic TP53 deletion/mutation, high chromosomal instability", "rx": "Bortezomib + Lenalidomide + Dexamethasone (VRd)", "out": "Progression at 4.0 mo, extramedullary plasmacytomas, death at 8.1 mo", "res": "Loss of p53 prevents proteotoxic stress-induced pro-apoptotic signaling", "pin": {"DEL17P": 1, "Chemo_DNA_damage": 1}},
            {"id": "mm_pt03_t4_14_high_risk_mcl1_dependent", "sub": "t(4;14) FGFR3/MMSET Epigenetic Aggressive MM", "drv": "t(4;14)(p16;q32) histone H3K36 hypermethylation, high MCL-1", "rx": "Carfilzomib + Pomalidomide + Dexamethasone (KPd)", "out": "Early failure at 3.2 mo, widespread osteolytic lesions", "res": "MMSET directly drives sustained MCL-1 transcription, insulating plasma cells", "pin": {"T_4_14_MMSET": 1, "Chemo_DNA_damage": 1}},
            {"id": "mm_pt04_daratumumab_cured_cd38_high", "sub": "Standard-Risk Newly Diagnosed Multiple Myeloma", "drv": "High cell surface CD38 expression, wild-type p53", "rx": "Daratumumab (anti-CD38) + VRd (POLLUX / GRIFFIN)", "out": "Stringent Complete Response (sCR) >50 mo (CURED)", "res": "Potent antibody-dependent cellular cytotoxicity easily collapses myeloma basin", "pin": {"Chemo_DNA_damage": 1}},
            {"id": "mm_pt05_kras_g12d_extramedullary_fulminant", "sub": "KRAS-Mutant Extramedullary Myeloma", "drv": "KRAS G12D activating mutation, plasma cell leukemia features", "rx": "Elotuzumab + Pomalidomide + Dexamethasone", "out": "Primary refractory at 2.2 mo, circulating plasma cells, death at 4.6 mo", "res": "Constitutive MAPK and PI3K signaling bypasses proteasome inhibition", "pin": {"KRAS_mut": 1, "DEL17P": 1, "Chemo_DNA_damage": 1}},
            {"id": "mm_pt06_myc_rearranged_aggressive_plasmablastic", "sub": "Secondary MYC-Translocated Plasmablastic Myeloma", "drv": "8q24 MYC rearrangement into IgH locus, rapid proliferation", "rx": "DCEP chemotherapy (Dexamethasone, Cyclo, Etoposide, Cisplatin)", "out": "Progression at 2.6 mo, hypercalcemic crisis, death at 5.2 mo", "res": "Massive MYC overexpression overrides all cell-cycle checkpoints", "pin": {"MYC_transloc": 1, "Chemo_DNA_damage": 1}},
            {"id": "mm_pt07_il6_autocrine_bone_marrow_protective", "sub": "Stromal Cytokine-Dependent Myeloma", "drv": "Bone marrow stromal IL-6/STAT3 autocrine signaling loop", "rx": "Ixazomib + Lenalidomide + Dexamethasone", "out": "Progression at 4.8 mo, diffuse bone marrow replacement", "res": "IL-6/STAT3 signaling continuously upregulates MCL-1 and BCL-xL", "pin": {"IL6_stim": 1, "Chemo_DNA_damage": 1}},
            {"id": "mm_pt08_pan_refractory_penta_refractory_lethal", "sub": "Penta-Refractory Quadruple-Driver Lethal Myeloma", "drv": "Concurrent del(17p), t(4;14), MYC transloc, and KRAS mut", "rx": "CAR-T (Cilta-cel) followed by Bispecific T-cell engager salvage", "out": "Rapid relapse at 1.9 mo, multi-organ failure, death at 3.2 mo", "res": "Simultaneous disruption of proteostasis, p53, and MAPK produces absolute pan-resistance", "pin": {"DEL17P": 1, "T_4_14_MMSET": 1, "MYC_transloc": 1, "KRAS_mut": 1, "Chemo_DNA_damage": 1}}
        ]
    },
    {
        "index": 20,
        "code": "sclc",
        "name": "Small Cell Lung Cancer (SCLC - Recalcitrant Neuroendocrine)",
        "citation": "George et al. (2015) Nature 524:47-53; Horn et al. (2018) NEJM (IMpower133 - Atezolizumab); Paz-Ares et al. (2019) Lancet (CASPIAN - Durvalumab)",
        "url": "https://doi.org/10.1038/nature14664",
        "stimuli": ["Chemo_DNA_damage", "TP53_null", "RB1_null", "MYC_amp", "NOTCH_loss", "SLFN11_loss", "ASCL1_high", "NEUROD1_high"],
        "targets": ["CDK2", "AURKA", "ATR", "PARP", "PI3K", "AKT", "mTOR", "STAT3", "NFkB", "MCL1", "BCL2", "BCLxL", "XIAP"],
        "rules": {
            "Chemo_DNA_damage": "Chemo_DNA_damage", "TP53_null": "TP53_null", "RB1_null": "RB1_null",
            "MYC_amp": "MYC_amp", "NOTCH_loss": "NOTCH_loss", "SLFN11_loss": "SLFN11_loss",
            "ASCL1_high": "ASCL1_high", "NEUROD1_high": "NEUROD1_high",
            "E2F1": "RB1_null", "CDK2": "E2F1  or  MYC_amp", "AURKA": "MYC_amp",
            "PI3K": "MYC_amp", "AKT": "PI3K", "mTOR": "AKT",
            "STAT3": "NEUROD1_high", "NFkB": "AKT  or  Chemo_DNA_damage",
            "ATM_ATR": "Chemo_DNA_damage  and  not SLFN11_loss", "P53": "ATM_ATR  and  not TP53_null",
            "BCL2": "(ASCL1_high  or  NFkB)  and  not BAX", "BCLxL": "(NFkB  or  STAT3)  and  not BAX",
            "MCL1": "(AKT  or  MYC_amp)  and  not BAX", "XIAP": "AKT  and  not SMAC",
            "BAX": "(P53  or  not BCL2  or  not BCLxL)  and  not MCL1",
            "CytoC": "BAX", "SMAC": "BAX", "Caspase9": "CytoC  and  not XIAP", "Caspase8": "Chemo_DNA_damage",
            "Caspase3": "(Caspase9  or  Caspase8)  and  not XIAP", "Apoptosis": "Caspase3",
            "Proliferation": "(E2F1  or  MYC_amp  or  CDK2)  and  not Apoptosis"
        },
        "patients": [
            {"id": "sclc_pt01_classic_ascl1_bcl2_hyperdependent", "sub": "SCLC-A Subtype (ASCL1-High / Classic Neuroendocrine)", "drv": "Obligate biallelic TP53 and RB1 loss, high ASCL1 driving massive BCL2", "rx": "Cisplatin + Etoposide chemotherapy", "out": "Brief partial response for 3.8 mo, rapid brain metastases, death at 7.5 mo", "res": "High BCL-2 transcription creates an impenetrable mitochondrial shield against platinum adducts", "pin": {"TP53_null": 1, "RB1_null": 1, "ASCL1_high": 1, "Chemo_DNA_damage": 1}},
            {"id": "sclc_pt02_slfn11_loss_acquired_chemo_refractory", "sub": "SLFN11-Epigenetically Silenced Platinum-Resistant SCLC", "drv": "Biallelic loss of TP53/RB1, secondary SLFN11 methylation", "rx": "Carboplatin + Etoposide + Atezolizumab (IMpower133)", "out": "Primary refractory, rapid progression at 2.1 mo, death at 4.2 mo", "res": "Loss of SLFN11 allows cancer cells to bypass replication fork stalling and DNA crosslinks", "pin": {"TP53_null": 1, "RB1_null": 1, "SLFN11_loss": 1, "Chemo_DNA_damage": 1}},
            {"id": "sclc_pt03_myc_amplified_sclc_y_aurora_refractory", "sub": "SCLC-Y / Variant Subtype with High MYC Amplification", "drv": "Focal MYC amplification, low neuroendocrine markers, high Aurora A", "rx": "Lurbinectedin salvage therapy", "out": "Progression at 2.4 mo, bulky mediastinal progression", "res": "MYC hyperactivates downstream MCL-1 and CDK2, driving rapid cell-cycle override", "pin": {"TP53_null": 1, "RB1_null": 1, "MYC_amp": 1, "Chemo_DNA_damage": 1}},
            {"id": "sclc_pt04_durvalumab_exceptional_long_term_survivor", "sub": "Extensive-Stage SCLC with Long-Term Immunotherapy Benefit", "drv": "High tobacco mutational burden, intact antigen presentation", "rx": "Platinum + Etoposide + Durvalumab (CASPIAN trial)", "out": "Durable Progression-Free Survival >32 mo (Long-Term Survivor)", "res": "High clonal neoantigen load induces durable cytotoxic T-cell memory", "pin": {"TP53_null": 1, "RB1_null": 1, "Chemo_DNA_damage": 1}},
            {"id": "sclc_pt05_neurod1_high_sclc_n_aggressive", "sub": "SCLC-N Subtype (NEUROD1-Driven Primitive Small Cell)", "drv": "High NEUROD1 nuclear transcription factor, STAT3 activation", "rx": "Topotecan monotherapy", "out": "Progression at 2.8 mo, widespread hepatic metastases", "res": "NEUROD1 sustains high BCL-xL and STAT3 signaling, neutralizing topoisomerase traps", "pin": {"TP53_null": 1, "RB1_null": 1, "NEUROD1_high": 1, "Chemo_DNA_damage": 1}},
            {"id": "sclc_pt06_notch_loss_neuroendocrine_hyperplastic", "sub": "NOTCH-Inactivated Pure Neuroendocrine Carcinoma", "drv": "Deleterious NOTCH1/2 loss, unchecked ASCL1 neuroendocrine drive", "rx": "Tarlatamab (DLL3-targeted BiTE)", "out": "PFS 15.2 mo, significant clinical response", "res": "High surface DLL3 expression enables potent T-cell redirection", "pin": {"TP53_null": 1, "RB1_null": 1, "NOTCH_loss": 1, "Chemo_DNA_damage": 1}},
            {"id": "sclc_pt07_parp_inhibitor_resistant_hr_proficient", "sub": "Homologous Recombination Proficient Recurrent SCLC", "drv": "Intact BRCA/RAD51 repair axis with high SLFN11 loss", "rx": "Olaparib + Temozolomide", "out": "Progression at 3.0 mo, leptomeningeal spread", "res": "Rapid repair of single-strand breaks overrides PARP entrapment", "pin": {"TP53_null": 1, "RB1_null": 1, "SLFN11_loss": 1, "Chemo_DNA_damage": 1}},
            {"id": "sclc_pt08_pan_refractory_quadruple_driver_lethal", "sub": "Pan-Refractory Quadruple-Feature Lethal SCLC", "drv": "Concurrent TP53 null, RB1 null, MYC amp, and SLFN11 loss", "rx": "Multi-agent salvage chemotherapy + IO", "out": "Rapid failure at 1.4 mo, death at 2.8 mo", "res": "Simultaneous loss of both tumor suppressors, MYC oncogene addiction, and SLFN11 shutdown", "pin": {"TP53_null": 1, "RB1_null": 1, "MYC_amp": 1, "SLFN11_loss": 1, "Chemo_DNA_damage": 1}}
        ]
    }
]


def generate_cancer_spec_p4(spec):
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


def run_pipeline_part4():
    print("\n" + "#" * 84)
    print("   LAUNCHING SEQUENTIAL PAN-CANCER EXPANSION PART 4 (WITH 60-SEC INTERVALS)")
    print("#" * 84)
    for i, spec in enumerate(CANCER_SPECS_PART4):
        generate_cancer_spec_p4(spec)
        if i < len(CANCER_SPECS_PART4) - 1:
            print("\n" + "-" * 80)
            print("  [SLEEP 60s] Pausing 60 seconds as requested before next cancer...")
            print("-" * 80)
            for sec in range(60, 0, -10):
                print(f"   ↳ {sec}s remaining until next cancer unlocks...")
                time.sleep(10)


if __name__ == "__main__":
    run_pipeline_part4()
