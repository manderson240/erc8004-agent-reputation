from __future__ import annotations

from eth_account import Account
from web3 import Web3

from sdk.agent_reputation import AgentProfile, ERC8004ReputationClient


TEST_REGISTRY = "0x1234567890123456789012345678901234567890"
ORACLE_KEY = "0x" + "11" * 32


def test_erc8004_ema_and_passport() -> None:
    client = ERC8004ReputationClient(registry_address=TEST_REGISTRY, chain_id=5000)

    ema1 = client.compute_updated_ema(current_ema=0, total_evals=0, new_score=9000)
    assert ema1 == 9000

    ema2 = client.compute_updated_ema(current_ema=9000, total_evals=1, new_score=8000)
    assert ema2 == 8800

    agent = AgentProfile(
        agent_id="0x" + "aa" * 32,
        owner_address="0x0000000000000000000000000000000000000400",
        endpoint="https://agent.cohezion.ai",
        metadata_uri="ipfs://QmMetadata123",
        total_evaluations=2,
        reputation_ema_bps=8800,
        is_active=True,
    )
    passport = client.generate_a2ui_reputation_passport(agent)
    assert passport["component"] == "AgentReputationPassport"
    assert passport["props"]["reputation_score"] == "88.00%"
    assert passport["props"]["badge_color"] == "emerald"


def test_erc8004_ema_boundary_clamping() -> None:
    client = ERC8004ReputationClient(registry_address=TEST_REGISTRY, chain_id=5000)
    ema_zero = client.compute_updated_ema(current_ema=5000, total_evals=10, new_score=0)
    assert 0 <= ema_zero <= 10000

    ema_max = client.compute_updated_ema(current_ema=5000, total_evals=10, new_score=10000)
    assert 0 <= ema_max <= 10000
    assert ema_max > 5000


def test_erc8004_solidity_keccak_digest_parity() -> None:
    client = ERC8004ReputationClient(registry_address=TEST_REGISTRY, chain_id=31337)
    agent_id = "0x" + Web3.keccak(text="COHEZION_RESEARCH_AGENT_01").hex()
    rubric = "0x" + Web3.keccak(text="SWE_BENCH_VERIFIED").hex()

    expected = "0x" + Web3.solidity_keccak(
        ["bytes32", "uint256", "uint256", "bytes32", "uint256", "address"],
        [bytes.fromhex(agent_id[2:]), 0, 9100, bytes.fromhex(rubric[2:]), 31337, TEST_REGISTRY],
    ).hex()

    got = client.compute_evaluation_digest(agent_id=agent_id, score=9100, rubric_hash=rubric, nonce=0)
    assert got == expected
    assert got != client.compute_evaluation_digest(agent_id=agent_id, score=9100, rubric_hash=rubric, nonce=1)


def test_erc8004_oracle_ecdsa_sign_and_recover() -> None:
    client = ERC8004ReputationClient(registry_address=TEST_REGISTRY, chain_id=31337)
    sig = client.sign_evaluation(
        agent_id="COHEZION_RESEARCH_AGENT_01",
        score=9250,
        rubric_hash="SWE_BENCH_VERIFIED",
        nonce=0,
        oracle_private_key=ORACLE_KEY,
    )
    recovered = client.recover_oracle_signer(sig)
    assert recovered == Account.from_key(ORACLE_KEY).address
