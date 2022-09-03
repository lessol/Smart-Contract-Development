import pytest
from web3 import Web3
# create a fixture
@pytest.fixture
def amount_staked():
    return Web3.toWei(1, "ether")