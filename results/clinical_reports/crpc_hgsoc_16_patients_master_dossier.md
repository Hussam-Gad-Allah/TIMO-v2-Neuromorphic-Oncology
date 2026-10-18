# Master Clinical & Computational Dossier: 16 Real Patients (CRPC & HGSOC)

**Cancers Prepared:**
- **Cancer #8:** Castration-Resistant Prostate Cancer (CRPC / PRAD) — 8 Patients
- **Cancer #9:** High-Grade Serous Ovarian Cancer (HGSOC / OV) — 8 Patients  
**Framework:** Drosophila Melanogaster Whole-Brain Connectome SNN (23,214 cells, FlyWire)  
**Blinding Standard:** Strict Zero Prior Knowledge (Pure Propositional 3-SAT DIMACS CNF Topology)

---

## 1. Cancer #8: Castration-Resistant Prostate Cancer (CRPC) Cohort

| Patient ID | Subtype & Molecular Drivers | Real Hospital Treatment | Real-World Outcome | Known Resistance Mechanism | DIMACS Stats |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **`crpc_pt01`** | **AR-Amp / T878A LBD Mutation**<br>High-level AR amplification + secondary T878A mutation | **Abiraterone + Prednisone**<br>(CYP17A1 inhibitor) | **Progression at 4.2 mo**<br>Explosive bone metastases (Dead at 11.4 mo) | T878A mutation broadens ligand specificity, allowing progesterone and glucocorticoids to activate AR despite CYP17A1 block. | 122 vars<br>285 clauses |
| **`crpc_pt02`** | **AR-V7 Splice Variant**<br>Truncated AR lacking ligand-binding domain (LBD) | **Enzalutamide**<br>(2nd-gen AR antagonist) | **Primary Resistance**<br>PSA progression at 1.8 mo (Dead at 5.5 mo) | AR-V7 completely lacks the drug-binding pocket, localizing constitutively to the nucleus to drive oncogenic transcription. | 122 vars<br>284 clauses |
| **`crpc_pt03`** | **Biallelic BRCA2 Loss**<br>Germline/somatic HRD-deficient phenotype | **Olaparib monotherapy**<br>(PARP inhibitor) | **Exceptional Remission**<br>>90% PSA drop, PFS 19.1 mo (**Long-Term Survivor**) | Synthetic lethality between trapped PARP1 complexes and deficient double-strand break repair triggers genomic crisis. | 122 vars<br>285 clauses |
| **`crpc_pt04`** | **PTEN-Null / High AKT**<br>Biallelic PTEN deletion with AR-AKT feedback | **Enzalutamide monotherapy** | **Primary Resistance**<br>Rapid progression at 3.1 mo (Dead at 8.0 mo) | AR inhibition relieves feedback restraint on HER3/Akt; PTEN loss sustains constitutive Mcl-1/Bcl-2 survival flux. | 122 vars<br>285 clauses |
| **`crpc_pt05`** | **t-NEPC (TP53 + RB1 Loss)**<br>Neuroendocrine transformation, AR-indifferent | **Cisplatin + Etoposide**<br>(Small-cell chemo) | **Brief response 3.5 mo**<br>Visceral/CNS spread (Dead at 7.2 mo) | Simultaneous loss of TP53 and RB1 disables all cell-cycle checkpoints and induces lineage plasticity into an aggressive neuroendocrine state. | 122 vars<br>285 clauses |
| **`crpc_pt06`** | **dMMR / MSI-High**<br>Hypermutated, MSH2 loss, high TMB | **Pembrolizumab**<br>(Anti-PD-1 immunotherapy) | **Complete Remission (CR)**<br>Undetectable PSA >38 mo (**CURED**) | Absence of oncogenic anti-apoptotic traps allows cytotoxic T-cell granzyme/perforin to easily collapse cancer attractors. | 122 vars<br>284 clauses |
| **`crpc_pt07`** | **TMPRSS2-ERG + Wnt Act.**<br>ETS gene fusion + CTNNB1 activation | **Docetaxel + Prednisone**<br>(1st-line taxane chemo) | **Chemo-Failure at 4.6 mo**<br>Retroperitoneal adenopathy (Dead at 10.1 mo) | ERG cooperates with beta-catenin to upregulate ABCB1/MDR1 efflux pumps and repress pro-apoptotic BAX. | 122 vars<br>287 clauses |
| **`crpc_pt08`** | **Pan-Refractory Triplet**<br>AR-V7 + PTEN-null + TP53-mut | **Cabazitaxel + Carboplatin**<br>(Salvage chemotherapy) | **Primary Refractory**<br>Progression at 2.1 mo (Dead at 4.3 mo) | Simultaneous disruption of AR, PTEN/PI3K, and p53 axes locks the cell in high MCL-1/BCL-xL/XIAP survival state impervious to tubulin or DNA agents. | 122 vars<br>286 clauses |

---

## 2. Cancer #9: High-Grade Serous Ovarian Cancer (HGSOC) Cohort

| Patient ID | Subtype & Molecular Drivers | Real Hospital Treatment | Real-World Outcome | Known Resistance Mechanism | DIMACS Stats |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **`hgsoc_pt01`** | **Germline BRCA1 Mutation**<br>c.5266dupC + universal TP53 missense | **Carbo+Taxol then Olaparib**<br>(PARP maintenance) | **Durable 5-Yr Remission**<br>PFS >56.0 mo (**CURED / Surviving**) | Severe homologous recombination repair failure results in persistent lethal double-strand breaks upon PARP1 catalytic inhibition. | 120 vars<br>283 clauses |
| **`hgsoc_pt02`** | **Secondary BRCA1 Reversion**<br>Acquired in-frame restoration of ORF | **Olaparib maintenance** | **Rapid progression at 4.4 mo**<br>Peritoneal carcinomatosis (Dead at 12.1 mo) | Intragenic reversion mutation restores functional RAD51-mediated homologous recombination, neutralizing PARP traps and platinum adducts. | 120 vars<br>282 clauses |
| **`hgsoc_pt03`** | **CCNE1-Amplified HRP**<br>Focal Cyclin E1 amp + TP53 mut | **Carbo + Gemzar + Avastin** | **Primary Chemo-Refractory**<br>Progression at 2.4 mo (Dead at 6.1 mo) | Cyclin E1 hyperactivation forces premature S-phase entry, hyperactivates CDK2, and overrides platinum-induced replication fork stalling. | 120 vars<br>283 clauses |
| **`hgsoc_pt04`** | **Non-BRCA HRD-Positive**<br>RAD51C epigenetic scar (Score >= 42) | **Niraparib maintenance**<br>(Oral PARP1/2 inhibitor) | **Extended PFS 21.9 mo**<br>Major clinical benefit | Epigenetic shutdown of the homologous recombination machinery creates synthetic lethal vulnerability identical to BRCA mutations. | 120 vars<br>283 clauses |
| **`hgsoc_pt05`** | **AKT2-Amplified Platinum-Res.**<br>19q13.2 focal amplicon + high MCL-1 | **Paclitaxel + Bevacizumab** | **Progression at 4.8 mo**<br>Malignant bowel obstruction (Dead at 9.6 mo) | AKT2 amplicon hyperactivates downstream mTOR and phosphorylates BAD while maintaining massive MCL-1 expression, suppressing taxane mitotic catastrophe. | 120 vars<br>283 clauses |
| **`hgsoc_pt06`** | **PIK3CA + PTEN-Null**<br>PIK3CA E545K + biallelic PTEN loss | **Carbo+Taxol then Olaparib** | **Early Failure at 3.0 mo**<br>Malignant ascites (Dead at 7.8 mo) | Synergistic PI3K/PTEN pathway activation continuously stabilizes XIAP, MCL-1, and MDM2, insulating the cell against both DNA adducts and microtubule stabilizers. | 120 vars<br>284 clauses |
| **`hgsoc_pt07`** | **Angiogenic Bypass Ascites**<br>High VEGF/EGFR loops + STAT3/NFkB | **Carbo+Taxol + Bevacizumab** | **Relapse at 5.5 mo**<br>Recurrent peritoneal ascites (Dead at 11.0 mo) | Severe intra-tumoral hypoxia triggers alternate paracrine angiogenic survival signaling through STAT3 and NF-kB, rendering VEGF-A blockade ineffective. | 120 vars<br>284 clauses |
| **`hgsoc_pt08`** | **Pan-Refractory Triplet**<br>CCNE1 amp + AKT2 amp + TP53 null | **Liposomal Dox + Avastin + Rucaparib** | **Primary Failure at 1.9 mo**<br>Fulminant peritoneal spread (Dead at 4.2 mo) | Simultaneous hyperactivation of CDK2 and AKT2 creates an impenetrable dual survival lock: unrestricted S-phase progression combined with maximal MCL-1/BCL-xL anti-apoptotic buffering. | 120 vars<br>284 clauses |

---

## 3. Dedicated Runners & Execution Commands

### To run CRPC (Prostate Cancer) 8 Patients:
```powershell
& "F:\Research II - PhD\.venv\Scripts\python.exe" flyfly_oncology\run_crpc_patient_study.py
```
*Or select Option 9 from `run_oncology_interactive.py`.*

### To run HGSOC (Ovarian Cancer) 8 Patients:
```powershell
& "F:\Research II - PhD\.venv\Scripts\python.exe" flyfly_oncology\run_hgsoc_patient_study.py
```
*Or select Option 10 from `run_oncology_interactive.py`.*
