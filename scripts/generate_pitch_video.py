#!/usr/bin/env python3
"""Automated 2560x1440 (2K QHD) 6-Scene Code Walkthrough & Pitch Video Generator
for ERC-8004 Agent Reputation Registry (The Turing Test: Mantle AI Agent Swarm Hackathon & Aevum Track 4).
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from PIL import Image


WIDTH = 2560
HEIGHT = 1440
CHROME_CAPTURE_HEIGHT = 1527
REPO_ROOT = Path(__file__).resolve().parents[1]


def _resolve_chrome_bin() -> str:
    env_bin = os.getenv("CHROME_HEADLESS_BIN")
    if env_bin and Path(env_bin).is_file():
        return env_bin
    candidates = sorted(
        Path.home().glob(
            ".cache/ms-playwright/chromium_headless_shell-*/"
            "chrome-headless-shell-linux64/chrome-headless-shell"
        )
    )
    if candidates:
        return str(candidates[-1])
    found = shutil.which("chrome-headless-shell")
    if found:
        return found
    raise FileNotFoundError(
        "Playwright chrome-headless-shell not found; set CHROME_HEADLESS_BIN"
    )


def _load_slice(rel_path: str, start_line: int, end_line: int) -> str:
    """Load exact verbatim source lines (zero ellipses) and HTML-escape safely."""
    lines = (REPO_ROOT / rel_path).read_text(encoding="utf-8").splitlines()
    return html.escape("\n".join(lines[start_line - 1 : end_line]))


REGISTRY_PART1 = _load_slice("src/ERC8004AgentRegistry.sol", 75, 130)
REGISTRY_PART2 = _load_slice("src/ERC8004AgentRegistry.sol", 155, 222)
SDK_CODE = _load_slice("sdk/agent_reputation.py", 101, 166)

SCENES = [
    {
        "id": "scene0_title_hero",
        "narration": (
            "ERC-8004 Agent Reputation Registry. I built an on-chain identity, Confirmation of Payee lookup, "
            "and constant-gas reputation registry targeting Mantle and Aevum Builder Challenge Track Four. "
            "Evaluations use oracle-signed EIP-191 keccak digests bound to a per-agent nonce, chain ID, and contract address, "
            "with admin and oracle key rotation plus pre-flight verifyPayee checks for escrow buyers. "
            "Nine Foundry tests, including a two hundred fifty-six run fuzz test, and four Solidity-parity Python tests all pass."
        ),
        "html_body": """
            <div class="header" style="text-align:center;margin-top:12px;margin-bottom:24px;">
                <span class="badge" style="font-size:20px;padding:8px 26px;">The Turing Test (Mantle) &amp; Aevum Track 4</span>
                <h1 style="font-size:64px;margin-top:14px;margin-bottom:10px;letter-spacing:-2px;">ERC-8004 Agent Reputation Registry</h1>
                <p class="subtitle" style="font-size:26px;margin:0 auto;max-width:1950px;color:#38bdf8;font-weight:500;">
                    Confirmation of Payee, Chain-ID Domain Separation, Oracle Rotation &amp; Constant-Gas EMA
                </p>
            </div>
            <div class="grid-4" style="margin-top:20px;margin-bottom:20px;">
                <div class="card" style="text-align:center;border-color:rgba(56,189,248,0.4);background:rgba(56,189,248,0.08);">
                    <h3 style="font-size:30px;color:#38bdf8;">Confirm Payee</h3>
                    <p style="font-size:18px;color:#cbd5e1;">verifyPayee(addr) resolves verified active agent, endpoint &amp; EMA</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(34,197,94,0.4);background:rgba(34,197,94,0.08);">
                    <h3 style="font-size:30px;color:#22c55e;">Chain-ID Bound</h3>
                    <p style="font-size:18px;color:#cbd5e1;">EIP-191 keccak binds agentId, nonce, qagScore, block.chainid &amp; registry</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(192,132,252,0.4);background:rgba(192,132,252,0.08);">
                    <h3 style="font-size:30px;color:#c084fc;">Key Rotation</h3>
                    <p style="font-size:18px;color:#cbd5e1;">Admin-gated setEvalOracle &amp; transferAdmin + Solidity-parity Python SDK</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(245,158,11,0.4);background:rgba(245,158,11,0.08);">
                    <h3 style="font-size:30px;color:#f59e0b;">9 + 4 Tests</h3>
                    <p style="font-size:18px;color:#cbd5e1;">Foundry 9/9 (256 fuzz runs) + Pytest 4/4 (keccak parity &amp; recovery)</p>
                </div>
            </div>
            <div class="flow-container" style="margin-top:16px;">
                <div class="chip chip-green" style="font-size:17px;padding:10px 20px;">verifyPayee Pre-Flight Check</div>
                <div class="chip chip-blue" style="font-size:17px;padding:10px 20px;">block.chainid + Nonce Protection</div>
                <div class="chip chip-green" style="font-size:17px;padding:10px 20px;">Bounded [0, 10000] O(1) EMA</div>
                <div class="chip chip-blue" style="font-size:17px;padding:10px 20px;">forge test &amp;&amp; uv run pytest -q</div>
            </div>
        """,
    },
    {
        "id": "scene1_problem_workflow",
        "narration": (
            "Architecture and hardening. "
            "Step one: An agent owner registers an ID, endpoint, and metadata URI, and sets a primary payee ID if owning multiple agents. "
            "Step two: Wallets and payment escrows call verifyPayee to confirm an active worker address and inspect its reputation before sending funds. "
            "Step three: Independent evaluators sign keccak256 digests over agent ID, nonce, score, rubric hash, block.chainid, and contract address. "
            "Admin rotation lets governance rotate the evalOracle key without redeploying the registry."
        ),
        "html_body": """
            <div class="header">
                <span class="badge">Architecture | Verifiable Agent Identity &amp; Payee Verification</span>
                <h1>Oracle-Signed Constant-Gas Registry &amp; Payee Lookup</h1>
                <p class="subtitle">Domain-separated scoring, admin oracle key rotation, and pre-transfer verifyPayee checks.</p>
            </div>
            <div class="flow-container" style="margin-top:24px;">
                <div class="flow-step">
                    <div class="flow-num">01</div>
                    <h4>Identity &amp; Payee Link</h4>
                    <p>registerAgent stores owner, endpoint, metadataUri, and ownerToAgentId mapping.</p>
                    <div class="chip">setPayeeAgent Support</div>
                </div>
                <div class="flow-arrow">-&gt;</div>
                <div class="flow-step highlight">
                    <div class="flow-num">02</div>
                    <h4>Pre-Flight verifyPayee</h4>
                    <p>Escrows call verifyPayee(worker) to check verified status, active flag, and EMA bps.</p>
                    <div class="chip chip-blue">Confirmation of Payee</div>
                </div>
                <div class="flow-arrow">-&gt;</div>
                <div class="flow-step">
                    <div class="flow-num">03</div>
                    <h4>Chain-ID ECDSA + O(1) EMA</h4>
                    <p>recordEvaluation checks block.chainid + nonce + evalOracle before fixed-point EMA.</p>
                    <div class="chip chip-green">setEvalOracle Rotation</div>
                </div>
            </div>
            <div class="grid-2" style="margin-top:24px;">
                <div class="card success">
                    <h3>Hardened Features</h3>
                    <ul>
                        <li><strong>Cross-chain replay lock:</strong> digest binds <code>block.chainid</code> and <code>address(this)</code></li>
                        <li><strong>Admin key rotation:</strong> <code>setEvalOracle</code> and <code>transferAdmin</code> rotate signers safely</li>
                        <li><strong>Python digest parity:</strong> <code>Web3.solidity_keccak</code> + <code>eth_account</code> produces valid contract signatures</li>
                        <li><strong>RPC Payee helper:</strong> <code>verify_payee_rpc</code> queries <code>verifyPayee(address)</code> over JSON-RPC</li>
                    </ul>
                </div>
                <div class="card danger">
                    <h3>Honest Scope and Limits</h3>
                    <ul>
                        <li><strong>Local EVM only:</strong> tested in Foundry EVM; live Mantle/Aevum broadcast awaits funded burner key</li>
                        <li><strong>Anti-self-scoring:</strong> stops fake self-ratings, not permissionless multi-address registration (Sybil)</li>
                        <li><strong>Deploy script ready:</strong> <code>script/DeployERC8004.s.sol</code> configures oracle from env</li>
                        <li><strong>Off-chain calls:</strong> SDK queries live nodes only when an RPC URL is provided</li>
                    </ul>
                </div>
            </div>
        """,
    },
    {
        "id": "scene2_core_source_code",
        "narration": (
            "Here is src/ERC8004AgentRegistry.sol, lines seventy-five through two hundred twenty-two. "
            "On the left, admin-gated setEvalOracle and transferAdmin rotate governance cleanly, alongside registerAgent and setPayeeAgent. "
            "On the right, recordEvaluation verifies EIP-191 oracle signatures with block.chainid domain separation "
            "and updates the constant-gas EMA, followed by verifyPayee for active, inactive, and unknown address lookups."
        ),
        "html_body": f"""
            <div class="header">
                <span class="badge">Code Walkthrough | On-Chain Registry</span>
                <h1>Core Smart Contract: ERC8004AgentRegistry.sol</h1>
                <p class="subtitle">Verbatim Solidity source from <code>src/ERC8004AgentRegistry.sol</code> (lines 75 to 130 and 155 to 222).</p>
            </div>
            <div class="code-grid-2">
                <div class="code-box">
                    <div class="linux-bar">
                        <span class="linux-tab">ERC8004AgentRegistry.sol (Lines 75 to 130)</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <pre style="font-size:11.8px;line-height:1.22;padding:12px 16px;">{REGISTRY_PART1}</pre>
                    <div class="eval-flow">
                        <span class="flow-pill pass">[OK] Admin &amp; Oracle Rotation</span>
                        <span class="flow-pill pass">[OK] Primary Payee Mapping</span>
                    </div>
                </div>
                <div class="code-box">
                    <div class="linux-bar">
                        <span class="linux-tab">ERC8004AgentRegistry.sol (Lines 155 to 222)</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <pre style="font-size:10.8px;line-height:1.15;padding:12px 16px;">{REGISTRY_PART2}</pre>
                    <div class="eval-flow">
                        <span class="flow-pill pass">[OK] block.chainid ECDSA</span>
                        <span class="flow-pill pass">[OK] verifyPayee Lookup</span>
                    </div>
                </div>
            </div>
        """,
    },
    {
        "id": "scene3_verifier_source_code",
        "narration": (
            "Next is sdk/agent_reputation.py, lines one hundred one through one hundred sixty-six. "
            "compute_evaluation_digest uses Web3.solidity_keccak over the exact Solidity field layout, "
            "sign_evaluation and recover_oracle_signer create and verify EIP-191 proofs via eth_account, "
            "verify_payee_rpc calls the contract view directly, and compute_updated_ema matches the Solidity integer math."
        ),
        "html_body": f"""
            <div class="header">
                <span class="badge">Code Walkthrough | Solidity-Parity Python SDK</span>
                <h1>sdk/agent_reputation.py</h1>
                <p class="subtitle">Verbatim Python code from <code>sdk/agent_reputation.py</code> (lines 101 to 166).</p>
            </div>
            <div class="grid-2" style="gap:28px;height:980px;">
                <div class="code-box">
                    <div class="linux-bar">
                        <span class="linux-tab">sdk/agent_reputation.py (Lines 101 to 166)</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <pre style="font-size:11.6px;line-height:1.18;padding:12px 16px;">{SDK_CODE}</pre>
                    <div class="eval-flow">
                        <span class="flow-pill pass">[OK] Keccak EIP-191 Parity</span>
                        <span class="flow-pill pass">[OK] verify_payee_rpc</span>
                    </div>
                </div>
                <div class="card" style="display:flex;flex-direction:column;justify-content:space-between;">
                    <div>
                        <h3>Hardened Contract &amp; SDK Properties</h3>
                        <ul>
                            <li><strong>Byte-for-byte digest parity:</strong> tested against <code>keccak256(abi.encodePacked(...))</code> with <code>block.chainid</code></li>
                            <li><strong>Rotation safe:</strong> admin can rotate <code>evalOracle</code> or transfer admin control cleanly</li>
                            <li><strong>Inactive payee check:</strong> <code>verifyPayee</code> returns <code>verified=false</code> when an agent is deactivated or unknown</li>
                            <li><strong>EMA invariant:</strong> stays bounded in <code>[0, 10000]</code> across 256 fuzz runs</li>
                        </ul>
                    </div>
                    <div class="card success" style="padding:20px;">
                        <h4 style="color:#22c55e;font-size:20px;margin-bottom:6px;">Deployment Ready</h4>
                        <p style="font-size:17px;">script/DeployERC8004.s.sol is included for Mantle or Aevum broadcast once a funded burner key and starter-kit RPC URL are placed in .env.</p>
                    </div>
                </div>
            </div>
        """,
    },
    {
        "id": "scene4_honest_vs_adversarial_exec",
        "narration": (
            "Side-by-side Foundry tests. "
            "On the left, EMA evaluation updates to eight thousand eight hundred bps, oracle key rotation transfers authority cleanly, "
            "and verifyPayee distinguishes active, inactive, and unknown accounts. "
            "On the right, signatures generated for a different chain ID, wrong signing keys, or unregistered agents revert."
        ),
        "html_body": """
            <div class="header">
                <span class="badge">Foundry Tests | Payee &amp; Rotation vs. Adversarial Reverts</span>
                <h1>EMA + Rotation + Payee vs. Replay &amp; Unregistered Reverts</h1>
                <p class="subtitle">Real tests enforced in test/ERC8004AgentRegistry.t.sol.</p>
            </div>
            <div class="code-grid-2">
                <div class="terminal-mini">
                    <div class="linux-bar">
                        <span class="linux-tab">EMA, Rotation &amp; verifyPayee</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <div class="term-lines" style="font-size:16.5px;">
                        <p class="t-line"><span class="t-prompt">$</span> forge test --match-test "EMA|Rotation|VerifyPayee"</p>
                        <p class="t-line"><span class="t-green">[PASS]</span> test_RecordMultipleEvaluationsEMA() (gas: 217593)</p>
                        <p class="t-line t-indent">9000 -&gt; 8000 (20% alpha) == <span class="t-green">8800 bps</span></p>
                        <p class="t-line"><span class="t-green">[PASS]</span> test_AdminAndOracleRotation() (gas: 112436)</p>
                        <p class="t-line"><span class="t-green">[PASS]</span> test_VerifyPayeeActiveInactiveAndUnknown() (gas: 105545)</p>
                        <p class="t-banner-pass">PASS: O(1) EMA, KEY ROTATION &amp; PAYEE CHECK</p>
                    </div>
                </div>
                <div class="terminal-mini danger-border">
                    <div class="linux-bar danger-header">
                        <span class="linux-tab-danger">Wrong ChainId, Bad Signer &amp; Missing Agent</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <div class="term-lines" style="font-size:16.5px;">
                        <p class="t-line"><span class="t-prompt">$</span> forge test --match-test test_RevertOn</p>
                        <p class="t-line"><span class="t-green">[PASS]</span> test_RevertOnWrongChainIdSignature() (gas: 70474)</p>
                        <p class="t-line t-indent t-red">rejects cross-chain replayed oracle signatures</p>
                        <p class="t-line"><span class="t-green">[PASS]</span> test_RevertOnInvalidOracleSignature() (gas: 68214)</p>
                        <p class="t-line"><span class="t-green">[PASS]</span> test_RevertOnUnregisteredAgent() (gas: 37800)</p>
                        <div class="t-banner-fail">ALL ADVERSARIAL CASES REJECTED</div>
                    </div>
                </div>
            </div>
        """,
    },
    {
        "id": "scene5_verification_and_impact",
        "narration": (
            "Full test results. "
            "All nine Foundry contract tests, including the two hundred fifty-six run fuzz test, pass in twelve point two five milliseconds. "
            "All four Python tests verify EMA bounds, keccak digest parity, and ECDSA recovery in zero point four one seconds. "
            "Reproduce all tests locally from manderson240/erc8004-agent-reputation."
        ),
        "html_body": """
            <div class="header">
                <span class="badge">Verification | Foundry (9/9) + Pytest (4/4)</span>
                <h1>Foundry (9/9) + Pytest (4/4) Passing</h1>
                <p class="subtitle">Verified across Solidity contracts and Solidity-parity Python SDK tests.</p>
            </div>
            <div class="grid-2" style="margin-top:18px;gap:26px;">
                <div class="terminal-window" style="height:640px;">
                    <div class="linux-bar">
                        <span class="linux-tab">forge test &amp;&amp; uv run pytest -q</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <div class="terminal-content" style="font-size:13.0px;line-height:1.28;">
                        <p class="cmd">$ forge test</p>
                        <p><span class="pass">[PASS]</span> testFuzz_EvaluationEMA(uint256,uint256) (runs: 256)</p>
                        <p><span class="pass">[PASS]</span> test_AdminAndOracleRotation() (gas: 112436)</p>
                        <p><span class="pass">[PASS]</span> test_RecordMultipleEvaluationsEMA() (gas: 217593)</p>
                        <p><span class="pass">[PASS]</span> test_RecordSingleEvaluation() (gas: 160953)</p>
                        <p><span class="pass">[PASS]</span> test_RegisterAgent() (gas: 35785)</p>
                        <p><span class="pass">[PASS]</span> test_RevertOnInvalidOracleSignature() (gas: 68214)</p>
                        <p><span class="pass">[PASS]</span> test_RevertOnUnregisteredAgent() (gas: 37800)</p>
                        <p><span class="pass">[PASS]</span> test_RevertOnWrongChainIdSignature() (gas: 70474)</p>
                        <p><span class="pass">[PASS]</span> test_VerifyPayeeActiveInactiveAndUnknown() (gas: 105545)</p>
                        <p class="cmd" style="margin-top:6px;">$ uv run pytest -q</p>
                        <p><span class="pass">4 passed</span> in 0.41s (EMA bounds, passport, keccak parity, ECDSA recovery)</p>
                        <p class="success-banner">Foundry 9 passed (12.25ms) | Pytest 4 passed (0.41s)</p>
                    </div>
                </div>
                <div class="card" style="display:flex;flex-direction:column;justify-content:space-between;height:640px;">
                    <div>
                        <h3 style="color:#38bdf8;">Summary &amp; Repository</h3>
                        <ul>
                            <li><strong>Deployment:</strong> tested in local Foundry EVM; <code>DeployERC8004.s.sol</code> ready for testnet broadcast</li>
                            <li><strong>Rotation:</strong> admin can rotate <code>evalOracle</code> via <code>setEvalOracle</code></li>
                            <li><strong>Replay security:</strong> signed digest binds <code>nonce</code>, <code>block.chainid</code> &amp; <code>address(this)</code></li>
                            <li><strong>Payee verification:</strong> <code>verifyPayee</code> supports Aevum Track 4 integration</li>
                            <li><strong>GitHub Repository:</strong> <code>manderson240/erc8004-agent-reputation</code></li>
                        </ul>
                    </div>
                    <div class="card success" style="padding:18px;">
                        <h4 style="color:#22c55e;font-size:20px;margin-bottom:6px;">One-Command Local Verification</h4>
                        <div class="code-pill" style="font-size:15.5px;">forge test &amp;&amp; uv run pytest -q</div>
                    </div>
                </div>
            </div>
        """,
    },
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" style="background-color:#030712;width:100%;height:100%;margin:0;padding:0;">
<head><meta charset="UTF-8"><style>
* { box-sizing:border-box; margin:0; padding:0; }
html, body {
  width:2560px; height:1440px;
  background:radial-gradient(circle at 50% 12%, #182234 0%, #0b0f19 55%, #030712 100%) !important;
  font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color:#f8fafc; padding:30px 60px;
  display:flex; flex-direction:column; justify-content:space-between; overflow:hidden;
}
.header { margin-bottom:12px; }
.badge { display:inline-block; padding:6px 18px; background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.4); border-radius:9999px; color:#38bdf8; font-size:17px; font-weight:700; text-transform:uppercase; letter-spacing:2px; margin-bottom:6px; }
h1 { font-size:46px; font-weight:800; color:#ffffff; margin-bottom:6px; letter-spacing:-1px; }
.subtitle { font-size:22px; color:#94a3b8; line-height:1.35; }
.grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:30px; }
.grid-4 { display:grid; grid-template-columns:repeat(4,1fr); gap:24px; }
.flow-container { display:flex; align-items:center; justify-content:space-between; background:rgba(30,41,59,0.45); border:1px solid rgba(148,163,184,0.2); border-radius:18px; padding:18px 32px; gap:16px; }
.flow-step { flex:1; background:#0d1322; border:1px solid #334155; border-radius:14px; padding:18px; text-align:center; }
.flow-step.highlight { border-color:#38bdf8; background:rgba(56,189,248,0.12); }
.flow-num { font-size:20px; font-weight:900; color:#38bdf8; margin-bottom:4px; }
.flow-step h4 { font-size:22px; color:#f8fafc; margin-bottom:4px; }
.flow-step p { font-size:16px; color:#94a3b8; margin-bottom:8px; line-height:1.35; }
.flow-arrow { font-size:26px; color:#64748b; padding:0 12px; font-weight:bold; font-family:monospace; }
.chip { display:inline-block; padding:6px 14px; background:#1e293b; border-radius:8px; font-size:14px; font-weight:600; color:#cbd5e1; }
.chip-blue { background:rgba(56,189,248,0.2); color:#38bdf8; border:1px solid rgba(56,189,248,0.4); }
.chip-green { background:rgba(34,197,94,0.2); color:#22c55e; border:1px solid rgba(34,197,94,0.4); }
.card { background:rgba(30,41,59,0.65); border:1px solid rgba(148,163,184,0.2); border-radius:18px; padding:24px; }
.card.danger { background:rgba(239,68,68,0.08); border-color:rgba(239,68,68,0.35); }
.card.success { background:rgba(34,197,94,0.08); border-color:rgba(34,197,94,0.35); }
.card h3 { font-size:26px; color:#f1f5f9; margin-bottom:10px; font-weight:700; }
.card p { font-size:18px; color:#cbd5e1; line-height:1.4; }
.card ul { list-style:none; }
.card ul li { font-size:18px; color:#cbd5e1; line-height:1.8; }
.card ul li strong { color:#ffffff; }
.code-grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:26px; height:980px; }
.code-box { background:#0a0e17; border:1px solid #1e293b; border-radius:14px; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 25px 50px -12px rgba(0,0,0,0.7); }
.linux-bar { background:#181f30; padding:10px 18px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #222d42; }
.linux-tab { background:#0a0e17; padding:4px 12px; border-radius:6px 6px 0 0; border:1px solid #222d42; border-bottom:none; color:#38bdf8; font-family:monospace; font-size:16px; font-weight:600; }
.linux-tab-danger { background:#0a0e17; padding:4px 12px; border-radius:6px 6px 0 0; border:1px solid rgba(239,68,68,0.4); border-bottom:none; color:#ef4444; font-family:monospace; font-size:16px; font-weight:600; }
.danger-header { background:#241319; border-bottom-color:rgba(239,68,68,0.3); }
.danger-border { border-color:rgba(239,68,68,0.45) !important; }
.linux-controls { display:flex; gap:14px; font-size:16px; color:#94a3b8; font-family:monospace; font-weight:bold; }
pre { padding:16px 22px; font-family:"JetBrains Mono","DejaVu Sans Mono",monospace; color:#e2e8f0; overflow:hidden; flex:1; }
.eval-flow { padding:12px 18px; background:#0e1526; border-top:1px solid #1e293b; display:flex; gap:10px; }
.flow-pill.pass { padding:5px 12px; border-radius:6px; font-size:14px; font-weight:700; background:rgba(34,197,94,0.18); color:#22c55e; border:1px solid rgba(34,197,94,0.35); }
.terminal-mini { background:#0a0e17; border:1px solid #1e293b; border-radius:14px; overflow:hidden; display:flex; flex-direction:column; }
.term-lines { padding:20px 24px; font-family:"JetBrains Mono",monospace; line-height:1.75; flex:1; display:flex; flex-direction:column; justify-content:space-between; }
.t-line { color:#f8fafc; } .t-prompt { color:#4ade80; font-weight:bold; } .t-cyan { color:#38bdf8; font-weight:bold; } .t-yellow { color:#fbbf24; font-weight:bold; } .t-green { color:#22c55e; font-weight:bold; } .t-red { color:#ef4444; font-weight:bold; } .t-indent { padding-left:22px; }
.t-banner-pass { margin-top:10px; padding:10px 16px; background:rgba(34,197,94,0.18); border:1px solid rgba(34,197,94,0.45); border-radius:8px; color:#22c55e; font-weight:800; font-size:18px; text-align:center; }
.t-banner-fail { margin-top:10px; padding:10px 16px; background:rgba(239,68,68,0.18); border:1px solid rgba(239,68,68,0.45); border-radius:8px; color:#ef4444; font-weight:800; font-size:18px; text-align:center; }
.terminal-window { background:#0a0e17; border:1px solid #1e293b; border-radius:14px; overflow:hidden; display:flex; flex-direction:column; }
.terminal-content { padding:20px 26px; font-family:"JetBrains Mono",monospace; flex:1; display:flex; flex-direction:column; justify-content:space-between; }
.cmd { color:#f8fafc; font-weight:bold; } .pass { color:#22c55e; font-weight:bold; } .success-banner { color:#22c55e; font-weight:bold; font-size:18px; margin-top:8px; }
.code-pill { display:inline-block; padding:8px 14px; background:#030712; border:1px solid #334155; border-radius:8px; font-family:monospace; color:#38bdf8; }
.footer { display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(148,163,184,0.2); padding-top:14px; font-size:17px; color:#64748b; }
.footer-brand { font-weight:bold; color:#94a3b8; }
</style></head>
<body>
  __BODY__
  <div class="footer">
    <div class="footer-brand">ERC-8004 Agent Reputation Registry | The Turing Test (Mantle) &amp; Aevum Track 4</div>
    <div>Confirmation of Payee &amp; chain-ID ECDSA EMA | 9/9 Foundry + 4/4 pytest | github.com/manderson240/erc8004-agent-reputation</div>
  </div>
</body></html>"""


def _synthesize_audio(text: str, output_mp3: Path) -> None:
    pocket_bin = shutil.which("pocket-tts") or str(Path.home() / ".local" / "bin" / "pocket-tts")
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    with tempfile.TemporaryDirectory() as td:
        wavs: list[Path] = []
        for idx, sent in enumerate(sentences):
            wav = Path(td) / f"part_{idx}.wav"
            subprocess.run(
                [pocket_bin, "generate", "--text", sent, "--device", "cpu", "--quantize", "--max-tokens", "150", "--output-path", str(wav), "-q"],
                check=True,
                capture_output=True,
            )
            if wav.exists() and wav.stat().st_size > 1000:
                wavs.append(wav)
        clist = Path(td) / "list.txt"
        clist.write_text("\n".join(f"file '{w}'" for w in wavs), encoding="utf-8")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(clist), "-af", "apad=pad_dur=1.25", "-c:a", "libmp3lame", "-b:a", "192k", str(output_mp3)],
            check=True,
            capture_output=True,
        )


def main() -> None:
    chrome_bin = _resolve_chrome_bin()
    out_mp4 = REPO_ROOT / "docs" / "erc8004_reputation_demo.mp4"
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        profile_dir = work / "chrome_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)
        parts: list[Path] = []
        for scene in SCENES:
            sid = scene["id"]
            print(f"Rendering {sid} at {WIDTH}x{HEIGHT} QHD...")
            html_file = work / f"{sid}.html"
            raw_png = work / f"{sid}_raw.png"
            png_file = work / f"{sid}.png"
            mp3_file = work / f"{sid}.mp3"
            seg_mp4 = work / f"{sid}.mp4"
            html_file.write_text(HTML_TEMPLATE.replace("__BODY__", scene["html_body"]), encoding="utf-8")
            subprocess.run(
                [
                    chrome_bin,
                    "--headless",
                    "--no-sandbox",
                    "--hide-scrollbars",
                    "--disable-gpu",
                    f"--user-data-dir={profile_dir}",
                    "--force-device-scale-factor=1",
                    f"--screenshot={raw_png}",
                    f"--window-size={WIDTH},{CHROME_CAPTURE_HEIGHT}",
                    str(html_file),
                ],
                check=True,
                capture_output=True,
            )
            Image.open(raw_png).crop((0, 0, WIDTH, HEIGHT)).save(png_file)
            _synthesize_audio(scene["narration"], mp3_file)
            subprocess.run(
                ["ffmpeg", "-y", "-loop", "1", "-i", str(png_file), "-i", str(mp3_file), "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest", str(seg_mp4)],
                check=True,
                capture_output=True,
            )
            parts.append(seg_mp4)
        clist = work / "concat.txt"
        clist.write_text("\n".join(f"file '{p}'" for p in parts), encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(clist), "-c", "copy", str(out_mp4)], check=True, capture_output=True)
    info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", str(out_mp4)], text=True))
    print(f"GENERATED: {out_mp4} ({float(info['format']['duration']):.2f}s, {int(info['format']['size'])/(1024*1024):.2f} MB)")


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"Elapsed: {time.time() - t0:.1f}s")
