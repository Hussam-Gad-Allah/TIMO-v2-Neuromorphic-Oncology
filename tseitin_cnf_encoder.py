"""
Tseitin 3-CNF Encoder for Biological Boolean Networks (Dubrova & Teslenko, 2011).
Translates arbitrary Boolean gene regulatory equations into equisatisfiable 3-CNF formulas
with auxiliary Tseitin variables and drug intervention control switches.
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple


class TseitinCNFEncoder:
    def __init__(self, model_dict: Dict):
        self.model_name = model_dict["name"]
        self.raw_rules = model_dict["rules"]
        self.stimuli = model_dict.get("stimuli", [])
        self.druggable_targets = model_dict.get("drug_targets", [])
        self.phenotypes = model_dict.get("phenotypes", {})

        self.var_to_id: Dict[str, int] = {}
        self.id_to_var: Dict[int, str] = {}
        self.var_roles: Dict[str, str] = {}
        self.clauses: List[List[int]] = []
        self._next_var_id = 1

    def _get_or_create_var(self, name: str, role: str = "gene") -> int:
        if name not in self.var_to_id:
            vid = self._next_var_id
            self._next_var_id += 1
            self.var_to_id[name] = vid
            self.id_to_var[vid] = name
            self.var_roles[name] = role
        return self.var_to_id[name]

    def _tseitin_from_ast(self, node: ast.AST) -> int:
        """Recursively decomposes AST expressions into Tseitin CNF clauses."""
        if isinstance(node, ast.Name):
            return self._get_or_create_var(node.id, role="gene")
        elif isinstance(node, ast.Constant):
            # Boolean constant True/False
            aux_name = f"CONST_{bool(node.value)}"
            aux_id = self._get_or_create_var(aux_name, role="auxiliary")
            if node.value:
                self.clauses.append([aux_id])
            else:
                self.clauses.append([-aux_id])
            return aux_id
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            child_id = self._tseitin_from_ast(node.operand)
            aux_name = f"AUX_NOT_{child_id}"
            aux_id = self._get_or_create_var(aux_name, role="auxiliary")
            # aux <-> not child: (aux or child) and (not aux or not child)
            self.clauses.append([aux_id, child_id])
            self.clauses.append([-aux_id, -child_id])
            return aux_id
        elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
            child_ids = [self._tseitin_from_ast(v) for v in node.values]
            curr_id = child_ids[0]
            for next_child in child_ids[1:]:
                aux_name = f"AUX_AND_{curr_id}_{next_child}"
                aux_id = self._get_or_create_var(aux_name, role="auxiliary")
                # aux <-> (c1 and c2): (not aux or c1) and (not aux or c2) and (aux or not c1 or not c2)
                self.clauses.append([-aux_id, curr_id])
                self.clauses.append([-aux_id, next_child])
                self.clauses.append([aux_id, -curr_id, -next_child])
                curr_id = aux_id
            return curr_id
        elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            child_ids = [self._tseitin_from_ast(v) for v in node.values]
            curr_id = child_ids[0]
            for next_child in child_ids[1:]:
                aux_name = f"AUX_OR_{curr_id}_{next_child}"
                aux_id = self._get_or_create_var(aux_name, role="auxiliary")
                # aux <-> (c1 or c2): (aux or not c1) and (aux or not c2) and (not aux or c1 or c2)
                self.clauses.append([aux_id, -curr_id])
                self.clauses.append([aux_id, -next_child])
                self.clauses.append([-aux_id, curr_id, next_child])
                curr_id = aux_id
            return curr_id
        else:
            raise ValueError(f"Unsupported AST node type: {type(node)}")

    def encode(self, pin_curative: bool = True, pin_stimuli: bool = True) -> Tuple[int, int, List[List[int]], Dict]:
        """Performs Tseitin transformation of the gene network into 3-CNF format."""
        self.var_to_id.clear()
        self.id_to_var.clear()
        self.var_roles.clear()
        self.clauses.clear()
        self._next_var_id = 1

        # 1. Pre-register all biological genes
        for gene in self.raw_rules.keys():
            self._get_or_create_var(gene, role="gene")

        # 2. Pre-register drug intervention control switches
        for drug in self.druggable_targets:
            drug_var_name = f"DRUG_INHIB_{drug}"
            self._get_or_create_var(drug_var_name, role="drug")

        # 3. Encode gene regulatory steady-state equations: gene <-> (f_gene and not DRUG_INHIB)
        for gene, rule_str in self.raw_rules.items():
            gene_id = self.var_to_id[gene]
            parsed_expr = ast.parse(rule_str.strip(), mode="eval").body
            f_gene_id = self._tseitin_from_ast(parsed_expr)

            if gene in self.druggable_targets:
                drug_id = self.var_to_id[f"DRUG_INHIB_{gene}"]
                # Effective target: eff <-> (f_gene and not drug_id)
                # gene <-> (f_gene and not drug_id)
                # (not gene or f_gene) and (not gene or not drug_id) and (gene or not f_gene or drug_id)
                self.clauses.append([-gene_id, f_gene_id])
                self.clauses.append([-gene_id, -drug_id])
                self.clauses.append([gene_id, -f_gene_id, drug_id])
            else:
                # Undruggable gene: gene <-> f_gene
                # (not gene or f_gene) and (gene or not f_gene)
                self.clauses.append([-gene_id, f_gene_id])
                self.clauses.append([gene_id, -f_gene_id])

        # 4. Pinned variables
        pinned_map = {}
        if pin_stimuli:
            for s in self.stimuli:
                if s in self.var_to_id:
                    sid = self.var_to_id[s]
                    self.clauses.append([sid])  # Stimulus must be active (1)
                    self.var_roles[s] = "pinned_stimulus"
                    pinned_map[s] = 1

        if pin_curative:
            curative = self.phenotypes.get("curative_state", {})
            for target_gene, target_val in curative.items():
                if target_gene in self.var_to_id:
                    gid = self.var_to_id[target_gene]
                    if target_val == 1:
                        self.clauses.append([gid])
                    else:
                        self.clauses.append([-gid])
                    self.var_roles[target_gene] = "pinned_target"
                    pinned_map[target_gene] = target_val

        meta_mapping = {
            "model_name": self.model_name,
            "n_vars": len(self.var_to_id),
            "n_clauses": len(self.clauses),
            "var_to_id": self.var_to_id,
            "id_to_var": {int(k): v for k, v in self.id_to_var.items()},
            "var_roles": self.var_roles,
            "pinned_variables": pinned_map,
            "druggable_variables": [f"DRUG_INHIB_{d}" for d in self.druggable_targets],
            "gene_variables": list(self.raw_rules.keys())
        }

        return len(self.var_to_id), len(self.clauses), self.clauses, meta_mapping

    def export_dimacs(self, cnf_path: Path, mapping_path: Path = None):
        """Exports the CNF formula in standard DIMACS format."""
        n_vars, n_clauses, clauses, meta = self.encode()

        cnf_path = Path(cnf_path)
        cnf_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            f"c Biomedical 3-SAT Oncology Benchmark: {self.model_name}",
            f"c Encoded via Dubrova & Teslenko (2011) Tseitin Transformation",
            f"p cnf {n_vars} {n_clauses}"
        ]
        for c in clauses:
            lines.append(" ".join(str(lit) for lit in c) + " 0")

        with open(cnf_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        if mapping_path is None:
            mapping_path = cnf_path.with_suffix(".mapping.json")

        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        print(f"[TseitinEncoder] Exported {cnf_path.name}: {n_vars} variables, {n_clauses} clauses")
        print(f"[TseitinEncoder] Mapping saved to {mapping_path.name}")
        return cnf_path, mapping_path


if __name__ == "__main__":
    from flyfly_oncology.dataset_downloader import load_model
    t_lgl = load_model("t_lgl")
    encoder = TseitinCNFEncoder(t_lgl)
    out_dir = Path(__file__).resolve().parent / "data" / "cnf_encoded"
    encoder.export_dimacs(out_dir / "t_lgl_leukemia.cnf")

    aml = load_model("aml")
    encoder_aml = TseitinCNFEncoder(aml)
    encoder_aml.export_dimacs(out_dir / "aml_leukemia.cnf")
