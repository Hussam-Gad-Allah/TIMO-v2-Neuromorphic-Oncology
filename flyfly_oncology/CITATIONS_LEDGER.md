# Scientific Citations Ledger — flyfly_oncology
**Module:** Biomedical Connectome-Guided Boolean Oncology Engine  
**Standard:** APA Citation Standard + PubMed / DOI + Direct Software Architecture Mapping  

---

### 1. Dorkenwald2024
- **Citation (APA):** Dorkenwald, S., McKellar, C. E., Macrina, T., Kemnitz, N., Lee, K., Lu, R., ... & Seung, H. S. (2024). Neuronal wiring diagram of an adult brain. *Nature*, 634, 124-138.
- **Digital Object Identifier (DOI):** [10.1038/s41586-024-07558-y](https://doi.org/10.1038/s41586-024-07558-y)
- **PubMed Identifier (PMID):** 39358515
- **Software Implementation Role:** طوبولوجيا كونيكتوم ذبابة الفاكهة الكامل (FlyWire) ومصفوفة التشابكات الموجهة المقروءة في graph_core.pt (23,214 خلية عصبية و 2.55M تشابك عصبي).
- **Mapped Code Component:** `flyfly_sat/data/processed/graph_core.pt & GraphContext`

### 2. Shiu2024
- **Citation (APA):** Shiu, P. K., Sterne, G. R., Spindler, A. R., Leahy, C. R., Sterne, R. G., & Scott, K. (2024). A leaky integrate-and-fire computational model based on the adult Drosophila brain connectome. *Nature*, 634, 181-190.
- **Digital Object Identifier (DOI):** [10.1038/s41586-024-07763-9](https://doi.org/10.1038/s41586-024-07763-9)
- **PubMed Identifier (PMID):** 39358514
- **Software Implementation Role:** معادلات نموذج التسرب والتكامل العصبي (LIF) والثوابت البيولوجية المقاسة معملياً (V_REST = -52.0 mV, V_TH = -45.0 mV, TAU_M = 20.0 ms, TAU_S = 5.0 ms, W_SYN = 0.275 mV, T_REFRACTORY = 2.2 ms, DELAY_MS = 1.8 ms).
- **Mapped Code Component:** `flyfly_oncology.fly_oncology_solver.FlyBrainSNN`

### 3. Groschner2018_Abbott1997
- **Citation (APA):** Groschner, L. N., Chan Wah Hak, L., Bogacz, R., DasGupta, S., & Miesenböck, G. (2018) / Abbott, L. F., Varela, J. A., Sen, K., & Nelson, S. B. (1997) (2018/1997). Dendritic integration of sensory evidence in perceptual decisions / Synaptic depression and cortical gain control. *Nature / Science*, 562 / 275, 56-62 / 221-224.
- **Digital Object Identifier (DOI):** [10.1038/s41586-018-0355-2 / 10.1126/science.275.5297.221](https://doi.org/10.1038/s41586-018-0355-2 / 10.1126/science.275.5297.221)
- **PubMed Identifier (PMID):** 30046105 / 8985017
- **Software Implementation Role:** لدونة استنزاف الحويصلات العصبية قبل التشابكية (Tsodyks-Markram Short-Term Synaptic Depression: TAU_REC = 400.0 ms, U_SE = 0.15) وقفل الجموح المشبكي لمنع التذبذب بين الحلول المتشابهة.
- **Mapped Code Component:** `flyfly_oncology.fly_oncology_solver.FlyBrainSNN.step & last_flip_step`

### 4. Wilson2013
- **Citation (APA):** Wilson, R. I. (2013). Early olfactory processing in Drosophila: mechanisms and principles. *Annual Review of Neuroscience*, 36, 217-241.
- **Digital Object Identifier (DOI):** [10.1146/annurev-neuro-062111-150533](https://doi.org/10.1146/annurev-neuro-062111-150533)
- **PubMed Identifier (PMID):** 23841839
- **Software Implementation Role:** الانتشار الحسي الجانبي في الفص الشمي (Antennal Lobe Lateral Interneuron Diffusion) والتثبيط عبر GABA والترشيح التراجعي للنبضات الزائدة.
- **Mapped Code Component:** `flyfly_oncology.fly_oncology_solver (Antennal Lobe gain diffusion & GABA filter)`

### 5. Lindsay2017
- **Citation (APA):** Lindsay, T., Sustar, A., & Dickinson, M. (2017). The function and organization of descending neurons in Drosophila melanogaster. *Current Biology*, 27, 1118-1132.
- **Digital Object Identifier (DOI):** [10.1016/j.cub.2016.11.058](https://doi.org/10.1016/j.cub.2016.11.058)
- **PubMed Identifier (PMID):** 28111152
- **Software Implementation Role:** التآزر الحركي المركب (Compound Motor Synergies) في الخلايا العصبية الهابطة لتفعيل مجموعات جينات وأدوية متزامنة من الرتب 2 إلى 5 لتخطي القيعان الطاقية.
- **Mapped Code Component:** `flyfly_oncology.fly_oncology_solver.compound_synergy_probe`

### 6. Zhang2008
- **Citation (APA):** Zhang, R., Shah, M. V., Yang, J., Nyland, S. B., Liu, X., Yun, J. K., Albert, R., & Loughran, T. P. (2008). Network model of survival signaling in T-cell large granular lymphocyte leukemia. *Proceedings of the National Academy of Sciences (PNAS)*, 105, 16308-16313.
- **Digital Object Identifier (DOI):** [10.1073/pnas.0806447105](https://doi.org/10.1073/pnas.0806447105)
- **PubMed Identifier (PMID):** 18852469
- **Software Implementation Role:** البنية الأساسية لشبكة البقاء والموت المبرمج في إبيضاض الدم الليمفاوي الحبيبي الكبير (T-LGL Leukemia Boolean Network: 60 عقدة و 142 علاقة بيولوجية).
- **Mapped Code Component:** `flyfly_oncology.dataset_downloader & t_lgl_leukemia_zhang2008.json`

### 7. Saadatpour2011
- **Citation (APA):** Saadatpour, A., Wang, R. S., Liao, A., Liu, X., Loughran, T. P., Albert, I., & Albert, R. (2011). Dynamical and structural analysis of a T cell survival network identifies novel candidate targets for T-cell large granular lymphocyte leukemia. *PLoS Computational Biology*, 7, e1002267.
- **Digital Object Identifier (DOI):** [10.1371/journal.pcbi.1002267](https://doi.org/10.1371/journal.pcbi.1002267)
- **PubMed Identifier (PMID):** 22102804
- **Software Implementation Role:** التحليل الديناميكي غير المتزامن لشبكة اللوكيميا وقائمة الـ 19 هدفاً علاجياً المؤكدة معملياً (Wet-Lab Ground Truth) لمعايرة وتأكيد مخرجات الذبابة.
- **Mapped Code Component:** `flyfly_oncology.temporal_cell_simulator.WET_LAB_GROUND_TRUTH`

### 8. Palma2021
- **Citation (APA):** Palma, A., Jarrah, A. S., Tieri, P., Cesareni, G., & Castiglione, F. (2021). Gene regulatory network modeling of Acute Myeloid Leukemia (AML) patient-specific response to chemotherapy. *Journal of Personalized Medicine*, 11, 117.
- **Digital Object Identifier (DOI):** [10.3390/jpm11020117](https://doi.org/10.3390/jpm11020117)
- **PubMed Identifier (PMID):** 33578936
- **Software Implementation Role:** الشبكات المنطقية المخصصة لمرضى إبيضاض الدم النقوي الحاد (AML Patient-Specific Boolean Models, FLT3-ITD, NPM1, DNMT3A, BCL2/MCL1 drug resistance).
- **Mapped Code Component:** `flyfly_oncology.dataset_downloader & aml_palma2021.json`

### 9. Dubrova2011
- **Citation (APA):** Dubrova, E., & Teslenko, M. (2011). A SAT-based algorithm for finding attractors in synchronous Boolean networks. *IEEE/ACM Transactions on Computational Biology and Bioinformatics*, 8, 1393-1399.
- **Digital Object Identifier (DOI):** [10.1109/TCBB.2010.20](https://doi.org/10.1109/TCBB.2010.20)
- **PubMed Identifier (PMID):** 21778527
- **Software Implementation Role:** خوارزمية تحويل الشبكات المنطقية الجينية إلى صيغة 3-SAT المكافئة (Tseitin CNF Encoding) وتثبيت متغيرات الحالة المستقرة.
- **Mapped Code Component:** `flyfly_oncology.tseitin_cnf_encoder`

### 10. Garg2008
- **Citation (APA):** Garg, A., Di Cara, A., Xenarios, I., Mendoza, L., & De Micheli, G. (2008). Synchronous versus asynchronous modeling of gene regulatory networks. *Bioinformatics*, 24, 1917-1925.
- **Digital Object Identifier (DOI):** [10.1093/bioinformatics/btn336](https://doi.org/10.1093/bioinformatics/btn336)
- **PubMed Identifier (PMID):** 18614585
- **Software Implementation Role:** نظام التحديث غير المتزامن العام (General Asynchronous Updating Scheme - GAUS) لمحاكاة الخلايا السرطانية عبر مسارات مونت كارلو العشوائية في الزمن المتصل.
- **Mapped Code Component:** `flyfly_oncology.temporal_cell_simulator.TemporalCellSimulator`

### 11. Eduati2020
- **Citation (APA):** Eduati, F., Jaaks, P., Wappler, J., Cramer, T., Merten, C. A., Garnett, M. J., & Saez-Rodriguez, J. (2020). Patient-specific logic models of signaling pathways from screenings on cancer biopsies to prioritize personalized combination therapies. *Molecular Systems Biology*, 16, e8664.
- **Digital Object Identifier (DOI):** [10.15252/msb.20188664](https://doi.org/10.15252/msb.20188664)
- **PubMed Identifier (PMID):** 32073727
- **Software Implementation Role:** Patient-specific logic modeling of Pancreatic Ductal Adenocarcinoma (PDAC) signaling pathways and combination therapy prioritization.
- **Mapped Code Component:** `flyfly_oncology/data/raw_published/pdac_kras_model.json`

### 12. Verhaak2010
- **Citation (APA):** Verhaak, R. G., Hoadley, K. A., Purdom, E., Wang, V., Qi, Y., Wilkerson, M. D., ... & Hayes, D. N. (2010). Integrated genomic analysis identifies clinically relevant subtypes of glioblastoma characterized by abnormalities in PDGFRA, IDH1, EGFR, and NF1. *Cancer Cell*, 17, 98-110.
- **Digital Object Identifier (DOI):** [10.1016/j.ccr.2009.12.020](https://doi.org/10.1016/j.ccr.2009.12.020)
- **PubMed Identifier (PMID):** 20129251
- **Software Implementation Role:** Glioblastoma Multiforme (GBM) genomic subtypes and RTK/RAS/PI3K/p53 Boolean network architecture.
- **Mapped Code Component:** `flyfly_oncology/data/raw_published/gbm_model.json`

### 13. Zanudo2017
- **Citation (APA):** Zañudo, J. G. T., Scaltriti, M., & Albert, R. (2017). A network modeling approach to elucidate drug resistance mechanisms and predict combinatorial drug treatments in breast cancer. *Cancer Convergence*, 1, 5.
- **Digital Object Identifier (DOI):** [10.1186/s41236-017-0007-6](https://doi.org/10.1186/s41236-017-0007-6)
- **PubMed Identifier (PMID):** 29623958
- **Software Implementation Role:** Boolean network model of breast cancer drug resistance and combinatorial target identification (TNBC cohort).
- **Mapped Code Component:** `flyfly_oncology/data/raw_published/tnbc_model.json`

### 14. Kopetz2019
- **Citation (APA):** Kopetz, S., Grothey, A., Yaeger, R., Van Cutsem, E., Desai, J., Yoshino, T., ... & Tabernero, J. (2019). Encorafenib, Binimetinib, and Cetuximab in BRAF V600E-Mutated Colorectal Cancer. *New England Journal of Medicine*, 381, 1632-1643.
- **Digital Object Identifier (DOI):** [10.1056/NEJMoa1908075](https://doi.org/10.1056/NEJMoa1908075)
- **PubMed Identifier (PMID):** 31566309
- **Software Implementation Role:** Clinical validation benchmark for EGFR/BRAF/MEK feedback reactivation and combinatorial blockade in metastatic colorectal cancer (mCRC).
- **Mapped Code Component:** `flyfly_oncology/data/raw_published/mcrc_model.json`

### 15. Mackay2017_DIPG
- **Citation (APA):** Mackay, A., Burford, A., Carvalho, D., Izquierdo, E., Fazal-Salom, J., Taylor, K. R., ... & Jones, C. (2017). Integrated Molecular Meta-Analysis of 1,000 Pediatric High-Grade and Diffuse Intrinsic Pontine Glioma. *Cancer Cell*, 32, 520-537.
- **Digital Object Identifier (DOI):** [10.1016/j.ccell.2017.08.017](https://doi.org/10.1016/j.ccell.2017.08.017)
- **PubMed Identifier (PMID):** 28966033
- **Software Implementation Role:** Prospective Unsolved Cohort #1: H3K27M-mutant Diffuse Intrinsic Pontine Glioma (DIPG/DMG) co-segregating with ACVR1, PDGFRA, and TP53 alterations.
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt01_dipg_h3k27m.cnf`

### 16. Howard2023_MRT
- **Citation (APA):** Howard, T. P., Arnoff, T. E., Song, M. R., Giacomini, C., & Roberts, C. W. M. (2023). SMARCB1 loss creates epigenetic and apoptotic vulnerabilities in malignant rhabdoid tumors. *Cancer Cell*, 41, 412-428.
- **Digital Object Identifier (DOI):** [10.1016/j.ccell.2023.02.008](https://doi.org/10.1016/j.ccell.2023.02.008)
- **PubMed Identifier (PMID):** 36898377
- **Software Implementation Role:** Prospective Unsolved Cohort #2: SMARCB1 (INI1)-null Malignant Rhabdoid Tumor (MRT) driven by EZH2/PRC2 and MYC overdrive.
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt02_mrt_smarcb1_null.cnf`

### 17. Tirode2014_Ewing
- **Citation (APA):** Tirode, F., Surdez, D., Ma, X., Parker, M., Le Deley, M. C., Bahrami, A., ... & Delattre, O. (2014). Genomic landscape of Ewing sarcoma defines an aggressive subtype with co-association of STAG2 and TP53 mutations. *Cancer Discovery*, 4, 1342-1353.
- **Digital Object Identifier (DOI):** [10.1158/2159-8290.CD-14-0622](https://doi.org/10.1158/2159-8290.CD-14-0622)
- **PubMed Identifier (PMID):** 25223734
- **Software Implementation Role:** Prospective Unsolved Cohort #3: Metastatic Ewing Sarcoma with EWSR1-FLI1 fusion and STAG2/TP53 co-mutation.
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt03_ewing_ewsr1_fli1.cnf`

### 18. Shern2014_ARMS
- **Citation (APA):** Shern, J. F., Chen, L., Chmielecki, J., Wei, J. S., Patidar, R., Rosenberg, M., ... & Khan, J. (2014). Comprehensive genomic analysis of rhabdomyosarcoma reveals a landscape of alterations affecting a common genetic axis in fusion-positive and fusion-negative tumors. *Cancer Discovery*, 4, 216-231.
- **Digital Object Identifier (DOI):** [10.1158/2159-8290.CD-13-0639](https://doi.org/10.1158/2159-8290.CD-13-0639)
- **PubMed Identifier (PMID):** 24436047
- **Software Implementation Role:** Prospective Unsolved Cohort #4: Fusion-Positive Alveolar Rhabdomyosarcoma (PAX3-FOXO1 + MYCN/CDK4 axis).
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt04_arms_pax3_foxo1.cnf`

### 19. Honeyman2014_FLHCC
- **Citation (APA):** Honeyman, J. N., Simon, E. P., Robine, N., Chiaroni-Clarke, R., Darcy, D. G., Lim, I. I., ... & Simon, S. M. (2014). Detection of a recurrent DNAJB1-PRKACA chimeric transcript in fibrolamellar hepatocellular carcinoma. *Science*, 343, 1010-1014.
- **Digital Object Identifier (DOI):** [10.1126/science.1249099](https://doi.org/10.1126/science.1249099)
- **PubMed Identifier (PMID):** 24578576
- **Software Implementation Role:** Prospective Unsolved Cohort #5: Fibrolamellar Hepatocellular Carcinoma (FL-HCC) driven by the DNAJB1-PRKACA chimeric kinase.
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt05_flhcc_dnajb1_prkaca.cnf`

### 20. Ho2013_ACC
- **Citation (APA):** Ho, A. S., Kannan, K., Roy, D. M., Morris, L. G., Ganly, I., Katabi, N., ... & Chan, T. A. (2013). The mutational landscape of adenoid cystic carcinoma. *Nature Genetics*, 45, 791-798.
- **Digital Object Identifier (DOI):** [10.1038/ng.2643](https://doi.org/10.1038/ng.2643)
- **PubMed Identifier (PMID):** 23685749
- **Software Implementation Role:** Prospective Unsolved Cohort #6: Metastatic Adenoid Cystic Carcinoma (ACC) with MYB-NFIB fusion and NOTCH1 activation.
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt06_acc_myb_nfib.cnf`

### 21. Liao2020_NUT
- **Citation (APA):** Liao, S., Maertens, O., Cichowski, K., & Elledge, S. J. (2020). Genetic modifiers of BET inhibitor sensitivity in NUT carcinoma. *Clinical Cancer Research*, 26, 1691-1703.
- **Digital Object Identifier (DOI):** [10.1158/1078-0432.CCR-19-2898](https://doi.org/10.1158/1078-0432.CCR-19-2898)
- **PubMed Identifier (PMID):** 31969334
- **Software Implementation Role:** Prospective Unsolved Cohort #7: Thoracic NUT Carcinoma driven by BRD4-NUTM1 megadomains and SOX2/MYC super-enhancers.
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt07_nut_brd4_nutm1.cnf`

### 22. Lee2014_MPNST
- **Citation (APA):** Lee, W., Teckie, S., Wiesner, T., Ran, L., Prieto Granada, C. N., Lin, M., ... & Chi, P. (2014). PRC2 is recurrently inactivated through EED or SUZ12 loss in malignant peripheral nerve sheath tumors. *Nature Genetics*, 46, 1227-1232.
- **Digital Object Identifier (DOI):** [10.1038/ng.3095](https://doi.org/10.1038/ng.3095)
- **PubMed Identifier (PMID):** 25240281
- **Software Implementation Role:** Prospective Unsolved Cohort #8: Malignant Peripheral Nerve Sheath Tumor (MPNST) with NF1, CDKN2A, and PRC2 (SUZ12/EED) loss.
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt08_mpnst_nf1_prc2_loss.cnf`

### 23. Robertson2017_UVM
- **Citation (APA):** Robertson, A. G., Shih, J., Yau, C., Gibb, E. A., Oba, J., Mungall, K. L., ... & Woodman, S. E. (2017). Integrative Analysis Identifies Four Molecular and Clinical Subsets in Uveal Melanoma. *Cancer Cell*, 32, 204-220.
- **Digital Object Identifier (DOI):** [10.1016/j.ccell.2017.07.003](https://doi.org/10.1016/j.ccell.2017.07.003)
- **PubMed Identifier (PMID):** 28810145
- **Software Implementation Role:** Prospective Unsolved Cohort #9: Metastatic Uveal Melanoma (mUVM) driven by GNAQ/GNA11 Q209L and BAP1 loss.
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt09_uvm_gnaq_bap1_liver_met.cnf`

### 24. Bueno2016_MPM
- **Citation (APA):** Bueno, R., Stawiski, E. W., Goldstein, L. D., Durinck, S., De Rienzo, A., Modrusan, Z., ... & Seshagiri, S. (2016). Comprehensive genomic analysis of malignant pleural mesothelioma identifies recurrent mutations, gene fusions and splicing alterations. *Nature Genetics*, 48, 407-416.
- **Digital Object Identifier (DOI):** [10.1038/ng.3520](https://doi.org/10.1038/ng.3520)
- **PubMed Identifier (PMID):** 26928227
- **Software Implementation Role:** Prospective Unsolved Cohort #10: Sarcomatoid Malignant Pleural Mesothelioma (MPM) with BAP1, NF2, and CDKN2A loss.
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt10_mpm_bap1_nf2_cdkn2a.cnf`

### 25. Slotkin2021_DSRCT
- **Citation (APA):** Slotkin, E. K., Bowman, A. S., Levine, M. F., & Shukla, N. (2021). Comprehensive molecular profiling of desmoplastic small round cell tumor reveals recurrent oncogenic dependencies. *Clinical Cancer Research*, 27, 2890-2901.
- **Digital Object Identifier (DOI):** [10.1158/1078-0432.CCR-20-4165](https://doi.org/10.1158/1078-0432.CCR-20-4165)
- **PubMed Identifier (PMID):** 33602685
- **Software Implementation Role:** Prospective Unsolved Cohort #11: Desmoplastic Small Round Cell Tumor (DSRCT) driven by EWSR1-WT1 chimeric transcription factor.
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt11_dsrct_ewsr1_wt1.cnf`

### 26. Tarpey2017_Chordoma
- **Citation (APA):** Tarpey, P. S., Behjati, S., Young, M. D., Martincorena, I., Alexandrov, L. B., Farndon, S. J., ... & Campbell, P. J. (2017). The driver landscape of sporadic chordoma. *Nature Communications*, 8, 890.
- **Digital Object Identifier (DOI):** [10.1038/s41467-017-01026-0](https://doi.org/10.1038/s41467-017-01026-0)
- **PubMed Identifier (PMID):** 28986566
- **Software Implementation Role:** Prospective Unsolved Cohort #12: Skull-Base Clival Chordoma driven by TBXT (Brachyury), CDKN2A loss, and PI3K/EGFR survival signaling.
- **Mapped Code Component:** `flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt12_chordoma_tbxt_egfr.cnf`
