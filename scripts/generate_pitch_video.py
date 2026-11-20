#!/usr/bin/env python3
"""Automated 2560x1440 (2K QHD) 6-Scene Code Walkthrough & Pitch Video Generator
for ERC-8004 Agent Reputation Registry (The Turing Test: Mantle AI Agent Swarm Hackathon).
"""

from __future__ import annotations

import html
import json
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


def _load_slice(rel_path: str, start_line: int, end_line: int) -> str:
    """Load exact verbatim source lines (zero ellipses) and HTML-escape safely."""
    lines = (REPO_ROOT / rel_path).read_text(encoding="utf-8").splitlines()
    return html.escape("\n".join(lines[start_line - 1 : end_line]))


REGISTRY_PART1 = _load_slice("src/ERC8004AgentRegistry.sol", 55, 114)
REGISTRY_PART2 = _load_slice("src/ERC8004AgentRegistry.sol", 115, 163)
SDK_CODE = _load_slice("sdk/agent_reputation.py", 15, 72)

SCENES = [
    {
        "id": "scene0_title_hero",
        "narration": (
            "ERC-8004 Agent Reputation Registry. I built an on-chain registry for agent identity and reputation, aimed at Mantle. "
            "Agents register an ID, one evaluation oracle signs their scores, and the contract keeps an Exponential Moving Average "
            "between zero and ten thousand basis points with a constant-gas update. "
            "The signature is bound to a per-agent nonce and the contract address, so an agent owner cannot score their own agent. "
            "Six Foundry tests, including a two hundred fifty-six run fuzz test, and three Python tests all pass."
        ),
        "html_body": """
            <div class="header" style="text-align:center;margin-top:12px;margin-bottom:24px;">
                <span class="badge" style="font-size:20px;padding:8px 26px;">The Turing Test: Mantle AI Agent Swarm Hackathon</span>
                <h1 style="font-size:64px;margin-top:14px;margin-bottom:10px;letter-spacing:-2px;">ERC-8004 Agent Reputation Registry</h1>
                <p class="subtitle" style="font-size:26px;margin:0 auto;max-width:1950px;color:#38bdf8;font-weight:500;">
                    Constant-gas fixed-point EMA reputation and oracle-signed scores, built for Mantle
                </p>
            </div>
            <div class="grid-4" style="margin-top:20px;margin-bottom:20px;">
                <div class="card" style="text-align:center;border-color:rgba(56,189,248,0.4);background:rgba(56,189,248,0.08);">
                    <h3 style="font-size:30px;color:#38bdf8;">O(1) EMA</h3>
                    <p style="font-size:18px;color:#cbd5e1;">α=20% fixed-point [0, 10000] bps update with no storage arrays</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(34,197,94,0.4);background:rgba(34,197,94,0.08);">
                    <h3 style="font-size:30px;color:#22c55e;">Oracle-Only Scoring</h3>
                    <p style="font-size:18px;color:#cbd5e1;">ECDSA evalOracle signature + incrementing per-agent nonce</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(192,132,252,0.4);background:rgba(192,132,252,0.08);">
                    <h3 style="font-size:30px;color:#c084fc;">Python Helpers</h3>
                    <p style="font-size:18px;color:#cbd5e1;">Same EMA formula off-chain &amp; an A2UI-style passport dict</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(245,158,11,0.4);background:rgba(245,158,11,0.08);">
                    <h3 style="font-size:30px;color:#f59e0b;">6 + 3 Tests</h3>
                    <p style="font-size:18px;color:#cbd5e1;">Foundry 6/6 (256 fuzz runs) + Pytest 3/3 passing</p>
                </div>
            </div>
            <div class="flow-container" style="margin-top:16px;">
                <div class="chip chip-green" style="font-size:17px;padding:10px 20px;">Targets Mantle (not yet deployed)</div>
                <div class="chip chip-blue" style="font-size:17px;padding:10px 20px;">ERC-8004 idea + A2UI-style passport</div>
                <div class="chip chip-green" style="font-size:17px;padding:10px 20px;">Bounded [0, 10000] Basis Points</div>
                <div class="chip chip-blue" style="font-size:17px;padding:10px 20px;">1-Command: forge test &amp;&amp; uv run pytest</div>
            </div>
        """,
    },
    {
        "id": "scene1_problem_workflow",
        "narration": (
            "The problem I wanted to address. "
            "If agents can post their own reviews, scores are easy to fake, and storing every evaluation in an on-chain array gets expensive. "
            "Step one: Autonomous agents register unique bytes32 identities via registerAgent. "
            "Step two: Independent evaluators sign evaluation digests covering agentId, incrementing nonce, score, rubric hash, and contract address. "
            "Step three: ERC8004AgentRegistry verifies the signature via ecrecover and updates the reputation Exponential Moving Average in constant gas. "
            "Anyone can still register agent IDs, so this stops self-scoring, not Sybil registration."
        ),
        "html_body": """
            <div class="header">
                <span class="badge">Architecture • Verifiable Agent Credit Registry</span>
                <h1>Oracle-Signed Constant-Gas Agent Reputation</h1>
                <p class="subtitle">Signed scores and a fixed-point EMA, tested in Foundry and aimed at Mantle.</p>
            </div>
            <div class="flow-container" style="margin-top:24px;">
                <div class="flow-step">
                    <div class="flow-num">01</div>
                    <h4>Agent Identity</h4>
                    <p>registerAgent stores owner, endpoint, and metadataUri with duplicate-ID guard.</p>
                    <div class="chip">ERC-8004 Agent ID</div>
                </div>
                <div class="flow-arrow">➔</div>
                <div class="flow-step highlight">
                    <div class="flow-num">02</div>
                    <h4>Oracle ECDSA + Nonce</h4>
                    <p>recordEvaluation increments agentNonces[agentId] and checks ecrecover == evalOracle.</p>
                    <div class="chip chip-blue">Anti-Replay &amp; No Self-Scoring</div>
                </div>
                <div class="flow-arrow">➔</div>
                <div class="flow-step">
                    <div class="flow-num">03</div>
                    <h4>O(1) Fixed-Point EMA</h4>
                    <p>Computes (score*2000 + prior*8000)/10000 inside strict [0, 10000] bounds.</p>
                    <div class="chip chip-green">Constant Gas Update</div>
                </div>
            </div>
            <div class="grid-2" style="margin-top:24px;">
                <div class="card danger">
                    <h3>Common Registry Problems</h3>
                    <ul>
                        <li><strong>Self-Rating:</strong> Agents post fake positive reviews of themselves</li>
                        <li><strong>O(N) Loops:</strong> Iterating historical arrays runs out of gas at scale</li>
                        <li><strong>Signature Replay:</strong> Missing per-agent nonce lets attackers resubmit old scores</li>
                        <li><strong>Overflow Drift:</strong> Unbounded scoring breaks downstream credit weights</li>
                    </ul>
                </div>
                <div class="card success">
                    <h3>What ERC8004AgentRegistry Does</h3>
                    <ul>
                        <li><strong>Oracle Signed:</strong> Only signed <code>evalOracle</code> attestations mutate reputation</li>
                        <li><strong>O(1) State:</strong> Fixed-point α=0.20 EMA, a fixed number of storage writes per update</li>
                        <li><strong>Strict Nonces:</strong> Monotonic <code>agentNonces</code> in the signed message block replays</li>
                        <li><strong>Bounded Math:</strong> <code>reputationEmaBps &lt;= 10000</code> checked by a 256-run fuzz test</li>
                    </ul>
                </div>
            </div>
        """,
    },
    {
        "id": "scene2_core_source_code",
        "narration": (
            "Now let us walk through the verbatim Solidity contract in src/ERC8004AgentRegistry.sol lines fifty-five through one hundred sixty-three. "
            "On the left, the constructor, registerAgent, and updateAgent reject zero or duplicate IDs and allow updates only by the owner or admin. "
            "On the right, recordEvaluation increments per-agent evaluation nonces, checks oracle ecrecover over contract-bound digests, "
            "and computes the exact integer fixed-point Exponential Moving Average update."
        ),
        "html_body": f"""
            <div class="header">
                <span class="badge">Code Walkthrough • On-Chain Registry</span>
                <h1>Core Smart Contract: ERC8004AgentRegistry.sol</h1>
                <p class="subtitle">Verbatim Solidity implementation from <code>src/ERC8004AgentRegistry.sol</code> (lines 55 to 163, zero ellipses).</p>
            </div>
            <div class="code-grid-2">
                <div class="code-box">
                    <div class="linux-bar">
                        <span class="linux-tab">src/ERC8004AgentRegistry.sol (Lines 55 to 114)</span>
                        <div class="linux-controls"><span>_</span><span>□</span><span>✕</span></div>
                    </div>
                    <pre style="font-size:13.2px;line-height:1.25;">{REGISTRY_PART1}</pre>
                    <div class="eval-flow">
                        <span class="flow-pill pass">[OK] Agent Identity</span>
                        <span class="flow-pill pass">[OK] Owner Auth Check</span>
                    </div>
                </div>
                <div class="code-box">
                    <div class="linux-bar">
                        <span class="linux-tab">src/ERC8004AgentRegistry.sol (Lines 115 to 163)</span>
                        <div class="linux-controls"><span>_</span><span>□</span><span>✕</span></div>
                    </div>
                    <pre style="font-size:13.6px;line-height:1.28;">{REGISTRY_PART2}</pre>
                    <div class="eval-flow">
                        <span class="flow-pill pass">[OK] Nonce-Bound ECDSA</span>
                        <span class="flow-pill pass">[OK] O(1) α=2000 bps EMA</span>
                    </div>
                </div>
            </div>
        """,
    },
    {
        "id": "scene3_verifier_source_code",
        "narration": (
            "Alongside the Solidity contract is sdk/agent_reputation.py lines fifteen through seventy-two. "
            "ERC8004ReputationClient builds JSON agent manifests, "
            "computes the same fixed-point EMA update as the Solidity integer division, "
            "and builds A2UI-style AgentReputationPassport dicts. "
            "Its digest helper uses SHA-256 and does not match the contract's keccak message, so it cannot produce signatures the contract accepts. "
            "It does not connect to a chain."
        ),
        "html_body": f"""
            <div class="header">
                <span class="badge">Code Walkthrough • Python Helpers &amp; A2UI-Style Passport</span>
                <h1>Off-Chain Helpers: sdk/agent_reputation.py</h1>
                <p class="subtitle">Same EMA formula as Solidity &amp; an A2UI-style passport dict (<code>sdk/agent_reputation.py</code> lines 15 to 72).</p>
            </div>
            <div class="grid-2" style="gap:28px;height:980px;">
                <div class="code-box">
                    <div class="linux-bar">
                        <span class="linux-tab">sdk/agent_reputation.py (Lines 15 to 72)</span>
                        <div class="linux-controls"><span>_</span><span>□</span><span>✕</span></div>
                    </div>
                    <pre style="font-size:13.4px;line-height:1.28;">{SDK_CODE}</pre>
                    <div class="eval-flow">
                        <span class="flow-pill pass">[OK] Same Integer EMA</span>
                        <span class="flow-pill pass">[OK] Passport Dict</span>
                    </div>
                </div>
                <div class="card" style="display:flex;flex-direction:column;justify-content:space-between;">
                    <div>
                        <h3>Properties the Tests Check</h3>
                        <ul>
                            <li><strong>Bound:</strong> Since <code>0 ≤ score ≤ 10000</code> and <code>ALPHA_BPS = 2000</code>, <code>reputationEmaBps</code> stays inside <code>[0, 10000]</code>.</li>
                            <li><strong>Replay Resistance:</strong> Sequential <code>agentNonces[agentId]++</code> prevents double-counting signed rubrics.</li>
                            <li><strong>Oracle Only:</strong> Scores for unregistered agents or with a wrong signer revert.</li>
                            <li><strong>Known gap:</strong> the Python digest helper does not match the contract message.</li>
                        </ul>
                    </div>
                    <div class="card success" style="padding:20px;">
                        <h4 style="color:#22c55e;font-size:20px;margin-bottom:6px;">Fuzz Test</h4>
                        <p style="font-size:17px;">256 Foundry runs with two random scores (bounded to 0 to 10000) check the EMA formula and the upper bound.</p>
                    </div>
                </div>
            </div>
        """,
    },
    {
        "id": "scene4_honest_vs_adversarial_exec",
        "narration": (
            "Side-by-side Foundry tests. "
            "On the left, test Record Multiple Evaluations records nine thousand and then eight thousand basis points, "
            "and the test asserts the on-chain average is eight thousand eight hundred. "
            "On the right, scoring an unregistered agent, or a score signed by the wrong key, reverts."
        ),
        "html_body": """
            <div class="header">
                <span class="badge">Foundry Tests • Valid EMA Update vs. Rejected Scores</span>
                <h1>Valid EMA Update vs. Rejected Scores</h1>
                <p class="subtitle">What the tests in test/ERC8004AgentRegistry.t.sol set up and assert.</p>
            </div>
            <div class="code-grid-2">
                <div class="terminal-mini">
                    <div class="linux-bar">
                        <span class="linux-tab">forge test: two evaluations</span>
                        <div class="linux-controls"><span>_</span><span>□</span><span>✕</span></div>
                    </div>
                    <div class="term-lines" style="font-size:17px;">
                        <p class="t-line"><span class="t-prompt">$</span> forge test --match-test test_RecordMultipleEvaluationsEMA</p>
                        <p class="t-line t-cyan">Test step 1: recordEvaluation(score=9000, nonce=0)</p>
                        <p class="t-line t-indent">first score becomes the EMA: <span class="t-green">9000 bps</span></p>
                        <p class="t-line t-cyan">Test step 2: recordEvaluation(score=8000, nonce=1)</p>
                        <p class="t-line t-indent">(8000*2000 + 9000*8000)/10000</p>
                        <p class="t-line t-indent">assertEq(reputationEmaBps, <span class="t-green">8800</span>)</p>
                        <p class="t-line">[PASS] test_RecordMultipleEvaluationsEMA() (gas: 213138)</p>
                        <div class="t-banner-pass">PASS: EMA UPDATED</div>
                    </div>
                </div>
                <div class="terminal-mini danger-border">
                    <div class="linux-bar danger-header">
                        <span class="linux-tab-danger">forge test: rejected scores</span>
                        <div class="linux-controls"><span>_</span><span>□</span><span>✕</span></div>
                    </div>
                    <div class="term-lines" style="font-size:17px;">
                        <p class="t-line"><span class="t-prompt">$</span> forge test --match-test test_RevertOn</p>
                        <p class="t-line t-yellow">Test 1: score an agentId that was never registered</p>
                        <p class="t-line t-indent t-red">expectRevert("Agent does not exist")</p>
                        <p class="t-line">[PASS] test_RevertOnUnregisteredAgent() (gas: 37745)</p>
                        <p class="t-line t-yellow">Test 2: score signed by key 0xBEEF, not the oracle</p>
                        <p class="t-line t-indent t-red">expectRevert("Invalid evaluation oracle signature")</p>
                        <p class="t-line">[PASS] test_RevertOnInvalidOracleSignature() (gas: 65960)</p>
                        <div class="t-banner-fail">BOTH SCORES REJECTED</div>
                    </div>
                </div>
            </div>
        """,
    },
    {
        "id": "scene5_verification_and_impact",
        "narration": (
            "Running the tests. "
            "Foundry runs all six tests, including the two hundred fifty-six run fuzz test, "
            "and Pytest runs the three Python helper tests. All pass. "
            "The contract is not deployed yet, and it uses a single trusted oracle key. "
            "You can reproduce this locally with forge test and uv run pytest."
        ),
        "html_body": """
            <div class="header">
                <span class="badge">Verification • Foundry + Pytest</span>
                <h1>Foundry (6/6) + Pytest (3/3)</h1>
                <p class="subtitle">Tests for the Solidity contract and the off-chain Python helpers.</p>
            </div>
            <div class="grid-2" style="margin-top:18px;gap:26px;">
                <div class="terminal-window" style="height:640px;">
                    <div class="linux-bar">
                        <span class="linux-tab">forge test &amp;&amp; uv run pytest</span>
                        <div class="linux-controls"><span>_</span><span>□</span><span>✕</span></div>
                    </div>
                    <div class="terminal-content" style="font-size:14.8px;line-height:1.45;">
                        <p class="cmd">$ forge test -v</p>
                        <p><span class="pass">[PASS]</span> test_RegisterAgent() (gas: 35746)</p>
                        <p><span class="pass">[PASS]</span> test_RecordSingleEvaluation() (gas: 158716)</p>
                        <p><span class="pass">[PASS]</span> test_RecordMultipleEvaluationsEMA() (gas: 213138)</p>
                        <p><span class="pass">[PASS]</span> test_RevertOnUnregisteredAgent() (gas: 37745)</p>
                        <p><span class="pass">[PASS]</span> test_RevertOnInvalidOracleSignature() (gas: 65960)</p>
                        <p><span class="pass">[PASS]</span> testFuzz_EvaluationEMA(uint256,uint256) (runs: 256)</p>
                        <p class="cmd" style="margin-top:8px;">$ uv run pytest tests/test_reputation_sdk.py -v</p>
                        <p><span class="pass">PASSED</span> 3/3 manifest, EMA, passport &amp; digest tests</p>
                        <p class="success-banner">Foundry 6 passed • Pytest 3 passed</p>
                    </div>
                </div>
                <div class="card" style="display:flex;flex-direction:column;justify-content:space-between;height:640px;">
                    <div>
                        <h3 style="color:#38bdf8;">Limits</h3>
                        <ul>
                            <li><strong>Deployment:</strong> not deployed; tested in Foundry's local EVM only</li>
                            <li><strong>Oracle:</strong> one trusted <code>evalOracle</code> key, no rotation</li>
                            <li><strong>Signed message:</strong> binds the contract address, not the chain ID</li>
                            <li><strong>Registry Contract:</strong> <code>src/ERC8004AgentRegistry.sol</code></li>
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
.flow-arrow { font-size:30px; color:#64748b; padding:0 12px; font-weight:bold; }
.chip { display:inline-block; padding:6px 14px; background:#1e293b; border-radius:8px; font-size:14px; font-weight:600; color:#cbd5e1; }
.chip-blue { background:rgba(56,189,248,0.2); color:#38bdf8; border:1px solid rgba(56,189,248,0.4); }
.chip-green { background:rgba(34,197,94,0.2); color:#22c55e; border:1px solid rgba(34,197,94,0.4); }
.card { background:rgba(30,41,59,0.65); border:1px solid rgba(148,163,184,0.2); border-radius:18px; padding:24px; }
.card.danger { background:rgba(239,68,68,0.08); border-color:rgba(239,68,68,0.35); }
.card.success { background:rgba(34,197,94,0.08); border-color:rgba(34,197,94,0.35); }
.card-icon { font-size:36px; margin-bottom:8px; }
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
    <div class="footer-brand">ERC-8004 Agent Reputation Registry • The Turing Test: Mantle AI Agent Swarm Hackathon</div>
    <div>Constant-gas fixed-point EMA + oracle-signed scores • github.com/manderson240/erc8004-agent-reputation</div>
  </div>
</body></html>"""


def _synthesize_audio(text: str, output_mp3: Path) -> None:
    pocket_bin = shutil.which("pocket-tts") or "/home/mike-anderson/.local/bin/pocket-tts"
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
    out_mp4 = REPO_ROOT / "docs" / "erc8004_reputation_demo.mp4"
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        parts: list[Path] = []
        for scene in SCENES:
            sid = scene["id"]
            print(f"🎬 Rendering {sid} at {WIDTH}x{HEIGHT} QHD...")
            html_file = work / f"{sid}.html"
            raw_png = work / f"{sid}_raw.png"
            png_file = work / f"{sid}.png"
            mp3_file = work / f"{sid}.mp3"
            seg_mp4 = work / f"{sid}.mp4"
            html_file.write_text(HTML_TEMPLATE.replace("__BODY__", scene["html_body"]), encoding="utf-8")
            subprocess.run(
                ["google-chrome", "--headless", "--hide-scrollbars", "--disable-gpu", "--force-device-scale-factor=1", f"--screenshot={raw_png}", f"--window-size={WIDTH},{CHROME_CAPTURE_HEIGHT}", str(html_file)],
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
