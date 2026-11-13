"""ERC-8004 Verifiable Agent Reputation SDK.

Implements client-side agent registration, evaluation scoring via QAG/Agent Diagnostic Triad,
and Google A2UI 1.0 Agent Reputation Passport generation.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AgentProfile:
    agent_id: str
    owner_address: str
    endpoint: str
    metadata_uri: str
    total_evaluations: int = 0
    reputation_ema_bps: int = 0
    is_active: bool = True


class ERC8004ReputationClient:
    """Client for ERC-8004 On-Chain Verifiable Agent Identity and Reputation."""

    def __init__(self, registry_address: str, chain_id: int = 5000) -> None:
        self.registry_address = registry_address
        self.chain_id = chain_id

    def create_agent_manifest(
        self,
        name: str,
        description: str,
        capabilities: List[str],
        version: str = "1.0.0",
    ) -> Dict[str, Any]:
        """Creates standard ERC-8004 Agent Card metadata."""
        return {
            "standard": "ERC-8004",
            "version": version,
            "name": name,
            "description": description,
            "capabilities": capabilities,
            "created_at": int(time.time()),
        }

    def compute_updated_ema(self, current_ema: int, total_evals: int, new_score: int) -> int:
        """Computes updated EMA matching ERC8004AgentRegistry (alpha = 0.20)."""
        if total_evals == 0:
            return new_score
        return (new_score * 2000 + current_ema * 8000) // 10000

    def generate_a2ui_reputation_passport(
        self,
        agent: AgentProfile,
        recent_rubric: str = "SWE-BENCH-MANTLE-EVAL",
    ) -> Dict[str, Any]:
        """Generates Google A2UI 1.0 declarative UI component for Agent Reputation."""
        rep_pct = f"{agent.reputation_ema_bps / 100:.2f}%"
        status_badge = "emerald" if agent.reputation_ema_bps >= 8500 else ("amber" if agent.reputation_ema_bps >= 7000 else "rose")

        return {
            "surface_version": "1.0",
            "component": "AgentReputationPassport",
            "props": {
                "agent_id": agent.agent_id,
                "reputation_score": rep_pct,
                "badge_tier": "Certified Verified Agent" if agent.reputation_ema_bps >= 8500 else "Candidate Agent",
                "badge_color": status_badge,
            },
            "children": [
                {
                    "component": "MetricGrid",
                    "props": {
                        "columns": 3,
                        "metrics": [
                            {"label": "Reputation Score", "value": rep_pct},
                            {"label": "Total Evaluations", "value": str(agent.total_evaluations)},
                            {"label": "Status", "value": "Active" if agent.is_active else "Suspended"},
                        ],
                    },
                },
                {
                    "component": "EvaluationRadar",
                    "props": {
                        "latest_rubric": recent_rubric,
                        "registry_contract": self.registry_address,
                        "chain_id": self.chain_id,
                    },
                },
            ],
            "metadata": {
                "endpoint": agent.endpoint,
                "metadata_uri": agent.metadata_uri,
                "timestamp": int(time.time()),
            },
        }
