from brownie import network, MockV3Aggregator, config, accounts
from web3 import Web3

DECIMALS = 8
STARTING_PRICE = 200000000000
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]

def get_account():
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS 
    or network.show_active() in FORKED_LOCAL_ENVIRONMENTS):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])

def deploy_mocks():
    print(f"The active networkis {network.show_active()}")
    print("Deploying Mocks...")
    # check if MockV3Aggregator contract has already been deployed
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(DECIMALS, Web3.toWei(STARTING_PRICE,"ether"), {"from": get_account()})
    print("MOCKS Deployed!!")


