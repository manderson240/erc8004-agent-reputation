// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/ERC8004AgentRegistry.sol";

contract DeployERC8004 is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployerAddr = vm.addr(deployerPrivateKey);
        address evalOracle = vm.envOr("EVAL_ORACLE", deployerAddr);

        vm.startBroadcast(deployerPrivateKey);
        ERC8004AgentRegistry registry = new ERC8004AgentRegistry(evalOracle);
        console.log("ERC8004AgentRegistry deployed at:", address(registry));
        console.log("Eval oracle:", evalOracle);
        console.log("Chain ID:", block.chainid);
        vm.stopBroadcast();
    }
}
