"""
Asynchronous Temporal Cell Simulator for Cancer Attractor Dynamics.
Based on the General Asynchronous Updating Scheme (GAUS) of Garg et al. (2008)
and the T-LGL / AML leukemia attractor models of Saadatpour et al. (2011) and Palma et al. (2021).
Performs independent stochastic Monte Carlo trajectories to validate drug efficacy and basin stability.
"""

import ast
import json
import random
import re
from typing import Dict, List, Set, Tuple

# 19 Wet-Lab Experimentally Verified Ground-Truth Targets (Saadatpour et al. 2011; Palma et al. 2021)
WET_LAB_GROUND_TRUTH = {
    "S1P": "Sphingosine-1-Phosphate: Inhibition restores Ceramide and DISC apoptosis",
    "SPHK1": "Sphingosine Kinase 1: Inhibition cuts off S1P production",
    "PDGFR": "PDGF Receptor: Inhibition blocks downstream SPHK1, Ras, and PI3K",
    "PDGF": "Platelet-Derived Growth Factor: Microenvironment cytokine inhibition",
    "IL15": "Interleukin-15: Master cytokine survival factor in T-LGL",
    "JAK": "Janus Kinase: Inhibition blocks persistent STAT3 activation",
    "STAT3": "STAT3: Key transcription factor for Mcl-1 and Bcl-xL survival genes",
    "PI3K": "Phosphatidylinositol 3-Kinase: Regulates cell viability and NF-kB",
    "NFkB": "Nuclear Factor kappa-B: Drives transcription of anti-apoptotic FLIP, IAP, Mcl1",
    "Ras": "Ras GTPase: Upstream driver of MEK/ERK survival",
    "MEK": "Mitogen-Activated Protein Kinase Kinase: Proliferation cascade",
    "ERK": "Extracellular Signal-Regulated Kinase: Inhibits Bim/FoxO3 apoptotic axis",
    "Mcl1": "Mcl-1: Essential anti-apoptotic Bcl-2 family protein in leukemic survival",
    "BclxL": "Bcl-xL: Synergistic anti-apoptotic protein protecting cancer cells",
    "sFas": "Soluble Fas: Decoy receptor; inhibition restores membrane Fas-mediated death",
    "Ceramide": "Ceramide: Pro-apoptotic lipid; activation triggers Caspase activation",
    "Fas": "Fas Receptor: Death receptor activation",
    "GAP": "GTPase-Activating Protein: Negative regulator terminating Ras signaling",
    "Caspase": "Caspase-8/3: Direct executioners of apoptotic cell death",
    # AML Verified Targets (Palma et al. 2021)
    "FLT3": "FLT3 Tyrosine Kinase: Primary target in FLT3-ITD acute myeloid leukemia",
    "BCL2": "Bcl-2: Target of Venetoclax in AML",
    "PIM": "PIM Kinase: Compensatory survival pathway in AML",
    "PI3K_AKT": "PI3K/AKT Signaling: Overcomes drug resistance in AML",
    "STAT5": "STAT5: Leukemic stem cell renewal driver",
    # PDAC Pancreatic Targets (Eduati et al. 2020 / Briones-Andrade et al. 2024)
    "KRAS": "KRAS GTPase: Primary oncogenic driver in >90% of pancreatic ductal adenocarcinoma",
    "BRAF": "B-Raf Kinase: Immediate downstream effector of mutant KRAS in PDAC",
    "AKT": "Protein Kinase B (Akt): Key mediator of survival and XIAP maintenance",
    "mTOR": "Mammalian Target of Rapamycin: Master metabolic regulator in PDAC",
    "EGFR": "Epidermal Growth Factor Receptor: Autocrine loop driving bypass resistance",
    "SRC": "Proto-oncogene tyrosine-protein kinase Src: Upstream activator of STAT3",
    "XIAP": "X-linked Inhibitor of Apoptosis: Hallmark anti-apoptotic defense blocking Caspase-3/9",
    # GBM Glioblastoma Targets (Verhaak 2010 / Brennan 2013 / Stupp 2005)
    "MET": "HGF/c-MET Receptor: Mesenchymal subtype driver and radiation resistance node",
    "CDK4": "Cyclin-Dependent Kinase 4: Master G1/S cell cycle driver amplified in GBM",
    "EGFRvIII": "EGFR Variant III: Constitutively active oncogenic deletion mutant in GBM",
    "MGMT": "O6-Methylguanine-DNA Methyltransferase: Mediates Temozolomide alkylation resistance",
    "PTEN": "Phosphatase and Tensin Homolog: Negative regulator of PI3K/Akt pathway",
    "CDKN2A": "Cyclin-Dependent Kinase Inhibitor 2A: Deleted in Classical/Proneural GBM",
    # TNBC Breast Targets (Lehmann 2011 / Robson 2017 OlympiAD / TCGA-BRCA)
    "PARP": "Poly(ADP-ribose) Polymerase: Synthetic lethality target in BRCA1/2-deficient TNBC",
    # mCRC Colorectal Targets (Flobak 2015 / BEACON Trial / CALGB-80405)
    "beta_catenin": "beta-Catenin: Central oncoprotein of canonical Wnt pathway driving colorectal stemness",
    "SMAD4": "SMAD4: Tumor suppressor mediating TGF-beta pathway, often lost in metastatic progression"
}


class RuleCompiler(ast.NodeTransformer):
    """Transforms raw boolean rule AST into dictionary lookups s['gene']."""
    def visit_Name(self, node):
        return ast.Subscript(
            value=ast.Name(id='s', ctx=ast.Load()),
            slice=ast.Constant(value=node.id),
            ctx=ast.Load()
        )


class TemporalCellSimulator:
    def __init__(self, model_dict: Dict):
        self.model_name = model_dict["name"]
        self.raw_rules = model_dict["rules"]
        self.stimuli = set(model_dict.get("stimuli", []))
        self.genes = sorted(list(self.raw_rules.keys()))
        self.compiled_rules = {}

        # Pre-compile boolean rules for high-speed Monte Carlo simulation
        for gene, rule_str in self.raw_rules.items():
            parsed = ast.parse(rule_str.strip(), mode='eval')
            transformed = RuleCompiler().visit(parsed)
            ast.fix_missing_locations(transformed)
            code = compile(transformed, filename=f"<rule_{gene}>", mode='eval')
            self.compiled_rules[gene] = code

    def _get_initial_cancer_state(self) -> Dict[str, int]:
        """Initializes the cell in the active proliferative cancer attractor."""
        s = {g: 0 for g in self.genes}
        
        # 1. Active disease stimuli
        for stim in self.stimuli:
            if stim in s:
                s[stim] = 1

        # 2. Characteristic Proliferative Attractor Phenotype
        active_cancer_markers = [
            "Proliferation", "S1P", "SPHK1", "Ras", "MEK", "ERK", 
            "STAT3", "JAK", "PI3K", "NFkB", "Mcl1", "MCL1", "BclxL", "BCLxL", "FLIP", "cFLIP", "IAP", "XIAP",
            "PDGFR", "FasT", "sFas", "IL2RB", "FLT3", "STAT5", "PI3K_AKT", "MYC", "BCL2",
            "KRAS", "BRAF", "AKT", "mTOR", "SRC", "EGFR", "CyclinD",
            "MET", "CDK4", "EGFRvIII", "TCF4", "beta_catenin"
        ]
        for m in active_cancer_markers:
            if m in s:
                s[m] = 1

        # Apoptosis executioners are strictly inactive in the baseline cancer cell
        s["Apoptosis"] = 0
        if "Ceramide" in s:
            s["Ceramide"] = 0
        if "Caspase" in s:
            s["Caspase"] = 0
        if "Caspase3" in s:
            s["Caspase3"] = 0
        if "Caspase9" in s:
            s["Caspase9"] = 0
        if "Caspase8" in s:
            s["Caspase8"] = 0
        if "Fas" in s:
            s["Fas"] = 0
        if "BAX_BAK" in s:
            s["BAX_BAK"] = 0
        if "CytoC" in s:
            s["CytoC"] = 0

        return s

    def run_trajectory(self, inhibited_genes: Set[str], noise_prob: float = 0.0, max_steps: int = 1500, rng: random.Random = None) -> Tuple[bool, bool, int]:
        """
        Runs a single Monte Carlo asynchronous trajectory (General Asynchronous Updating Scheme).
        Returns: (apoptosis_reached, proliferation_active, steps_taken)
        """
        if rng is None:
            rng = random.Random()

        s = self._get_initial_cancer_state()
        
        # Enforce drug knockdowns from t=0
        for g in inhibited_genes:
            if g in s:
                s[g] = 0

        apoptosis_reached = False
        steps_taken = max_steps

        for step in range(1, max_steps + 1):
            # Select random gene to update asynchronously
            target_gene = rng.choice(self.genes)

            if target_gene in inhibited_genes:
                # Pharmacologically inhibited gene remains locked at 0
                s[target_gene] = 0
            elif target_gene in self.stimuli:
                # Environmental disease stimuli remain persistently active
                s[target_gene] = 1
            else:
                # Evaluate biological logic rule
                code = self.compiled_rules[target_gene]
                try:
                    eval_val = 1 if bool(eval(code, {"__builtins__": {}}, {"s": s})) else 0
                except Exception:
                    eval_val = s[target_gene]

                # Apply biological noise (thermal / transcriptional fluctuation)
                if noise_prob > 0.0 and rng.random() < noise_prob:
                    eval_val = 1 - eval_val

                s[target_gene] = eval_val

            # Check if Apoptosis committed
            if s.get("Apoptosis", 0) == 1 and s.get("Proliferation", 0) == 0:
                apoptosis_reached = True
                steps_taken = step
                break

        final_proliferation = (s.get("Proliferation", 0) == 1)
        return apoptosis_reached, final_proliferation, steps_taken

    def validate(self, candidate_drugs: List[str], n_trajectories: int = 200, max_steps: int = 1500, seed: int = 42, noise_prob: float = 0.02) -> Dict:
        """
        Comprehensive In-Loop Temporal Validation of proposed drug interventions.
        Evaluates both Clean (noise=0.0) and Noisy Basin Stability (configurable noise_prob, default 0.02 / 2%).
        """
        # Normalize drug names (strip DRUG_INHIB_ prefix if passed from solver)
        clean_drugs = set()
        for d in candidate_drugs:
            clean_name = d.replace("DRUG_INHIB_", "").strip()
            if clean_name in self.genes:
                clean_drugs.add(clean_name)

        rng = random.Random(seed)

        # 1. Clean Simulation (noise = 0.0)
        clean_apop_count = 0
        clean_prolif_suppressed_count = 0
        clean_steps_list = []

        for _ in range(n_trajectories):
            apop, prolif, st = self.run_trajectory(clean_drugs, noise_prob=0.0, max_steps=max_steps, rng=rng)
            if apop:
                clean_apop_count += 1
                clean_steps_list.append(st)
            if not prolif:
                clean_prolif_suppressed_count += 1

        apoptosis_rate_clean = (clean_apop_count / n_trajectories) * 100.0
        proliferation_suppression_rate = (clean_prolif_suppressed_count / n_trajectories) * 100.0
        mean_steps = float(sum(clean_steps_list) / len(clean_steps_list)) if clean_steps_list else float(max_steps)

        # 2. Noisy Basin Stability Simulation (stochastic perturbation = noise_prob)
        noisy_apop_count = 0
        for _ in range(n_trajectories):
            apop, _, _ = self.run_trajectory(clean_drugs, noise_prob=noise_prob, max_steps=max_steps, rng=rng)
            if apop:
                noisy_apop_count += 1

        apoptosis_rate_noisy = (noisy_apop_count / n_trajectories) * 100.0

        # 3. Match against Wet-Lab Published Ground Truth
        matches = [d for d in clean_drugs if d in WET_LAB_GROUND_TRUTH]

        # 4. Rigorous Acceptance Threshold:
        # Must achieve >= 85.0% clean mechanistic apoptosis AND >= 90.0% noisy apoptosis AND use between 1 and 3 drugs
        n_drugs = len(clean_drugs)
        passed_verification = (apoptosis_rate_clean >= 85.0) and (apoptosis_rate_noisy >= 90.0) and (1 <= n_drugs <= 3)

        report = {
            "model_name": self.model_name,
            "candidate_drugs": sorted(list(clean_drugs)),
            "n_drugs": n_drugs,
            "noise_prob": round(noise_prob, 4),
            "noise_percent": round(noise_prob * 100.0, 1),
            "apoptosis_rate_clean": round(apoptosis_rate_clean, 2),
            "apoptosis_rate_noisy": round(apoptosis_rate_noisy, 2),
            "proliferation_suppression_rate": round(proliferation_suppression_rate, 2),
            "mean_steps_to_apoptosis": round(mean_steps, 1),
            "wet_lab_ground_truth_matches": matches,
            "passed_verification": passed_verification,
            "verdict": "VERIFIED_THERAPEUTIC_ATTRACTOR" if passed_verification else "REJECTED_INEFFECTIVE_OR_UNSTABLE"
        }

        return report


if __name__ == "__main__":
    from flyfly_oncology.dataset_downloader import load_model
    model = load_model("t_lgl")
    validator = TemporalCellSimulator(model)
    
    print("Testing monotherapy: ['S1P']...")
    rep1 = validator.validate(["S1P"])
    print(json.dumps(rep1, indent=2))

    print("\nTesting monotherapy: ['Mcl1']...")
    rep2 = validator.validate(["Mcl1"])
    print(json.dumps(rep2, indent=2))

    print("\nTesting non-effective gene: ['CD45']...")
    rep3 = validator.validate(["CD45"])
    print(json.dumps(rep3, indent=2))
