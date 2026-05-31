#!/usr/bin/env bash
# Create this agent's isolated virtualenv and install all dependencies (including predmarket from GitHub).
set -euo pipefail

AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${AGENT_DIR}/.venv"

echo "Creating virtual environment at ${VENV_DIR}"
python3 -m venv "${VENV_DIR}"

echo "Installing prediction_market_research_agent and dependencies..."
"${VENV_DIR}/bin/pip" install -U pip
"${VENV_DIR}/bin/pip" install -e "${AGENT_DIR}[dev]"

echo ""
echo "Done. Activate with:"
echo "  source ${VENV_DIR}/bin/activate"
echo ""
echo "Then run:"
echo "  pm-research list --limit 5"
