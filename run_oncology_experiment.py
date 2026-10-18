"""
Main Oncology Experiment Runner: FlyFly Oncology Champions League Phase.
Couples the Drosophila FlyWire whole-brain connectome SNN with cancer Boolean networks (3-SAT)
and in-loop asynchronous temporal cell validation.
"""

from pathlib import Path
import sys

# Ensure root is on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from run_oncology_experiment import main

if __name__ == "__main__":
    main()
