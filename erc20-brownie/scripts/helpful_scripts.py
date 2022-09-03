from brownie import (accounts, 
    network, 
    config, 
    MockV3Aggregator, 
    Contract, 
    VRFCoordinatorMock, 
    LinkToken,
    interface
)

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]

def get_account(index=None, id=None):
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)  
    # local blockchain
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS 
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    # default
    return accounts.add(config["wallets"]["from_key"])
