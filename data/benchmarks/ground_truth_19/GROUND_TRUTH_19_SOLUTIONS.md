# 19 Literature Ground-Truth Oncology Benchmarks
## Validated Wet-Lab Interventions from Saadatpour et al. (2011) and Palma et al. (2021)

These 19 benchmark instances represent experimentally verified single and combinatorial therapeutic targets.
Our goal is for the Drosophila FlyWire connectome SNN to independently discover and verify each published ground-truth solution.

| # | Benchmark Filename | Target Gene(s) | Published Ground Truth Solution | Biological Rationale / Mechanism | Scientific Citation |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **01** | `gt01_tlgl_S1P_knockout.cnf` | `['S1P']` | **`S1P`** | Inhibition of S1P cuts off leukemic survival signaling and restores Ceramide synthesis, activating Caspase-8/3. | Saadatpour et al. (2011), Table 1; Zhang et al. (2008) |
| **02** | `gt02_tlgl_SPHK1_inhibition.cnf` | `['SPHK1']` | **`SPHK1`** | SPHK1 inhibition eliminates S1P production, restoring endogenous pro-apoptotic Ceramide accumulation. | Saadatpour et al. (2011), Table 1 |
| **03** | `gt03_tlgl_PDGFR_inhibition.cnf` | `['PDGFR']` | **`PDGFR`** | Blocks the PDGF autocrine survival loop, inactivating SPHK1 and PI3K downstream cascades. | Saadatpour et al. (2011), Table 1; Zhang et al. (2008) |
| **04** | `gt04_tlgl_PDGF_neutralization.cnf` | `['PDGF']` | **`PDGF`** | Antibody neutralization of autocrine PDGF cytokine abolishes microenvironmental proliferative stimulus. | Saadatpour et al. (2011), Table 1 |
| **05** | `gt05_tlgl_IL15_neutralization.cnf` | `['IL15']` | **`IL15`** | Blocks primary autocrine cytokine loop responsible for constitutive JAK-STAT3 activation. | Saadatpour et al. (2011), Table 1; Chen et al. (2012) |
| **06** | `gt06_tlgl_JAK_inhibition.cnf` | `['JAK']` | **`JAK`** | JAK inhibition (e.g., Tofacitinib / Ruxolitinib) deprives STAT3 of activating phosphorylation. | Saadatpour et al. (2011), Table 1 |
| **07** | `gt07_tlgl_STAT3_knockdown.cnf` | `['STAT3']` | **`STAT3`** | Abolishes transcriptional activation of key downstream anti-apoptotic Bcl-2 family members Mcl-1 and Bcl-xL. | Saadatpour et al. (2011), Table 1; Epling-Burnette et al. (2001) |
| **08** | `gt08_tlgl_PI3K_inhibition.cnf` | `['PI3K']` | **`PI3K`** | Inactivates AKT and NF-kB, downregulating anti-apoptotic proteins FLIP and IAP. | Saadatpour et al. (2011), Table 1 |
| **09** | `gt09_tlgl_NFkB_inhibition.cnf` | `['NFkB']` | **`NFkB`** | NF-kB inhibition (Bortezomib / Bay-11) relieves repression on apoptotic DISC assembly. | Saadatpour et al. (2011), Table 1 |
| **10** | `gt10_tlgl_RAS_inhibition.cnf` | `['RAS']` | **`RAS`** | Shuts off upstream driver of the proliferative MAPK/MEK/ERK phosphorylation cascade. | Saadatpour et al. (2011), Table 1 |
| **11** | `gt11_tlgl_MEK_inhibition.cnf` | `['MEK']` | **`MEK`** | Inhibition with Trametinib prevents phosphorylation of downstream ERK, blocking Proliferation. | Saadatpour et al. (2011), Table 1 |
| **12** | `gt12_tlgl_ERK_inhibition.cnf` | `['ERK']` | **`ERK`** | Blocks ERK-mediated survival phosphorylation and releases pro-apoptotic transcriptional repressions. | Saadatpour et al. (2011), Table 1 |
| **13** | `gt13_tlgl_MCL1_inhibition.cnf` | `['MCL1']` | **`MCL1`** | Direct inhibition of Mcl-1 releases BID and activates Caspase-mediated mitochondrial apoptosis. | Saadatpour et al. (2011), Table 1; Zhang et al. (2008) |
| **14** | `gt14_tlgl_BclxL_inhibition.cnf` | `['BclxL']` | **`BclxL`** | Neutralization of Bcl-xL permits BID-dependent mitochondrial outer membrane permeabilization. | Saadatpour et al. (2011), Table 1 |
| **15** | `gt15_tlgl_sFas_neutralization.cnf` | `['sFas']` | **`sFas`** | Eliminates soluble decoy sFas, allowing membrane-bound Fas to bind FasL and trigger DISC/Caspase apoptosis. | Saadatpour et al. (2011), Table 1; Liu et al. (2002) |
| **16** | `gt16_tlgl_Ceramide_restoration.cnf` | `['Ceramide']` | **`Ceramide`** | Exogenous Ceramide administration or metabolic accumulation directly activates Caspase-3/8. | Saadatpour et al. (2011), Table 1 |
| **17** | `gt17_tlgl_Fas_death_agonist.cnf` | `['Fas']` | **`Fas`** | Agonistic stimulation of Fas receptor drives death-inducing signaling complex (DISC) assembly. | Saadatpour et al. (2011), Table 1 |
| **18** | `gt18_tlgl_GAP_activation.cnf` | `['GAP']` | **`GAP`** | Stimulates GTP hydrolysis to switch active Ras-GTP into inactive Ras-GDP, extinguishing survival signals. | Saadatpour et al. (2011), Table 1 |
| **19** | `gt19_aml_BCL2_MCL1_synergy.cnf` | `['BCL2', 'MCL1']` | **`BCL2`, `MCL1`** | Overcomes FLT3-ITD resistance. Dual inhibition of BCL2 (Venetoclax) + MCL1 frees BAX/BAK for 100% apoptosis. | Palma et al. (2021), J. Pers. Med. 11(2):117 |
