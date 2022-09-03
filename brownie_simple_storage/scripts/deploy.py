# import adress and private key
from brownie import accounts, config, SimpleStorage, network
import os

# 3 ways to add accounts with address to test with

# 1. Brownie local ganache-cli accounts
# account = accounts[0]

# 2. add accounts natively to brownie script
# brownie accounts new freecode-account
# account = accounts.load("freecode-account")

# 3. private key in env
# create a .env file and add export PRIVATE_KEY
# create brownie-config.yaml and add dotenv: .env
# account = accounts.add(os.getenv("PRIVATE_KEY"))
# or
# in brownie-config.yaml add wallets: from_key: ${PRIVATE_KEY}
# account = accounts.add(config["wallets"]["from_key"])


def deploy_simple_storage():
    account = get_account()
    simple_storage = SimpleStorage.deploy({"from": account})
    # brownie knows if a function is a call or transact
    stored_value = simple_storage.retreive()
    print(stored_value)
    transaction = simple_storage.store(15, {"from": account})
    # wait for a transaction to finish. how many blocks to wait
    transaction.wait(1)
    updated_stored_value = simple_storage.retreive()
    print(updated_stored_value)

def get_account():
    # working on a development network using local account
    if(network.show_active() == "development"):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])

def main():
    deploy_simple_storage()