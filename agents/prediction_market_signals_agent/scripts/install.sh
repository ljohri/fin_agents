#!/usr/bin/env bash
set -euo pipefail

AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "${AGENT_DIR}/../.." && pwd)"
VENV_DIR="${AGENT_DIR}/.venv"

python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/pip" install -U pip
"${VENV_DIR}/bin/pip" install -e "${REPO_ROOT}/libs/fin_agents_common[langfuse]"
"${VENV_DIR}/bin/pip" install -e "${REPO_ROOT}/agents/prediction_market_research_agent[dev]"
"${VENV_DIR}/bin/pip" install -e "${AGENT_DIR}[dev]"

echo "Installed. Activate: source ${VENV_DIR}/bin/activate"
