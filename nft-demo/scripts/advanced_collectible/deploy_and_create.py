from brownie import AdvancedCollectible, config, network
from scripts.helpful_scripts import get_account, OPENSEA_URL, get_contract, fund_with_link
from web3 import Web3

def deploy_and_create():
    account = get_account()
    # We want to be able to use the deployed contracts if we are on a trstnet
    # Otherwise, we want to deploy some mocks and use those
    # Opensea testnet only works with rinkeby
    advanced_collectible = AdvancedCollectible.deploy(
        get_contract("vrf_coordinator"),
        get_contract("link_token"),
        config["networks"][network.show_active()]["keyhash"],
        config["networks"][network.show_active()]["fee"],
        {"from":account}
    )
    fund_with_link(advanced_collectible.address, amount=Web3.toWei(0.1, "ether"))
    creating_tx =  advanced_collectible.createCollectible({"from":account})
    creating_tx.wait(1)
    print("New token has been created!!")
    # returning the creating_tx to then get the requestId for mock fulfill randomness
    return advanced_collectible, creating_tx
   

def main():
    deploy_and_create()