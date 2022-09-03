from brownie import FundMe, MockV3Aggregator, accounts, network, config
# get functions from other scripts
from scripts.helpful_scripts import get_account, deploy_mocks, LOCAL_BLOCKCHAIN_ENVIRONMENTS


def deploy_fund_me():
    account = get_account()
    # need to pass the price feed address to out fundme contract
    # the publish_source = true says we would like to publish and verify this contract

    # if we are on a persistent network like rinkeby, use the associated address
    # otherwise, deploy mocks
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        price_feed_address = config["networks"][network.show_active()]["eth_usd_price_feed"]
    # else if we are on a development chain
    else:
        deploy_mocks()
        # if there is already MockV3Aggregator contracts deployed, use the most recent one
        price_feed_address = MockV3Aggregator[-1].address

    fund_me = FundMe.deploy(
    price_feed_address,
    {"from": account}, 
    publish_source=config["networks"][network.show_active()]["verify"]
    )
    print(f"Contract deployed to {fund_me.address}")
    return fund_me

def main():
    deploy_fund_me()