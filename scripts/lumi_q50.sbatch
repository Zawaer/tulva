#!/bin/bash
#SBATCH --job-name=tulva-q50
#SBATCH --account=project_462001763
#SBATCH --reservation=QxF2026
#SBATCH --partition=small
#SBATCH --time=01:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=tulva-q50-%j.out
# Submit from the repo root on LUMI: sbatch scripts/lumi_q50.sbatch   (Q20: export LUMI_DEVICE=q20)
# Check the Q50 QuickStart: hackathon access differs slightly from Q20 (device name / env var).
module load Local-quantum
module load fiqci-vtt-qiskit
export DEVICES=("${LUMI_DEVICE:-q50}")
source $RUN_SETUP
pip install --user -q scipy pandas matplotlib >/dev/null 2>&1 || true
bash scripts/hardware_day.sh lumi
