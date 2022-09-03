from brownie import Lottery, accounts, network, config
from scripts.helpful_scripts import get_account, get_contract, fund_with_link
import time

def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy( 
        get_contract("eth_usd_price_feed").address, # eth_usd contract address
        get_contract("vrf_coordinator").address, #vrf coordinator address
        get_contract("link_token").address, #link token address
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
        )
    print("Deployed Lottery")
    return lottery

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from":account})
    starting_tx.wait(1) # good practice to wait for the last transaction to go through
    print("The lottery has started!")

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1] # get the most recent contract
    value = lottery.getEntranceFee() + 10000000 # get the entrance fee for the lottery
    # enter the lottery. This is a transaction & payable, so a value must be provided for msg.value
    tx = lottery.enter({"from":account, "value":value}) 
    tx.wait(1)
    print("You have entered the lottery!!")

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund the contract with LINK to get random number
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    # now we can end the lottery
    end_lottery_tx = lottery.endLottery({"from": account})
    end_lottery_tx.wait(1)
    # to wait 60 seconds. It usually takes some time to receive info back from chainlink node
    # we're waiting to get the winner
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner!")
    print("The lottery has ended!")

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()