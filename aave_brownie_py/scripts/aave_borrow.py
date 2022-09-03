from scripts.helpful_scripts import get_account
from brownie import network, config, interface
from scripts.get_weth import get_weth
from web3 import Web3
# the amount 
amount = Web3.toWei(0.1, "ether")

def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    
    # if using a local blockchain environment
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    
    # get the lending pool contract
    lending_pool = get_lending_pool()
    # approve sending out ERC20 tokens
    approve_erc20(amount, lending_pool.address, erc20_address, account)

    #deposit into lending pool
    print("Depositing...")
    #function deposit(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)
    tx = lending_pool.deposit(erc20_address,amount, account.address, 0, {"from": account})
    tx.wait(1)
    print("Deposited!")

    #get user account data: deposit info, collateral info, debt, ...
    # based on user data, how much can we borrow
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow some DAI")
    # need to get DAI in terms of ETH
    dai_eth_price_feed = config["networks"][network.show_active()]["dai_eth_price_feed"]
    dai_eth_price = get_asset_price(dai_eth_price_feed)
    
    # borrowable_eth -> borrowable_dai * 95% b/c we don't want to get liquidated
    amount_dai_to_borrow = (1/dai_eth_price) * (borrowable_eth * 0.95)
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")

    # lets borrow
    print("Now we will borrow!")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    # borrow(address asset, uint256 amount, uint256 interestRateMode, uint16 referralCode, address onBehalfOf)
    borrow_tx = lending_pool.borrow(
        dai_address, 
        Web3.toWei(amount_dai_to_borrow, "ether"), 
        1, 
        0, 
        account.address, 
        {"from":account}
    )
    borrow_tx.wait(1)
    print("We have borrowed some DAI")
    # how much did we borrow. Get account data
    get_borrowable_data(lending_pool, account)

    #repay the borrowed amount
    repay_all(amount, lending_pool, account)
    print("You just deposited, borrowed, and repayed with Aave, Brownie, and Chainlink")

def repay_all(amount, lending_pool, account):
    # approve sending out ERC20 token
    approve_erc20(
        Web3.toWei(amount, "ether"), 
        lending_pool, 
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account, 
        {"from":account}
    )
    repay_tx.wait(1)
    print("Repayed!!")

def get_asset_price(price_feed_address):
    # get ABI and address to work with contract. Use interface
    # dai_eth_price_feed is now a contract we can interact with
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1] # answer is at index 1
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH price is {converted_latest_price}")
    return float(converted_latest_price) #334437918817434


def get_borrowable_data(lending_pool, account):
    #function getUserAccountData(address user)
    (
        total_collateral_eth, 
        total_debt_eth, 
        available_borrow_eth, 
        current_liquidation_threshold,
        ltv,
        health_factor,
    )=lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH deposited.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return(float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    # need address and abi
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved")
    return tx

def get_lending_pool():
    # abi and address needed to work with getLending contract
    # use interface to get abi and address
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_addreses = lending_pool_addresses_provider.getLendingPool() #address
    lending_pool = interface.ILendingPool(lending_pool_addreses)
    return lending_pool

