# ERC-8004: Verifiable On-Chain AI Agent Identity & Reputation Protocol



> **Trustless Agent Identity, Verifiable QAG Evaluation Attestation, and Dynamic Reputation Tracking on Mantle Network**  
> *Submitted to The Turing Test: Mantle AI Agent Swarm Hackathon*

[![Foundry](https://img.shields.io/badge/Foundry-passing-brightgreen.svg)](https://github.com/foundry-rs/foundry)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

---

## Executive Summary

As decentralized AI agent swarms proliferate across EVM ecosystems like Mantle, consumer and developer agents face a critical discovery and trust dilemma:
- **Which agent is legitimate?** Anyone can spin up an endpoint and claim state-of-the-art capability.
- **How is performance verified?** Self-reported benchmarks are easily gamed or faked.
- **How is reputation dynamically tracked without gas bloat?** Storing entire evaluation histories on-chain is prohibitive.

**ERC-8004 Agent Reputation Protocol** introduces an on-chain soulbound identity standard and an Exponential Moving Average (EMA) verifiable scoring mechanism. Independent evaluation oracles attest to agent benchmark runs (e.g. QAG claim accuracy, code generation correctness) via cryptographic ECDSA signatures, continuously updating the agent's on-chain credit score.

---

## System Architecture

```mermaid
flowchart TD
    subgraph CreatorLayer["Agent Creator & Swarm Ecosystem"]
        Developer["Agent Creator / Developer EOA"]
        AgentSwarm["Autonomous Agent Swarm (Mantle Network)"]
    end

    subgraph MantleChain["Mantle Network (Modular L2 Execution Layer)"]
        Registry["ERC8004AgentRegistry.sol<br/><i>Soulbound Identity & Invariant Enforcer</i>"]
        EMACalculator["Fixed-Point EMA Math Engine<br/>(alpha = 2000 bps = 20%)"]
        NonceTracker["Replay-Resistant Nonce Store<br/>(agentId -> nonce)"]
        ScoreStore["On-Chain Credit Ledger<br/>(reputationScore, evalCount, lastUpdate)"]
    end

    subgraph OracleNetwork["Independent Evaluation Oracle Network"]
        EvalOracle["Evaluation Oracle Node"]
        BenchmarkRunner["Standardized Rubric Runner<br/>(QAG Fidelity, SWE-Bench, Safety AST)"]
        DigestSigner["ECDSA secp256k1 Signer<br/>keccak256(agentId, nonce, score, rubricHash)"]
    end

    subgraph PresentationLayer["Visual Verification & Governance"]
        A2UI["Google A2UI 1.0 Declarative Engine"]
        Passport["Dynamic Agent Reputation Passport<br/>(Certified Status, Radar Chart, Historical EMA)"]
    end

    Developer -->|"1. registerAgent(endpoint, metadataURI)"| Registry
    Registry -->|"Mint Soulbound ID"| NonceTracker

    AgentSwarm -->|"Execute Tasks"| EvalOracle
    EvalOracle --> BenchmarkRunner
    BenchmarkRunner -->|"Compute Score in [0, 10000]"| DigestSigner
    DigestSigner -->|"2. recordEvaluation(agentId, score, rubricHash, v, r, s)"| Registry

    Registry -->|"Verify Oracle Sig & Nonce"| NonceTracker
    Registry -->|"Update Score via EMA"| EMACalculator
    EMACalculator --> ScoreStore

    Registry -.->|"3. emit EvaluationRecorded"| A2UI
    A2UI --> Passport

    classDef creator fill:#1e1e2e,stroke:#cba6f7,stroke-width:2px,color:#cdd6f4;
    classDef mantle fill:#181825,stroke:#89b4fa,stroke-width:2px,color:#cdd6f4;
    classDef oracle fill:#313244,stroke:#a6e3a1,stroke-width:2px,color:#cdd6f4;
    classDef visual fill:#313244,stroke:#f38ba8,stroke-width:2px,color:#cdd6f4;

    class CreatorLayer,Developer,AgentSwarm creator;
    class MantleChain,Registry,EMACalculator,NonceTracker,ScoreStore mantle;
    class OracleNetwork,EvalOracle,BenchmarkRunner,DigestSigner oracle;
    class PresentationLayer,A2UI,Passport visual;
```

### Dynamic Reputation Evaluation Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Creator as Agent Creator
    participant Registry as ERC8004AgentRegistry.sol
    actor Swarm as Mantle Agent Swarm
    participant Oracle as Evaluation Oracle
    participant A2UI as A2UI Passport Engine

    Creator->>Registry: registerAgent("https://agent.ai", "ipfs://metadata")
    activate Registry
    Registry->>Registry: Assign agentId & initialize nonce = 0
    Registry-->>Creator: emit AgentRegistered(agentId, creator)
    deactivate Registry

    Swarm->>Oracle: Request Benchmark Evaluation
    activate Oracle
    Oracle->>Oracle: Execute QAG Fidelity & Safety Tests
    Oracle->>Oracle: Derive score = 8800 bps, rubricHash
    Oracle->>Oracle: Sign digest = keccak256(agentId, nonce, score, rubricHash)
    Oracle-->>Swarm: Deliver Proof (score, rubricHash, v, r, s)
    deactivate Oracle

    activate Swarm
    Swarm->>Registry: recordEvaluation(agentId, score, rubricHash, v, r, s)
    deactivate Swarm
    activate Registry

    Registry->>Registry: Verify signature == evaluationOracle
    Registry->>Registry: Increment agent nonce to prevent replay
    Registry->>Registry: EMA = (score * 2000 + prevEMA * 8000) / 10000
    Registry-->>A2UI: emit EvaluationRecorded(agentId, newScore, evalCount)
    deactivate Registry

    activate A2UI
    A2UI-->>Swarm: Render Updated On-Chain Reputation Passport
    deactivate A2UI
```

### Agent Reputation Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> Unregistered
    Unregistered --> Registered: registerAgent() [Nonce = 0, Score = 0]
    
    Registered --> Evaluating: Benchmark Task Assigned
    Evaluating --> Certified: recordEvaluation() [Score >= 8000 bps]
    Evaluating --> Probationary: recordEvaluation() [Score < 6000 bps]
    
    Certified --> Evaluating: New Evaluation Triggered
    Probationary --> Evaluating: Recovery Benchmark Triggered
    
    Probationary --> Revoked: Consecutive Low Scores (< 3000 bps)
    Revoked --> [*]: Blacklisted by Swarm Protocol
```

---

## Technical Specifications

### Smart Contract: `ERC8004AgentRegistry.sol`
1. **On-Chain Exponential Moving Average (EMA)**:
   $$\text{EMA}_{t} = \frac{\text{Score}_{t} \cdot \alpha + \text{EMA}_{t-1} \cdot (10000 - \alpha)}{10000}$$
   Using fixed basis-point math ($\alpha = 2000$, i.e. 20%), preventing precision decay while penalizing sudden quality degradation.
2. **Replay-Resistant Nonce Architecture**:
   Each agent maintains an independent evaluation nonce incremented on every verified score.
3. **Decoupled Verification**:
   Separates agent identity from evaluation oracles, preventing developer self-scoring while maintaining permissionless agent onboarding.

---

## Testing & Verification

### 1. Foundry Test Suite
```bash
forge test -vvv
```
Output:
```
Ran 6 tests for test/ERC8004AgentRegistry.t.sol:ERC8004AgentRegistryTest
[PASS] testFuzz_EvaluationEMA(uint256,uint256) (runs: 256, μ: 214714, ~: 214666)
[PASS] test_RecordMultipleEvaluationsEMA() (gas: 213138)
[PASS] test_RecordSingleEvaluation() (gas: 158716)
[PASS] test_RegisterAgent() (gas: 35746)
[PASS] test_RevertOnInvalidOracleSignature() (gas: 65960)
[PASS] test_RevertOnUnregisteredAgent() (gas: 37745)
Suite result: ok. 6 passed; 0 failed; 0 skipped
```

### 2. Python SDK Tests
```bash
uv run pytest
```

---

## Deployment (Mantle Sepolia / Mainnet)

```bash
forge create --rpc-url https://rpc.sepolia.mantle.xyz \
  --private-key $PRIVATE_KEY \
  src/ERC8004AgentRegistry.sol:ERC8004AgentRegistry \
  --constructor-args $EVAL_ORACLE_ADDRESS
```

---

## License

MIT License. Open-source public good for the Mantle AI Agent ecosystem.
