// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title ERC8004AgentRegistry
 * @notice Standardized On-Chain AI Agent Identity and Verifiable Reputation Registry.
 * Implements ERC-8004 specifications with EMA-based QAG evaluation tracking.
 */
contract ERC8004AgentRegistry {
    struct Agent {
        bytes32 agentId;
        address owner;
        string endpoint;
        string metadataUri;
        uint256 totalEvaluations;
        uint256 reputationEmaBps; // 0 to 10000 (representing 0.00% to 100.00%)
        uint256 lastEvaluatedAt;
        bool isActive;
    }

    address public immutable evalOracle;
    address public admin;

    // agentId => Agent
    mapping(bytes32 => Agent) public agents;
    // agentId => evaluationNonce
    mapping(bytes32 => uint256) public agentNonces;

    // EMA weight factor: alpha = 2000 (20.00%) for new evaluation, (10000 - 2000 = 8000) for prior EMA
    uint256 public constant ALPHA_BPS = 2000;
    uint256 public constant BPS_DENOMINATOR = 10000;

    event AgentRegistered(
        bytes32 indexed agentId,
        address indexed owner,
        string endpoint,
        string metadataUri
    );

    event AgentUpdated(
        bytes32 indexed agentId,
        string endpoint,
        string metadataUri,
        bool isActive
    );

    event EvaluationRecorded(
        bytes32 indexed agentId,
        uint256 evaluationIndex,
        uint256 newScoreBps,
        uint256 updatedReputationEmaBps,
        bytes32 rubricHash
    );

    constructor(address _evalOracle) {
        require(_evalOracle != address(0), "Invalid eval oracle address");
        evalOracle = _evalOracle;
        admin = msg.sender;
    }

    /**
     * @notice Registers a new autonomous agent.
     */
    function registerAgent(
        bytes32 agentId,
        string calldata endpoint,
        string calldata metadataUri
    ) external {
        require(agentId != bytes32(0), "Invalid agentId");
        require(agents[agentId].owner == address(0), "Agent already registered");

        agents[agentId] = Agent({
            agentId: agentId,
            owner: msg.sender,
            endpoint: endpoint,
            metadataUri: metadataUri,
            totalEvaluations: 0,
            reputationEmaBps: 0,
            lastEvaluatedAt: 0,
            isActive: true
        });

        emit AgentRegistered(agentId, msg.sender, endpoint, metadataUri);
    }

    /**
     * @notice Updates endpoint or metadata for an existing agent.
     */
    function updateAgent(
        bytes32 agentId,
        string calldata endpoint,
        string calldata metadataUri,
        bool isActive
    ) external {
        Agent storage agent = agents[agentId];
        require(agent.owner != address(0), "Agent not found");
        require(agent.owner == msg.sender || msg.sender == admin, "Unauthorized update");

        agent.endpoint = endpoint;
        agent.metadataUri = metadataUri;
        agent.isActive = isActive;

        emit AgentUpdated(agentId, endpoint, metadataUri, isActive);
    }

    /**
     * @notice Records an independent verifiable quality evaluation (QAG score) for an agent.
     * @param agentId Unique agent identifier.
     * @param qagScore Evaluated score in basis points (0 - 10000).
     * @param rubricHash Hash of the evaluation dataset/rubric.
     * @param v ECDSA recovery byte.
     * @param r ECDSA signature parameter.
     * @param s ECDSA signature parameter.
     */
    function recordEvaluation(
        bytes32 agentId,
        uint256 qagScore,
        bytes32 rubricHash,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external {
        Agent storage agent = agents[agentId];
        require(agent.owner != address(0), "Agent does not exist");
        require(agent.isActive, "Agent is inactive");
        require(qagScore <= BPS_DENOMINATOR, "Score exceeds maximum");

        uint256 nonce = agentNonces[agentId]++;

        // Verify cryptographic oracle signature over (agentId, nonce, qagScore, rubricHash, address(this))
        bytes32 messageHash = keccak256(
            abi.encodePacked(
                "\x19Ethereum Signed Message:\n32",
                keccak256(abi.encodePacked(agentId, nonce, qagScore, rubricHash, address(this)))
            )
        );

        address recovered = ecrecover(messageHash, v, r, s);
        require(recovered == evalOracle, "Invalid evaluation oracle signature");

        // Calculate Exponential Moving Average (EMA)
        uint256 updatedEma;
        if (agent.totalEvaluations == 0) {
            updatedEma = qagScore;
        } else {
            updatedEma = (qagScore * ALPHA_BPS + agent.reputationEmaBps * (BPS_DENOMINATOR - ALPHA_BPS)) / BPS_DENOMINATOR;
        }

        agent.totalEvaluations++;
        agent.reputationEmaBps = updatedEma;
        agent.lastEvaluatedAt = block.timestamp;

        emit EvaluationRecorded(agentId, nonce, qagScore, updatedEma, rubricHash);
    }

    /**
     * @notice Returns complete agent information.
     */
    function getAgent(bytes32 agentId) external view returns (Agent memory) {
        require(agents[agentId].owner != address(0), "Agent not found");
        return agents[agentId];
    }
}
