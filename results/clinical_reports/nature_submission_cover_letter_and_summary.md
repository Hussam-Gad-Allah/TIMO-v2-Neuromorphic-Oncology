# Nature Communications Submission Package & Executive Summary

**Manuscript Title:** Zero-Shot Combinatorial Optimization Across Hard Landscapes Directed by a Drosophila Connectome Sub-Circuit  
**Short Running Title:** Insect Connectome Combinatorial Optimization  
**Lead & Corresponding Author:** Hussam Gad-Allah*  
**Affiliations:**  
¹ Advanced Autonomous Oncology & Neuromorphic Computing Laboratory, Cairo, Egypt  
² Faculty of Computers & Artificial Intelligence, Cairo University / CAPU, Giza, Egypt  
**Official Emails:** 12422023437409@pg.cu.edu.eg, hossamhassanahmed140@fcba.capu.edu.eg  
**ORCID:** [0009-0002-6823-2951](https://orcid.org/0009-0002-6823-2951)  
**Target Journal:** *Nature Communications* (Primary Research Article)  
**Model Framework Designation:** **TIMO** (**T**opological **I**nsect-connectome **M**odel for **O**ptimization)  
**Intellectual Property & Copyright:** © 2026 Hussam Gad-Allah. All rights reserved.

---

## 1. Official Editorial Cover Letter

**To:**  
The Senior Editors  
*Nature Communications*  
Springer Nature Publishing AG  

**Date:** October 16, 2026  

**Dear Editors,**

I am pleased to submit our original research article titled **"Zero-Shot Combinatorial Optimization Across Hard Landscapes Directed by a Drosophila Connectome Sub-Circuit"** for consideration as a Primary Research Article in *Nature Communications*.

Resolving non-differentiable combinatorial constraints represents a persistent computational bottleneck across computer science. Near the algorithmic phase boundary ($\alpha = M/N \approx 4.26$), Boolean satisfiability (3-SAT) instances construct chaotic energy landscapes where deterministic CDCL solvers suffer exponential memory growth and gradient-based neural networks fail due to non-existent gradients. Conversely, biological nervous systems resolve multi-sensory physical conflicts under severe metabolic limits without backpropagation updates.

In this work, we demonstrate that an anatomically grounded 23,214-neuron sub-circuit of the *Drosophila melanogaster* connectome (FlyWire FAFB release v783; 2,552,344 directed synapses) operates as an asynchronous, zero-shot combinatorial solver. We designate this architecture **TIMO** (**T**opological **I**nsect-connectome **M**odel for **O**ptimization). Across a complete, transparent chronological record of **110 experimental executions totaling 116,287.76 seconds (32.30 hours) of GPU simulation and 144,686,214 clause evaluations across eight engineering stages**, we show how progressively activating five biological skills—lateral GABAergic inhibition, mushroom body clause-hardness conditioning, area-restricted foraging patch descent, 456-neuron 3D visual repulsion memory, and high-order descending motor synergies (`1-flip` to `9-flip` tunneling)—transforms solver performance from 0% (`snn_only` baseline) to a **100% empirical solve rate across evaluated UF100 phase-transition benchmarks (10/10 solved; fastest solve 4.57 s) and structured verification instances (`1sp.cnf` solved in 29.18 s where classical greedy local search fails after 2,000,371 steps)**.

### Key Conceptual & Empirical Advances:
1. **Complete Eight-Stage Evolutionary Audit (110 Runs / 32.30 Hours):** Rather than reporting only post-hoc tuned parameters, we present the complete chronological trajectory from Stage 0/1 unmodulated connectome baselines (`0%` solve rate) to Stage 6–8 full bio-skill integration (`100%` solve rate), quantifying the exact wall-clock speedup of each biological mechanism (e.g., $8.69\times$ wall-clock speedup from dopaminergic stagnant-attractor eviction on `uf50-02`, saving 81.44 minutes; $35.14\times$ speedup from 5-flip motor synergies on `uf100-01`, saving 65.10 minutes; and $688.68\times$ speedup on `satisfiable_50_218` down to 2.43 s).
2. **Connectome Scope Isolation (23,214 Core Sub-Circuit vs. Whole Brain):** We show that simulating the unconstrained whole brain (139,255 neurons) is unnecessary. Isolating an interpretable 23,214-neuron foraging and steering core (while leaving 116,041 peripheral neurons dormant) preserves a 100% empirical solution rate while reducing memory residency by 86.1% and accelerating execution speed from 42 steps/s to over 1,200 steps/s.
3. **3D Visual Spatial Repulsion Memory & Limit-Cycle Escape Mechanics:** We demonstrate that 456 optic projection neurons (`enable_vision`) encode visited local minima peaks and valleys into a decaying 3D repulsive potential field, while central complex heading saccades break periodic limit-cycle tori.
4. **Superiority Over Classical Greedy Multi-Restart Search on Structured Verification:** On structured verification benchmarks (`1sp.cnf`, $N=75, M=271$), classical `greedy_only` local search fails after 2,000,371 steps and 1,696 random restarts (`BestUnsat = 1`), whereas Full TIMO tunnels directly to `unsat = 0` in 7,200 steps (29.18 s — $277.83\times$ fewer steps).

This manuscript is original work and is not under consideration for publication elsewhere. All 110 run logs, processed connectome graphs, and analysis scripts are archived in the accompanying Source Data package (`submission_data_package/`), and custom simulation code is available to editors and reviewers upon request (with public release under the MIT License upon formal publication).

Thank you for your consideration of our work.

Sincerely,

**Hussam Gad-Allah**  
Advanced Autonomous Oncology & Neuromorphic Computing Laboratory  
Faculty of Computers & Artificial Intelligence, Cairo University / CAPU, Giza, Egypt  
Emails: 12422023437409@pg.cu.edu.eg, hossamhassanahmed140@fcba.capu.edu.eg  
ORCID: https://orcid.org/0009-0002-6823-2951  

---

## 2. Executive Summary of Wall-Clock Runtime & Speedup Metrics (110 Runs)

| Metric / Comparison Dimension | Without Bio-Skills / Baseline | With Bio-Skills (Full TIMO) | Net Improvement / Speedup |
| :--- | :---: | :---: | :---: |
| **Overall Solve Rate (Stages 0–1 vs. Stages 6–7)** | **0.0%** (`0/18` SNN runs solved) | **100.0%** (`10/10` UF100, `5/5` Structured) | **+100.0% solve rate** |
| **`satisfiable_20_known` Wall Time** | 179.44 s (`[012]` timeout) / 140.41 s (`[017]`) | **49.82 s** (`[023]` `+food_patch_descent`) | **$3.60\times$ / $2.82\times$ faster** |
| **`satisfiable_50_218` Wall Time** | 235.82 s (`A03` timeout) / 1,673.50 s (`[018]`) | **2.43 s** (`[095]` Full TIMO + `5-Flip`) | **$688.68\times$ faster** (saved 27.85 min) |
| **`uf50-02.cnf` Wall Time (Stagnant Eviction)** | 5,521.81 s [92.03 min] (`[026]` timeout) | **635.24 s [10.59 min]** (`[030]` `+refresh_best`) | **$8.69\times$ faster** (saved 81.44 min) |
| **`uf100-01.cnf` Wall Time (`5-Flip` Synergy)** | 4,020.20 s [67.00 min] (`[054]` timeout) | **114.40 s [1.91 min]** (`[055]` `+synergy_5flip`) | **$35.14\times$ faster** (saved 65.10 min) |
| **`uf100-04.cnf` Wall Time (Vision + `5-Flip`)** | 4,357.54 s [72.63 min] (`[070]` timeout) | **760.27 s [12.67 min]** (`[080]` Full TIMO) | **$5.73\times$ faster** (saved 59.95 min) |
| **`uf100-05.cnf` Wall Time (Vision + `5-Flip`)** | 996.47 s [16.61 min] (`[071]` stalled) | **41.09 s [0.68 min]** (`[081]` Full TIMO) | **$24.25\times$ faster** (saved 15.92 min) |
| **`uf100-06.cnf` Fastest UF100 Solve** | Unsolved without `9-Flip` | **4.57 s [0.08 min]** (`[082]`, 1,000 steps) | **Fastest 100-var phase-boundary solve** |
| **`1sp.cnf` Structured Verification** | `greedy_only` **FAILED** (2,000,371 steps, 1,696 restarts) | **SOLVED in 29.18 s** (`[092]`, 7,200 steps) | **$277.83\times$ fewer steps** |
