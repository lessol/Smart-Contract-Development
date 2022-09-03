from brownie import network, Box, ProxyAdmin, TransparentUpgradeableProxy, Contract, BoxV2
from scripts.helpful_scripts import get_account, encode_function_data, upgrade

def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from":account}) # this is the implementation contract
    
    # hooking up a proxy to our implementation contract
    proxy_admin = ProxyAdmin.deploy({"from": account})

    #encode the initializer function into bytes
    initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from":account, "gas_limit": 1000000},
    )

    print(f"Proxy deployed to {proxy}, you can now upgrade to V2!")
    # assign this proxy address the abi of the Box contract
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    
    # upgrade from Box to BoxV2 to use increment function
    box_v2 = BoxV2.deploy({"from":account})
    upgrade_transaction = upgrade(
        account, 
        proxy, 
        box_v2.address, 
        proxy_admin_contract = proxy_admin
    )
    upgrade_transaction.wait(1)
    print("Proxy has been updated!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from":account})
    print(proxy_box.retreive())


