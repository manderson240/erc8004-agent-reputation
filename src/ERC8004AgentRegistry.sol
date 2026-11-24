// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title ERC8004AgentRegistry
 * @notice Standardized On-Chain AI Agent Identity, Confirmation-of-Payee Lookup, and Verifiable Reputation Registry.
 * Implements ERC-8004 style agent identity and EMA-based QAG evaluation tracking.
 */
contract ERC8004AgentRegistry {
    struct Agent {
        bytes32 agentId;
        address owner;
        string endpoint;
        string metadataUri;
        uint256 totalEvaluations;
        uint256 reputationEmaBps; // 0 to 10000 (0.00% to 100.00%)
        uint256 lastEvaluatedAt;
        bool isActive;
    }

    address public evalOracle;
    address public admin;

    // agentId => Agent
    mapping(bytes32 => Agent) public agents;
    // agentId => evaluationNonce
    mapping(bytes32 => uint256) public agentNonces;
    // payee wallet => primary registered agentId (for Confirmation of Payee lookup)
    mapping(address => bytes32) public ownerToAgentId;

    // EMA weight factor: alpha = 2000 (20.00%) for new evaluation, 8000 for prior EMA
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

    event EvalOracleUpdated(address indexed oldOracle, address indexed newOracle);
    event AdminTransferred(address indexed oldAdmin, address indexed newAdmin);
    event PrimaryPayeeAgentUpdated(address indexed payee, bytes32 indexed agentId);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }

    constructor(address _evalOracle) {
        require(_evalOracle != address(0), "Invalid eval oracle address");
        evalOracle = _evalOracle;
        admin = msg.sender;
    }

    /**
     * @notice Updates the evaluation oracle signer address.
     */
    function setEvalOracle(address newOracle) external onlyAdmin {
        require(newOracle != address(0), "Invalid eval oracle address");
        emit EvalOracleUpdated(evalOracle, newOracle);
        evalOracle = newOracle;
    }

    /**
     * @notice Transfers admin control to a new address.
     */
    function transferAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "Invalid admin address");
        emit AdminTransferred(admin, newAdmin);
        admin = newAdmin;
    }

    /**
     * @notice Registers a new autonomous agent and sets primary payee mapping if unset.
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

        if (ownerToAgentId[msg.sender] == bytes32(0)) {
            ownerToAgentId[msg.sender] = agentId;
            emit PrimaryPayeeAgentUpdated(msg.sender, agentId);
        }

        emit AgentRegistered(agentId, msg.sender, endpoint, metadataUri);
    }

    /**
     * @notice Links the caller's wallet to one of their registered agents for Confirmation of Payee lookup.
     */
    function setPayeeAgent(bytes32 agentId) external {
        Agent storage agent = agents[agentId];
        require(agent.owner == msg.sender, "Caller is not agent owner");
        require(agent.isActive, "Agent is inactive");
        ownerToAgentId[msg.sender] = agentId;
        emit PrimaryPayeeAgentUpdated(msg.sender, agentId);
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
     * @dev Digest binds agentId, nonce, qagScore, rubricHash, block.chainid, and address(this).
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

        bytes32 rawHash = keccak256(
            abi.encodePacked(agentId, nonce, qagScore, rubricHash, block.chainid, address(this))
        );
        bytes32 messageHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", rawHash)
        );

        address recovered = ecrecover(messageHash, v, r, s);
        require(recovered != address(0) && recovered == evalOracle, "Invalid evaluation oracle signature");

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
     * @notice Resolves a payee wallet address against the ERC-8004 agent registry (Confirmation of Payee).
     */
    function verifyPayee(address payee)
        external
        view
        returns (
            bool verified,
            bytes32 agentId,
            string memory endpoint,
            string memory metadataUri,
            uint256 reputationEmaBps,
            uint256 totalEvaluations
        )
    {
        bytes32 id = ownerToAgentId[payee];
        if (id == bytes32(0)) {
            return (false, bytes32(0), "", "", 0, 0);
        }
        Agent storage agent = agents[id];
        if (!agent.isActive || agent.owner != payee) {
            return (false, id, agent.endpoint, agent.metadataUri, agent.reputationEmaBps, agent.totalEvaluations);
        }
        return (true, id, agent.endpoint, agent.metadataUri, agent.reputationEmaBps, agent.totalEvaluations);
    }

    /**
     * @notice Returns complete agent information.
     */
    function getAgent(bytes32 agentId) external view returns (Agent memory) {
        require(agents[agentId].owner != address(0), "Agent not found");
        return agents[agentId];
    }
}
