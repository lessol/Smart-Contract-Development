// SPDX-Licence-Identifier: MIT

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

pragma solidity ^0.6.6;

contract Lottery is VRFConsumerBase {
    // I. variables

    // address of the admin or owner
    address admin;
    // address of the winner
    address payable public recentWinner;
    // most recent random number
    uint256 randomness;
    // static entrance fee
    uint256 public usdEntryFee;
    // array of type address to hold all players that 
    // paid to enter the lottery
    address payable[] public players;
    // AggregatorV3Interface
    AggregatorV3Interface internal ethUsdPriceFeed;
    // enum to represent lottery state
    enum LOTTERY_STATE {
        OPEN, 
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state; // var of type LOTTERY_STATE
    // fee for VRFConsumerBase
    uint256 public fee; // this can change from blockchain to blockchain
    bytes32 public keyhash; // a way to uniquely identify the chainlink VRF node
    // event
    event RequestedRandomness(bytes32 requestId);

    // a constructor with inheritance from VRFConsumerBase
    constructor(
        address _priceFeedAddress, 
        address _vrfCoordinator, 
        address _link,
        uint256 _fee,
        bytes32 _keyhash
        ) public VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        // set lottery state to close when lottery is deployed
        lottery_state = LOTTERY_STATE.CLOSED;
        // set owner or admin
        admin = msg.sender;
        fee = _fee;
        keyhash = _keyhash;
    }

    // 1. function to enter the lottery
    function enter() public payable{
        // someone can only enter the lottery if the lottery is open
        require (lottery_state == LOTTERY_STATE.OPEN);
        // $50 minimum to enter the lottery is required
        require(msg.value >= getEntranceFee(), "Not enough ETH");
        // add the the sender of the function call to players array
        players.push(msg.sender);
    }
    
    // 2. function to establish the fee to enter the lottery
    function getEntranceFee() public view returns(uint256){
        // get the price
        (,int256 price,,,) = ethUsdPriceFeed.latestRoundData();
        // convert int256 price to uint256
        uint256 adjustedPrice = uint256(price) * 10**10; // 18 decimals
        // $50, $2000 per ETH, to get price in eth: 50/2000
        // however solidity does not work with decimals
        uint256 costToEnter = (usdEntryFee * 10 ** 18) / adjustedPrice;

        return costToEnter;
    }

    // admin modifier
    modifier onlyAdmin {
        require(msg.sender == admin);
        _;
    }

    // 3. function for the admin to start the lottery
    function startLottery() public onlyAdmin {
        // initially lottery is closed, once this function is called its opened
        // function can only be called by admin
        require(lottery_state == LOTTERY_STATE.CLOSED, "Can't start a new lottery yet");
        lottery_state = LOTTERY_STATE.OPEN;
    }

    // 4. function for the admin to end the lottery
    function endLottery() public onlyAdmin{
        // when we are ending a lottery, we are calculating the winner
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        // returns (bytes32 requestId) means it will return a bytes32 var called requestId
        bytes32 requestId = requestRandomness(keyhash, fee);
        emit RequestedRandomness(requestId);
    }

    // internal b/c we only want our chainlink node to call this function
    // override means were overriding the original declaration of this function 
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER, "You aren't there yet!");
        require(_randomness > 0, "random-not-found");
        
        // pick a random winner based on random number generated and number of players
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        
        // transfer all the money from this lottery to the winner
        recentWinner.transfer(address(this).balance);

        // reset lottery
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}