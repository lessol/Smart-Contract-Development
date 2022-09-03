from brownie import network, AdvancedCollectible
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract, get_account
from scripts.advanced_collectible.deploy_and_create import deploy_and_create
import pytest
import time

def test_can_create_advanced_collectible_integration():
    #deploy a contract
    # create an NFT
    # get a random breed back

    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for integration testing")
    # Act
    advanced_collectible, creatiion_tx = deploy_and_create()
    time.sleep(60)
    # Assert
    # check to see if the token counter has increased
    assert (advanced_collectible.tokenCounter() == 1)