from brownie import SimpleStorage, accounts, config



# testing setup: 1. Arrange, 2. Act, 3. Assert

# to test one function: brownie test -k test_deploy()
# to test in python shell: brownie test -pdb
# more robust testing with comments: brownie test -s

# first test
def test_deploy():
    # Arrange
    account = accounts[0]
    # Act
    simple_storage = SimpleStorage.deploy({"from": account})
    stored_value = simple_storage.retreive()
    expected = 0
    # Assert
    assert stored_value == expected

# 2nd test
def test_updating_storage():
    # Arrange
    account = accounts[0]
    simple_storage = SimpleStorage.deploy({"from": account})
    # Act
    expected = 15
    simple_storage.store(expected, {"from": account})
    # Assert
    assert expected == simple_storage.retreive()