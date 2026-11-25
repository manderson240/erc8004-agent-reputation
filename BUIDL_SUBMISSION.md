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
- Local EVM and Shanghai bytecode verification are complete, and **`ERC8004AgentRegistry` is deployed live on QDay Aevum Chain `44005`**:
  - Contract: [`0x4595b33f41723c6f70F60adf05A69c8D2AB978e2`](https://explorer-test.qday.info/address/0x4595b33f41723c6f70F60adf05A69c8D2AB978e2) (Deploy CREATE Tx: [`0xfbf843e0c4b3cb807872fabca096f8883bd3413d81dc193675af703163f2670d`](https://explorer-test.qday.info/tx/0xfbf843e0c4b3cb807872fabca096f8883bd3413d81dc193675af703163f2670d))
  - Exact deployed source commit (because explorer verification is offline): [`src/ERC8004AgentRegistry.sol` @ `86e2bc1`](https://github.com/manderson240/erc8004-agent-reputation/blob/86e2bc1f49b52a05000d1218b528381dcce5c873/src/ERC8004AgentRegistry.sol)
  - Live payee registration (`agentId` `0x2c7fb9c0b01fe7e7c8a2bba8097381ca1ffb43a320301373c1633b9792c65fda`): [`0x0de99e26e50d436f849b026b6ba5555b9a2a7b0ab46cded74f986c5efeec2c1d`](https://explorer-test.qday.info/tx/0x0de99e26e50d436f849b026b6ba5555b9a2a7b0ab46cded74f986c5efeec2c1d) (block `4118216`), wired into `AevumAgentEscrow` (`0xFF26781D65a8D7589699B6bcd4Cb137Bf67A7d64`, CREATE Tx [`0x456d4103...`](https://explorer-test.qday.info/tx/0x456d4103e6c983dbcb3519dbd363428345fc0d8da48b3ca93fb135284eee461a)).
  - Live EIP-191 `recordEvaluation` Tx (`score = 9200` bps / `92.00%` EMA, `totalEvaluations = 1`): [`0x5226bbb51ed1a408021195f07b7070a795632a67b8b87a5418e75d786e7a9d31`](https://explorer-test.qday.info/tx/0x5226bbb51ed1a408021195f07b7070a795632a67b8b87a5418e75d786e7a9d31) (block `4119030`).

### Verification
- `forge build --force && python3 scripts/check_shanghai.py`: `OK: 2 bytecode blobs verified Shanghai-safe.`
- `forge test -vv`: 9 of 9 Foundry tests pass in 17.10ms (23.05ms CPU time), including wrong-`chainId` revert tests, invalid signer and unregistered agent revert tests, admin/oracle rotation, `verifyPayee` active/inactive/unknown checks, and a 256-run EMA fuzz test (`testFuzz_EvaluationEMA`).
- `uv run pytest -q`: 4 of 4 Python tests pass in 0.45s, verifying Solidity keccak digest parity, ECDSA signing/recovery, EMA bounds, and A2UI passport output.
- Demo video: `docs/erc8004_reputation_demo.mp4` (`170.52s`, `170.522031s` via `ffprobe`, `16225773` bytes), hosted at https://raw.githubusercontent.com/manderson240/erc8004-agent-reputation/main/docs/erc8004_reputation_demo.mp4.
- Third-party dependency notices: [`NOTICE.md`](NOTICE.md) (MIT license).

### Future Roadmap
- Add multi-oracle quorum aggregation across specialized evaluation signers while keeping constant-slot on-chain EMA storage.
- Migrate or bridge registered agent identities and EMA scores to QDay's official ERC-8004 registry once QDay promotes it out of internal testing, and prepare Q1 2027 mainnet adapters.
