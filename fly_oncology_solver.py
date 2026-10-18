"""
Fly Oncology Solver (Closed-Loop Neuromorphic Oncology Engine).
Independent model coupling the Drosophila FlyWire whole-brain connectome SNN
with biomedical cancer Boolean networks (3-SAT) and in-loop asynchronous temporal validation.
"""

import itertools
import json
import os
import time
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import torch

from flyfly_oncology.temporal_cell_simulator import TemporalCellSimulator, WET_LAB_GROUND_TRUTH
from flyfly_oncology.telemetry_logger import OncologyTelemetryLogger

# === Biological Connectome Parameters (Shiu et al. 2024, Groschner et al. 2018) ===
V_REST = -52.0
V_RESET = -52.0
V_TH = -45.0
TAU_M = 20.0
TAU_S = 5.0
W_SYN = 0.275
T_REFRACTORY = 2.2
DELAY_MS = 1.8
TAU_REC = 400.0
U_SE = 0.15


class FlyBrainSNN:
    """Leaky Integrate-and-Fire Simulator with Tsodyks-Markram Short-Term Plasticity."""
    def __init__(self, crow: torch.Tensor, col: torch.Tensor, values: torch.Tensor, N: int, dt: float = 1.0, device: str = "cuda"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.dt = dt
        self.N = N
        self.delay_steps = max(1, int(DELAY_MS / dt))
        self.refractory_steps = max(1, int(T_REFRACTORY / dt))

        crow_32 = crow.to(device=self.device, dtype=torch.int32)
        col_32 = col.to(device=self.device, dtype=torch.int32)
        val_f = (values.to(device=self.device, dtype=torch.float32) * W_SYN)

        self.W = torch.sparse_csr_tensor(crow_32, col_32, val_f, size=(N, N), device=self.device)

        self.v = torch.full((N, 1), V_REST, device=self.device, dtype=torch.float32)
        self.i_syn = torch.zeros((N, 1), device=self.device, dtype=torch.float32)
        self.vesicles = torch.ones((N, 1), device=self.device, dtype=torch.float32)
        self.spike_buffer = torch.zeros((self.delay_steps, N, 1), device=self.device, dtype=torch.float32)
        self.buffer_idx = 0
        self.refractory_time = torch.zeros((N, 1), device=self.device, dtype=torch.int32)

        self.alpha_m = float(np.exp(-dt / TAU_M))
        self.alpha_s = float(np.exp(-dt / TAU_S))
        self.alpha_rec = float(np.exp(-dt / TAU_REC))

    def reset_state(self):
        self.v.fill_(V_REST)
        self.i_syn.fill_(0.0)
        self.vesicles.fill_(1.0)
        self.spike_buffer.fill_(0.0)
        self.refractory_time.fill_(0)
        self.buffer_idx = 0

    def step(self, external_current: Optional[torch.Tensor] = None, dopamine: float = 0.0) -> torch.Tensor:
        self.i_syn = self.i_syn * self.alpha_s
        delayed_spikes = self.spike_buffer[self.buffer_idx] * self.vesicles
        synaptic_input = torch.sparse.mm(self.W, delayed_spikes)
        self.i_syn += synaptic_input

        self.v = V_REST + (self.v - V_REST) * self.alpha_m
        total_input = self.i_syn
        if external_current is not None:
            total_input += external_current

        active_mask = (self.refractory_time == 0)
        self.v += total_input * active_mask

        spikes = (self.v >= V_TH) & active_mask
        self.v[spikes] = V_RESET
        self.refractory_time[spikes] = self.refractory_steps
        self.refractory_time = torch.clamp(self.refractory_time - 1, min=0)

        self.vesicles = torch.where(spikes, self.vesicles * (1.0 - U_SE), self.vesicles)
        self.vesicles = 1.0 + (self.vesicles - 1.0) * self.alpha_rec

        self.spike_buffer[self.buffer_idx] = spikes.float()
        self.buffer_idx = (self.buffer_idx + 1) % self.delay_steps
        return spikes


class OncologyClauseEvaluator:
    """GPU-Vectorized Clause Evaluator with Dynamic Blocking Clause Feedback."""
    def __init__(self, clauses: List[List[int]], n_vars: int, device: torch.device):
        self.device = device
        self.n_vars = n_vars
        self.clauses_list = [list(c) for c in clauses]
        self._rebuild_tensors()

    def _rebuild_tensors(self):
        C = len(self.clauses_list)
        K = max(len(c) for c in self.clauses_list)
        idx = np.zeros((C, K), dtype=np.int64)
        pos = np.zeros((C, K), dtype=bool)
        valid = np.zeros((C, K), dtype=bool)
        for i, clause in enumerate(self.clauses_list):
            for j, lit in enumerate(clause):
                idx[i, j] = abs(lit) - 1
                pos[i, j] = (lit > 0)
                valid[i, j] = True

        self.idx = torch.tensor(idx, device=self.device)
        self.pos = torch.tensor(pos, device=self.device)
        self.valid = torch.tensor(valid, device=self.device)
        self.n_clauses = C

        # Co-occurrence matrix for receptive field expansions
        co = torch.zeros((self.n_vars, self.n_vars), device=self.device, dtype=torch.int32)
        for clause in self.clauses_list:
            cvars = [abs(lit) - 1 for lit in clause]
            for v1 in cvars:
                for v2 in cvars:
                    if v1 != v2:
                        co[v1, v2] += 1
        self.co_occur = co
        deg = co.float().sum(dim=1, keepdim=True).clamp(min=1.0)
        self.adj_norm = (co.float() / deg).to(self.device)

    def add_blocking_clause(self, clause: List[int]):
        """Dynamically appends a No-Good Blocking Clause to immediately invalidate a rejected drug state."""
        self.clauses_list.append(clause)
        self._rebuild_tensors()

    def sat_mask(self, assignment: torch.Tensor) -> torch.Tensor:
        a = assignment[self.idx]
        lit_true = torch.where(self.pos, a == 1.0, a == 0.0) & self.valid
        return lit_true.any(dim=1)

    def unsat_count(self, assignment: torch.Tensor) -> int:
        return int(self.n_clauses - self.sat_mask(assignment).sum().item())

    def unsat_vars(self, assignment: torch.Tensor) -> List[int]:
        bad = ~self.sat_mask(assignment)
        if not bool(bad.any().item()):
            return []
        v = self.idx[bad][self.valid[bad]]
        return torch.unique(v).tolist()

    def neighbor_unsat_counts(self, assignment: torch.Tensor) -> torch.Tensor:
        V = assignment.numel()
        batch = assignment.unsqueeze(0).repeat(V, 1)
        ar = torch.arange(V, device=assignment.device)
        batch[ar, ar] = 1.0 - batch[ar, ar]
        a = batch[:, self.idx]
        lit_true = torch.where(self.pos.unsqueeze(0), a == 1.0, a == 0.0) & self.valid.unsqueeze(0)
        sat = lit_true.any(dim=2)
        return self.n_clauses - sat.sum(dim=1)


def greedy_descent(evaluator: OncologyClauseEvaluator, assignment: torch.Tensor, pinned_mask: torch.Tensor, druggable_indices: Optional[torch.Tensor] = None, max_drugs: int = 3, max_flips: int = 50):
    """Steepest-descent 1-flip local search strictly constrained by pinned_mask and clinical drug sparsity."""
    cur = evaluator.unsat_count(assignment)
    flips = 0
    while cur > 0 and flips < max_flips:
        counts = evaluator.neighbor_unsat_counts(assignment).clone().float()
        counts[pinned_mask] = evaluator.n_clauses + 9999.0
        if druggable_indices is not None and len(druggable_indices) > 0:
            active_drugs = (assignment[druggable_indices] == 1.0).sum().item()
            if active_drugs >= max_drugs:
                inactive_drugs = druggable_indices[assignment[druggable_indices] == 0.0]
                counts[inactive_drugs] = evaluator.n_clauses + 9999.0
        best_idx = int(torch.argmin(counts).item())
        best_val = int(counts[best_idx].item())
        if best_val < cur:
            assignment = assignment.clone()
            assignment[best_idx] = 1.0 - assignment[best_idx]
            cur = best_val
            flips += 1
        else:
            break
    return assignment, cur, flips


@dataclass
class OncologySolverConfig:
    max_steps: int = 200000
    seed: int = 42
    window_size: int = 3
    flip_ratio: float = 0.20
    max_cpg: float = 150.0
    min_base_cpg: float = 50.0
    pool_size: int = 5
    patience_critical: int = 3000
    patience_mid: int = 6000
    patience_far: int = 3000
    shock_after: int = 3
    enable_gaba: bool = True
    enable_clause_weights: bool = True
    enable_synergy_flips: bool = True
    enable_octopamine: bool = True
    gaba_decay: float = 0.998
    gaba_gain_coeff: float = 0.6
    weight_update_interval: int = 300
    octopamine_patience: int = 8000
    max_allowed_drugs: int = 3
    target_apoptosis: float = 90.0  # 90.0 for clinical remission, 100.0 for complete eradication
    validation_noise: float = 0.02  # Asynchronous stochastic perturbation probability (Garg 2008, Saadatpour 2011)
    multi_solution: bool = False
    max_solutions: int = 1


SNNConfig = OncologySolverConfig


class FlyOncologySolver:
    def __init__(
        self,
        cnf_path: Path,
        mapping_path: Optional[Path] = None,
        model_dict: Optional[Dict] = None,
        graph_path: Optional[Path] = None,
        cfg: Optional[OncologySolverConfig] = None,
        logger: Optional[OncologyTelemetryLogger] = None,
        pinned_vars: Optional[Dict] = None,
        resume_checkpoint: Optional[Dict] = None,
        resume_checkpoint_path: Optional[Path] = None
    ):
        self.cnf_path = Path(cnf_path)
        if mapping_path is None:
            mapping_path = Path(str(cnf_path).replace(".cnf", ".mapping.json"))
        self.mapping_path = Path(mapping_path)

        if graph_path is None:
            graph_path = Path("flyfly_sat/data/processed/graph_core.pt")
        self.graph_path = Path(graph_path)

        self.model_dict = model_dict
        self.cfg = cfg if cfg is not None else OncologySolverConfig()

        if logger is None:
            run_name = model_dict.get("name", "OncologyModel").replace(" ", "_") if model_dict else "OncologyRun"
            self.logger = OncologyTelemetryLogger(run_name=run_name)
        else:
            self.logger = logger

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.resume_checkpoint = resume_checkpoint
        self.resume_checkpoint_path = resume_checkpoint_path

        # 1. Load CNF metadata and mapping (with automatic synthetic mapping for general CNFs)
        if self.mapping_path.exists():
            with open(self.mapping_path, "r", encoding="utf-8") as f:
                self.mapping = json.load(f)
            self.n_vars = self.mapping["n_vars"]
            self.id_to_var = {int(k): v for k, v in self.mapping["id_to_var"].items()}
            self.var_to_id = self.mapping["var_to_id"]
            self.var_roles = self.mapping.get("var_roles", {})
            self.pinned_vars = dict(self.mapping.get("pinned_variables", {}))
            self.druggable_vars = set(self.mapping.get("druggable_variables", []))
        else:
            # Automatic generic mapping for arbitrary DIMACS CNF files
            max_v = 0
            with open(self.cnf_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("c"):
                        continue
                    if line.startswith("p"):
                        parts = line.split()
                        if len(parts) >= 3 and parts[2].isdigit():
                            max_v = max(max_v, int(parts[2]))
                        continue
                    c = [int(x) for x in line.split() if int(x) != 0]
                    for lit in c:
                        max_v = max(max_v, abs(lit))
            self.n_vars = max_v
            self.id_to_var = {i: f"x{i}" for i in range(1, max_v + 1)}
            self.var_to_id = {f"x{i}": i for i in range(1, max_v + 1)}
            self.var_roles = {f"x{i}": "boolean_var" for i in range(1, max_v + 1)}
            self.pinned_vars = {}
            self.druggable_vars = set()
            self.mapping = {
                "n_vars": self.n_vars,
                "id_to_var": self.id_to_var,
                "var_to_id": self.var_to_id,
                "var_roles": self.var_roles,
                "pinned_variables": {},
                "druggable_variables": []
            }

        if pinned_vars is not None:
            self.pinned_vars.update(pinned_vars)

        self.is_pure_sat = (model_dict is None or not model_dict.get("rules")) and (len(self.druggable_vars) == 0)

        # 2. Parse CNF clauses
        clauses = []
        with open(self.cnf_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("c") or line.startswith("p"):
                    continue
                c = [int(x) for x in line.split() if int(x) != 0]
                if c:
                    clauses.append(c)

        self.ev = OncologyClauseEvaluator(clauses, self.n_vars, self.device)
        self.n_clauses = self.ev.n_clauses
        self.initial_n_clauses = self.n_clauses

        # 3. Load FlyWire Connectome Subgraph (Read-Only)
        print(f"[FlyOncologySolver] Loading connectome graph from: {self.graph_path}...")
        graph_data = torch.load(self.graph_path, map_location="cpu", weights_only=False)
        self.root_ids = graph_data["root_ids"]
        self.N = len(self.root_ids)
        crow = graph_data["crow"]
        col = graph_data["col"]
        val = graph_data["val"]
        annot_groups = np.asarray(graph_data.get("annot_group", []))

        self.sensory_candidates = np.where(annot_groups == "olfactory")[0]
        MOTOR_GROUPS = ("descending", "brain_motor_neuron", "neck_motor_neuron", "motor")
        self.motor_candidates = np.where(np.isin(annot_groups, MOTOR_GROUPS))[0]

        print(f"[FlyOncologySolver] Connectome: N={self.N:,} | Sensory ORNs={len(self.sensory_candidates):,} | Motor={len(self.motor_candidates):,}")
        self.brain = FlyBrainSNN(crow, col, val, self.N, dt=1.0, device=str(self.device))

        # 4. Asynchronous Temporal Cell Validator
        if not self.is_pure_sat and self.model_dict:
            patient_model = dict(self.model_dict)
            active_pinned = [
                k for k, v in self.pinned_vars.items()
                if v == 1 and k not in ("Apoptosis", "Proliferation")
            ]
            if active_pinned:
                patient_model["stimuli"] = active_pinned
            self.temporal_validator = TemporalCellSimulator(patient_model)
        else:
            self.temporal_validator = None

        # 5. Pinned Variables Mask (Disease stimuli & clinical target Apoptosis=1, Prolif=0)
        self.pinned_mask = torch.zeros(self.n_vars, device=self.device, dtype=torch.bool)
        self.pinned_values = torch.zeros(self.n_vars, device=self.device, dtype=torch.float32)
        for var_name, pin_val in self.pinned_vars.items():
            if var_name in self.var_to_id:
                vid = self.var_to_id[var_name] - 1
                self.pinned_mask[vid] = True
                self.pinned_values[vid] = float(pin_val)

        # Druggable variable indices
        self.druggable_indices = torch.tensor(
            [self.var_to_id[d] - 1 for d in self.druggable_vars if d in self.var_to_id],
            device=self.device, dtype=torch.long
        )

        self.rng = np.random.default_rng(self.cfg.seed)
        torch.manual_seed(self.cfg.seed)
        self._init_solver_state()

        # Restore from checkpoint if specified
        if self.resume_checkpoint is not None:
            self.restore_checkpoint(self.resume_checkpoint)
        elif self.resume_checkpoint_path is not None:
            self.restore_checkpoint(self.resume_checkpoint_path)

    def _init_solver_state(self):
        V, cfg = self.n_vars, self.cfg
        self.brain.reset_state()

        # Allocate Neuromuscular Pools
        max_p_motor = max(1, len(self.motor_candidates) // V)
        max_p_sensory = max(1, len(self.sensory_candidates) // V)
        self.P = min(cfg.pool_size, max_p_motor, max_p_sensory)
        P = self.P

        sens_picks = self.rng.choice(self.sensory_candidates, V * P, replace=False)
        self.sensory = torch.tensor(sens_picks, device=self.device, dtype=torch.long)

        motor_picks = self.rng.choice(self.motor_candidates, V * P, replace=False)
        self.motor_pools = torch.tensor(motor_picks, device=self.device, dtype=torch.long).view(V, P)

        # Initial Assignment: Random, but strictly enforcing Pinned Disease State
        self.assignment = torch.randint(0, 2, (V,), device=self.device, dtype=torch.float32)
        self.assignment[self.pinned_mask] = self.pinned_values[self.pinned_mask]

        # Initially zero all drug intervention switches
        if len(self.druggable_indices) > 0:
            self.assignment[self.druggable_indices] = 0.0

        self.motor_hist = torch.zeros((V, cfg.window_size), device=self.device)
        self.last_flip_step = torch.full((V,), -999999, device=self.device, dtype=torch.long)
        self.flips_total = torch.zeros(V, device=self.device, dtype=torch.long)

        self.best_unsat = self.ev.unsat_count(self.assignment)
        self.best_assignment = self.assignment.clone()
        self.last_best_step = 0
        self.start_step = 0
        self.last_switch_step = 0
        self.failures = 0
        self.blocking_clauses_count = 0
        self.synergies_count = 0
        self.blocking_clauses_history = []
        self.synergy_flips_history = []
        self.evaluated_drug_sets = set()

    def save_checkpoint(self, step: int, status: str = "running"):
        """Save atomic checkpoint containing full search state, assignments, and blocking clauses."""
        active_drugs = self._get_active_drugs(self.assignment)
        cur_u = int(self.ev.unsat_count(self.assignment))
        ck_json = {
            "step": int(step),
            "status": status,
            "best_unsat": int(self.best_unsat),
            "cur_unsat": cur_u,
            "last_best_step": int(self.last_best_step),
            "failures": int(self.failures),
            "blocking_clauses_count": int(self.blocking_clauses_count),
            "synergies_count": int(self.synergies_count),
            "assignment": self.assignment.cpu().int().tolist(),
            "best_assignment": self.best_assignment.cpu().int().tolist(),
            "active_drugs": active_drugs,
            "blocking_clauses": [list(c) for c in self.ev.clauses_list[self.initial_n_clauses:]],
            "evaluated_drug_sets": [list(d) for d in self.evaluated_drug_sets],
            "blocking_history": self.blocking_clauses_history,
            "synergy_history": self.synergy_flips_history,
            "cnf_path": str(self.cnf_path),
            "mapping_path": str(self.mapping_path) if self.mapping_path and self.mapping_path.exists() else None,
            "model_name": self.model_dict.get("name") if self.model_dict else "Pure SAT / Custom Benchmark",
            "seed": self.cfg.seed,
            "noise_percent": getattr(self.logger, "noise_percent", 2.0),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if hasattr(self.logger, "save_checkpoint"):
            self.logger.save_checkpoint(ck_json)

        ck_pt = {
            "step": int(step),
            "status": status,
            "assignment": self.assignment.cpu(),
            "best_assignment": self.best_assignment.cpu(),
            "best_unsat": int(self.best_unsat),
            "motor_pools": self.motor_pools.cpu(),
            "sensory": self.sensory.cpu(),
            "motor_hist": self.motor_hist.cpu(),
            "last_flip_step": self.last_flip_step.cpu(),
            "flips_total": self.flips_total.cpu(),
            "brain": {
                "v": self.brain.v.cpu(),
                "i_syn": self.brain.i_syn.cpu(),
                "vesicles": self.brain.vesicles.cpu(),
                "spike_buffer": self.brain.spike_buffer.cpu(),
                "refractory_time": self.brain.refractory_time.cpu(),
                "buffer_idx": self.brain.buffer_idx
            }
        }
        if hasattr(self.logger, "save_checkpoint_pt"):
            self.logger.save_checkpoint_pt(ck_pt)

    def restore_checkpoint(self, ck_source):
        """Restore solver state from a checkpoint dictionary or file path."""
        ck_data = ck_source
        pt_path = None
        if isinstance(ck_source, (str, Path)):
            p = Path(ck_source)
            if p.is_dir():
                if (p / "checkpoint.json").exists():
                    with open(p / "checkpoint.json", "r", encoding="utf-8") as f:
                        ck_data = json.load(f)
                pt_path = p / "checkpoint.pt"
            elif p.suffix == ".json" and p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    ck_data = json.load(f)
                pt_path = p.with_suffix(".pt")
            elif p.suffix == ".pt" and p.exists():
                pt_path = p
                ck_data = {}

        if not isinstance(ck_data, dict):
            return

        if pt_path is None and hasattr(self, "logger") and getattr(self.logger, "checkpoint_pt_path", None):
            if self.logger.checkpoint_pt_path.exists():
                pt_path = self.logger.checkpoint_pt_path

        if "assignment" in ck_data:
            self.assignment = torch.tensor(ck_data["assignment"], device=self.device, dtype=torch.float32)
        if "best_assignment" in ck_data:
            self.best_assignment = torch.tensor(ck_data["best_assignment"], device=self.device, dtype=torch.float32)
        elif "assignment" in ck_data:
            self.best_assignment = self.assignment.clone()

        self.best_unsat = int(ck_data.get("best_unsat", self.ev.unsat_count(self.assignment)))
        self.start_step = int(ck_data.get("step", 0)) + 1
        self.last_best_step = int(ck_data.get("last_best_step", self.start_step))
        self.failures = int(ck_data.get("failures", 0))

        # Restore dynamic blocking clauses
        saved_blocking = ck_data.get("blocking_clauses", [])
        for c in saved_blocking:
            self.ev.add_blocking_clause(c)
        self.blocking_clauses_count = len(saved_blocking)

        # Restore evaluated combinations
        saved_evaluated = ck_data.get("evaluated_drug_sets", [])
        self.evaluated_drug_sets = set(tuple(sorted(d)) for d in saved_evaluated)

        self.blocking_clauses_history = ck_data.get("blocking_history", [])
        self.synergy_flips_history = ck_data.get("synergy_history", [])

        # Restore torch tensors if available
        if pt_path and pt_path.exists():
            try:
                pt_data = torch.load(pt_path, map_location=self.device, weights_only=False)
                if "assignment" in pt_data and "assignment" not in ck_data:
                    self.assignment = pt_data["assignment"].to(self.device).float()
                if "best_assignment" in pt_data and "best_assignment" not in ck_data:
                    self.best_assignment = pt_data["best_assignment"].to(self.device).float()
                if "motor_pools" in pt_data:
                    self.motor_pools = pt_data["motor_pools"].to(self.device)
                if "sensory" in pt_data:
                    self.sensory = pt_data["sensory"].to(self.device)
                if "motor_hist" in pt_data:
                    self.motor_hist = pt_data["motor_hist"].to(self.device)
                if "last_flip_step" in pt_data:
                    self.last_flip_step = pt_data["last_flip_step"].to(self.device)
                if "flips_total" in pt_data:
                    self.flips_total = pt_data["flips_total"].to(self.device)
                if "brain" in pt_data:
                    b = pt_data["brain"]
                    self.brain.v.copy_(b["v"].to(self.device))
                    self.brain.i_syn.copy_(b["i_syn"].to(self.device))
                    self.brain.vesicles.copy_(b["vesicles"].to(self.device))
                    self.brain.spike_buffer.copy_(b["spike_buffer"].to(self.device))
                    self.brain.refractory_time.copy_(b["refractory_time"].to(self.device))
                    self.brain.buffer_idx = b["buffer_idx"]
            except Exception as e:
                print(f"[FlyOncologySolver] Warning loading torch checkpoint: {e}")

        cur_unsat = self.ev.unsat_count(self.assignment)
        active_drugs = self._get_active_drugs(self.assignment)
        print(f"\n[+] CHECKPOINT RESTORED: Resuming from Step {self.start_step:,}!")
        print(f"    Best UNSAT: {self.best_unsat} | Current UNSAT: {cur_unsat}")
        print(f"    Active Target(s): {active_drugs or 'None'} | Blocking Clauses: {self.blocking_clauses_count}")
        print(f"    Evaluated Combinations: {len(self.evaluated_drug_sets)} prior tests cached\n")

    def _get_active_drugs(self, assignment: torch.Tensor) -> List[str]:
        drugs = []
        for d in self.druggable_vars:
            vid = self.var_to_id[d] - 1
            if assignment[vid].item() == 1.0:
                drugs.append(d.replace("DRUG_INHIB_", ""))
        return sorted(drugs)

    def run(self) -> Dict:
        return self._execute_solve()

    def solve(self) -> Dict:
        return self._execute_solve()

    def _execute_solve(self) -> Dict:
        cfg = self.cfg
        brain = self.brain
        V, P = self.n_vars, self.P
        t0 = time.time()

        # Log manifest
        sensory_rids = [int(self.root_ids[idx].item()) for idx in self.sensory.cpu().tolist()]
        motor_rids = [int(self.root_ids[idx].item()) for idx in self.motor_pools.view(-1).cpu().tolist()]
        manifest_data = {
            "model_name": self.model_dict["name"] if self.model_dict else "Pure SAT / Custom Benchmark",
            "cnf_path": str(self.cnf_path),
            "n_vars": self.n_vars,
            "n_clauses": self.ev.n_clauses,
            "n_neurons": self.N,
            "P_pool_size": self.P,
            "sensory_root_ids_sample": sensory_rids[:20],
            "motor_root_ids_sample": motor_rids[:20],
            "total_sensory_neurons": len(sensory_rids),
            "total_motor_neurons": len(motor_rids),
            "biological_constants": {
                "V_REST": V_REST, "V_RESET": V_RESET, "V_TH": V_TH,
                "TAU_M": TAU_M, "TAU_S": TAU_S, "W_SYN": W_SYN,
                "T_REFRACTORY": T_REFRACTORY, "DELAY_MS": DELAY_MS,
                "TAU_REC": TAU_REC, "U_SE": U_SE
            },
            "pinned_variables": self.pinned_vars,
            "druggable_variables": list(self.druggable_vars),
            "config": asdict(cfg)
        }
        self.logger.log_manifest(manifest_data)

        gaba_conc = torch.zeros(V, device=self.device, dtype=torch.float32)
        clause_weights = torch.ones(self.ev.n_clauses, device=self.device, dtype=torch.float32)
        last_weight_update = 0

        status = "timeout"
        final_verif_report = {}
        total_target_steps = self.start_step + cfg.max_steps
        solved_step = total_target_steps

        model_display = self.model_dict['name'] if self.model_dict else 'Pure SAT / Custom Benchmark'
        print("=" * 70)
        print(f"Virtual Fly SNN Engine | {model_display}")
        print(f"Variables: {V} | Clauses: {self.ev.n_clauses} | Pinned Locked: {int(self.pinned_mask.sum())}")
        if self.start_step > 0:
            print(f"RESUMING from step {self.start_step:,} up to {total_target_steps:,} (+{cfg.max_steps:,} steps)")
        evaluated_drug_sets = self.evaluated_drug_sets

        try:
            for step in range(self.start_step, total_target_steps):
                unsat_count = self.ev.unsat_count(self.assignment)

                if unsat_count < self.best_unsat:
                    self.best_unsat = unsat_count
                    self.best_assignment = self.assignment.clone()
                    self.last_best_step = step
                    self.failures = 0
                    if cfg.enable_gaba:
                        gaba_conc *= 0.5
                    print(f"[Step {step:6d}] New best unsat: {unsat_count} unsatisfied clauses")
                    self.save_checkpoint(step, status="running")

                # Periodic console heartbeat (every 2,000 steps)
                if step > self.start_step and step % 2000 == 0:
                    cur_drugs = self._get_active_drugs(self.assignment)
                    print(f"  [Step {step:7d} / {total_target_steps:,}] cur_unsat: {unsat_count:3d} | best: {self.best_unsat:3d} | drugs: {cur_drugs or 'None'}")

                # Periodic checkpointing (every 5,000 steps)
                if step > self.start_step and step % 5000 == 0:
                    self.save_checkpoint(step, status="running")

                # Pure SAT Termination
                if self.is_pure_sat and unsat_count == 0:
                    status = "sat_solved"
                    solved_step = step
                    self.best_unsat = 0
                    self.best_assignment = self.assignment.clone()
                    print(f"\n    [+] SUCCESS! SATISFIABILITY ACHIEVED (0 unsatisfied clauses) at step {step:,}!\n")
                    self.save_checkpoint(step, status="sat_solved")
                    break

                # --- IN-LOOP ASYNCHRONOUS TEMPORAL VERIFICATION & BLOCKING CLAUSE FEEDBACK ---
                active_drugs = self._get_active_drugs(self.assignment)
                drug_key = tuple(sorted(active_drugs))

                should_validate = False
                if not self.is_pure_sat and self.temporal_validator is not None:
                    if unsat_count == 0:
                        should_validate = True
                    elif 1 <= len(active_drugs) <= cfg.max_allowed_drugs and drug_key not in evaluated_drug_sets:
                        val_thresh = max(40, int(0.125 * self.ev.n_clauses))
                        if unsat_count <= val_thresh and (step % 30 == 0 or unsat_count < self.best_unsat):
                            should_validate = True

                if should_validate:
                    evaluated_drug_sets.add(drug_key)
                    print(f"\n[Step {step:5d}] In-Loop Validation Candidate: {active_drugs} (unsat: {unsat_count})")
                    print(f"    --> Calling Asynchronous Temporal Cell Validator (200 trajectories)...")

                    verif = self.temporal_validator.validate(active_drugs, n_trajectories=200, seed=cfg.seed + step, noise_prob=cfg.validation_noise)
                    verif["step"] = step
                    self.logger.log_verification(verif)

                    if verif["passed_verification"]:
                        if final_verif_report is None or verif.get("apoptosis_rate_noisy", 0.0) > final_verif_report.get("apoptosis_rate_noisy", 0.0):
                            final_verif_report = verif
                            solved_step = step
                            status = "biomedical_verified"

                        is_100_percent = (verif.get("apoptosis_rate_clean", 0.0) >= 90.0 and verif.get("apoptosis_rate_noisy", 0.0) >= 99.0)
                        is_target_met = (verif.get("apoptosis_rate_clean", 0.0) >= 85.0 and (verif.get("apoptosis_rate_noisy", 0.0) >= cfg.target_apoptosis or is_100_percent))

                        if is_target_met:
                            status = "biomedical_verified"
                            final_verif_report = verif
                            solved_step = step
                            badge = "100% COMPLETE ERADICATION" if is_100_percent else f"{verif['apoptosis_rate_noisy']}% CLINICAL REMISSION"
                            print(f"    [+] SUCCESS! Verification PASSED ({badge})")
                            print(f"    [+] Discovered Curative Target(s): {active_drugs}\n")
                            self.logger.log_step({
                                "step": step,
                                "unsat": unsat_count,
                                "best_unsat": self.best_unsat,
                                "dopamine_hunger": round(float(unsat_count / float(self.ev.n_clauses)), 4),
                                "flipped_neurons": 0,
                                "mean_gaba": round(float(gaba_conc.mean().item()), 4),
                                "max_gaba": round(float(gaba_conc.max().item()), 4),
                                "active_drugs": active_drugs,
                                "mean_vesicles": round(float(brain.vesicles.mean().item()), 4),
                                "mean_v": round(float(brain.v.mean().item()), 2),
                                "total_spikes": 0,
                                "blocking_clauses": self.blocking_clauses_count
                            })
                            self.save_checkpoint(step, status="biomedical_verified")
                            break
                        else:
                            print(f"    [i] Candidate {active_drugs} achieved {verif['apoptosis_rate_noisy']}% (Remission). Repelling fly to search for 100% COMPLETE ERADICATION...")
                            blocking_lits = [
                                -self.var_to_id[f"DRUG_INHIB_{d}"]
                                for d in active_drugs
                                if f"DRUG_INHIB_{d}" in self.var_to_id
                            ]
                            if blocking_lits and len(active_drugs) >= cfg.max_allowed_drugs:
                                self.ev.add_blocking_clause(blocking_lits)
                            for d in active_drugs:
                                var_name = f"DRUG_INHIB_{d}"
                                if var_name in self.var_to_id:
                                    vid = self.var_to_id[var_name] - 1
                                    gaba_conc[vid] += 2.0
                    else:
                        # REJECTION: Add Dynamic Blocking Clause to forbid this ineffective combination
                        print(f"    [-] CLOSED-LOOP REJECTION: Ineffective in asynchronous dynamics ({verif['verdict']}, noisy={verif['apoptosis_rate_noisy']}%)")
                        self.blocking_clauses_count += 1

                        # Construct No-Good Clause: only ban supersets if already at max_allowed_drugs
                        blocking_lits = []
                        for d in active_drugs:
                            var_name = f"DRUG_INHIB_{d}"
                            vid = self.var_to_id[var_name]
                            blocking_lits.append(-vid)

                        if not blocking_lits:
                            blocking_lits = [self.var_to_id[d] for d in list(self.druggable_vars)[:3]]

                        if len(active_drugs) >= cfg.max_allowed_drugs:
                            self.ev.add_blocking_clause(blocking_lits)
                            clause_weights = torch.ones(self.ev.n_clauses, device=self.device, dtype=torch.float32)

                        self.blocking_clauses_history.append({
                            "step": step,
                            "candidate_drugs": list(active_drugs),
                            "clause_literals": list(blocking_lits),
                            "verdict": verif.get("verdict"),
                            "apoptosis_rate_clean": verif.get("apoptosis_rate_clean"),
                            "apoptosis_rate_noisy": verif.get("apoptosis_rate_noisy"),
                            "biological_rationale": "Insufficient apoptotic commitment under asynchronous Monte Carlo dynamics"
                        })

                        # Induce localized GABAergic punishment & vesicle depletion on rejected drugs
                        for d in active_drugs:
                            var_name = f"DRUG_INHIB_{d}"
                            vid = self.var_to_id[var_name] - 1
                            if len(active_drugs) >= cfg.max_allowed_drugs:
                                gaba_conc[vid] += 6.0
                                self.last_flip_step[vid] = step
                                self.motor_hist[vid].fill_(-1.0)
                                self.assignment[vid] = 0.0
                            else:
                                gaba_conc[vid] += 1.5

                        # Refresh unsat after adding blocking clause and resetting rejected drug
                        unsat_count = self.ev.unsat_count(self.assignment)
                        print(f"    [-] Dynamic Blocking Clause Added! unsat refreshed to {unsat_count}. GABA punishment engaged.\n")

                stuck_steps = step - self.last_best_step

                # Biological Food-Patch Local Search (Lindsay et al. 2017)
                if (unsat_count <= 10 and step % 20 == 0) or (step % 200 == 0 and stuck_steps > 300):
                    cand_a, cand_u, _ = greedy_descent(
                        self.ev, self.assignment, self.pinned_mask,
                        self.druggable_indices, cfg.max_allowed_drugs
                    )
                    if cand_u < unsat_count:
                        self.assignment = cand_a
                        unsat_count = cand_u
                        if unsat_count < self.best_unsat:
                            self.best_unsat = unsat_count
                            self.best_assignment = self.assignment.clone()
                            self.last_best_step = step
                            print(f"[Step {step:6d}] Food-patch descent: {unsat_count} unsatisfied clauses")

                # Ballistic Saccade / Reset on prolonged stagnation
                if stuck_steps > 2000 and (stuck_steps % 1000 == 0):
                    unpinned_indices = (~self.pinned_mask).nonzero().view(-1)
                    n_saccade = min(4, len(unpinned_indices))
                    saccade_picks = unpinned_indices[torch.randperm(len(unpinned_indices))[:n_saccade]]
                    self.assignment[saccade_picks] = 1.0 - self.assignment[saccade_picks]
                    unsat_count = self.ev.unsat_count(self.assignment)

                # --- SNN Sensory Drive ---
                if cfg.enable_gaba:
                    gaba_conc *= cfg.gaba_decay

                hunger = unsat_count / float(self.ev.n_clauses)
                base_amp = max(cfg.min_base_cpg, cfg.max_cpg * hunger)
                amp = base_amp

                ext = torch.zeros((brain.N, 1), device=self.device)
                n_s = len(self.sensory)
                phases = (step / 3.0) + (torch.arange(n_s, device=self.device) / n_s) * 2.0 * np.pi

                bad_mask = ~self.ev.sat_mask(self.assignment)
                gain = torch.full((V,), 0.05, device=self.device)
                if bad_mask.any():
                    bad_indices = self.ev.idx[bad_mask]
                    bad_valid = self.ev.valid[bad_mask]
                    var_drive = torch.zeros(V, device=self.device, dtype=torch.float32)
                    var_drive.scatter_add_(0, bad_indices[bad_valid], torch.ones_like(bad_indices[bad_valid], dtype=torch.float32))
                    if var_drive.max() > 0:
                        norm_drive = var_drive / var_drive.max()
                        if hasattr(self.ev, 'adj_norm'):
                            diffused = torch.matmul(self.ev.adj_norm.t(), norm_drive)
                            norm_drive = 0.7 * norm_drive + 0.3 * (diffused / (diffused.max() + 1e-5))
                        gain = 0.05 + 0.95 * norm_drive

                if cfg.enable_gaba:
                    gain = gain * (1.0 / (1.0 + cfg.gaba_gain_coeff * gaba_conc))

                # Strictly zero sensory drive for pinned variables
                gain[self.pinned_mask] = 0.0
                # Enhance drive for druggable intervention channels
                gain[self.druggable_indices] *= 1.3

                gain_per_sensory = gain.repeat_interleave(P)
                wave = torch.sin(phases) * (amp * gain_per_sensory)
                ext[self.sensory, 0] += torch.clamp(wave, min=0.0)
                ext += torch.randn((brain.N, 1), device=self.device) * (0.05 + hunger * 0.15)

                # Brain step
                spikes = brain.step(external_current=ext, dopamine=hunger)

                # Motor Readout
                raw = spikes[self.motor_pools.view(-1)].squeeze(-1)
                pool_rate = raw.view(V, P).float().mean(dim=1)
                self.motor_hist[:, step % cfg.window_size] = pool_rate
                rates = self.motor_hist.sum(dim=1)

                if cfg.enable_gaba:
                    rates = rates * (1.0 / (1.0 + cfg.gaba_gain_coeff * gaba_conc))

                # Mask pinned variables so they are NEVER flipped
                rates[self.pinned_mask] = -1.0

                # Clinical Drug Sparsity Constraint: Prevent activating more than max_allowed_drugs
                if len(self.druggable_indices) > 0:
                    active_drug_count = int((self.assignment[self.druggable_indices] == 1.0).sum().item())
                    if active_drug_count >= cfg.max_allowed_drugs:
                        inactive_drugs = self.druggable_indices[self.assignment[self.druggable_indices] == 0.0]
                        rates[inactive_drugs] = -1.0

                eff_flip_ratio = cfg.flip_ratio
                flip_mask = (rates >= (cfg.window_size * eff_flip_ratio)) & (~self.pinned_mask)
                flipped_vars = []

                if flip_mask.any():
                    masked_rates = rates * flip_mask.float()
                    k_probe = min(5, V)
                    top_vals, top_indices = torch.topk(masked_rates, k=k_probe)
                    r1 = top_vals[0].item()

                    # Compound Motor Synergy
                    ratio_thresh = 0.75
                    synergy_cluster = [int(top_indices[i].item()) for i in range(k_probe)
                                       if top_vals[i].item() > 0 and (top_vals[i].item() / r1) >= ratio_thresh
                                       and not self.pinned_mask[int(top_indices[i].item())]]

                    do_synergy = (cfg.enable_synergy_flips and len(synergy_cluster) >= 2 and stuck_steps > 100)

                    if do_synergy:
                        cand_assignment = self.assignment.clone()
                        for c_v in synergy_cluster:
                            cand_assignment[c_v] = 1.0 - cand_assignment[c_v]
                        cand_unsat = self.ev.unsat_count(cand_assignment)
                        if cand_unsat < unsat_count:
                            self.assignment = cand_assignment
                            flipped_vars = synergy_cluster
                            self.synergies_count += 1
                            self.synergy_flips_history.append({
                                "step": step,
                                "cluster_indices": synergy_cluster,
                                "cluster_symbols": [self.id_to_var.get(v+1, f"v_{v+1}") for v in synergy_cluster],
                                "rates": [float(top_vals[i].item()) for i in range(len(synergy_cluster))],
                                "unsat_before": unsat_count,
                                "unsat_after": cand_unsat
                            })
                        else:
                            do_synergy = False

                    if not do_synergy:
                        # Presynaptic Vesicle Depletion & Candidate Exploration
                        refractory_tenure = 8 if unsat_count <= 3 else 5
                        for k_idx in range(k_probe):
                            cand_v = int(top_indices[k_idx].item())
                            if top_vals[k_idx].item() <= 0 or self.pinned_mask[cand_v]:
                                continue

                            cand_assignment = self.assignment.clone()
                            cand_assignment[cand_v] = 1.0 - cand_assignment[cand_v]
                            cand_unsat = self.ev.unsat_count(cand_assignment)
                            is_refractory = (step - self.last_flip_step[cand_v]) < refractory_tenure

                            # Aspiration criterion
                            if cand_unsat < unsat_count:
                                self.assignment = cand_assignment
                                flipped_vars = [cand_v]
                                break
                            elif cand_unsat == unsat_count and not is_refractory:
                                self.assignment = cand_assignment
                                flipped_vars = [cand_v]
                                break
                            else:
                                self.motor_hist[cand_v] = -1.0

                    for v in flipped_vars:
                        self.flips_total[v] += 1
                        self.last_flip_step[v] = step
                        if cfg.enable_gaba:
                            gaba_conc[v] += 1.0
                        self.motor_hist[v].zero_()

                # Logging (high-density sampling for 3D flight trajectory)
                if step % 10 == 0:
                    self.logger.log_step({
                        "step": step,
                        "unsat": unsat_count,
                        "best_unsat": self.best_unsat,
                        "dopamine_hunger": round(float(hunger), 4),
                        "flipped_neurons": len(flipped_vars),
                        "mean_gaba": round(float(gaba_conc.mean().item()), 4),
                        "max_gaba": round(float(gaba_conc.max().item()), 4),
                        "active_drugs": self._get_active_drugs(self.assignment),
                        "mean_vesicles": round(float(brain.vesicles.mean().item()), 4),
                        "mean_v": round(float(brain.v.mean().item()), 2),
                        "total_spikes": int(spikes.sum().item()),
                        "blocking_clauses": self.blocking_clauses_count
                    })

        except KeyboardInterrupt:
            status = "interrupted"
            cur_st = step if 'step' in locals() else self.start_step
            print(f"\n[!] Simulation interrupted by user at step {cur_st:,}!")
            self.save_checkpoint(cur_st, status="interrupted")
        finally:
            cur_st = step if 'step' in locals() else self.start_step
            self.save_checkpoint(cur_st, status=status)

        elapsed = time.time() - t0

        # Extract Gene States (if biological rules exist)
        final_gene_states = {}
        if self.model_dict and "rules" in self.model_dict:
            for g in self.model_dict["rules"].keys():
                if g in self.var_to_id:
                    vid = self.var_to_id[g] - 1
                    final_gene_states[g] = int(self.assignment[vid].item())

        active_drugs = self._get_active_drugs(self.assignment)
        matches = [d for d in active_drugs if d in WET_LAB_GROUND_TRUTH]

        final_steps_taken = solved_step if status in ("biomedical_verified", "sat_solved") else (step if 'step' in locals() else total_target_steps)

        summary = {
            "model_name": self.model_dict["name"] if self.model_dict else "Pure SAT / Custom Benchmark",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "steps_taken": final_steps_taken,
            "best_unsat": int(self.best_unsat),
            "final_unsat": int(unsat_count) if 'unsat_count' in locals() else int(self.best_unsat),
            "elapsed_seconds": round(elapsed, 2),
            "active_drugs": active_drugs,
            "validation_noise": cfg.validation_noise,
            "verification_verdict": final_verif_report.get("verdict", "INCOMPLETE"),
            "apoptosis_rate_clean": final_verif_report.get("apoptosis_rate_clean", 0.0),
            "apoptosis_rate_noisy": final_verif_report.get("apoptosis_rate_noisy", 0.0),
            "proliferation_suppression_rate": final_verif_report.get("proliferation_suppression_rate", 0.0),
            "mean_steps_to_apoptosis": final_verif_report.get("mean_steps_to_apoptosis", 0.0),
            "wet_lab_matches": matches,
            "blocking_clauses_count": self.blocking_clauses_count,
            "synergy_flips_count": self.synergies_count,
            "gene_states": final_gene_states,
            "pre_treatment_states": {g: 1 if g in ("Proliferation", "S1P", "Mcl1", "BclxL") else 0 for g in final_gene_states}
        }

        self.logger.log_synergies_and_blocking_clauses(self.blocking_clauses_history, self.synergy_flips_history)
        self.logger.log_solution(summary)
        if self.model_dict:
            self.logger.generate_executive_report(summary)
        self.logger.close()
        return summary
