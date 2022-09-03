// SPDX-License-Identifier: MIT

pragma solidity 0.6.6;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

// Inherit ERC721 contract
contract SimpleCollectible is ERC721 {

    // the amount of tokens minted
    uint256 public tokenCounter;

    constructor () public ERC721("Dog", "PUG"){
        tokenCounter = 0;
    }

    // create the collectible 
    function createCollectible(string memory tokenURI) public returns(uint256) {
        uint256 newTokenId = tokenCounter;
        // _safeMint(Owner_address, uniqueTokenId)
        _safeMint(msg.sender, newTokenId);
        // allow the nft to have an image associated with it through tokenURI
        _setTokenURI(newTokenId, tokenURI);
        tokenCounter = tokenCounter + 1;
        return newTokenId;
    }

}