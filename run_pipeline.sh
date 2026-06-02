#!/bin/bash
# Run the Human-vs-AI SVO pipeline in Docker.
# Usage:
#   bash run_pipeline.sh                  # full run (STARK + validation + report)
#   bash run_pipeline.sh --process-only   # rebuild tables/figures from existing TSVs (no STARK)
#   bash run_pipeline.sh --force          # rerun STARK even for completed files
#
# Expects STARK to be at ~/STARK/stark.py on the host.
# Override with: STARK_DIR=/other/path bash run_pipeline.sh
set -euo pipefail

STARK_DIR="${STARK_DIR:-$HOME/STARK}"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
IMAGE="nh-svo-pipeline"

if [ ! -f "$STARK_DIR/stark.py" ]; then
  echo "ERROR: STARK not found at $STARK_DIR/stark.py"
  echo "Clone it first:  git clone https://github.com/clarinsi/STARK.git ~/STARK"
  exit 1
fi

echo "=== Building Docker image (only rebuilds if requirements.txt changed) ==="
docker build -t "$IMAGE" "$REPO_DIR"

echo "=== Running pipeline ==="
docker run --rm \
  -v "$REPO_DIR":/repo \
  -v "$STARK_DIR":/stark:ro \
  -e STARK_PY=/stark/stark.py \
  -e MPLCONFIGDIR=/tmp/mplconfig \
  "$IMAGE" "$@"
