from brownie import network, AdvancedCollectible
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract, get_account
from scripts.advanced_collectible.deploy_and_create import deploy_and_create
import pytest

def test_can_create_advanced_collectible():
    #deploy a contract
    # create an NFT
    # get a random breed back

    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    # Act
    advanced_collectible, creatiion_tx = deploy_and_create()
    requestId = creatiion_tx.events["requestedCollectible"]["requestId"]
    randomNum = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, randomNum, advanced_collectible.address, {"from": get_account()})
    # Assert
    # check to see if the token counter has increased
    assert (advanced_collectible.tokenCounter() == 1)
    assert (advanced_collectible.tokenIdToBreed(0)) == randomNum % 3