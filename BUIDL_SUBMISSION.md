# DoraHacks BUIDL Submission: ERC-8004 Agent Reputation

## 1. Project Overview
- **Project Name**: ERC-8004 On-Chain Agent Reputation Protocol
- **Tagline**: Verifiable Agent Identity, Cryptographic Evaluation Attestations, and Dynamic On-Chain Reputation for Mantle AI Agent Swarms
- **Hackathon**: The Turing Test: Mantle AI Agent Swarm Hackathon
- **Track**: AI Agents / Infrastructure / Identity & Reputation
- **Target Network**: Mantle Sepolia & Mantle Mainnet

---

## 2. The Core Problem
Decentralized AI agent swarms on Mantle cannot collaborate trustlessly without an objective, tamper-proof reputation system. Existing attempts either:
- Rely on centralized leaderboards that cannot be queried by smart contracts.
- Attempt to store full execution logs on-chain, creating prohibitive gas costs.
- Are vulnerable to Sybil attacks and self-attestation gaming.

---

## 3. Our Solution
ERC-8004 implements an on-chain identity and reputation layer specifically architected for Mantle's high-speed, low-fee modular architecture:
1. **On-Chain Exponential Moving Average (EMA)**: Updates agent credit scores in $O(1)$ gas complexity using basis-point math.
2. **Cryptographic Oracle Attestation**: Scores are verified via ECDSA signatures over rubric hashes and unique agent nonces.
3. **Google A2UI 1.0 Visual Passports**: Generates interactive visual credentials for agent marketplaces and human supervision.

---

## 4. Verification Evidence
- **Solidity Contracts**: `ERC8004AgentRegistry.sol`
- **Foundry Tests**: 6/6 tests passing (including 256-run fuzzing suite).
- **SDK**: Python 3.11+ client with automated A2UI 1.0 passport rendering.
