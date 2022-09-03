from scripts.helpful_scripts import get_account
from brownie import interface, network, config, accounts

def get_weth():
    # Mint WETH by depositing ETH. we need to interact with the weth kovan contract 
    # to interact w/ the contract we need the address and abi. do this through interface
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from":account, "value": 0.1 * 10**18}) # depost 0.1 eth
    tx.wait(1)
    print(f"Received 0.1 WETH")
    return tx

def main():
    get_weth()
