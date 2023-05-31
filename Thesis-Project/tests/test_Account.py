import sys
sys.path.append('c:\\Users\\migue\\PES V2\\Thesis-Project')

import pytest
from testUtil import *
from Classes.Account import Account
from algosdk.account import generate_account
from algosdk.v2client.algod import AlgodClient
from algosdk.mnemonic import to_private_key

@pytest.fixture
def non_existing_account(setup_algod_client):
    # Generates a account
    new_private_key, new_public_key = generate_account()
    account = Account(new_private_key, new_public_key, setup_algod_client)
    return account

def test_account_exists(setup_account):
    assert setup_account.account_exists()

def test_account2_exists(setup_account2):
    assert setup_account2.account_exists()

def test_account_doesnt_exists(non_existing_account):
    assert non_existing_account.account_exists() == False

def test_existing_account_no_apps(setup_account):
    print(setup_account.get_created_apps())
    assert setup_account.get_created_apps() == []

def test_existing_account2_no_apps(setup_account2):
    assert setup_account2.get_created_apps() == []