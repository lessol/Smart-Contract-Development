// SPDX-license-Identifier: MIT

// Purpose: the reward token for engaging

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DappToken is ERC20 {

    constructor() public ERC20("Dapp Token", "DAPP") {
        // initial supply of 1 million
        _mint(msg.sender, 1000000000000000000000000);
    }
}


