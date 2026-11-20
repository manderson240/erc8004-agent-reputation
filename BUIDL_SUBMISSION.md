# DoraHacks BUIDL Submission: ERC-8004 Agent Reputation

**Hackathon**: The Turing Test: Mantle AI Agent Swarm Hackathon  
**Track**: AI Agents / Infrastructure / Identity & Reputation  
**Target network**: Mantle Sepolia and Mantle Mainnet (not deployed yet)  
**Repository**: https://github.com/manderson240/erc8004-agent-reputation  

This file mirrors what I enter in the DoraHacks form.

---

## Form fields

### Name
```text
ERC-8004 Agent Reputation Registry
```

### Brief description (120 characters max, this one is 112)
```text
Solidity registry where one oracle signs agent scores and the contract keeps an on-chain moving average of them.
```

### Tags
```text
AI Agents, Infrastructure, Identity & Reputation
```

### Team
```text
(fill in before submitting)
```

### Links
- GitHub: https://github.com/manderson240/erc8004-agent-reputation
- Demo video: `docs/erc8004_reputation_demo.mp4`

### Contact
```text
(fill in before submitting)
```

---

## Description

### Why I built this

Agents in a swarm need some way to tell which other agents have a track record. If agents report their own benchmark scores, the scores are easy to fake. Keeping a full evaluation history on-chain is expensive. I wanted a registry where only a designated evaluator can change an agent's score, and where the score is one number that updates in constant gas.

### How it works

I wrote one contract, [`src/ERC8004AgentRegistry.sol`](src/ERC8004AgentRegistry.sol):

1. `registerAgent(agentId, endpoint, metadataUri)` stores an agent record owned by the caller.
2. `recordEvaluation(agentId, qagScore, rubricHash, v, r, s)` checks that the agent exists and is active, that the score is at most 10000 basis points, and that `ecrecover` over `keccak256(agentId, nonce, qagScore, rubricHash, address(this))` (with the Ethereum signed-message prefix) returns the `evalOracle` address set in the constructor. The per-agent nonce is incremented on each call, so a signature works only once.
3. The score is folded into `reputationEmaBps` with `(score * 2000 + prevEMA * 8000) / 10000`. The first score is stored as is.
4. `updateAgent` lets the owner or admin change the endpoint, metadata, or active flag. `getAgent` returns the record.

[`sdk/agent_reputation.py`](sdk/agent_reputation.py) has off-chain helpers: an agent manifest builder, the same EMA formula in Python, and a function that builds an A2UI-style passport dict for display. It does not talk to a chain.

### Mantle

The `foundry.toml` file has `mantle_sepolia` and `mantle_mainnet` RPC endpoints, and the README has the `forge create` command for Mantle Sepolia. I have not deployed the contract yet, so there is no contract address to link. Each `recordEvaluation` call writes a fixed number of storage slots, which keeps per-update cost flat on an L2.

### Limits

- Not deployed; tested only in Foundry's local EVM.
- One trusted oracle key, which cannot be rotated. The scores in the tests are hard-coded, and there is no benchmark runner in this repo.
- Anyone can register agent IDs. The signature check only stops self-scoring.
- The admin can change any agent, and there is no admin transfer.
- The signed message includes the contract address but not the chain ID.
- The Python `compute_evaluation_digest` (SHA-256 over a string) does not match the contract's keccak256 message, so the SDK cannot produce valid signatures.
- I have not checked the contract against the ERC-8004 draft interfaces.

### Verification

On my run, all 6 Foundry tests pass (including a 256-run fuzz test of the EMA) and all 3 pytest tests pass in 0.01 s.

```bash
git clone https://github.com/manderson240/erc8004-agent-reputation.git
cd erc8004-agent-reputation
forge test -vvv
uv run pytest -q
```

---

## Architecture diagrams

See [README.md](README.md#how-it-works) for the scoring sequence and the agent state diagram.
