# TIMO v2: Topological Insect-connectome Model for Oncology

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0%2B-ee4c2c.svg)](https://pytorch.org/)
[![Connectome: FlyWire FAFB v783](https://img.shields.io/badge/Connectome-FlyWire%20FAFB%20v783-orange.svg)](https://codex.flywire.ai/)
[![Target: Nature Machine Intelligence](https://img.shields.io/badge/Target-Nature%20Machine%20Intelligence-darkgreen.svg)]()

> **Drosophila Connectome Spiking Dynamics Decode Synergistic Drug Attractors in Refractory Human Cancers**
>
> **Author:** Hussam Gad-Allah ([ORCID: 0009-0002-6823-2951](https://orcid.org/0009-0002-6823-2951))
> *Department of Data Science, Faculty of Graduate Studies for Statistical Research (FGSSR), Cairo University, Giza, Egypt*
> *Department of Business Information Systems, Faculty of Commerce and Business Administration, Capital University (CAPU), Giza, Egypt*
>
> **Companion Study (TIMO v1):** *"Zero-Shot Combinatorial Optimization Across Hard Landscapes Directed by a Drosophila Connectome Sub-Circuit"* ([GitHub: TIMO-Neuromorphic-SAT](https://github.com/Hussam-Gad-Allah/TIMO-Neuromorphic-SAT))

---

## Overview

**TIMO v2** (**T**opological **I**nsect-connectome **M**odel for **O**ncology) is a closed-loop neuromorphic precision oncology engine that embeds the **23,214-neuron core sub-circuit of the adult *Drosophila melanogaster* whole-brain connectome** (FlyWire FAFB v783; 2,552,344 directed synapses) inside a cybernetic feedback loop coupled to an in-loop **General Asynchronous Updating Scheme (GAUS)** temporal cellular simulator (200 independent tumor cells simulated across 1,500 asynchronous time steps per candidate).

Unlike open-loop static SAT solvers that terminate upon finding any steady-state assignment, **TIMO v2** tests every candidate drug combination in real time against asynchronous receptor bypass and multi-tier transcriptional noise (**2.0% physiological**, **5.0% inflammatory**, **10.0% hyper-mutational**, and **18.0% critical thermal chaos**). Whenever a proposed regimen fails to achieve both **$\ge 85\%$ clean mechanistic apoptosis** and **$\ge 90\%$ noisy apoptosis**, TIMO v2 automatically synthesizes a dynamic propositional **No-Good blocking clause**:

$$C_{\text{block}}^{(k)} = \bigvee_{d \in \mathcal{D}_{\text{failed}}^{(k)}} \neg \text{DRUG\_INHIB}_d$$

and injects localized GABAergic inhibition onto the corresponding descending premotor channels, physically deflecting the connectome's 3D trajectory toward an orthogonal synthetic lethal basin.

---

## Key Empirical Highlights

1. **Retrospective Clinical Validation (62 Patient Profiles + Pan-Cancer Atlas):**
   * Validated across **62 published patient-specific genomic networks** spanning **T-LGL leukemia** (Saadatpour et al., *PLoS Comput. Biol.* 2011), **AML** (Palma et al., *Front. Physiol.* 2018), **PDAC**, **GBM**, **TNBC**, and **mCRC**, plus 160 stratified pan-cancer profiles across 20 tumor lineages, achieving **100% concordance** with experimentally verified wet-lab targets and FDA-approved combination regimens (such as *Gilteritinib + Venetoclax* in *FLT3-ITD* AML and *Encorafenib + Cetuximab* in *BRAF V600E* mCRC).
2. **Prospective Discovery Across 12 Refractory & Orphan Cancers (48 Multi-Noise Runs):**
   * Deployed prospectively across **12 lethal pediatric and adult malignancies** lacking curative systemic pharmacotherapies (*DIPG H3K27M, MRT SMARCB1-null, Ewing Sarcoma EWSR1-FLI1, Alveolar Rhabdomyosarcoma PAX3-FOXO1, Fibrolamellar HCC DNAJB1-PRKACA, Adenoid Cystic Carcinoma MYB-NFIB, Midline NUT Carcinoma BRD4-NUTM1, MPNST NF1/PRC2-null, Metastatic Uveal Melanoma GNAQ/BAP1, Sarcomatoid Mesothelioma BAP1/NF2/CDKN2A-null, DSRCT EWSR1-WT1, and Clival Chordoma TBXT*), isolating actionable 2- and 3-drug combinations achieving **94.0%–100.0% apoptotic eradication** across all four noise tiers.
3. **Interactive 3D Cyber-Space Flight & Bio-Electric Telemetry Visualizer (`view_fly_3d.py`):**
   * Includes a self-contained Three.js 3D state-space visualizer displaying real-time `PEAK UNSAT`, `LOWEST UNSAT RECORD`, dynamic blocking clause deflections, bio-electric LIF currents ($\text{nA}$), membrane voltage ($\text{mV}$), firing frequency ($\text{Hz}$), and live GAUS cellular noise telemetry.

---

## Turnkey Quickstart

### 1. Clone & Activate Environment
```bash
git clone https://github.com/Hussam-Gad-Allah/TIMO-v2-Neuromorphic-Oncology.git
cd TIMO-v2-Neuromorphic-Oncology

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Unified Interactive Turnkey Launcher (`launcher.py` / `run_timo_v2.bat`)
Double-click `run_timo_v2.bat` (Windows) or run:
```bash
python launcher.py
```
This opens the interactive menu to:
* Launch the **3D Connectome Flight & Oncology Telemetry Visualizer** (`view_fly_3d.py`)
* Run the **12 Unsolved Cancers Prospective Multi-Noise Study** (`run_unsolved_prospective_study.py`)
* Run any individual clinical cohort or custom patient `.cnf` network

### 3. Direct CLI Commands
```bash
# Launch the 3D State-Space Visualizer in your browser (100% offline-ready):
python view_fly_3d.py

# Run the 12 Unsolved Cancers Prospective Study (2%, 5%, 10%, 18% noise):
python run_unsolved_prospective_study.py

# Regenerate the Clinical & Pharmacological Comparison Report:
python build_unsolved_sweep_clinical_report.py
```

---

## Prospective Discovery Summary Across 12 Unsolved Cancers

| ID | Refractory Malignancy | Oncogenic Driver | Discovered Drug Synergy (TIMO v2) | Clinical Agents (FDA / Phase I–III) | Noisy Apoptosis (2% / 5% / 10% / 18%) |
| :-: | :--- | :--- | :--- | :--- | :---: |
| **pt01** | **DIPG / DMG** | *H3K27M + ACVR1 + TP53* | `AKT + BCLxL + CDK4_6` | Capivasertib + Navitoclax + Abemaciclib | **99.0% / 100% / 100% / 100%** |
| **pt02** | **Malignant Rhabdoid (MRT)** | *SMARCB1 null + EZH2* | `AKT + BCLxL + EZH2` | Capivasertib + Navitoclax + Tazemetostat | **99.5% / 100% / 100% / 100%** |
| **pt03** | **Metastatic Ewing Sarcoma** | *EWSR1-FLI1 + TP53 + STAG2* | `BCLxL + CDK4_6 + IGF1R` | Navitoclax + Palbociclib + Linsitinib | **100% / 99.5% / 100% / 100%** |
| **pt04** | **Alveolar Rhabdomyosarcoma** | *PAX3-FOXO1 + MYCN* | `AKT + BCLxL + CDK4_6` | Capivasertib + Navitoclax + Ribociclib | **100% / 99.0% / 100% / 100%** |
| **pt05** | **Fibrolamellar HCC (FL-HCC)** | *DNAJB1-PRKACA Chimera* | `MCL1 + PI3K + PRKACA` | Tapotoclax + Alpelisib + BLU-2864 | **100% / 100% / 100% / 100%** |
| **pt06** | **Adenoid Cystic (ACC)** | *MYB-NFIB + NOTCH1* | `AKT + BCL2 + NOTCH1` | Capivasertib + Venetoclax + Nirogacestat | **99.0% / 100% / 99.5% / 100%** |
| **pt07** | **Midline NUT Carcinoma** | *BRD4-NUTM1 + MYC* | `ERK + HDAC + PI3K` | Ulixertinib + Vorinostat + Copanlisib | **94.0% / 100% / 100% / 100%** |
| **pt08** | **MPNST** | *NF1 null + SUZ12/EED null* | `EZH2 + MEK + mTOR` | Tazemetostat + Trametinib + Sapanisertib | **99.0% / 100% / 100% / 100%** |
| **pt09** | **Metastatic Uveal Melanoma** | *GNAQ Q209L + BAP1 null* | `BCLxL + FAK + MEK` | Navitoclax + Defactinib + Trametinib | **97.5% / 99.0% / 98.5% / 100%** |
| **pt10** | **Sarcomatoid Mesothelioma** | *BAP1 + NF2 + CDKN2A null* | `BCLxL + EZH2 + FAK` | Navitoclax + Tazemetostat + Defactinib | **99.0% / 99.0% / 99.5% / 100%** |
| **pt11** | **DSRCT** | *EWSR1-WT1 Chimera* | `AKT + EZH2` *(2-Drug)* | Capivasertib + Tazemetostat | **99.0% / 96.5% / 100% / 100%** |
| **pt12** | **Clival & Sacral Chordoma** | *TBXT Amp + CDKN2A null* | `BCLxL + CDK4_6 + EGFR` | Navitoclax + Palbociclib + Afatinib | **97.5% / 99.5% / 100% / 100%** |

---

## Citation

```bibtex
@article{gadallah2026timo_v2_oncology,
  title   = {Drosophila Connectome Spiking Dynamics Decode Synergistic Drug Attractors in Refractory Human Cancers},
  author  = {Gad-Allah, Hussam},
  journal = {Nature Machine Intelligence},
  year    = {2026}
}
```

## License
Released under the [MIT License](LICENSE).
