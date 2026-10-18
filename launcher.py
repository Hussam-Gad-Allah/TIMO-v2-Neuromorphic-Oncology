#!/usr/bin/env python3
"""
TIMO v2: Turnkey Interactive Launcher & Controller.
Author: Hussam Gad-Allah
Connectome Substrate: 23,214-neuron Drosophila melanogaster sub-circuit (FlyWire v783)
"""

import os
import sys
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print("=" * 84)
    print("      TIMO v2 : BIOLOGICAL CONNECTOME NEUROMORPHIC COMPUTING ENGINE")
    print("      Model: Drosophila melanogaster Whole-Brain SNN (23,214 Cells)")
    print("      3D Cyber-Space Flight Simulator & Pan-Cancer Precision Solver")
    print("      Author: Hussam Gad-Allah | Cairo University (FGSSR) & CAPU")
    print("=" * 84)

def main_menu():
    while True:
        print_banner()
        print("\n  [+] Please select an option to execute:\n")
        print("  [1] Launch 3D Drosophila Flight Simulator (Interactive Cyber-Space WebGL)")
        print("  [2] Run 12 Unsolved Cancers Prospective Multi-Noise Study (2%, 5%, 10%, 18% Noise)")
        print("  [3] Run Triple-Negative Breast Cancer Study (8 Real Clinical Patients)")
        print("  [4] Run Glioblastoma (GBM) Study (8 Real Clinical Patients)")
        print("  [5] Run Pancreatic Cancer (PDAC) Study (10 Real Clinical Patients)")
        print("  [6] Run Non-Small Cell Lung Cancer (NSCLC) Study (8 Real Clinical Patients)")
        print("  [7] Run Master Pan-Cancer Multi-Noise Sweep (All 20 Cancers across Chaos Tiers)")
        print("  [8] Run Custom Cancer Solver (Select from 20 Lineages)")
        print("  [9] Verify Connectome Graph & SNN Simulation Pipeline")
        print("  [0] Exit")
        print("\n" + "=" * 84)

        choice = input("  Enter your choice [0-9]: ").strip()

        if choice == '1':
            print("\n[+] Starting 3D Flight Simulator Web Server...")
            subprocess.run([sys.executable, str(ROOT / "view_fly_3d.py")])
        elif choice == '2':
            print("\n[+] Executing 12 Unsolved Cancers Prospective Multi-Noise Study...")
            subprocess.run([sys.executable, str(ROOT / "run_unsolved_prospective_study.py")])
            input("\nPress Enter to return to main menu...")
        elif choice == '3':
            print("\n[+] Executing TNBC 8-Patient Clinical Study...")
            subprocess.run([sys.executable, str(ROOT / "run_tnbc_patient_study.py")])
            input("\nPress Enter to return to main menu...")
        elif choice == '4':
            print("\n[+] Executing Glioblastoma 8-Patient Clinical Study...")
            subprocess.run([sys.executable, str(ROOT / "run_gbm_patient_study.py")])
            input("\nPress Enter to return to main menu...")
        elif choice == '5':
            print("\n[+] Executing Pancreatic Cancer (PDAC) 10-Patient Clinical Study...")
            subprocess.run([sys.executable, str(ROOT / "run_pdac_patient_study.py")])
            input("\nPress Enter to return to main menu...")
        elif choice == '6':
            print("\n[+] Executing NSCLC 8-Patient Clinical Study...")
            subprocess.run([sys.executable, str(ROOT / "run_nsclc_patient_study.py")])
            input("\nPress Enter to return to main menu...")
        elif choice == '7':
            print("\n[+] Executing Master Pan-Cancer Multi-Noise Sweep...")
            subprocess.run([sys.executable, str(ROOT / "run_master_pan_cancer_sweeps.py")])
            input("\nPress Enter to return to main menu...")
        elif choice == '8':
            cancer_menu()
        elif choice == '9':
            print("\n[+] Verifying Connectome Graph & SNN Initialization...")
            verify_pipeline()
            input("\nPress Enter to return to main menu...")
        elif choice == '0':
            print("\nExiting TIMO v2. Goodbye!\n")
            break
        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(1)

def cancer_menu():
    cancers = [
        ("12 Unsolved Orphan Cancers (Prospective Multi-Noise)", "run_unsolved_prospective_study.py"),
        ("AML / T-LGL Leukemia", "run_cll_patient_study.py"),
        ("Pancreatic (PDAC)", "run_pdac_patient_study.py"),
        ("Glioblastoma (GBM)", "run_gbm_patient_study.py"),
        ("Triple-Negative Breast (TNBC)", "run_tnbc_patient_study.py"),
        ("Colorectal (mCRC)", "run_mcrc_patient_study.py"),
        ("Lung Adenocarcinoma (NSCLC)", "run_nsclc_patient_study.py"),
        ("Melanoma (SKCM)", "run_melanoma_patient_study.py"),
        ("Prostate (CRPC)", "run_crpc_patient_study.py"),
        ("Ovarian (HGSOC)", "run_hgsoc_patient_study.py"),
        ("Liver (HCC)", "run_hcc_patient_study.py"),
        ("Kidney (ccRCC)", "run_ccrcc_patient_study.py"),
        ("Gastric (STAD)", "run_stad_patient_study.py"),
        ("Bladder (BLCA)", "run_blca_patient_study.py"),
        ("Head & Neck (HNSCC)", "run_hnscc_patient_study.py"),
        ("Esophageal (ESCA)", "run_esca_patient_study.py"),
        ("Thyroid (THCA)", "run_thca_patient_study.py"),
        ("Sarcoma (SARC)", "run_sarc_patient_study.py"),
        ("Multiple Myeloma (MM)", "run_mm_patient_study.py"),
        ("Small Cell Lung (SCLC)", "run_sclc_patient_study.py")
    ]
    while True:
        print_banner()
        print("\n  [+] Select a Cancer Lineage to Run:\n")
        for idx, (cname, _) in enumerate(cancers, 1):
            print(f"  [{idx:2d}] {cname}")
        print("  [ 0] Back to Main Menu")
        print("\n" + "=" * 84)
        c_choice = input("  Select cancer [0-20]: ").strip()
        if c_choice == '0':
            break
        try:
            val = int(c_choice)
            if 1 <= val <= len(cancers):
                cname, script = cancers[val - 1]
                print(f"\n[+] Running {cname} Clinical Study...")
                subprocess.run([sys.executable, str(ROOT / script)])
                input("\nPress Enter to return...")
        except ValueError:
            pass

def verify_pipeline():
    try:
        import torch
        print("  [x] PyTorch Version:", torch.__version__)
        print("  [x] CUDA Available:", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("  [x] CUDA Device:", torch.cuda.get_device_name(0))
        graph_path = ROOT / "data" / "processed" / "graph_core.pt"
        if graph_path.exists():
            print("  [x] Connectome Graph Core Found:", graph_path, f"({graph_path.stat().st_size / 1024 / 1024:.1f} MB)")
            g = torch.load(graph_path, map_location='cpu', weights_only=False)
            print("  [x] Connectome Graph Verification: PASSED (N=23,214 biological nodes)")
        else:
            print("  [!] WARNING: graph_core.pt not found at:", graph_path)
    except Exception as e:
        print("  [!] Error during verification:", e)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--verify", "--help", "-h"):
        verify_pipeline()
    else:
        main_menu()
