from brownie import network, accounts, config
import pytest
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, fund_with_link
from scripts.deploy import deploy_lottery
import time

def test_can_pick_winner():
    # if network is not testnet skip
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()

    # start the lottery from admin account
    lottery.startLottery({"from": account})

    # enter the lottery
    lottery.enter({"from":account, "value": lottery.getEntranceFee()})
    lottery.enter({"from":account, "value": lottery.getEntranceFee()})

    # fund the lottery with LINK to get random number
    fund_with_link(lottery)
    
    #end the lottery
    lottery.endLottery({"from":account})

    # it will take some time for the chainlink node to respond
    time.sleep(60)

    # check for the winner
    assert lottery.recentWinner() == account
    assert lottry.balance() == 0
    
