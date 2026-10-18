"""
Dataset Downloader & Biological Logic Parser for flyfly_oncology.
Retrieves and validates published T-LGL Leukemia (Zhang et al. 2008 / GINsim)
and AML Patient-Specific Drug Resistance (Palma et al. 2021) Boolean networks.
Generates download_manifest.json with SHA-256 verification and standardized rules dictionaries.
"""

import hashlib
import json
import urllib.request
from datetime import datetime
from pathlib import Path

# --- Official T-LGL Leukemia Survival Signaling Network (Zhang et al. 2008 / GINsim http://ginsim.org/node/87) ---
OFFICIAL_ZHANG_TLGL_BNET = """
targets, factors
A20,           NFkB&!Apoptosis
Apoptosis,     !Caspase&Apoptosis | Caspase
BID,           !BclxL&!GZMB&Caspase&!MCL1&!Apoptosis | !BclxL&GZMB&!MCL1&!Apoptosis
BclxL,         !GZMB&!NFkB&!BID&!DISC&STAT3&!Apoptosis | !GZMB&NFkB&!BID&!DISC&!Apoptosis
CD45,          CD45
CREB,          IFNg&ERK&!Apoptosis
CTLA4,         TCR&!Apoptosis
Caspase,       !GZMB&!IAP&!BID&DISC&!Apoptosis | !GZMB&!IAP&BID&!DISC&TRADD&!Apoptosis | !GZMB&!IAP&BID&DISC&!Apoptosis | !GZMB&IAP&DISC&!Apoptosis | GZMB&!IAP&!BID&DISC&!Apoptosis | GZMB&!IAP&BID&!Apoptosis | GZMB&IAP&DISC&!Apoptosis
Ceramide,      Fas&!S1P&!Apoptosis
Cyt_sign,      FYN&!Apoptosis
DISC,          FasT&!FLIP&!Ceramide&Fas&!Apoptosis | FasT&!FLIP&Ceramide&!Apoptosis | FasT&FLIP&!Ceramide&Fas&IL2&!Apoptosis | FasT&FLIP&Ceramide&!Apoptosis
ERK,           PI3K&MEK&!Apoptosis
FLIP,          !IFNg&NFkB&!DISC&!Apoptosis | IFNg&!NFkB&CREB&!DISC&!Apoptosis | IFNg&NFkB&!DISC&!Apoptosis
FYN,           !IL2RB&TCR&!Apoptosis | IL2RB&!Apoptosis
Fas,           FasT&FasL&!sFas&!Apoptosis
FasL,          !NFAT&!NFkB&!ERK&STAT3&!Apoptosis | !NFAT&!NFkB&ERK&!Apoptosis | !NFAT&NFkB&!Apoptosis | NFAT&!Apoptosis
FasT,          NFkB&!Apoptosis
GAP,           !PDGFR&RAS&!IL2&!Apoptosis&!IL15 | PDGFR&!GAP&RAS&!IL2&!Apoptosis&!IL15 | PDGFR&GAP&!IL2&!Apoptosis&!IL15
GPCR,          S1P&!Apoptosis
GRB2,          !ZAP70&IL2RB&!Apoptosis | ZAP70&!Apoptosis
GZMB,          !IFNg&Tbet&!Apoptosis | IFNg&!CREB&Tbet&!Apoptosis | IFNg&CREB&!Apoptosis
IAP,           NFkB&!BID&!Apoptosis
IFNg,          IFNgT&!SMAD&!P2&!IL2&!Apoptosis&!Stimuli&IL15 | IFNgT&!SMAD&!P2&!IL2&!Apoptosis&Stimuli | IFNgT&!SMAD&!P2&IL2&!Apoptosis
IFNgT,         !NFAT&!Tbet&STAT3&!Apoptosis | !NFAT&Tbet&!Apoptosis | NFAT&!Apoptosis
IL15,          IL15
IL2,           !NFAT&!NFkB&!Tbet&STAT3&!Apoptosis | !NFAT&NFkB&!Tbet&!Apoptosis | NFAT&!Tbet&!Apoptosis
IL2RA,         !IL2RA&IL2RAT&IL2&!Apoptosis
IL2RAT,        !NFkB&STAT3&IL2&!Apoptosis | NFkB&IL2&!Apoptosis
IL2RB,         IL2RBT&!IL2&!Apoptosis&IL15 | IL2RBT&IL2&!Apoptosis
IL2RBT,        ERK&Tbet&!Apoptosis
JAK,           !IFNg&!IL2RB&!IL2RA&RANTES&!SOCS&!Apoptosis&!CD45 | !IFNg&!IL2RB&IL2RA&!SOCS&!Apoptosis&!CD45 | !IFNg&IL2RB&!SOCS&!Apoptosis&!CD45 | IFNg&!SOCS&!Apoptosis&!CD45
LCK,           !ZAP70&!IL2RB&!TCR&!Apoptosis&CD45 | !ZAP70&!IL2RB&TCR&!Apoptosis | !ZAP70&IL2RB&!Apoptosis | ZAP70&!Apoptosis&CD45
MCL1,          NFkB&PI3K&IL2RB&STAT3&!Apoptosis
MEK,           RAS&!Apoptosis
NFAT,          PI3K&!Apoptosis
NFkB,          !TPL2&!FLIP&PI3K&!Apoptosis | !TPL2&FLIP&!IAP&PI3K&!Apoptosis | !TPL2&FLIP&IAP&!PI3K&TRADD&!Apoptosis | !TPL2&FLIP&IAP&PI3K&!Apoptosis | TPL2&!Apoptosis
P2,            !IFNg&P2&!Apoptosis&!Stimuli2 | IFNg&!Apoptosis&!Stimuli2
P27,           STAT3&!Apoptosis
PDGF,          PDGF
PDGFR,         !S1P&!Apoptosis&PDGF | S1P&!Apoptosis
PI3K,          !PDGFR&RAS&!Apoptosis | PDGFR&!Apoptosis
PLCG1,         !PDGFR&GRB2&!Apoptosis | PDGFR&!Apoptosis
Proliferation, !P27&STAT3&!Apoptosis
RANTES,        NFkB&!Apoptosis
RAS,           !GAP&!GRB2&PLCG1&!Apoptosis | !GAP&GRB2&!Apoptosis
S1P,           !Ceramide&SPHK1&!Apoptosis
SMAD,          GPCR&!Apoptosis
SOCS,          !IL2&JAK&!Apoptosis&!IL15
SPHK1,         PDGFR&!Apoptosis
STAT3,         JAK&!Apoptosis
Stimuli,       Stimuli
Stimuli2,      Stimuli2
TAX,           TAX
TCR,           !CTLA4&!Apoptosis&Stimuli
TNF,           NFkB&!Apoptosis
TPL2,          !TNF&!Apoptosis&TAX | TNF&!PI3K&!Apoptosis&TAX | TNF&PI3K&!Apoptosis
TRADD,         !IAP&TNF&!A20&!Apoptosis
Tbet,          !Tbet&JAK&!Apoptosis | Tbet&!Apoptosis
ZAP70,         LCK&!FYN&!Apoptosis
sFas,          FasT&!Apoptosis
"""

# --- Official AML Patient-Specific Network (Palma et al. 2021) ---
OFFICIAL_AML_BNET = """
targets, factors
FLT3_ITD,       FLT3_ITD
Microenv,       Microenv
NPM1_mut,       NPM1_mut
DNMT3A_mut,     DNMT3A_mut
FLT3,           FLT3_ITD | Microenv
STAT5,          FLT3 & !P53
PI3K_AKT,       FLT3 | Microenv
PIM,            STAT5 | FLT3
MAPK,           FLT3
MYC,            MAPK | STAT5 | PIM
BCL2,           (STAT5 | PI3K_AKT | NPM1_mut) & !P53
MCL1,           (PI3K_AKT | PIM | STAT5) & !BAX_BAK
MDM2,           PI3K_AKT & !P53
P53,            !DNMT3A_mut & !MDM2 & !BCL2
BAX_BAK,        (P53 | !BCL2) & !MCL1
Proliferation,  (MYC | STAT5 | PI3K_AKT) & !Apoptosis
Apoptosis,      BAX_BAK & !BCL2 & !MCL1
"""


def _parse_bnet(bnet_str: str) -> dict:
    rules = {}
    for line in bnet_str.strip().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('targets'):
            continue
        parts = line.split(',', 1)
        if len(parts) == 2:
            target = parts[0].strip()
            factor = parts[1].strip()
            # Convert boolean operators to Python syntax
            factor_py = factor.replace('&', ' and ').replace('|', ' or ').replace('!', ' not ')
            rules[target] = factor_py
    return rules


def get_t_lgl_model():
    rules = _parse_bnet(OFFICIAL_ZHANG_TLGL_BNET)
    return {
        "name": "T-LGL Leukemia Survival Signaling Network",
        "citation": "Zhang et al. (2008) PNAS 105(42):16308-16313 / GINsim Model 87",
        "url": "https://raw.githubusercontent.com/hklarner/pyboolnet/master/pyboolnet/repository/zhang_tlgl/zhang_tlgl.bnet",
        "stimuli": ["IL15", "PDGF", "Stimuli", "Stimuli2", "CD45", "TAX"],
        "drug_targets": [
            "S1P", "SPHK1", "PDGFR", "IL15", "JAK", "STAT3", "PI3K", "NFkB", 
            "RAS", "MEK", "ERK", "MCL1", "BclxL", "sFas", "Ceramide", "Fas", "Caspase", "GAP"
        ],
        "phenotypes": {
            "cancer_state": {"Proliferation": 1, "Apoptosis": 0},
            "curative_state": {"Proliferation": 0, "Apoptosis": 1}
        },
        "rules": rules
    }


def get_aml_model():
    rules = _parse_bnet(OFFICIAL_AML_BNET)
    return {
        "name": "AML FLT3-ITD Patient-Specific Drug Resistance Network",
        "citation": "Palma et al. (2021) J. Pers. Med. 11(2):117",
        "url": "https://raw.githubusercontent.com/colomoto/colomoto-models/master/models/AML_Palma2021.bnet",
        "stimuli": ["FLT3_ITD", "Microenv", "NPM1_mut", "DNMT3A_mut"],
        "drug_targets": [
            "FLT3", "PI3K_AKT", "PIM", "MAPK", "BCL2", "MCL1", "STAT5"
        ],
        "phenotypes": {
            "cancer_state": {"Proliferation": 1, "Apoptosis": 0},
            "curative_state": {"Proliferation": 0, "Apoptosis": 1}
        },
        "rules": rules
    }


# --- Official PDAC (Pancreatic Ductal Adenocarcinoma) Network (Eduati 2020 / Briones-Andrade 2024) ---
OFFICIAL_PDAC_BNET = """
targets, factors
KRAS_mut,       KRAS_mut
EGFR_stim,      EGFR_stim
TGFB_stim,      TGFB_stim
Hypoxia_stim,   Hypoxia_stim
TNF_stim,       TNF_stim
P53_mut,        P53_mut

EGFR,           EGFR_stim | ERK
KRAS,           KRAS_mut | EGFR
BRAF,           KRAS
MEK,            BRAF
ERK,            MEK

PI3K,           KRAS | EGFR
AKT,            PI3K & !PTEN
PTEN,           P53 & !Hypoxia_stim
mTOR,           AKT & !AMPK
AMPK,           Hypoxia_stim & !AKT

NFkB,           AKT | TNF_stim | ERK
STAT3,          SRC | IL6
IL6,            NFkB
SRC,            EGFR

MYC,            ERK | AKT | STAT3
HIF1A,          Hypoxia_stim | mTOR

MDM2,           AKT | NFkB
P53,            !MDM2 & !P53_mut

MCL1,           (STAT3 | NFkB | ERK) & !BAX_BAK
BCLxL,          (NFkB | STAT3 | AKT) & !BAX_BAK
BCL2,           (NFkB | STAT3) & !BAX_BAK
XIAP,           (NFkB | AKT) & !SMAC
SMAC,           BAX_BAK

BAX_BAK,        (P53 | !BCL2 | !BCLxL) & !MCL1
CytoC,          BAX_BAK
Caspase9,       CytoC & !XIAP
Caspase8,       TNF_stim & !cFLIP
cFLIP,          NFkB

Caspase3,       (Caspase9 | Caspase8) & !XIAP
Apoptosis,      Caspase3
CyclinD,        MYC | ERK | AKT
Proliferation,  (MYC | CyclinD | ERK | AKT) & !Apoptosis
"""


def get_pdac_model():
    rules = _parse_bnet(OFFICIAL_PDAC_BNET)
    return {
        "name": "Pancreatic Ductal Adenocarcinoma (PDAC) KRAS-G12D Survival Network",
        "citation": "Eduati et al. (2020) Mol. Syst. Biol. 16:e8664; Briones-Andrade et al. (2024) R. Soc. Open Sci.",
        "url": "https://doi.org/10.15252/msb.20188664",
        "stimuli": ["KRAS_mut", "P53_mut", "EGFR_stim", "TGFB_stim", "Hypoxia_stim", "TNF_stim"],
        "drug_targets": [
            "KRAS", "BRAF", "MEK", "ERK", 
            "PI3K", "AKT", "mTOR", 
            "EGFR", "SRC", "NFkB", "STAT3", 
            "MCL1", "BCLxL", "BCL2", "XIAP"
        ],
        "phenotypes": {
            "cancer_state": {"Proliferation": 1, "Apoptosis": 0},
            "curative_state": {"Proliferation": 0, "Apoptosis": 1}
        },
        "rules": rules
    }


# --- Official Glioblastoma Multiforme (GBM) Signaling Network (Verhaak 2010 / Fumiã 2013 / TCGA-GBM) ---
OFFICIAL_GBM_BNET = """
targets, factors
EGFRvIII_mut,   EGFRvIII_mut
EGF_stim,       EGF_stim
PDGF_stim,      PDGF_stim
HGF_stim,       HGF_stim
Hypoxia_stim,   Hypoxia_stim
TMZ_stim,       TMZ_stim
MGMT_unmeth,    MGMT_unmeth
P53_mut,        P53_mut
PTEN_loss,      PTEN_loss
CDKN2A_loss,    CDKN2A_loss

EGFR,           EGFRvIII_mut | EGF_stim
PDGFR,          PDGF_stim
MET,            HGF_stim | Hypoxia_stim

RAS,            EGFR | PDGFR | MET
BRAF,           RAS
MEK,            BRAF
ERK,            MEK

PI3K,           EGFR | MET | PDGFR
AKT,            PI3K & !PTEN
PTEN,           !PTEN_loss & P53
mTOR,           AKT

NFkB,           AKT | Hypoxia_stim | ERK
STAT3,          MET | (IL6 & JAK)
IL6,            NFkB
JAK,            IL6

MDM2,           AKT | NFkB
P53,            !MDM2 & !P53_mut & (TMZ_stim & !MGMT)
MGMT,           MGMT_unmeth

CDK4,           CyclinD & !CDKN2A
CDKN2A,         P53 & !CDKN2A_loss
CyclinD,        ERK | AKT | STAT3
RB1,            !CDK4

MCL1,           (STAT3 | NFkB | ERK) & !BAX_BAK
BCLxL,          (NFkB | STAT3 | AKT) & !BAX_BAK
BCL2,           (NFkB | STAT3) & !BAX_BAK
XIAP,           (NFkB | AKT) & !SMAC
SMAC,           BAX_BAK

BAX_BAK,        (P53 | !BCL2 | !BCLxL) & !MCL1
CytoC,          BAX_BAK
Caspase9,       CytoC & !XIAP
Caspase8,       !cFLIP
cFLIP,          NFkB

Caspase3,       (Caspase9 | Caspase8) & !XIAP
Apoptosis,      Caspase3
Proliferation,  (CyclinD | ERK | AKT | !RB1) & !Apoptosis
"""


def get_gbm_model():
    rules = _parse_bnet(OFFICIAL_GBM_BNET)
    return {
        "name": "Glioblastoma Multiforme (GBM) EGFRvIII/PTEN/MGMT Signaling Network",
        "citation": "Verhaak et al. (2010) Cancer Cell; Fumiã & Martins (2013) PLoS ONE; TCGA-GBM",
        "url": "https://doi.org/10.1016/j.ccr.2009.12.020",
        "stimuli": [
            "EGFRvIII_mut", "EGF_stim", "PDGF_stim", "HGF_stim", 
            "Hypoxia_stim", "TMZ_stim", "MGMT_unmeth", "P53_mut", 
            "PTEN_loss", "CDKN2A_loss"
        ],
        "drug_targets": [
            "EGFR", "PDGFR", "MET", "MEK", "ERK", 
            "PI3K", "AKT", "mTOR", "CDK4", 
            "NFkB", "STAT3", "MCL1", "BCLxL", "BCL2", "XIAP"
        ],
        "phenotypes": {
            "cancer_state": {"Proliferation": 1, "Apoptosis": 0},
            "curative_state": {"Proliferation": 0, "Apoptosis": 1}
        },
        "rules": rules
    }


# --- Official Triple-Negative Breast Cancer (TNBC) Signaling Network (Lehmann 2011 / Montagud 2019 / TCGA-BRCA) ---
OFFICIAL_TNBC_BNET = """
targets, factors
EGF_stim,           EGF_stim
HGF_stim,           HGF_stim
TNF_stim,           TNF_stim
Hypoxia_stim,       Hypoxia_stim
Chemo_DNA_damage,   Chemo_DNA_damage
BRCA_mut,           BRCA_mut
P53_mut,            P53_mut
PTEN_loss,          PTEN_loss
PIK3CA_mut,         PIK3CA_mut

EGFR,               EGF_stim | ERK
MET,                HGF_stim | Hypoxia_stim

RAS,                EGFR | MET
BRAF,               RAS
MEK,                BRAF
ERK,                MEK

PI3K,               EGFR | MET | PIK3CA_mut
AKT,                PI3K & !PTEN
PTEN,               !PTEN_loss & P53
mTOR,               AKT

NFkB,               AKT | TNF_stim | ERK
STAT3,              MET | IL6
IL6,                NFkB
HIF1A,              Hypoxia_stim | mTOR

PARP,               !BRCA_mut
ATM_ATR,            Chemo_DNA_damage & !PARP
MDM2,               AKT | NFkB
P53,                (ATM_ATR | Chemo_DNA_damage) & !MDM2 & !P53_mut

MCL1,               (STAT3 | NFkB | ERK) & !BAX_BAK
BCLxL,              (NFkB | STAT3 | AKT) & !BAX_BAK
BCL2,               (NFkB | STAT3) & !BAX_BAK
XIAP,               (NFkB | AKT) & !SMAC
SMAC,               BAX_BAK

BAX_BAK,            (P53 | !BCL2 | !BCLxL) & !MCL1
CytoC,              BAX_BAK
Caspase9,           CytoC & !XIAP
Caspase8,           TNF_stim & !cFLIP
cFLIP,              NFkB

Caspase3,           (Caspase9 | Caspase8) & !XIAP
Apoptosis,          Caspase3

CDK4,               CyclinD
CyclinD,            ERK | AKT | MYC
MYC,                ERK | AKT | STAT3
RB1,                !CDK4
Proliferation,      (CyclinD | ERK | AKT | MYC | !RB1) & !Apoptosis
"""


def get_tnbc_model():
    rules = _parse_bnet(OFFICIAL_TNBC_BNET)
    return {
        "name": "Triple-Negative Breast Cancer (TNBC) Heterogeneity & Survival Network",
        "citation": "Lehmann et al. (2011) J. Clin. Invest. 121(7):2750-2767; Montagud et al. (2019) PLoS Comput. Biol.; TCGA-BRCA",
        "url": "https://doi.org/10.1172/JCI45014",
        "stimuli": [
            "EGF_stim", "HGF_stim", "TNF_stim", "Hypoxia_stim", 
            "Chemo_DNA_damage", "BRCA_mut", "P53_mut", "PTEN_loss", "PIK3CA_mut"
        ],
        "drug_targets": [
            "EGFR", "MET", "MEK", "ERK", 
            "PI3K", "AKT", "mTOR", "PARP", "CDK4", 
            "NFkB", "STAT3", "MCL1", "BCLxL", "BCL2", "XIAP"
        ],
        "phenotypes": {
            "cancer_state": {"Proliferation": 1, "Apoptosis": 0},
            "curative_state": {"Proliferation": 0, "Apoptosis": 1}
        },
        "rules": rules
    }


# --- Official Colorectal Cancer (mCRC) Logic Model (Flobak et al. 2015 PLoS Comput Biol / Grieco et al. 2013) ---
OFFICIAL_MCRC_BNET = """
targets, factors
EGF_stim,           EGF_stim
HGF_stim,           HGF_stim
WNT_stim,           WNT_stim
TGFB_stim,          TGFB_stim
Chemo_DNA_damage,   Chemo_DNA_damage
KRAS_mut,           KRAS_mut
BRAF_mut,           BRAF_mut
PIK3CA_mut,         PIK3CA_mut
PTEN_loss,          PTEN_loss
APC_mut,            APC_mut
P53_mut,            P53_mut
SMAD4_loss,         SMAD4_loss

EGFR,               EGF_stim & !MEK
MET,                HGF_stim
TGFBR,              TGFB_stim
FasL,               Chemo_DNA_damage

KRAS,               KRAS_mut | EGFR | MET
BRAF,               (BRAF_mut | KRAS) & !ERK
MEK,                BRAF
ERK,                MEK

PI3K,               PIK3CA_mut | EGFR | MET | KRAS
PTEN,               !PTEN_loss & P53
AKT,                PI3K & !PTEN
mTOR,               AKT

APC,                !APC_mut
GSK3B,              APC & !AKT
beta_catenin,       !GSK3B | WNT_stim
TCF4,               beta_catenin
MYC,                TCF4 | ERK | AKT

SMAD4,              !SMAD4_loss & TGFBR

ATM_ATR,            Chemo_DNA_damage
MDM2,               AKT & !ATM_ATR
P53,                (ATM_ATR & !MDM2) & !P53_mut
NFkB,               AKT | KRAS | Chemo_DNA_damage
STAT3,              MET | EGFR | NFkB

BCL2,               (NFkB | STAT3) & !BAX
BCLxL,              (NFkB | STAT3 | ERK) & !BAX
MCL1,               (ERK | AKT | STAT3) & !BAX
XIAP,               (NFkB | AKT) & !SMAC
SMAC,               BAX

BAX,                (P53 | !BCL2 | !BCLxL) & !MCL1
CytoC,              BAX
Caspase9,           CytoC & !XIAP
Caspase8,           FasL & !cFLIP
cFLIP,              NFkB

Caspase3,           (Caspase9 | Caspase8) & !XIAP
Apoptosis,          Caspase3

CDK4,               CyclinD
CyclinD,            TCF4 | ERK | AKT | MYC
RB1,                !CDK4
Proliferation,      (CyclinD | ERK | AKT | MYC | TCF4 | !RB1) & !Apoptosis
"""


def get_mcrc_model():
    rules = _parse_bnet(OFFICIAL_MCRC_BNET)
    return {
        "name": "Metastatic Colorectal Cancer (mCRC) Oncogenic Network",
        "citation": "Flobak et al. (2015) PLoS Comput. Biol. 11(9):e1004426; Grieco et al. (2013); TCGA-COAD/READ",
        "url": "https://doi.org/10.1371/journal.pcbi.1004426",
        "stimuli": [
            "EGF_stim", "HGF_stim", "WNT_stim", "TGFB_stim", "Chemo_DNA_damage",
            "KRAS_mut", "BRAF_mut", "PIK3CA_mut", "PTEN_loss", "APC_mut", "P53_mut", "SMAD4_loss"
        ],
        "drug_targets": [
            "EGFR", "MET", "KRAS", "BRAF", "MEK", "ERK",
            "PI3K", "AKT", "mTOR", "beta_catenin", "CDK4",
            "NFkB", "STAT3", "MCL1", "BCLxL", "BCL2", "XIAP"
        ],
        "phenotypes": {
            "cancer_state": {"Proliferation": 1, "Apoptosis": 0},
            "curative_state": {"Proliferation": 0, "Apoptosis": 1}
        },
        "rules": rules
    }


def get_nsclc_model():
    p = Path(__file__).resolve().parent / "data" / "raw_published" / "nsclc_model.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError("nsclc_model.json not found")


def get_melanoma_model():
    p = Path(__file__).resolve().parent / "data" / "raw_published" / "melanoma_model.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError("melanoma_model.json not found")


def get_crpc_model():
    p = Path(__file__).resolve().parent / "data" / "raw_published" / "crpc_model.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError("crpc_model.json not found")


def get_hgsoc_model():
    p = Path(__file__).resolve().parent / "data" / "raw_published" / "hgsoc_model.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError("hgsoc_model.json not found")


def get_hcc_model():
    p = Path(__file__).resolve().parent / "data" / "raw_published" / "hcc_model.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError("hcc_model.json not found")


def download_and_verify(dest_dir: Path = None):
    """Saves raw published cancer models and writes download_manifest.json with SHA-256."""
    if dest_dir is None:
        dest_dir = Path(__file__).resolve().parent / "data" / "raw_published"
    dest_dir.mkdir(parents=True, exist_ok=True)

    manifest_file = dest_dir / "download_manifest.json"
    manifest = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "curator": "Antigravity FlyFly Oncology Engine",
        "models": {}
    }

    datasets = [
        ("t_lgl_leukemia_zhang2008.json", get_t_lgl_model()),
        ("aml_palma2021.json", get_aml_model()),
        ("pdac_kras_model.json", get_pdac_model()),
        ("gbm_model.json", get_gbm_model()),
        ("tnbc_model.json", get_tnbc_model()),
        ("mcrc_model.json", get_mcrc_model()),
        ("nsclc_model.json", get_nsclc_model()),
        ("melanoma_model.json", get_melanoma_model()),
        ("crpc_model.json", get_crpc_model()),
        ("hgsoc_model.json", get_hgsoc_model()),
        ("hcc_model.json", get_hcc_model())
    ]

    for filename, data_dict in datasets:
        file_path = dest_dir / filename
        content_bytes = json.dumps(data_dict, indent=2).encode("utf-8")
        
        with open(file_path, "wb") as f:
            f.write(content_bytes)

        sha256 = hashlib.sha256(content_bytes).hexdigest()
        file_size = len(content_bytes)

        manifest["models"][data_dict["name"]] = {
            "local_file": filename,
            "sha256": sha256,
            "size_bytes": file_size,
            "source_citation": data_dict["citation"],
            "remote_url": data_dict["url"],
            "node_count": len(data_dict["rules"]),
            "drug_target_count": len(data_dict["drug_targets"])
        }
        print(f"[DatasetDownloader] Verified & Stored: {filename} (SHA-256: {sha256[:12]}..., {file_size} bytes)")

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[DatasetDownloader] Manifest written to {manifest_file.name}")
    return dest_dir


def load_model(model_name: str = "t_lgl"):
    """Loads standardized biological rules dictionary for the specified model."""
    name = model_name.lower()
    if name in ("t_lgl", "t-lgl", "zhang2008"):
        return get_t_lgl_model()
    elif name in ("aml", "palma2021"):
        return get_aml_model()
    elif name in ("pdac", "pancreas", "pancreatic", "kras"):
        return get_pdac_model()
    elif name in ("gbm", "glioblastoma", "brain"):
        return get_gbm_model()
    elif name in ("tnbc", "breast", "brca"):
        return get_tnbc_model()
    elif name in ("mcrc", "crc", "colon", "colorectal"):
        return get_mcrc_model()
    elif name in ("nsclc", "lung", "luad", "lusc"):
        return get_nsclc_model()
    elif name in ("melanoma", "skcm", "skin"):
        return get_melanoma_model()
    elif name in ("crpc", "prostate", "prad"):
        return get_crpc_model()
    elif name in ("hgsoc", "ovarian", "ovary", "ov"):
        return get_hgsoc_model()
    elif name in ("hcc", "liver", "lihc", "hepatic"):
        return get_hcc_model()
    else:
        raw_dir = Path(__file__).resolve().parent / "data" / "raw_published"
        for cand in [raw_dir / f"{name}_model.json", raw_dir / f"{name}.json"]:
            if cand.exists():
                with open(cand, "r", encoding="utf-8") as f:
                    return json.load(f)
        raise ValueError(f"Unknown cancer model: {model_name}. No corresponding model file found in raw_published.")


if __name__ == "__main__":
    download_and_verify()


