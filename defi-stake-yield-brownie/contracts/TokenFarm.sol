// SPDX-License-Identifier: MIT

// purpose: stakeTokens, unStakeTokens, issueTokens as reward, addAllowedTokens, getEthValue

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable{

    // DappToken to be rewarded
    IERC20 public dappToken;
    // array that holds the address of allowed tokens
    address[] public allowedTokens;
    // address array that holds the addresses of all the stakers
    address[] public stakers;
    // mapping to map token address -> staker address -> amount staked
    mapping(address => mapping(address => uint256)) public stakingBalance;
    // mapping to map the user's address -> amount of unique tokens staked
    mapping(address => uint256) public uniqueTokensStaked;
    // mapping to map a token to its associated priceFeed
    mapping(address => address) public tokenPriceFeedMapping;



    constructor(address _dappTokenAddress) public {
        // get the dappToken address that will be rewarded
        dappToken = IERC20(_dappTokenAddress);  
    }

    // function to set the price feed associated with a token
    function setPriceFeedContract(address _token, address _priceFeed) public onlyOwner{
        tokenPriceFeedMapping[_token] = _priceFeed;
    }

    // function to issue DappToken's as a reward for staked amount
    function issueTokens() public onlyOwner {
        // Issue tokens to all stakers by iterating through list of stakers
        for (uint256 i = 0; i < stakers.length; i++) {
            address recipient = stakers[i]; // get a staker's address

            // send the recipient DappTokens based on total value locked
            uint256 userTotalValue = getUserTotalValue(recipient);
            // can use transfer function b/c our contract owns the tokens being rewarded
            dappToken.transfer(recipient, userTotalValue);
        }
    }

    function getUserTotalValue(address _user) public view returns(uint256){
        // totalValue is the total value the user has across all tokens staked
        uint256 totalValue = 0;
        // if user has no tokens staked their tvl is 0
        require(uniqueTokensStaked[_user] > 0, "No tokens staked!");
        // if they have tokens staked, find them and get their total value
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            totalValue = totalValue + getUserSingleTokenValue(_user, allowedTokens[i]);
        }
        // return the total value lockced of all tokens
        return totalValue;
    }

    // get how much of a single token does a user have staked
    function getUserSingleTokenValue(address _user, address _token) public view returns(uint256) {
        // if they staked 1 ETH, we return $2000. if they staked 200 DAI, return $200

        // user has no tokens staked
        if (uniqueTokensStaked[_user] <= 0) {
            return 0;
        }

        // need the price of the token.
        // token value = price of the token * amount the user has staked for this token
        (uint256 price, uint256 decimals) = getTokenValue(_token);
        uint256 tokenValue = (price *  stakingBalance[_token][_user]) / (10**decimals);
        return tokenValue;
    }

    function getTokenValue(address _token) public view returns(uint256, uint256) {
        // priceFeedAddress
        address priceFeedAddress = tokenPriceFeedMapping[_token];
        // grab the price feed contract for this token
        AggregatorV3Interface priceFeed = AggregatorV3Interface(priceFeedAddress); 
        // get the current price of the token
        (,int256 price,,,) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());
        // return the price of the tokens and the decimals it uses
        return (uint256(price), decimals);
    }

    // stake some amount of some token provided by its token address
    function stakeTokens(uint256 _amount, address _token) public {
        // what tokens can they stake? 
        // how much can they stake? any amount greater than 0
        require(tokenIsAllowed(_token), "Token is currently not allowed");
        require(_amount > 0, "Staked amount must be more than 0");

        // using transferFrom b/c our contract dosen't own the ERC20 tokens
        // get token abi via IERC20 interface
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);

        // update the amount of unique/different tokens a user has staked
        updateUniqueTokensStaked(msg.sender, _token);
        
        // map token address -> staker address -> amount staked
        stakingBalance[_token][msg.sender] = stakingBalance[_token][msg.sender] + _amount;

        // add staker to list of stakers, only if they are not already on the list
        // check if the user's uniqueTokensStaked is = 1, meaning they just staked, thus add to list
        // this is using a mapping via dictionary, checking if the user calling has any tokens staked.
        if (uniqueTokensStaked[msg.sender] == 1) {
            stakers.push(msg.sender);
        }
    }

    // internal function so that only this contract can call this function
    function updateUniqueTokensStaked(address _user, address _token) internal {
        // if the user's staked balance is less than 0. no tokens have been staked
        if (stakingBalance[_token][_user] <= 0) {
            // increase the unique Tokens Staked of this user by 1
            uniqueTokensStaked[_user] = uniqueTokensStaked[_user] + 1;
        }
    }

    // only the admin can add allowed tokens to array or list of allowedTokens
    function addAllowedTokens(address _token) public onlyOwner {
        allowedTokens.push(_token);
    }

    // return if a token is allowed in TokenFarm
    function tokenIsAllowed(address _token) public returns(bool) {
        // iterate through allowedTokens array & check if _token is in the list
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            if(allowedTokens[i] == _token) {
                return true;
            }
        }
        return false;
    }

    // function to unstake staked tokens. public so that anyone can call this
    function unstakeTokens(address _token) public {
        // find out how much of this token does the user have
        uint256 balance = stakingBalance[_token][msg.sender];
        require(balance > 0, "Staking balance cannot be 0");

        // transfer
        IERC20(_token).transfer(msg.sender, balance);
        
        // update staking balance of this token
        stakingBalance[_token][msg.sender] = 0;

        // update the amount of unique tokens this user has staked. reduce by 1
        uniqueTokensStaked[msg.sender] = uniqueTokensStaked[msg.sender] - 1;

        // if this user no longer has any tokens staked, remove them from stakers list/array
        // not really necessary
    }
}
