"""ERC-8004 Verifiable Agent Reputation SDK.

Implements client-side agent registration, Solidity-matching evaluation digest
and EIP-191 ECDSA signing, Confirmation-of-Payee lookup, and A2UI 1.0 cards.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List

from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3


ERC8004_VERIFY_PAYEE_ABI = [
    {
        "type": "function",
        "name": "verifyPayee",
        "stateMutability": "view",
        "inputs": [{"name": "payee", "type": "address"}],
        "outputs": [
            {"name": "verified", "type": "bool"},
            {"name": "agentId", "type": "bytes32"},
            {"name": "endpoint", "type": "string"},
            {"name": "metadataUri", "type": "string"},
            {"name": "reputationEmaBps", "type": "uint256"},
            {"name": "totalEvaluations", "type": "uint256"},
        ],
    }
]


def to_bytes32(value: str) -> bytes:
    """Normalize a 32-byte hex string or arbitrary text identifier into 32 bytes."""
    if value.startswith("0x") and len(value) == 66:
        try:
            return bytes.fromhex(value[2:])
        except ValueError:
            pass
    return bytes(Web3.keccak(text=value))


@dataclass
class AgentProfile:
    agent_id: str
    owner_address: str
    endpoint: str
    metadata_uri: str
    total_evaluations: int = 0
    reputation_ema_bps: int = 0
    is_active: bool = True


@dataclass(frozen=True, slots=True)
class EvaluationSignature:
    digest_hex: str
    v: int
    r_hex: str
    s_hex: str
    signer: str


@dataclass(frozen=True, slots=True)
class PayeeVerification:
    payee: str
    verified: bool
    agent_id: str
    endpoint: str
    metadata_uri: str
    reputation_ema_bps: int
    total_evaluations: int


class ERC8004ReputationClient:
    """Client for ERC-8004 On-Chain Verifiable Agent Identity and Reputation."""

    def __init__(self, registry_address: str, chain_id: int = 5000) -> None:
        self.registry_address = Web3.to_checksum_address(registry_address)
        self.chain_id = int(chain_id)

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

    def compute_evaluation_digest(
        self, agent_id: str, score: int, rubric_hash: str, nonce: int
    ) -> str:
        """Compute keccak256 digest matching ERC8004AgentRegistry.recordEvaluation()."""
        raw = Web3.solidity_keccak(
            ["bytes32", "uint256", "uint256", "bytes32", "uint256", "address"],
            [
                to_bytes32(agent_id),
                int(nonce),
                int(score),
                to_bytes32(rubric_hash),
                int(self.chain_id),
                self.registry_address,
            ],
        )
        return "0x" + raw.hex()

    def sign_evaluation(
        self,
        agent_id: str,
        score: int,
        rubric_hash: str,
        nonce: int,
        oracle_private_key: str,
    ) -> EvaluationSignature:
        """Sign an evaluation digest using EIP-191 personal sign compatible with on-chain ecrecover."""
        digest_hex = self.compute_evaluation_digest(agent_id, score, rubric_hash, nonce)
        msg = encode_defunct(hexstr=digest_hex)
        signed = Account.sign_message(msg, private_key=oracle_private_key)
        signer_addr = Account.from_key(oracle_private_key).address
        return EvaluationSignature(
            digest_hex=digest_hex,
            v=int(signed.v),
            r_hex="0x" + int(signed.r).to_bytes(32, "big").hex(),
            s_hex="0x" + int(signed.s).to_bytes(32, "big").hex(),
            signer=signer_addr,
        )

    def recover_oracle_signer(self, sig: EvaluationSignature) -> str:
        """Recover signer address from an EvaluationSignature for pre-flight verification."""
        msg = encode_defunct(hexstr=sig.digest_hex)
        vrs = (sig.v, int(sig.r_hex, 16), int(sig.s_hex, 16))
        return Account.recover_message(msg, vrs=vrs)

    def verify_payee_rpc(self, rpc_url: str, payee_address: str) -> PayeeVerification:
        """Query ERC8004AgentRegistry.verifyPayee(address) over JSON-RPC."""
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        payee = Web3.to_checksum_address(payee_address)
        contract = w3.eth.contract(address=self.registry_address, abi=ERC8004_VERIFY_PAYEE_ABI)
        verified, aid, endpoint, metadata_uri, rep_bps, total_evals = contract.functions.verifyPayee(payee).call()
        return PayeeVerification(
            payee=payee,
            verified=bool(verified),
            agent_id="0x" + bytes(aid).hex(),
            endpoint=str(endpoint),
            metadata_uri=str(metadata_uri),
            reputation_ema_bps=int(rep_bps),
            total_evaluations=int(total_evals),
        )

    def compute_updated_ema(self, current_ema: int, total_evals: int, new_score: int) -> int:
        """Computes updated EMA matching ERC8004AgentRegistry (alpha = 0.20)."""
        if total_evals == 0:
            return new_score
        return (new_score * 2000 + current_ema * 8000) // 10000

    def generate_a2ui_reputation_passport(
        self,
        agent: AgentProfile,
        recent_rubric: str = "SWE-BENCH-TESTNET-EVAL",
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
