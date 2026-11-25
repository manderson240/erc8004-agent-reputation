# DoraHacks BUIDL Submission: ERC-8004 Agent Reputation

**Hackathon**: The Turing Test / Aevum Builder Challenge #1 (Build 51828, Track 4 Confirmation of Payee Component)  
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
- Demo video (`170.52s`, 2560x1440 QHD): https://raw.githubusercontent.com/manderson240/erc8004-agent-reputation/main/docs/erc8004_reputation_demo.mp4

### Contact
- Telegram: `manderson240`
- Discord: `miked238725`

---

## Description

# ERC-8004 Agent Reputation Registry

### Why I built this
Agents working together across protocols need both a verifiable performance history and a way to confirm a recipient wallet belongs to an active, registered agent before sending tokens. Keeping full evaluation logs on-chain is expensive, so I store a constant-gas exponential moving average (EMA) updated by oracle signatures and expose a read-only `verifyPayee(address)` endpoint for pre-flight Confirmation of Payee checks.

QDay's starter kit notes that QDay's internal ERC-8004 registry is still in internal testing and not open for Aevum Builder Challenge #1 (Build 51828). This repository provides a self-deployable ERC-8004 registry and `verifyPayee(address)` endpoint targeting QDay Aevum Testnet (Chain ID `44005`, RPC `https://rpc-test.qday.info`, Explorer `https://explorer-test.qday.info`).

### How it works
[`src/ERC8004AgentRegistry.sol`](src/ERC8004AgentRegistry.sol):
1. `registerAgent(agentId, endpoint, metadataUri)` registers an active agent and maps the owner's address in `ownerToAgentId` (`setPayeeAgent` selects a primary payee ID for multi-agent owners).
2. `verifyPayee(address payee)` resolves whether an address maps to an active registered agent and returns `(verified, agentId, endpoint, metadataUri, reputationEmaBps, totalEvaluations)` for wallets and escrows such as `AevumAgentEscrow`.
3. `recordEvaluation(agentId, qagScore, rubricHash, v, r, s)` verifies an EIP-191 ECDSA signature over `keccak256(abi.encodePacked(agentId, nonce, qagScore, rubricHash, block.chainid, address(this)))` against `evalOracle`, preventing cross-chain or nonce replay, and updates the 20% EMA (`ALPHA_BPS = 2000`) in constant storage slots.
4. `setEvalOracle` and `transferAdmin` handle oracle key rotation and admin handoff.

[`sdk/agent_reputation.py`](sdk/agent_reputation.py) computes the exact matching Solidity keccak digest, signs and recovers EIP-191 oracle signatures via `eth_account`, queries `verifyPayee` via JSON-RPC (`verify_payee_rpc`), and formats A2UI 1.0 passport cards (`generate_a2ui_reputation_passport`).

### Shanghai EVM & Aevum Chain 44005 Deployment
- `foundry.toml` configures `solc_version = "0.8.24"` and `evm_version = "shanghai"` for QDay Aevum Testnet (`44005`, `https://rpc-test.qday.info`), using `--legacy` Type-0 transactions.
- `scripts/check_shanghai.py` scans compiled `src/` artifacts and verifies zero Cancun-only opcodes (`BLOBHASH`, `BLOBBASEFEE`, `TLOAD`, `TSTORE`, `MCOPY`).
- Recommended encrypted keystore deployment workflow:
  ```bash
  cast wallet new aevum-deployer
  forge script script/DeployERC8004.s.sol:DeployERC8004 --rpc-url aevum --broadcast --legacy --account aevum-deployer
  ```
- Local EVM and Shanghai bytecode verification are complete; live Aevum Chain `44005` broadcast awaits funding the `aevum-deployer` wallet via `/faucet` in the QDay Discord.

### Verification
- `forge build --force && python3 scripts/check_shanghai.py`: `OK: 2 bytecode blobs verified Shanghai-safe.`
- `forge test -vv`: 9 of 9 Foundry tests pass in 17.10ms (23.05ms CPU time), including wrong-`chainId` revert tests, invalid signer and unregistered agent revert tests, admin/oracle rotation, `verifyPayee` active/inactive/unknown checks, and a 256-run EMA fuzz test (`testFuzz_EvaluationEMA`).
- `uv run pytest -q`: 4 of 4 Python tests pass in 0.45s, verifying Solidity keccak digest parity, ECDSA signing/recovery, EMA bounds, and A2UI passport output.
- Demo video: `docs/erc8004_reputation_demo.mp4` (`170.52s`, `170.522031s` via `ffprobe`, `16225773` bytes), hosted at https://raw.githubusercontent.com/manderson240/erc8004-agent-reputation/main/docs/erc8004_reputation_demo.mp4.

### Future Roadmap
- Broadcast `script/DeployERC8004.s.sol` to QDay Aevum Testnet (Chain ID `44005`) once `aevum-deployer` receives faucet QDAY and record the deployment address and transaction receipt.
- Integrate `ERC8004AgentRegistry.verifyPayee(address)` with `AevumAgentEscrow` pre-transfer settlement hooks on Chain `44005`.
- Migrate or bridge registered agent identities and EMA scores to QDay's official ERC-8004 registry once QDay promotes it out of internal testing.
