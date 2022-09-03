from brownie import SimpleStorage, network, accounts, config

# interact with already deployed contracts on a network like rinkeby
def read_contract():
    # get the most recent deployment
    simple_storage = SimpleStorage[-1]
    # when working with a contract, brownie already know it address and ABI
    print(simple_storage.retreive()) # we expect to see 15

def main():
    read_contract()