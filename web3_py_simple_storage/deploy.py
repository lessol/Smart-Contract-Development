from solcx import compile_standard
import json
from web3 import Web3
import os

# open/read solidity file
with open("./SimpleStorage.sol", "r") as file:
    simpleStorage_file = file.read()

# Compile our solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simpleStorage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode","evm.sourceMap"]}
            }
        },
    
    },
    solc_version="0.6.0",
)

with open("compiled_code.json","w") as file:
    json.dump(compiled_sol,file)


# I. To deploy a contract

#1. Get the bytecode

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

#2. Get the abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# II. Connect to a blockchaoin VM Ganache

# for connecting to rinkeby or ganache
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/5dc5280102e74530bdce302fd94f3324"))
chain_id = 4
# an address to deploy from
my_address = "0x0B1B857Aacea6A820107e6c136E3710448Fb1498"
# the private key for this address to sign transactions
private_key = os.getenv("PRIVATE_KEY")


# III. Create the contract in python
# we have a contract now
SimpleStorage = w3.eth.contract(abi=abi, bytecode = bytecode)

# Get the latest transaction count or nonce
nonce = w3.eth.getTransactionCount(my_address)

# IV. Deploying the contract
    #1. build a transaction
    #2. sign a transaction
    #3. send a transaction

transaction = SimpleStorage.constructor().buildTransaction({"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from":my_address, "nonce": nonce})

# sign a transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print("Deploying contract...")

#send the signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# get transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Deployed")

# V. Working with the contract
# when working with a contract you always need the:
# Contract Address and Contract ABI

# contract address
simple_storage = w3.eth.contract(address = tx_receipt.contractAddress, abi=abi)

# two ways to interact with transactions 
#1. Call => Simulate making the call and getting a return value. Don't make a state change 
#2. Transact => Actually make a state change

# Initial value of favorite number
print(simple_storage.functions.retreive().call())
print("Updating contract...")

# to make a state change on the contract we have to make a transaction
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"gasPrice": w3.eth.gas_price,"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

transaction_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Updated!")
print(simple_storage.functions.retreive().call())