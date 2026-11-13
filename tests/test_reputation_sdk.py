import pytest
from sdk.agent_reputation import ERC8004ReputationClient, AgentProfile

def test_erc8004_sdk():
    client = ERC8004ReputationClient(registry_address="0xRegistry123456789012345678901234567890", chain_id=5000)

    # Test metadata creation
    manifest = client.create_agent_manifest(
        name="MantleSwarmResearcher",
        description="Autonomous LLM research agent",
        capabilities=["python", "solidity", "market_analysis"],
    )
    assert manifest["standard"] == "ERC-8004"
    assert "solidity" in manifest["capabilities"]

    # Test EMA computation
    ema1 = client.compute_updated_ema(current_ema=0, total_evals=0, new_score=9000)
    assert ema1 == 9000

    ema2 = client.compute_updated_ema(current_ema=9000, total_evals=1, new_score=8000)
    assert ema2 == 8800

    # Test A2UI Passport generation
    agent = AgentProfile(
        agent_id="0xAgentHash001",
        owner_address="0xOwnerAddress123",
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
