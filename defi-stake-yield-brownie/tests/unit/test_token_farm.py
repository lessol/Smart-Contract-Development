from brownie import network, TokenFarm, exceptions
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, INITIAL_PRICE_FEED_VALUE
from scripts.deploy import deploy_token_farm_and_dapp_token
import pytest

def test_set_price_feed_contract():
    #arrange
    # since this is a unit, check if we're on a local network
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    non_owner = get_account(index=1) # this gives a different account
    # get the deployed contracts
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    #Act
    price_feed_address = get_contract("eth_usd_price_feed")
    token_farm.setPriceFeedContract(dapp_token.address, price_feed_address, {"from":account})
    # assert
    assert token_farm.tokenPriceFeedMapping(dapp_token.address) == price_feed_address
    # setPriceFeedContract is onlyOwner. 
    # Test to see if a non-owner can call it. this will raise an exception
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(dapp_token.address, price_feed_address, {"from":non_owner})
    

def test_stake_tokens(amount_staked):
    #arrange
    # since this is a unit, check if we're on a local network
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    # get the deployed contracts
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    # send dapp_tokens to token_farm. need to approve transfer first
    dapp_token.approve(token_farm.address, amount_staked, {"from":account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from":account})
    # Assert
    assert (
        token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked
    )
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, dapp_token

def test_issue_tokens(amount_staked):
    #arrange
    # since this is a unit, check if we're on a local network
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    # get the starting balance of the account
    starting_balance = dapp_token.balanceOf(account.address)
    print(f"The starting balance of this account is {starting_balance}")
    # Act
    token_farm.issueTokens({"from":account})
    # assert
    # we are staking 1 dapp_token == in price to 1 ETH
    # soo.. we should get 2,000 dapp tokens in reward since the price of eth is 2000
    assert(
        dapp_token.balanceOf(account.address) == starting_balance + INITIAL_PRICE_FEED_VALUE
    )
