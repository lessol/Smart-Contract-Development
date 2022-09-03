// An NFT Contract
// Where the tokenURI can be one of three different dogs
// Randomly Selected

// SPDX-license-Identifier: MIT

pragma solidity ^0.6.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol"; // for verifiably random attribute

contract AdvancedCollectible is ERC721, VRFConsumerBase {

    uint256 public tokenCounter;
    bytes32 public keyhash;
    uint256 public fee;

    // mapping from tokenId to breed
    mapping(uint256 => Breed) public tokenIdToBreed;
    // mapping from requestId to sender account
    mapping(bytes32 => address) public requestIdToSender;

    // events for the mappings
    event requestedCollectible(bytes32 indexed requestId, address requester);
    event breedAssigned(uint256 indexed tokenId, Breed breed);

    enum Breed{PUG, SHIBA_INU, ST_BERNARD} 

    constructor(address _vrfCoordinator, address _linkToken, bytes32 _keyhash, uint256 _fee) public 
    VRFConsumerBase(_vrfCoordinator, _linkToken) 
    ERC721("Pug", "Dog") 
    {
        tokenCounter = 0;
        keyhash = _keyhash;
        fee = _fee;
    }

    function createCollectible() public returns(bytes32) {
        // create the randomness request to get a random breed (different URI) for the dog
        bytes32 requestId = requestRandomness(keyhash, fee);
        // Map requestId to sender of the function createCollectible
        requestIdToSender[requestId] = msg.sender;
        emit requestedCollectible(requestId, msg.sender);
    }

    // internal override since it is VRFCoordinator calling this function
    function fulfillRandomness(bytes32 requestId, uint256 randomNumber) internal override {
        // get a random breed from random number
        Breed theBreed = Breed(randomNumber % 3);
        // mapping to assign tokenId to random breed
        uint256 newTokenId = tokenCounter;
        tokenIdToBreed[newTokenId] = theBreed;
        emit breedAssigned(newTokenId, theBreed);
        // get the sender of this account
        address owner = requestIdToSender[requestId];
        // mint the token
        _safeMint(owner, newTokenId);
        // increment tokenCounter
        tokenCounter = tokenCounter + 1;
    }

    function setTokenURI(uint256 tokenId, string memory _tokenURI) public {
        // three token URIs for the three dogs
        // make it so that only the owner of the tokenId can change the token_URI
        require(_isApprovedOrOwner(_msgSender(), tokenId), "ERC721: caller is not owner nor approved");
        _setTokenURI(tokenId,_tokenURI);
    }
}