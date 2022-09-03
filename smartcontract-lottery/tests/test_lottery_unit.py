
# current price of ETH: 2,846
# for $50 we currently expect to get: 0.017 eth or 170000000000000000

from brownie import Lottery, accounts, network, config, exceptions
from scripts.deploy import deploy_lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract,fund_with_link
from web3 import Web3
import pytest

def test_get_entrance_fee():
    # since this only works in development networks, skip if not development
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #Arrange
    lottery = deploy_lottery()
    #Act
    # if the price of eth is 2,000 eth/usd and usdEntranceFee is 50usd
    # 2000/1 == 50/x == 0.025
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    #Assert
    assert (expected_entrance_fee == entrance_fee)

def test_cant_enter_unless_started():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # act/assert
    # ignores the virtualmachineError and performs the test to see if any account can 
    # enter a lottery that has not started
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from":get_account(), "value": lottery.getEntranceFee()})

def test_can_start_and_enter_lottery():
     # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    #act
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from":account, "value": lottery.getEntranceFee()})
    #assert
    # check that the account that enter the lottery is part of the players array
    assert lottery.players(0) == account

def test_can_end_lottery():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # act
    account = get_account()
    # start the lottery
    lottery.startLottery({"from":account})
    # have an account enter the lottery
    lottery.enter({"from":account, "value": lottery.getEntranceFee()})
    # fund the lottery with link to get random number and end lottery
    fund_with_link(lottery)
    lottery.endLottery({"from":account})
    # check if lottery has ended and closed
    assert lottery.lottery_state() == 2 # CALCULATING_WINNER

def test_can_pick_winner_correctly():
     # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    # act
    account = get_account()
    # start the lottery
    lottery.startLottery({"from":account}) 
    # enter the lottery from different accounts
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    # fund the lottery with link to get random number and end lottery
    fund_with_link(lottery)
    # end lottry and choose a winner 
    transaction = lottery.endLottery({"from":account})
    # get the event where winner is chosen
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    # this is a dummy event of getting a response(a random number) from a chainlink node
    get_contract("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RNG, lottery.address, {"from":account})

    # assert 

    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    # winner is 777 % 3 players = 0
    # check that recent winner is account[0]
    assert lottery.recentWinner() == account
    # check that lottery balance is now 0
    assert lottery.balance() == 0
    # check that account[0] received all the money from lottery
    assert account.balance() == starting_balance_of_account + balance_of_lottery
