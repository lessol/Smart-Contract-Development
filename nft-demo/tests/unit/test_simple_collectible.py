from brownie import SimpleCollectible, network
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.simple_collectible.deploy_and_create import deploy_and_create
import pytest

def test_can_create_simple_collectible():
    # since this is a unit test, we're only using development env
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    simple_collectible = deploy_and_create()
    
    assert simple_collectible.ownerOf(0) == get_account()