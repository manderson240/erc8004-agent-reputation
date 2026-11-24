# DoraHacks BUIDL Submission: ERC-8004 Agent Reputation

**Hackathon**: The Turing Test / Aevum Track 4 Confirmation of Payee Component  
**Track**: AI Agents / Identity & Reputation / Confirmation of Payee  
**Repository**: https://github.com/manderson240/erc8004-agent-reputation  

---

## Form fields

### Name
```text
ERC-8004 Agent Reputation Registry
```

### Brief description (119 characters)
```text
Solidity ERC-8004 registry for agent identity, oracle-signed reputation EMA, and Confirmation of Payee pre-flight checks.
```

### Tags
```text
AI Agents, Infrastructure, Identity & Reputation
```

### Team
```text
Mike Anderson (Solo builder, github.com/manderson240)
```

### Links
- GitHub: https://github.com/manderson240/erc8004-agent-reputation
- Demo video: https://github.com/manderson240/erc8004-agent-reputation/raw/main/docs/erc8004_reputation_demo.mp4

### Contact
- Telegram: `manderson240`
- Discord: `miked238725`

---

## Description

# ERC-8004 Agent Reputation Registry

### Why I built this
Agents working together across protocols need both a verifiable performance history and a way to confirm a recipient wallet belongs to an active, registered agent before sending tokens. Keeping full evaluation logs on-chain is expensive, so I store a constant-gas exponential moving average (EMA) updated by oracle signatures and expose a read-only `verifyPayee(address)` endpoint for pre-flight Confirmation of Payee checks.

### How it works
[`src/ERC8004AgentRegistry.sol`](src/ERC8004AgentRegistry.sol):
1. `registerAgent(agentId, endpoint, metadataUri)` registers an active agent and maps the owner's address in `ownerToAgentId`.
2. `verifyPayee(address payee)` resolves whether an address maps to an active registered agent and returns `(verified, agentId, endpoint, metadataUri, reputationEmaBps, totalEvaluations)`.
3. `recordEvaluation(agentId, qagScore, rubricHash, v, r, s)` verifies an EIP-191 ECDSA signature over `keccak256(abi.encodePacked(agentId, nonce, qagScore, rubricHash, block.chainid, address(this)))` against `evalOracle`, preventing cross-chain or nonce replay, and updates the 20% EMA in constant storage slots.
4. `setEvalOracle` and `transferAdmin` handle oracle key rotation and admin handoff.

[`sdk/agent_reputation.py`](sdk/agent_reputation.py) computes the exact matching Solidity keccak digest, signs and recovers EIP-191 oracle signatures via `eth_account`, queries `verifyPayee` via JSON-RPC, and formats A2UI 1.0 passport cards.

### Verification
- `forge test -vv`: 9 of 9 Foundry tests pass in 17.72 ms (including wrong-`chainId` revert tests, admin/oracle rotation, `verifyPayee` checks, and a 256-run EMA fuzz test).
- `uv run pytest -q`: 4 of 4 Python tests pass, verifying Solidity keccak digest parity, ECDSA signing/recovery, and EMA bounds.
- `script/DeployERC8004.s.sol` is ready for live testnet broadcast once funded.
