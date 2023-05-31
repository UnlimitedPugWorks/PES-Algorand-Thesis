import sys
sys.path.append('c:\\Users\\migue\\PES V2\\Thesis-Project')

import pytest
from Classes.PinataSDK import PinataSDK
from Classes.Account import Account
from Classes.LandRegistry import LandRegistry
from Classes.SmartContract import get_app_address
from algosdk.v2client.algod import AlgodClient
from algosdk.mnemonic import to_private_key
from testUtil import *

def pytest_configure():
    pytest.land_registry_app_id = 0
    pytest.new_asset_id = 0


@pytest.fixture
def deploy_land_registry(setup_account):
    land_registry = LandRegistry(setup_account, 0)
    assert land_registry.app_id != 0
    pytest.land_registry_app_id = land_registry.app_id
    return land_registry



def test_register_land(setup_algod_client, setup_account, deploy_land_registry, setup_pinata):
    land_registry = deploy_land_registry
    app_id = land_registry.app_id
    created_assets = setup_algod_client.account_info(get_app_address(app_id))['created-assets']
    total_created_assets = len(created_assets)
    new_asset_id = land_registry.register_land("test_name", "test_description", "tst", "land_deed.jpg", "land_deed.jpg", setup_pinata)
    created_assets = setup_algod_client.account_info(get_app_address(app_id))['created-assets']
    # Verifies if a new asset has been created
    assert len(created_assets) == (total_created_assets + 1)
    # Verifies if the new asset id is in the created assets
    assert verify_in_created_assets(new_asset_id, created_assets)
    pytest.new_asset_id = new_asset_id

def test_transfer_land(setup_algod_client, setup_account, setup_account2):
    # The asset Id of the registered land
    new_asset_id = pytest.new_asset_id
    # Land Registry is loaded
    land_registry = LandRegistry(setup_account, pytest.land_registry_app_id)
    # The App Id of the land registry
    app_id = land_registry.app_id
    # Receiver address which is going to receive the NFT
    receiver_address = setup_account2.address
    # Now that the asset has been successfuly created we will transfer it
    # The receiver_address must opt in to the asset otherwise it can't receive it
    setup_account2.opt_in_to_asset(new_asset_id)
    assets = setup_algod_client.account_info(receiver_address)['assets']
    # Verifies if the account opted in to the asset
    assert verify_in_assets(new_asset_id, assets)
    # Transfers land
    land_registry.transfer_land(receiver_address, new_asset_id)
    assets = setup_algod_client.account_info(receiver_address)['assets']
    # Verifies if the account has received the asset
    assert hasAsset(new_asset_id, assets)
    # Verifies if the land has not received the asset
    app_assets = setup_algod_client.account_info(get_app_address(app_id))['assets']
    assert noAsset(new_asset_id, app_assets)

def test_clawback_land(setup_algod_client, setup_account, setup_account2):
    # The asset Id of the registered land
    new_asset_id = pytest.new_asset_id
    # Land Registry is loaded
    land_registry = LandRegistry(setup_account, pytest.land_registry_app_id)
    print(land_registry.app_id)
    # The App Id of the land registry
    app_id = land_registry.app_id
    # Receiver address is the address that is going to be clawbacked
    receiver_address = setup_account2.address
    # Does a clawback
    land_registry.clawback_land(receiver_address, new_asset_id)
    # Verifies if the app has the clawbacked asset
    app_assets = setup_algod_client.account_info(get_app_address(app_id))['assets']
    assert hasAsset(new_asset_id, app_assets)
    # Verifies if the account that has been clawbacked no longer has the asset
    assets = setup_algod_client.account_info(receiver_address)['assets']
    assert noAsset(new_asset_id, assets)




