import sys
sys.path.append('c:\\Users\\migue\\PES V2\\Thesis-Project')

import pytest
import pytz
import json
import requests
from pyrfc3339 import generate, parse
import base64
from Classes.Account import Account
from Classes.Oracle import Oracle, timestamp_to_rfc3339,rfc3339_step
from Classes.PESManager import PESManager
from Classes.PESManagerUser import PESManagerUser
from Classes.PESSchemeUser import PESSchemeUser
from Classes.PESSchemeAssetUser import PESSchemeAssetUser
from Classes.SmartContract import var_to_base64, MIN_BALANCE, LOCAL_BYTE_PRICE, LOCAL_INT_PRICE, GLOBAL_BYTE_PRICE, GLOBAL_INT_PRICE, box_cost, deploy_cost, local_storage_cost
from Classes.Request import Request
from Classes.SingleRequest import SingleRequest
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from algosdk.account import generate_account
from Classes.Request import Request
from algosdk.mnemonic import to_private_key
from algosdk.encoding import encode_address, checksum, decode_address
from os.path import isfile, exists, split
from testUtil import *
from time import sleep
from datetime import timezone, datetime

big_description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas nec lobortis augue. Vestibulum lacinia sit amet ex id pharetra. Proin luctus nisi faucibus semper mollis. Duis id tortor vitae turpis ultricies posuere id vitae ex. Maecenas aliquet posuere felis ut commodo. Duis eu mi orci. Mauris vel varius neque. Vestibulum mollis consequat pellentesque. Etiam feugiat elit nec mi placerat sagittis. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eleifend ante viverra urna cursus, vel venenatis tellus imperdiet. Pellentesque rutrum nec ipsum at tempor. Phasellus eleifend enim id arcu interdum, dapibus fermentum nibh vulputate. Mauris condimentum felis nisl, et feugiat nisi posuere sed. Mauris ac massa sit amet lorem cursus dignissim. Donec arcu magna, scelerisque vitae massa tristique, consectetur bibendum dui. Sed egestas massa elementum elit posuere, at vehicula urna tincidunt. Ut faucibus malesuada mauris lobortis eleifend. Nunc placerat enim ipsum, non dignissim tortor dapibus eget. Morbi bibendum tincidunt fringilla. Fusce sed turpis sagittis, luctus elit vel, gravida purus. Sed ac enim eu felis suscipit vestibulum non sit amet arcu. Cras eleifend purus nec lectus blandit egestas. Curabitur ac efficitur nulla. Integer a vehicula augue. Aenean sed nunc non turpis accumsan tempus. Morbi quis ullamcorper nunc, sit amet volutpat neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed elementum molestie est. Aliquam porta faucibus neque vitae malesuada. Nulla augue turpis, egestas porta mollis ac, egestas et mi. Proin lobortis magna id nisi interdum, et tincidunt risus vestibulum. Curabitur condimentum eros ac nisl commodo maximus. Phasellus dapibus mauris ut nisi fringilla, quis congue lacus tempor. Sed dignissim odio non ultricies tempus. Fusce nec facilisis tortor, ac porta metus. Aenean massa velit, accumsan sit amet nisi a, placerat tincidunt odio. Fusce quis sapien augue. Suspendisse potenti. Nam iaculis gravida elit at pretium. Sed sollicitudin ullamcorper nibh, ut posuere turpis. Mauris at neque interdum, sodales ligula tristique, bibendum ex. Nam hendrerit ipsum quis ligula accumsan tempor. Sed vulputate mauris et mauris ultricies, non pharetra tellus eleifend. Interdum et malesuada fames ac ante ipsum primis in faucibus. Maecenas hendrerit pharetra mauris, id porta diam hendrerit eu. Praesent quis nisl lacinia quam pretium facilisis et ac lacus. Donec a purus varius, mattis dolor id, rutrum erat. Suspendisse sed porttitor elit. Nulla dignissim, neque ut ornare fermentum, dolor massa convallis est, id consequat nibh eros eget diam. Sed lacinia est massa, ut auctor lectus hendrerit eu. Aenean at diam vel libero condimentum ultrices. Etiam gravida porttitor mauris vitae mattis. Nullam volutpat dictum laoreet. In dolor nunc, tristique et nisi ut, efficitur faucibus leo. Aenean pharetra turpis ac nunc mollis, ac pretium enim finibus. Integer eleifend orci vel nunc vehicula, ut condimentum tortor ullamcorper. Vivamus lacinia nibh in ex mollis tempus. Nunc a laoreet dolor. Fusce placerat, arcu at pulvinar cursus, nisl sem laoreet sem, at auctor erat ligula sed ante. Sed risus nisl, faucibus ac suscipit eget, blandit quis lectus. Duis volutpat est sit amet arcu elementum efficitur. Integer ac sapien vitae nisi tincidunt facilisis. Aenean viverra nibh id tellus fringilla gravida. Mauris faucibus ac mauris quis volutpat."

MICRO_ALGO_PRICE = (0.17 / 1000000)

def pytest_configure():
    pytest.pes_manager = None
    pytest.oracle = None
    pytest.oracle_app_id = 0
    pytest.land_registry_address = None
    pytest.pes_scheme = None
    pytest.pes_scheme2 = None
    pytest.new_asset_id = None
    pytest.fractional_asset_id = 0
    pytest.period = 0
    pytest.nft_price = 0
    pytest.balance1 = 0
    pytest.balance2 = 0
    pytest.balance3 = 0
    pytest.balance4 = 0
    pytest.balance5 = 0
    pytest.balance6 = 0
    pytest.min_balance1 = 0
    pytest.min_balance2 = 0
    pytest.min_balance3 = 0
    pytest.min_balance4 = 0
    pytest.min_balance5 = 0
    pytest.min_balance6 = 0

@pytest.fixture
def deploy_oracle(setup_account5):
    oracle = Oracle(setup_account5)
    assert oracle.app_id != 0
    pytest.oracle = oracle
    pytest.oracle_app_id = oracle.app_id
    return oracle

@pytest.fixture
def deploy_land_registry(setup_account):
    land_registry = LandRegistry(setup_account, 0)
    print("land_registry.app_id="  + str(land_registry.app_id))
    assert land_registry.app_id != 0
    print(land_registry.app_id)
    pytest.land_registry_address = land_registry.app_address
    return land_registry


@pytest.fixture
def setup_balance_pre_test(setup_account, setup_account2, setup_account3, setup_account4, setup_account5, setup_account6):
    balance1 = setup_account.get_balance()
    balance2 = setup_account2.get_balance()
    balance3 = setup_account3.get_balance()
    balance4 = setup_account4.get_balance()
    balance5 = setup_account5.get_balance()
    balance6 = setup_account6.get_balance()
    min_balance1 = setup_account.get_min_balance()
    min_balance2 = setup_account2.get_min_balance()
    min_balance3 = setup_account3.get_min_balance()
    min_balance4 = setup_account4.get_min_balance()
    min_balance5 = setup_account5.get_min_balance()
    min_balance6 = setup_account6.get_min_balance()
    pytest.balance1 = balance1
    pytest.balance2 = balance2
    pytest.balance3 = balance3
    pytest.balance4 = balance4
    pytest.balance5 = balance5
    pytest.balance6 = balance6
    pytest.min_balance1 = min_balance1
    pytest.min_balance2 = min_balance2
    pytest.min_balance3 = min_balance3
    pytest.min_balance4 = min_balance4
    pytest.min_balance5 = min_balance5
    pytest.min_balance6 = min_balance6




@pytest.fixture
def setup_environment(setup_balance_pre_test, setup_algod_client, deploy_land_registry, deploy_oracle, setup_account, setup_account2, setup_pinata):
    # Loads Land Registry
    land_registry = deploy_land_registry
    app_id = deploy_land_registry.app_id
    # Obtains created assets of the Land Registry
    created_assets = setup_algod_client.account_info(get_app_address(app_id))['created-assets']
    total_created_assets = len(created_assets)
    # Creates the NFT from the registed land
    new_asset_id = land_registry.register_land("test_name", "test_description", "tst", "land_deed.jpg", "land_deed.jpg", setup_pinata)
    # Stores the asset id on the global variable
    pytest.new_asset_id = new_asset_id
    # Loads created assets from the Land Registry
    created_assets = setup_algod_client.account_info(get_app_address(app_id))['created-assets']
    print("Created asset id is " + str(new_asset_id))
    # Verifies if a new asset has been created
    assert len(created_assets) == (total_created_assets + 1)
    # Verifies if the new asset id is in the created assets
    assert verify_in_created_assets(new_asset_id, created_assets)
    # Now that the asset has been successfuly created we will transfer it
    receiver_address = setup_account2.address
    setup_account2.opt_in_to_asset(new_asset_id)
    assets = setup_algod_client.account_info(receiver_address)['assets']
    # Verifies if the account opted in to the asset
    assert verify_in_assets(new_asset_id, assets)
    land_registry.transfer_land(receiver_address, new_asset_id)
    assets = setup_algod_client.account_info(receiver_address)['assets']
    # Verifies if the account has received the asset
    assert hasAsset(new_asset_id, assets)
    # Verifies if the app not longer owns the account
    app_assets = setup_algod_client.account_info(get_app_address(app_id))['assets']
    assert noAsset(new_asset_id, app_assets) 

'''
def test_get_block_timestamp(setup_algod_client):
    algod_client = setup_algod_client
    status_node = algod_client.status()
    block_info = (algod_client.block_info(status_node['last-round'])['block'])
    current_ts = block_info['ts']
    print(status_node)
    print(current_ts)
    assert 1 == 0
'''


#def test_PES_Manager_deployment(setup_environment, setup_account3, deploy_oracle, setup_algod_client):
def test_PES_Manager_deployment(setup_environment, setup_account3, deploy_oracle, setup_algod_client):
    # Loads oracle app id
    oracle_app_id = pytest.oracle_app_id
    # Old Balance
    old_balance = setup_account3.get_balance()
    # Creates an PES Manager
    pes_manager = PESManager(setup_account3, 0, oracle_app_id, pytest.land_registry_address)
    # New balance
    new_balance = setup_account3.get_balance()
    assert pes_manager.app_id != 0
    pytest.pes_manager = pes_manager
    sp = setup_algod_client.suggested_params()
    assert abs(new_balance - old_balance) == MIN_BALANCE + 2 * sp.min_fee


# Verifies if the box is created correctly
def test_PES_Manager_create_box(setup_account2, setup_algod_client):
    # Loads oracle app id
    pes_manager= pytest.pes_manager
    pes_manager_id = pes_manager.app_id
    # Creates an pes_manager_user
    pes_manager_user = PESManagerUser(setup_account2, pes_manager_id)
    # Checks account balance before create_box
    old_balance = setup_account2.get_balance()
    # Opts in to PES Manager
    pes_manager_user.create_box_PESManager()
    # Checks account balance after create_box
    new_balance = setup_account2.get_balance()
    balance_diff = abs(new_balance - old_balance)
    print(balance_diff)
    sp = setup_algod_client.suggested_params()
    # Load algod client
    algod_client =  setup_algod_client
    # Looks for boxes on the app
    response = algod_client.application_boxes(pes_manager_id)
    assert len(response['boxes']) == 1
    box_names = []
    for box in response['boxes']:
        box_names.append(convert_box_names(box['name']))
    assert setup_account2.address in box_names
    box_value = (algod_client.application_box_by_name(pes_manager_id, decode_address(setup_account2.address)))['value']
    box_value_decoded = ord((base64.b64decode(box_value)).decode('utf-8'))
    assert box_value_decoded == 0
    assert balance_diff == box_cost(decode_address(setup_account2.address), 1) + 2 * sp.min_fee
    #assert balance_diff == 2500 + 400 * (len(decode_address(setup_account2.address)) + 1) + 2 * sp.min_fee


def test_create_PES_Scheme(setup_account2, setup_algod_client):
    # Loads oracle app id
    pes_manager = pytest.pes_manager
    pes_manager_id = pes_manager.app_id
    # Creates an pes_manager_user
    pes_manager_user = PESManagerUser(setup_account2, pes_manager_id)
    # Checks account balance before create_box
    old_balance = setup_account2.get_balance()
    # Creates an PES Scheme
    pes_scheme = pes_manager_user.create_PES_scheme(type=1)
    assert pes_scheme.app_id != 0
    pytest.pes_scheme = pes_scheme
    new_balance = setup_account2.get_balance()
    balance_diff = abs(new_balance - old_balance)
    sp = setup_algod_client.suggested_params()
    print(balance_diff)
    assert balance_diff == deploy_cost(8, 2) + 3 * sp.min_fee
    algod_client = setup_algod_client
    app_info = algod_client.application_info(pes_scheme.app_id)
    global_vars = get_global_variable(app_info)
    print(global_vars)
    # Verifies if the variables were stored correctly
    assert pytest.land_registry_address == convert_address(global_vars['Land_Registry_Address'])
    assert pytest.oracle_app_id == global_vars['Oracle_Id']
    assert pes_manager_user.account.address == convert_address(global_vars['Seller_Address'])
    assert 0 == global_vars['State']


def test_start_sale_PES_Scheme(setup_account2, setup_pinata, setup_algod_client):
    # Checks account balance before start_sale
    old_balance = setup_account2.get_balance()
    # Loads oracle
    oracle = pytest.oracle
    # Saves current_time 
    start_time = timestamp_to_rfc3339()
    # Saves end_time
    end_time = rfc3339_step()
    # Gets request
    oracle.get_requests(start_time, end_time)
    # Stores current number of requests
    start_request = len(oracle.request_list)
    # Loads oracle app id
    oracle_app_id = pytest.oracle_app_id
    # Loads the address from land_registry
    land_registry_address = pytest.land_registry_address
    # Seller Address
    seller_address = setup_account2.address
    # Loads sold_asset_id
    sold_asset_id = pytest.new_asset_id
    # Creates pes scheme
    pes_scheme = pytest.pes_scheme
    # The variables that are going to be used for the NFT
    decimals = 1
    name = "fractional_test_name"
    unit_name = "ftst"
    nft_price = 50
    period = 1
    pytest.period = period
    pytest.nft_price = nft_price
    current_date = datetime.now()
    # Starts the sale
    #created_asset_id = pes_scheme.start_sale(sold_asset_id, name, unit_name, "land_deed.jpg", "land_deed.jpg", big_description, decimals, nft_price, period, setup_pinata)
    created_asset_id = pes_scheme.start_sale(asset_id = sold_asset_id ,file_path = "pes_config.json")
    pytest.fractional_asset_id = created_asset_id
    # Verifies if the Fraction NFTs were created
    algod_client = setup_algod_client
    created_asset_info = (algod_client.asset_info(created_asset_id))['params']
    assert created_asset_info['decimals'] == decimals
    assert created_asset_info['total'] == pow(10, decimals)
    assert created_asset_info['creator'] == pes_scheme.app_address
    # Verifies if the PES Scheme has the Fractional NFTs
    account_asset_info = algod_client.account_asset_info(pes_scheme.app_address, created_asset_id)
    asset_holding = account_asset_info['asset-holding']
    assert asset_holding['amount'] == pow(10, decimals)
    app_info = algod_client.application_info(pes_scheme.app_id)
    global_vars = get_global_variable(app_info)
    # print(global_vars)
    # The sale has started
    assert global_vars['State'] == 1
    # The NFT_Price has been defined
    assert global_vars['NFT_Price'] == nft_price
    # The time to receive the response has been defined 
    #assert global_vars['Receive_Timestamp'] > current_date.timestamp()
    # Sleeps for 10 seconds
    # sleep(10)
    oracle.request_list.append(SingleRequest(0, algod_client, pes_scheme.app_id, sold_asset_id, setup_account2.address))
    # Gets request
    # oracle.get_requests(start_time, end_time)
    # Stores current number of requests
    end_requests = len(oracle.request_list)
    assert end_requests > start_request
    new_balance = setup_account2.get_balance()
    balance_diff = abs(new_balance - old_balance)
    sp = setup_algod_client.suggested_params()
    print(balance_diff)
    assert balance_diff == 11 * sp.min_fee + 3 * MIN_BALANCE 



def test_buy_PESScheme(setup_algod_client, setup_account4):
    # See the state of the seller and the asset before the buy
    seller_asset_info = (setup_algod_client.account_asset_info(get_app_address(pytest.pes_scheme.app_id), pytest.fractional_asset_id))['asset-holding']
    asset_info = setup_algod_client.asset_info(pytest.fractional_asset_id)
    assert seller_asset_info['amount'] == asset_info['params']['total']
    assert seller_asset_info['is-frozen'] == False
    # Checks account balance before buy
    old_balance = setup_account4.get_balance()
    # Buys the NFT
    pes_scheme_user = PESSchemeAssetUser(setup_account4, pytest.pes_scheme.app_id)
    quantity = 5
    pes_scheme_user.buy_NFT(quantity)
    # See the state of the buyer after the sale
    buyer_asset_info = (setup_algod_client.account_asset_info(setup_account4.address, pytest.fractional_asset_id))['asset-holding']
    assert buyer_asset_info['amount'] == quantity
    assert buyer_asset_info['is-frozen'] == True
    # See the state of the seller and the asset after the sale
    seller_asset_info = (setup_algod_client.account_asset_info(get_app_address(pytest.pes_scheme.app_id), pytest.fractional_asset_id))['asset-holding']
    asset_info = setup_algod_client.asset_info(pytest.fractional_asset_id)
    assert seller_asset_info['amount'] == asset_info['params']['total'] - quantity
    assert seller_asset_info['is-frozen'] == False
    new_balance = setup_account4.get_balance()
    balance_diff = abs(new_balance - old_balance)
    sp = setup_algod_client.suggested_params()
    print(balance_diff)
    assert balance_diff == (quantity * pytest.nft_price) + 7 * sp.min_fee  + box_cost(decode_address(setup_account4.address), 8)

def test_buy_PESScheme2(setup_algod_client, setup_account6):
    # See the state of the seller and the asset before the buy
    seller_asset_info = (setup_algod_client.account_asset_info(get_app_address(pytest.pes_scheme.app_id), pytest.fractional_asset_id))['asset-holding']
    asset_info = setup_algod_client.asset_info(pytest.fractional_asset_id)
    assert seller_asset_info['amount'] != asset_info['params']['total']
    assert seller_asset_info['is-frozen'] == False
    old_balance = setup_account6.get_balance()
    # Buys the Asset
    pes_scheme_user = PESSchemeAssetUser(setup_account6, pytest.pes_scheme.app_id)
    quantity = 5
    # Checks account balance before buy
    # Loads the Period
    period = pytest.period
    # Waits for the period to pass. Since period is in minutes and sleep's argument is in seconds, we need to multiply by 60
    #sleep(period * 70)
    pes_scheme_user.buy_NFT(quantity)
    # See the state of the buyer after the sale
    buyer_asset_info = (setup_algod_client.account_asset_info(setup_account6.address, pytest.fractional_asset_id))['asset-holding']
    assert buyer_asset_info['amount'] == quantity
    assert buyer_asset_info['is-frozen'] == True
    # See the state of the seller and the asset after the sale
    seller_asset_info = (setup_algod_client.account_asset_info(get_app_address(pytest.pes_scheme.app_id), pytest.fractional_asset_id))['asset-holding']
    asset_info = setup_algod_client.asset_info(pytest.fractional_asset_id)
    assert seller_asset_info['amount'] == 0
    assert seller_asset_info['is-frozen'] == False
    new_balance = setup_account6.get_balance()
    balance_diff = abs(new_balance - old_balance)
    sp = setup_algod_client.suggested_params()
    print(balance_diff)
    assert balance_diff == (quantity * pytest.nft_price) + 7 * sp.min_fee  + box_cost(decode_address(setup_account6.address), 8)


def test_receive_positive_response(setup_algod_client, setup_account2):
    old_balance = setup_account2.get_balance()
    # Loads the Oracle
    oracle = pytest.oracle
    # Counts Start Responses and requests
    start_responses = len(oracle.response_list)
    print(oracle.response_list)
    start_requests = len(oracle.request_list)
    print(oracle.request_list)
    # Response positively to the request
    oracle.respond_to_request(request = oracle.request_list[-1], answer = 1)
    #oracle.give_responses(1)
    # Counts Current Responses and requests
    current_responses = len(oracle.response_list)
    current_requests = len(oracle.request_list)
    print(current_responses)
    print(current_requests)
    # Checks if response was added to list
    # assert start_responses < current_responses
    # Checks if request was removed from the list
    # assert current_requests < start_requests
    # Loads the algod client
    algod_client = setup_algod_client
    # Loads the pes scheme
    pes_scheme = pytest.pes_scheme
    # Loads the global values
    app_info = algod_client.application_info(pes_scheme.app_id)
    global_vars = get_global_variable(app_info)
    # Verifies if the global state has been correctly changed
    assert global_vars['State'] == 3
    # Loads the app id of the Asset
    new_asset_id = pytest.new_asset_id
    account_asset_info = (algod_client.account_asset_info(setup_account2.address, new_asset_id))['asset-holding']
    # Verifies if the Land Asset was returned to the Seller
    assert account_asset_info['amount'] == 1
    assert account_asset_info['asset-id'] == new_asset_id
    # Verifies if the PES Scheme no longer has the Land Asset
    pes_scheme_assets = (algod_client.account_info(pes_scheme.app_address))['assets']
    assert verify_in_assets(new_asset_id, pes_scheme_assets) == False
    new_balance = setup_account2.get_balance()
    assert new_balance - old_balance == 500 + MIN_BALANCE



def test_show_created_pes_scheme(setup_account2, setup_algod_client):
    pes_manager= pytest.pes_manager
    pes_manager_id = pes_manager.app_id
    pes_manager_user = PESManagerUser(setup_account2, pes_manager_id)
    pytest.pes_scheme2 =  pes_manager_user.create_PES_scheme(type=1)


def test_give_refund(setup_account4, setup_account2, setup_algod_client):
    # Loads pes scheme
    pes_scheme = pytest.pes_scheme
    # Checks account balance before refund
    old_balance = setup_account4.get_balance()
    old_balance2 = setup_account2.get_balance()
    # Gives refund
    pes_scheme.give_refund(setup_account4.address)
    # Checks account balance before refund
    new_balance = setup_account4.get_balance()
    new_balance2 = setup_account2.get_balance()
    balance_diff = new_balance - old_balance
    balance_diff2 = new_balance2 - old_balance2
    print(balance_diff)
    sp = setup_algod_client.suggested_params()
    assert balance_diff == box_cost(decode_address(setup_account4.address), 8)
    assert balance_diff2 == -2 * sp.min_fee


def test_give_refund2(setup_account6, setup_account2, setup_algod_client):
    # Loads pes scheme
    pes_scheme = pytest.pes_scheme
    # Checks account balance before refund
    old_balance = setup_account6.get_balance()
    old_balance2 = setup_account2.get_balance()
    # Gives refund
    pes_scheme.give_refund(setup_account6.address)
    # Checks account balance before refund
    new_balance = setup_account6.get_balance()
    new_balance2 = setup_account2.get_balance()
    balance_diff = new_balance - old_balance
    balance_diff2 = new_balance2 - old_balance2
    print(balance_diff)
    sp = setup_algod_client.suggested_params()
    assert balance_diff ==  box_cost(decode_address(setup_account6.address), 8)
    assert balance_diff2 == -2 * sp.min_fee

def test_delete(setup_algod_client, setup_account2):
    # Loads pytest stuff
    pes_manager= pytest.pes_manager
    pes_manager_id = pes_manager.app_id
    # Loads the balance
    old_balance = setup_account2.get_balance()
    print(old_balance)
    #print(setup_account2.get_account_info())
    pes_manager_user = PESManagerUser(setup_account2, pes_manager_id)
    pes_scheme_app_id = pytest.pes_scheme.app_id
    sp = setup_algod_client.suggested_params()
    print("min_fee=" + str(sp.min_fee))
    pes_manager_user.delete_PES_Scheme(pes_scheme_app_id)
    new_balance = setup_account2.get_balance()
    print(new_balance)
    balance_diff = new_balance - old_balance
    #print(setup_account2.get_account_info())
    assert new_balance > old_balance
    assert balance_diff == (deploy_cost(8, 2) - 3 * sp.min_fee)
    #assert balance_diff == (528000 + 128500 - 5 * sp.min_fee)


def test_delete2(setup_algod_client, setup_account2):
    # Loads pytest stuff
    pes_manager= pytest.pes_manager
    pes_manager_id = pes_manager.app_id
    # Loads the balance
    old_balance = setup_account2.get_balance()
    print(old_balance)
    #print(setup_account2.get_account_info())
    pes_manager_user = PESManagerUser(setup_account2, pes_manager_id)
    pes_scheme_app_id = pytest.pes_scheme2.app_id
    sp = setup_algod_client.suggested_params()
    print("min_fee=" + str(sp.min_fee))
    pes_manager_user.delete_PES_Scheme(pes_scheme_app_id)
    new_balance = setup_account2.get_balance()
    print(new_balance)
    balance_diff = new_balance - old_balance
    #print(setup_account2.get_account_info())
    assert new_balance > old_balance
    assert balance_diff == (deploy_cost(8, 2) - 3 * sp.min_fee)
    #assert balance_diff == (528000- 3 * sp.min_fee)

'''
def test_final_costs(setup_algod_client, setup_account, setup_account2, setup_account3, setup_account4, setup_account5, setup_account6):
    sp = setup_algod_client.suggested_params()
    balance1 = setup_account.get_balance()
    balance2 = setup_account2.get_balance()
    balance3 = setup_account3.get_balance()
    balance4 = setup_account4.get_balance()
    balance5 = setup_account5.get_balance()
    balance6 = setup_account6.get_balance()
    min_balance1 = setup_account.get_min_balance()
    min_balance2 = setup_account2.get_min_balance()
    min_balance3 = setup_account3.get_min_balance()
    min_balance4 = setup_account4.get_min_balance()
    min_balance5 = setup_account5.get_min_balance()
    min_balance6 = setup_account6.get_min_balance()
    print("Account 1- LAND REGISTRY DEPLOYER")
    print(abs(pytest.balance1 - balance1))
    print(abs(pytest.min_balance1 - min_balance1))
    print(str(abs(pytest.balance1 - balance1)  * MICRO_ALGO_PRICE) + " €")
    assert abs(pytest.balance1 - balance1) + abs(pytest.min_balance1 - min_balance1) == 3 * MIN_BALANCE + 7 * sp.min_fee
    print("ES PROVIDER")
    print(abs(pytest.balance2 - balance2))
    print(abs(pytest.min_balance2 - min_balance2))
    print(str(abs(pytest.balance2 - balance2)  * MICRO_ALGO_PRICE) + " €")
    # 445200 = 438200
    assert abs(pytest.balance2 - balance2) + abs(pytest.min_balance2 - min_balance2) == 3 * MIN_BALANCE  + box_cost(decode_address(setup_account2.address), 1) + 30 * sp.min_fee -  (10 * pytest.nft_price)
    print("PES MANAGER DEPLOYER")
    print(abs(pytest.balance3 - balance3))
    print(abs(pytest.min_balance3 - min_balance3))
    print(str(abs(pytest.balance3 - balance3)  * MICRO_ALGO_PRICE) + " €")
    assert abs(pytest.balance3 - balance3) + abs(pytest.min_balance3 - min_balance3) == 2 * MIN_BALANCE + 2 * sp.min_fee + deploy_cost(1, 1)
    print("BUYER 1")
    print(abs(pytest.balance4 - balance4))
    print(abs(pytest.min_balance4 - min_balance4))
    print(str(abs(pytest.balance4 - balance4) * MICRO_ALGO_PRICE) + " €")
    assert abs(pytest.balance4 - balance4) + abs(pytest.min_balance4 - min_balance4) == (5 * pytest.nft_price) + 7 * sp.min_fee + MIN_BALANCE
    print("BUYER 2")
    print(abs(pytest.balance6 - balance6))
    print(abs(pytest.min_balance6 - min_balance6))
    print(str(abs(pytest.balance6 - balance6) * MICRO_ALGO_PRICE) + " €")
    assert abs(pytest.balance6 - balance6) + abs(pytest.min_balance6 - min_balance6) == (5 * pytest.nft_price) + 7 * sp.min_fee + MIN_BALANCE
    print("ORACLE DEPLOYER")
    print(abs(pytest.balance5 - balance5))
    print(abs(pytest.min_balance5 - min_balance5))
    print(str(abs(pytest.balance5 - balance5) * MICRO_ALGO_PRICE) + " €")
    assert abs(pytest.balance5 - balance5) + abs(pytest.min_balance5 - min_balance5) == 2 * MIN_BALANCE + 5 * sp.min_fee
'''

def convert_address(b64_address:str):
    bytes_address = base64.b64decode(b64_address)
    str_address = encode_address(bytes_address)
    return str_address


def convert_box_names(b64_box_name:str):
    bytes_box_name = base64.b64decode(b64_box_name)
    str_box_name = encode_address(bytes_box_name)
    return str_box_name

def get_description(encoded_description):
    description = base64.b64decode(encoded_description)
    return description.decode("utf-8")
