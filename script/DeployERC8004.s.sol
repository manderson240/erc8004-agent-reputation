// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/ERC8004AgentRegistry.sol";

contract DeployERC8004 is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envOr("PRIVATE_KEY", uint256(0));
        if (deployerPrivateKey != 0) {
            vm.startBroadcast(deployerPrivateKey);
        } else {
            vm.startBroadcast();
        }
        (, address deployerAddr,) = vm.readCallers();
        address evalOracle = vm.envOr("EVAL_ORACLE", deployerAddr);

        ERC8004AgentRegistry registry = new ERC8004AgentRegistry(evalOracle);
        vm.stopBroadcast();

        console.log("ERC8004AgentRegistry deployed at:", address(registry));
        console.log("Deployer:", deployerAddr);
        console.log("Eval oracle:", evalOracle);
        console.log("Chain ID:", block.chainid);
        console.log("Explorer: https://explorer-test.qday.info/address/", address(registry));
    }
}
