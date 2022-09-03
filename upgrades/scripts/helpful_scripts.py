from brownie import accounts, network, config
import eth_utils

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)  
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    # default
    return accounts.add(config["wallets"]["from_key"])

# initializer = box.store, (1, 2, 3, 4, 5) are the arguments passed to store()
def encode_function_data(initializer=None, *args):
    # if there is no initializer or there are 0 args return empty hex string
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    # return the encoded bytes
    return initializer.encode_input(*args)

def upgrade(account, 
    proxy, 
    new_implementation_address,
    proxy_admin_contract=None, 
    initializer=None, 
    *args
):  
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encode_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                new_implementation_address,
                encode_function_call,
                {"from":account}
            )
        else:
            transaction = proxy_admin_contract.upgrade(proxy.address, new_implementation_address, {"from":account})
    else:
        if initializer:
            encode_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                new_implementation_address, 
                encode_function_call,
                {"from":account}
            )
        else:
            transaction = proxy_admin_contract.upgradeTo(new_implementation_address, {"from": account})
    
    return transaction

