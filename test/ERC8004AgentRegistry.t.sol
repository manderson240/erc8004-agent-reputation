// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/ERC8004AgentRegistry.sol";

contract ERC8004AgentRegistryTest is Test {
    ERC8004AgentRegistry public registry;

    uint256 internal oraclePrivateKey = 0xCAFE;
    address internal oracle;
    address internal agentDev = address(0x400);

    bytes32 internal testAgentId = keccak256("COHEZION_RESEARCH_AGENT_01");

    function setUp() public {
        oracle = vm.addr(oraclePrivateKey);
        registry = new ERC8004AgentRegistry(oracle);

        vm.prank(agentDev);
        registry.registerAgent(
            testAgentId,
            "https://agent.cohezion.ai/v1",
            "ipfs://QmAgentCardMetadata123"
        );
    }

    function _signEvaluation(
        bytes32 agentId,
        uint256 nonce,
        uint256 score,
        bytes32 rubricHash
    ) internal view returns (uint8 v, bytes32 r, bytes32 s) {
        bytes32 rawHash = keccak256(
            abi.encodePacked(agentId, nonce, score, rubricHash, address(registry))
        );
        bytes32 ethSignedHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", rawHash)
        );
        (v, r, s) = vm.sign(oraclePrivateKey, ethSignedHash);
    }

    function test_RegisterAgent() public {
        ERC8004AgentRegistry.Agent memory agent = registry.getAgent(testAgentId);
        assertEq(agent.owner, agentDev);
        assertEq(agent.endpoint, "https://agent.cohezion.ai/v1");
        assertEq(agent.metadataUri, "ipfs://QmAgentCardMetadata123");
        assertEq(agent.totalEvaluations, 0);
        assertEq(agent.reputationEmaBps, 0);
        assertTrue(agent.isActive);
    }

    function test_RecordSingleEvaluation() public {
        bytes32 rubric = keccak256("SWE_BENCH_VERIFIED");
        uint256 score = 9100; // 91.00%

        (uint8 v, bytes32 r, bytes32 s) = _signEvaluation(testAgentId, 0, score, rubric);

        registry.recordEvaluation(testAgentId, score, rubric, v, r, s);

        ERC8004AgentRegistry.Agent memory agent = registry.getAgent(testAgentId);
        assertEq(agent.totalEvaluations, 1);
        assertEq(agent.reputationEmaBps, 9100);
        assertEq(agent.lastEvaluatedAt, block.timestamp);
    }

    function test_RecordMultipleEvaluationsEMA() public {
        bytes32 rubric = keccak256("SWE_BENCH_VERIFIED");

        // Evaluation 1: 9000
        (uint8 v1, bytes32 r1, bytes32 s1) = _signEvaluation(testAgentId, 0, 9000, rubric);
        registry.recordEvaluation(testAgentId, 9000, rubric, v1, r1, s1);

        // Evaluation 2: 8000
        // Expected EMA: 8000 * 0.2 + 9000 * 0.8 = 1600 + 7200 = 8800
        (uint8 v2, bytes32 r2, bytes32 s2) = _signEvaluation(testAgentId, 1, 8000, rubric);
        registry.recordEvaluation(testAgentId, 8000, rubric, v2, r2, s2);

        ERC8004AgentRegistry.Agent memory agent = registry.getAgent(testAgentId);
        assertEq(agent.totalEvaluations, 2);
        assertEq(agent.reputationEmaBps, 8800);
    }

    function test_RevertOnInvalidOracleSignature() public {
        bytes32 rubric = keccak256("RUBRIC");
        uint256 score = 9500;

        // Sign with unauthorized key
        bytes32 rawHash = keccak256(
            abi.encodePacked(testAgentId, uint256(0), score, rubric, address(registry))
        );
        bytes32 ethSignedHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", rawHash)
        );
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(0xBEEF, ethSignedHash);

        vm.expectRevert("Invalid evaluation oracle signature");
        registry.recordEvaluation(testAgentId, score, rubric, v, r, s);
    }

    function test_RevertOnUnregisteredAgent() public {
        bytes32 unknownAgent = keccak256("UNKNOWN_AGENT");
        bytes32 rubric = keccak256("RUBRIC");
        (uint8 v, bytes32 r, bytes32 s) = _signEvaluation(unknownAgent, 0, 9000, rubric);

        vm.expectRevert("Agent does not exist");
        registry.recordEvaluation(unknownAgent, 9000, rubric, v, r, s);
    }

    function testFuzz_EvaluationEMA(uint256 score1, uint256 score2) public {
        score1 = bound(score1, 0, 10000);
        score2 = bound(score2, 0, 10000);

        bytes32 rubric = keccak256("FUZZ_RUBRIC");

        (uint8 v1, bytes32 r1, bytes32 s1) = _signEvaluation(testAgentId, 0, score1, rubric);
        registry.recordEvaluation(testAgentId, score1, rubric, v1, r1, s1);

        (uint8 v2, bytes32 r2, bytes32 s2) = _signEvaluation(testAgentId, 1, score2, rubric);
        registry.recordEvaluation(testAgentId, score2, rubric, v2, r2, s2);

        uint256 expectedEma = (score2 * 2000 + score1 * 8000) / 10000;
        ERC8004AgentRegistry.Agent memory agent = registry.getAgent(testAgentId);

        assertEq(agent.reputationEmaBps, expectedEma);
        assertLe(agent.reputationEmaBps, 10000);
    }
}
