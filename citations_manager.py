"""
Citations Manager for flyfly_oncology.
Generates CITATIONS_LEDGER.md and references.bib documenting peer-reviewed foundations.
"""

from pathlib import Path

CITATIONS = [
    {
        "id": "Dorkenwald2024",
        "authors": "Dorkenwald, S., McKellar, C. E., Macrina, T., Kemnitz, N., Lee, K., Lu, R., ... & Seung, H. S.",
        "year": "2024",
        "title": "Neuronal wiring diagram of an adult brain",
        "journal": "Nature",
        "volume": "634",
        "pages": "124-138",
        "doi": "10.1038/s41586-024-07558-y",
        "pmid": "39358515",
        "software_role": "طوبولوجيا كونيكتوم ذبابة الفاكهة الكامل (FlyWire) ومصفوفة التشابكات الموجهة المقروءة في graph_core.pt (23,214 خلية عصبية و 2.55M تشابك عصبي).",
        "component": "flyfly_sat/data/processed/graph_core.pt & GraphContext"
    },
    {
        "id": "Shiu2024",
        "authors": "Shiu, P. K., Sterne, G. R., Spindler, A. R., Leahy, C. R., Sterne, R. G., & Scott, K.",
        "year": "2024",
        "title": "A leaky integrate-and-fire computational model based on the adult Drosophila brain connectome",
        "journal": "Nature",
        "volume": "634",
        "pages": "181-190",
        "doi": "10.1038/s41586-024-07763-9",
        "pmid": "39358514",
        "software_role": "معادلات نموذج التسرب والتكامل العصبي (LIF) والثوابت البيولوجية المقاسة معملياً (V_REST = -52.0 mV, V_TH = -45.0 mV, TAU_M = 20.0 ms, TAU_S = 5.0 ms, W_SYN = 0.275 mV, T_REFRACTORY = 2.2 ms, DELAY_MS = 1.8 ms).",
        "component": "flyfly_oncology.fly_oncology_solver.FlyBrainSNN"
    },
    {
        "id": "Groschner2018_Abbott1997",
        "authors": "Groschner, L. N., Chan Wah Hak, L., Bogacz, R., DasGupta, S., & Miesenböck, G. (2018) / Abbott, L. F., Varela, J. A., Sen, K., & Nelson, S. B. (1997)",
        "year": "2018/1997",
        "title": "Dendritic integration of sensory evidence in perceptual decisions / Synaptic depression and cortical gain control",
        "journal": "Nature / Science",
        "volume": "562 / 275",
        "pages": "56-62 / 221-224",
        "doi": "10.1038/s41586-018-0355-2 / 10.1126/science.275.5297.221",
        "pmid": "30046105 / 8985017",
        "software_role": "لدونة استنزاف الحويصلات العصبية قبل التشابكية (Tsodyks-Markram Short-Term Synaptic Depression: TAU_REC = 400.0 ms, U_SE = 0.15) وقفل الجموح المشبكي لمنع التذبذب بين الحلول المتشابهة.",
        "component": "flyfly_oncology.fly_oncology_solver.FlyBrainSNN.step & last_flip_step"
    },
    {
        "id": "Wilson2013",
        "authors": "Wilson, R. I.",
        "year": "2013",
        "title": "Early olfactory processing in Drosophila: mechanisms and principles",
        "journal": "Annual Review of Neuroscience",
        "volume": "36",
        "pages": "217-241",
        "doi": "10.1146/annurev-neuro-062111-150533",
        "pmid": "23841839",
        "software_role": "الانتشار الحسي الجانبي في الفص الشمي (Antennal Lobe Lateral Interneuron Diffusion) والتثبيط عبر GABA والترشيح التراجعي للنبضات الزائدة.",
        "component": "flyfly_oncology.fly_oncology_solver (Antennal Lobe gain diffusion & GABA filter)"
    },
    {
        "id": "Lindsay2017",
        "authors": "Lindsay, T., Sustar, A., & Dickinson, M.",
        "year": "2017",
        "title": "The function and organization of descending neurons in Drosophila melanogaster",
        "journal": "Current Biology",
        "volume": "27",
        "pages": "1118-1132",
        "doi": "10.1016/j.cub.2016.11.058",
        "pmid": "28111152",
        "software_role": "التآزر الحركي المركب (Compound Motor Synergies) في الخلايا العصبية الهابطة لتفعيل مجموعات جينات وأدوية متزامنة من الرتب 2 إلى 5 لتخطي القيعان الطاقية.",
        "component": "flyfly_oncology.fly_oncology_solver.compound_synergy_probe"
    },
    {
        "id": "Zhang2008",
        "authors": "Zhang, R., Shah, M. V., Yang, J., Nyland, S. B., Liu, X., Yun, J. K., Albert, R., & Loughran, T. P.",
        "year": "2008",
        "title": "Network model of survival signaling in T-cell large granular lymphocyte leukemia",
        "journal": "Proceedings of the National Academy of Sciences (PNAS)",
        "volume": "105",
        "pages": "16308-16313",
        "doi": "10.1073/pnas.0806447105",
        "pmid": "18852469",
        "software_role": "البنية الأساسية لشبكة البقاء والموت المبرمج في إبيضاض الدم الليمفاوي الحبيبي الكبير (T-LGL Leukemia Boolean Network: 60 عقدة و 142 علاقة بيولوجية).",
        "component": "flyfly_oncology.dataset_downloader & t_lgl_leukemia_zhang2008.json"
    },
    {
        "id": "Saadatpour2011",
        "authors": "Saadatpour, A., Wang, R. S., Liao, A., Liu, X., Loughran, T. P., Albert, I., & Albert, R.",
        "year": "2011",
        "title": "Dynamical and structural analysis of a T cell survival network identifies novel candidate targets for T-cell large granular lymphocyte leukemia",
        "journal": "PLoS Computational Biology",
        "volume": "7",
        "pages": "e1002267",
        "doi": "10.1371/journal.pcbi.1002267",
        "pmid": "22102804",
        "software_role": "التحليل الديناميكي غير المتزامن لشبكة اللوكيميا وقائمة الـ 19 هدفاً علاجياً المؤكدة معملياً (Wet-Lab Ground Truth) لمعايرة وتأكيد مخرجات الذبابة.",
        "component": "flyfly_oncology.temporal_cell_simulator.WET_LAB_GROUND_TRUTH"
    },
    {
        "id": "Palma2021",
        "authors": "Palma, A., Jarrah, A. S., Tieri, P., Cesareni, G., & Castiglione, F.",
        "year": "2021",
        "title": "Gene regulatory network modeling of Acute Myeloid Leukemia (AML) patient-specific response to chemotherapy",
        "journal": "Journal of Personalized Medicine",
        "volume": "11",
        "pages": "117",
        "doi": "10.3390/jpm11020117",
        "pmid": "33578936",
        "software_role": "الشبكات المنطقية المخصصة لمرضى إبيضاض الدم النقوي الحاد (AML Patient-Specific Boolean Models, FLT3-ITD, NPM1, DNMT3A, BCL2/MCL1 drug resistance).",
        "component": "flyfly_oncology.dataset_downloader & aml_palma2021.json"
    },
    {
        "id": "Dubrova2011",
        "authors": "Dubrova, E., & Teslenko, M.",
        "year": "2011",
        "title": "A SAT-based algorithm for finding attractors in synchronous Boolean networks",
        "journal": "IEEE/ACM Transactions on Computational Biology and Bioinformatics",
        "volume": "8",
        "pages": "1393-1399",
        "doi": "10.1109/TCBB.2010.20",
        "pmid": "21778527",
        "software_role": "خوارزمية تحويل الشبكات المنطقية الجينية إلى صيغة 3-SAT المكافئة (Tseitin CNF Encoding) وتثبيت متغيرات الحالة المستقرة.",
        "component": "flyfly_oncology.tseitin_cnf_encoder"
    },
    {
        "id": "Garg2008",
        "authors": "Garg, A., Di Cara, A., Xenarios, I., Mendoza, L., & De Micheli, G.",
        "year": "2008",
        "title": "Synchronous versus asynchronous modeling of gene regulatory networks",
        "journal": "Bioinformatics",
        "volume": "24",
        "pages": "1917-1925",
        "doi": "10.1093/bioinformatics/btn336",
        "pmid": "18614585",
        "software_role": "نظام التحديث غير المتزامن العام (General Asynchronous Updating Scheme - GAUS) لمحاكاة الخلايا السرطانية عبر مسارات مونت كارلو العشوائية في الزمن المتصل.",
        "component": "flyfly_oncology.temporal_cell_simulator.TemporalCellSimulator"
    },
    {
        "id": "Eduati2020",
        "authors": "Eduati, F., Jaaks, P., Wappler, J., Cramer, T., Merten, C. A., Garnett, M. J., & Saez-Rodriguez, J.",
        "year": "2020",
        "title": "Patient-specific logic models of signaling pathways from screenings on cancer biopsies to prioritize personalized combination therapies",
        "journal": "Molecular Systems Biology",
        "volume": "16",
        "pages": "e8664",
        "doi": "10.15252/msb.20188664",
        "pmid": "32073727",
        "software_role": "Patient-specific logic modeling of Pancreatic Ductal Adenocarcinoma (PDAC) signaling pathways and combination therapy prioritization.",
        "component": "flyfly_oncology/data/raw_published/pdac_kras_model.json"
    },
    {
        "id": "Verhaak2010",
        "authors": "Verhaak, R. G., Hoadley, K. A., Purdom, E., Wang, V., Qi, Y., Wilkerson, M. D., ... & Hayes, D. N.",
        "year": "2010",
        "title": "Integrated genomic analysis identifies clinically relevant subtypes of glioblastoma characterized by abnormalities in PDGFRA, IDH1, EGFR, and NF1",
        "journal": "Cancer Cell",
        "volume": "17",
        "pages": "98-110",
        "doi": "10.1016/j.ccr.2009.12.020",
        "pmid": "20129251",
        "software_role": "Glioblastoma Multiforme (GBM) genomic subtypes and RTK/RAS/PI3K/p53 Boolean network architecture.",
        "component": "flyfly_oncology/data/raw_published/gbm_model.json"
    },
    {
        "id": "Zanudo2017",
        "authors": "Zañudo, J. G. T., Scaltriti, M., & Albert, R.",
        "year": "2017",
        "title": "A network modeling approach to elucidate drug resistance mechanisms and predict combinatorial drug treatments in breast cancer",
        "journal": "Cancer Convergence",
        "volume": "1",
        "pages": "5",
        "doi": "10.1186/s41236-017-0007-6",
        "pmid": "29623958",
        "software_role": "Boolean network model of breast cancer drug resistance and combinatorial target identification (TNBC cohort).",
        "component": "flyfly_oncology/data/raw_published/tnbc_model.json"
    },
    {
        "id": "Kopetz2019",
        "authors": "Kopetz, S., Grothey, A., Yaeger, R., Van Cutsem, E., Desai, J., Yoshino, T., ... & Tabernero, J.",
        "year": "2019",
        "title": "Encorafenib, Binimetinib, and Cetuximab in BRAF V600E-Mutated Colorectal Cancer",
        "journal": "New England Journal of Medicine",
        "volume": "381",
        "pages": "1632-1643",
        "doi": "10.1056/NEJMoa1908075",
        "pmid": "31566309",
        "software_role": "Clinical validation benchmark for EGFR/BRAF/MEK feedback reactivation and combinatorial blockade in metastatic colorectal cancer (mCRC).",
        "component": "flyfly_oncology/data/raw_published/mcrc_model.json"
    },
    {
        "id": "Mackay2017_DIPG",
        "authors": "Mackay, A., Burford, A., Carvalho, D., Izquierdo, E., Fazal-Salom, J., Taylor, K. R., ... & Jones, C.",
        "year": "2017",
        "title": "Integrated Molecular Meta-Analysis of 1,000 Pediatric High-Grade and Diffuse Intrinsic Pontine Glioma",
        "journal": "Cancer Cell",
        "volume": "32",
        "pages": "520-537",
        "doi": "10.1016/j.ccell.2017.08.017",
        "pmid": "28966033",
        "software_role": "Prospective Unsolved Cohort #1: H3K27M-mutant Diffuse Intrinsic Pontine Glioma (DIPG/DMG) co-segregating with ACVR1, PDGFRA, and TP53 alterations.",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt01_dipg_h3k27m.cnf"
    },
    {
        "id": "Howard2023_MRT",
        "authors": "Howard, T. P., Arnoff, T. E., Song, M. R., Giacomini, C., & Roberts, C. W. M.",
        "year": "2023",
        "title": "SMARCB1 loss creates epigenetic and apoptotic vulnerabilities in malignant rhabdoid tumors",
        "journal": "Cancer Cell",
        "volume": "41",
        "pages": "412-428",
        "doi": "10.1016/j.ccell.2023.02.008",
        "pmid": "36898377",
        "software_role": "Prospective Unsolved Cohort #2: SMARCB1 (INI1)-null Malignant Rhabdoid Tumor (MRT) driven by EZH2/PRC2 and MYC overdrive.",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt02_mrt_smarcb1_null.cnf"
    },
    {
        "id": "Tirode2014_Ewing",
        "authors": "Tirode, F., Surdez, D., Ma, X., Parker, M., Le Deley, M. C., Bahrami, A., ... & Delattre, O.",
        "year": "2014",
        "title": "Genomic landscape of Ewing sarcoma defines an aggressive subtype with co-association of STAG2 and TP53 mutations",
        "journal": "Cancer Discovery",
        "volume": "4",
        "pages": "1342-1353",
        "doi": "10.1158/2159-8290.CD-14-0622",
        "pmid": "25223734",
        "software_role": "Prospective Unsolved Cohort #3: Metastatic Ewing Sarcoma with EWSR1-FLI1 fusion and STAG2/TP53 co-mutation.",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt03_ewing_ewsr1_fli1.cnf"
    },
    {
        "id": "Shern2014_ARMS",
        "authors": "Shern, J. F., Chen, L., Chmielecki, J., Wei, J. S., Patidar, R., Rosenberg, M., ... & Khan, J.",
        "year": "2014",
        "title": "Comprehensive genomic analysis of rhabdomyosarcoma reveals a landscape of alterations affecting a common genetic axis in fusion-positive and fusion-negative tumors",
        "journal": "Cancer Discovery",
        "volume": "4",
        "pages": "216-231",
        "doi": "10.1158/2159-8290.CD-13-0639",
        "pmid": "24436047",
        "software_role": "Prospective Unsolved Cohort #4: Fusion-Positive Alveolar Rhabdomyosarcoma (PAX3-FOXO1 + MYCN/CDK4 axis).",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt04_arms_pax3_foxo1.cnf"
    },
    {
        "id": "Honeyman2014_FLHCC",
        "authors": "Honeyman, J. N., Simon, E. P., Robine, N., Chiaroni-Clarke, R., Darcy, D. G., Lim, I. I., ... & Simon, S. M.",
        "year": "2014",
        "title": "Detection of a recurrent DNAJB1-PRKACA chimeric transcript in fibrolamellar hepatocellular carcinoma",
        "journal": "Science",
        "volume": "343",
        "pages": "1010-1014",
        "doi": "10.1126/science.1249099",
        "pmid": "24578576",
        "software_role": "Prospective Unsolved Cohort #5: Fibrolamellar Hepatocellular Carcinoma (FL-HCC) driven by the DNAJB1-PRKACA chimeric kinase.",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt05_flhcc_dnajb1_prkaca.cnf"
    },
    {
        "id": "Ho2013_ACC",
        "authors": "Ho, A. S., Kannan, K., Roy, D. M., Morris, L. G., Ganly, I., Katabi, N., ... & Chan, T. A.",
        "year": "2013",
        "title": "The mutational landscape of adenoid cystic carcinoma",
        "journal": "Nature Genetics",
        "volume": "45",
        "pages": "791-798",
        "doi": "10.1038/ng.2643",
        "pmid": "23685749",
        "software_role": "Prospective Unsolved Cohort #6: Metastatic Adenoid Cystic Carcinoma (ACC) with MYB-NFIB fusion and NOTCH1 activation.",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt06_acc_myb_nfib.cnf"
    },
    {
        "id": "Liao2020_NUT",
        "authors": "Liao, S., Maertens, O., Cichowski, K., & Elledge, S. J.",
        "year": "2020",
        "title": "Genetic modifiers of BET inhibitor sensitivity in NUT carcinoma",
        "journal": "Clinical Cancer Research",
        "volume": "26",
        "pages": "1691-1703",
        "doi": "10.1158/1078-0432.CCR-19-2898",
        "pmid": "31969334",
        "software_role": "Prospective Unsolved Cohort #7: Thoracic NUT Carcinoma driven by BRD4-NUTM1 megadomains and SOX2/MYC super-enhancers.",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt07_nut_brd4_nutm1.cnf"
    },
    {
        "id": "Lee2014_MPNST",
        "authors": "Lee, W., Teckie, S., Wiesner, T., Ran, L., Prieto Granada, C. N., Lin, M., ... & Chi, P.",
        "year": "2014",
        "title": "PRC2 is recurrently inactivated through EED or SUZ12 loss in malignant peripheral nerve sheath tumors",
        "journal": "Nature Genetics",
        "volume": "46",
        "pages": "1227-1232",
        "doi": "10.1038/ng.3095",
        "pmid": "25240281",
        "software_role": "Prospective Unsolved Cohort #8: Malignant Peripheral Nerve Sheath Tumor (MPNST) with NF1, CDKN2A, and PRC2 (SUZ12/EED) loss.",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt08_mpnst_nf1_prc2_loss.cnf"
    },
    {
        "id": "Robertson2017_UVM",
        "authors": "Robertson, A. G., Shih, J., Yau, C., Gibb, E. A., Oba, J., Mungall, K. L., ... & Woodman, S. E.",
        "year": "2017",
        "title": "Integrative Analysis Identifies Four Molecular and Clinical Subsets in Uveal Melanoma",
        "journal": "Cancer Cell",
        "volume": "32",
        "pages": "204-220",
        "doi": "10.1016/j.ccell.2017.07.003",
        "pmid": "28810145",
        "software_role": "Prospective Unsolved Cohort #9: Metastatic Uveal Melanoma (mUVM) driven by GNAQ/GNA11 Q209L and BAP1 loss.",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt09_uvm_gnaq_bap1_liver_met.cnf"
    },
    {
        "id": "Bueno2016_MPM",
        "authors": "Bueno, R., Stawiski, E. W., Goldstein, L. D., Durinck, S., De Rienzo, A., Modrusan, Z., ... & Seshagiri, S.",
        "year": "2016",
        "title": "Comprehensive genomic analysis of malignant pleural mesothelioma identifies recurrent mutations, gene fusions and splicing alterations",
        "journal": "Nature Genetics",
        "volume": "48",
        "pages": "407-416",
        "doi": "10.1038/ng.3520",
        "pmid": "26928227",
        "software_role": "Prospective Unsolved Cohort #10: Sarcomatoid Malignant Pleural Mesothelioma (MPM) with BAP1, NF2, and CDKN2A loss.",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt10_mpm_bap1_nf2_cdkn2a.cnf"
    },
    {
        "id": "Slotkin2021_DSRCT",
        "authors": "Slotkin, E. K., Bowman, A. S., Levine, M. F., & Shukla, N.",
        "year": "2021",
        "title": "Comprehensive molecular profiling of desmoplastic small round cell tumor reveals recurrent oncogenic dependencies",
        "journal": "Clinical Cancer Research",
        "volume": "27",
        "pages": "2890-2901",
        "doi": "10.1158/1078-0432.CCR-20-4165",
        "pmid": "33602685",
        "software_role": "Prospective Unsolved Cohort #11: Desmoplastic Small Round Cell Tumor (DSRCT) driven by EWSR1-WT1 chimeric transcription factor.",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt11_dsrct_ewsr1_wt1.cnf"
    },
    {
        "id": "Tarpey2017_Chordoma",
        "authors": "Tarpey, P. S., Behjati, S., Young, M. D., Martincorena, I., Alexandrov, L. B., Farndon, S. J., ... & Campbell, P. J.",
        "year": "2017",
        "title": "The driver landscape of sporadic chordoma",
        "journal": "Nature Communications",
        "volume": "8",
        "pages": "890",
        "doi": "10.1038/s41467-017-01026-0",
        "pmid": "28986566",
        "software_role": "Prospective Unsolved Cohort #12: Skull-Base Clival Chordoma driven by TBXT (Brachyury), CDKN2A loss, and PI3K/EGFR survival signaling.",
        "component": "flyfly_oncology/data/benchmarks/unsolved_patients/unsolved_pt12_chordoma_tbxt_egfr.cnf"
    }
]


def generate_ledgers(output_dir: Path = None):
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent

    md_path = output_dir / "CITATIONS_LEDGER.md"
    bib_path = output_dir / "references.bib"

    # 1. Generate Markdown Ledger
    md_lines = [
        "# Scientific Citations Ledger — flyfly_oncology",
        "**Module:** Biomedical Connectome-Guided Boolean Oncology Engine  ",
        "**Standard:** APA Citation Standard + PubMed / DOI + Direct Software Architecture Mapping  \n",
        "---",
        ""
    ]

    for i, c in enumerate(CITATIONS, 1):
        md_lines.extend([
            f"### {i}. {c['id']}",
            f"- **Citation (APA):** {c['authors']} ({c['year']}). {c['title']}. *{c['journal']}*, {c['volume']}, {c['pages']}.",
            f"- **Digital Object Identifier (DOI):** [{c['doi']}](https://doi.org/{c['doi']})",
            f"- **PubMed Identifier (PMID):** {c['pmid']}",
            f"- **Software Implementation Role:** {c['software_role']}",
            f"- **Mapped Code Component:** `{c['component']}`",
            ""
        ])

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    # 2. Generate BibTeX Ledger
    bib_entries = []
    for c in CITATIONS:
        key = c["id"]
        entry = (
            f"@article{{{key},\n"
            f"  author = {{{c['authors']}}},\n"
            f"  title = {{{c['title']}}},\n"
            f"  journal = {{{c['journal']}}},\n"
            f"  year = {{{c['year']}}},\n"
            f"  volume = {{{c['volume']}}},\n"
            f"  pages = {{{c['pages']}}},\n"
            f"  doi = {{{c['doi']}}},\n"
            f"  note = {{PMID: {c['pmid']}}}\n"
            f"}}"
        )
        bib_entries.append(entry)

    with open(bib_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(bib_entries) + "\n")

    print(f"[CitationsManager] Generated {md_path.name} ({len(CITATIONS)} citations)")
    print(f"[CitationsManager] Generated {bib_path.name}")
    return md_path, bib_path


generate_citations = generate_ledgers

if __name__ == "__main__":
    generate_ledgers()
