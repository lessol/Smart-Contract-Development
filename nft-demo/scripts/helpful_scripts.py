from brownie import accounts, config, network, VRFCoordinatorMock, LinkToken, Contract
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache", "mainnet-fork"]
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"
#https://testnets.opensea.io/assets/{token_address}{token_id}

BREED_MAPPING = {0:"PUG", 1:"SHIBA-INU", 2:"ST_BERNARD"}

def get_breed(breed_num):
    return BREED_MAPPING[breed_num]


def get_account(index=None, id=None):
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)  
    # local blockchain
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS ):
        return accounts[0]
    # default
    return accounts.add(config["wallets"]["from_key"])

# mapping to map name to contract type
contract_to_mock = {
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}

def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]

    # check if we need to deploy a mock, are we on a local blockchain
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS):
        #check if the contract hasn't  been deployed
        if (len(contract_type) <= 0):  #MockV3Aggregator.length
            deploy_mocks()
        # grab most recent deployment of contract
        contract = contract_type[-1] #MockV3Aggregator[-1]
    
    # testnet
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # we have the address and ABI
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
        
    return contract

def deploy_mocks():
    """
    Use this script if you want to deploy mocks to a testnet
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    account = get_account()
    print("Deploying Mock LinkToken...")
    link_token = LinkToken.deploy({"from": account})
    print(f"Link Token deployed to {link_token.address}")
    print("Deploying Mock VRF Coordinator...")
    vrf_coordinator = VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print(f"VRFCoordinator deployed to {vrf_coordinator.address}")
    print("All done!")

def fund_with_link(
    contract_address, account=None, link_token=None, amount=Web3.toWei(0.3, "ether")
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    funding_tx = link_token.transfer(contract_address, amount, {"from": account})
    funding_tx.wait(1)
    print(f"Funded {contract_address}")
    return funding_tx
