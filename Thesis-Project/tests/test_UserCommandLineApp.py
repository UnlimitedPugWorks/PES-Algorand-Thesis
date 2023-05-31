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
from Classes.SmartContract import var_to_base64, get_app_address
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from Classes.LandRegistryCommandLineApp import LandRegistryCommandLineApp
from Classes.PESManagerCommandLine import PESManagerCommandLine
from Classes.UserCommandLineApp import UserCommandLineApp  
from Classes.SingleRequest import SingleRequest
from algosdk.mnemonic import to_private_key
from algosdk.encoding import encode_address, checksum, decode_address
from os.path import isfile, exists, split
from testUtil import *
from time import sleep
from datetime import timezone, datetime


big_description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas nec lobortis augue. Vestibulum lacinia sit amet ex id pharetra. Proin luctus nisi faucibus semper mollis. Duis id tortor vitae turpis ultricies posuere id vitae ex. Maecenas aliquet posuere felis ut commodo. Duis eu mi orci. Mauris vel varius neque. Vestibulum mollis consequat pellentesque. Etiam feugiat elit nec mi placerat sagittis. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eleifend ante viverra urna cursus, vel venenatis tellus imperdiet. Pellentesque rutrum nec ipsum at tempor. Phasellus eleifend enim id arcu interdum, dapibus fermentum nibh vulputate. Mauris condimentum felis nisl, et feugiat nisi posuere sed. Mauris ac massa sit amet lorem cursus dignissim. Donec arcu magna, scelerisque vitae massa tristique, consectetur bibendum dui. Sed egestas massa elementum elit posuere, at vehicula urna tincidunt. Ut faucibus malesuada mauris lobortis eleifend. Nunc placerat enim ipsum, non dignissim tortor dapibus eget. Morbi bibendum tincidunt fringilla. Fusce sed turpis sagittis, luctus elit vel, gravida purus. Sed ac enim eu felis suscipit vestibulum non sit amet arcu. Cras eleifend purus nec lectus blandit egestas. Curabitur ac efficitur nulla. Integer a vehicula augue. Aenean sed nunc non turpis accumsan tempus. Morbi quis ullamcorper nunc, sit amet volutpat neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed elementum molestie est. Aliquam porta faucibus neque vitae malesuada. Nulla augue turpis, egestas porta mollis ac, egestas et mi. Proin lobortis magna id nisi interdum, et tincidunt risus vestibulum. Curabitur condimentum eros ac nisl commodo maximus. Phasellus dapibus mauris ut nisi fringilla, quis congue lacus tempor. Sed dignissim odio non ultricies tempus. Fusce nec facilisis tortor, ac porta metus. Aenean massa velit, accumsan sit amet nisi a, placerat tincidunt odio. Fusce quis sapien augue. Suspendisse potenti. Nam iaculis gravida elit at pretium. Sed sollicitudin ullamcorper nibh, ut posuere turpis. Mauris at neque interdum, sodales ligula tristique, bibendum ex. Nam hendrerit ipsum quis ligula accumsan tempor. Sed vulputate mauris et mauris ultricies, non pharetra tellus eleifend. Interdum et malesuada fames ac ante ipsum primis in faucibus. Maecenas hendrerit pharetra mauris, id porta diam hendrerit eu. Praesent quis nisl lacinia quam pretium facilisis et ac lacus. Donec a purus varius, mattis dolor id, rutrum erat. Suspendisse sed porttitor elit. Nulla dignissim, neque ut ornare fermentum, dolor massa convallis est, id consequat nibh eros eget diam. Sed lacinia est massa, ut auctor lectus hendrerit eu. Aenean at diam vel libero condimentum ultrices. Etiam gravida porttitor mauris vitae mattis. Nullam volutpat dictum laoreet. In dolor nunc, tristique et nisi ut, efficitur faucibus leo. Aenean pharetra turpis ac nunc mollis, ac pretium enim finibus. Integer eleifend orci vel nunc vehicula, ut condimentum tortor ullamcorper. Vivamus lacinia nibh in ex mollis tempus. Nunc a laoreet dolor. Fusce placerat, arcu at pulvinar cursus, nisl sem laoreet sem, at auctor erat ligula sed ante. Sed risus nisl, faucibus ac suscipit eget, blandit quis lectus. Duis volutpat est sit amet arcu elementum efficitur. Integer ac sapien vitae nisi tincidunt facilisis. Aenean viverra nibh id tellus fringilla gravida. Mauris faucibus ac mauris quis volutpat."

def pytest_configure():
    pytest.oracle = None
    pytest.oracle_app_id = 0
    pytest.land_registry_address = None
    pytest.land_registry_app_id = 0
    pytest.land_registry_command_line = None
    pytest.pes_manager_command_line = None
    pytest.user_command_line = None
    pytest.user_command_line2 = None
    pytest.user_command_line3 = None
    pytest.user_command_line4 = None
    pytest.user_command_line5 = None
    pytest.user_command_line6 = None
    pytest.pes_scheme_app_id = 0
    pytest.new_asset_id = 0
    pytest.fractional_asset_id = 0
    pytest.period = 0

@pytest.fixture
def deploy_oracle(setup_account5):
    oracle = Oracle(setup_account5)
    assert oracle.app_id != 0
    pytest.oracle = oracle
    pytest.oracle_app_id = oracle.app_id
    return oracle

@pytest.fixture
def deploy_land_registry_command(setup_account):
    land_registry_command_line = LandRegistryCommandLineApp(setup_account)
    land_registry_command_line.process_commands(["deploy"])
    land_registry = land_registry_command_line.land_registry
    assert land_registry.app_id != 0
    pytest.land_registry_app_id = land_registry.app_id
    pytest.land_registry_address = get_app_address(land_registry.app_id)
    pytest.land_registry_command_line = land_registry_command_line
    return land_registry_command_line

@pytest.fixture
def setup_environment(setup_algod_client, deploy_land_registry_command, setup_account, setup_account2, setup_pinata):
    # Loads the Land Registry Command Line
    land_registry_command_line = deploy_land_registry_command
    # Loads the Land Registry 
    land_registry = deploy_land_registry_command.land_registry
    # Loads the Land Registry's App Id
    app_id = land_registry.app_id
    # Verifies how many assets it has before creating a new one
    created_assets = setup_algod_client.account_info(get_app_address(app_id))['created-assets']
    total_created_assets = len(created_assets)
    # Creates a new asset
    new_asset_id = land_registry_command_line.process_commands(["register", "test_name", "test_description", "tst", "land_deed.jpg", "land_deed.jpg"])
    print(new_asset_id)
    # Verifies how many assets it has after creating a new one
    created_assets = setup_algod_client.account_info(get_app_address(app_id))['created-assets']
    print(created_assets)
    # Verifies if a new asset has been created
    assert len(created_assets) == (total_created_assets + 1)
    # Verifies if the new asset id is in the created assets
    assert verify_in_created_assets(new_asset_id, created_assets)
    # Stores the new asset id
    pytest.new_asset_id = new_asset_id
    # Loads created assets from the Land Registry
    created_assets = setup_algod_client.account_info(get_app_address(app_id))['created-assets']
    print("Created asset id is " + str(new_asset_id))
    # Verifies if a new asset has been created
    assert len(created_assets) == (total_created_assets + 1)
    # Verifies if the new asset id is in the created assets
    assert verify_in_created_assets(new_asset_id, created_assets)
    # Now that the asset has been successfuly created we will transfer it
    # Loads Land Registry
    land_registry = land_registry_command_line.land_registry
    # The App Id of the land registry
    app_id = land_registry.app_id
    # Receiver address which is going to receive the NFT
    receiver_address = setup_account2.address
    # Now that the asset has been successfuly created we will transfer it
    # The receiver_address must opt in to the asset otherwise it can't receive it
    user_command_line2 = UserCommandLineApp(setup_account2, setup_pinata)
    # Connects to land_regisry
    user_command_line2.process_LandRegistry(["connect", str(pytest.land_registry_app_id)])
    user_command_line2.process_LandRegistry(["AssetOptIn", str(new_asset_id)])
    pytest.user_command_line2 = user_command_line2
    assets = setup_algod_client.account_info(receiver_address)['assets']
    # Verifies if the account opted in to the asset
    assert verify_in_assets(new_asset_id, assets)
    # Transfers land
    land_registry_command_line.process_commands(["transfer", receiver_address, str(new_asset_id)])
    assets = setup_algod_client.account_info(receiver_address)['assets']
    # Verifies if the account has received the asset
    assert hasAsset(new_asset_id, assets)
    # Verifies if the land_registry has not received the asset
    app_assets = setup_algod_client.account_info(get_app_address(app_id))['assets']
    assert noAsset(new_asset_id, app_assets)
    
def test_PES_Manager_deployment(setup_environment, setup_account4, deploy_oracle):
    # Loads oracle app id
    oracle_app_id = pytest.oracle_app_id
    # Creates an NFT ManagerCommandLine
    pes_manager_command_line = PESManagerCommandLine(setup_account4)
    pes_manager_command_line.process_commands(["deploy", str(oracle_app_id), pytest.land_registry_app_id])
    assert pes_manager_command_line.pes_manager.app_id != 0
    pytest.pes_manager_command_line = pes_manager_command_line

# Verifies if the box is created correctly
def test_PES_Manager_opt_in(setup_account, setup_algod_client, setup_pinata):
    # Loads pes_manager_command_line
    pes_manager_command_line = pytest.pes_manager_command_line
    pes_manager_id = pes_manager_command_line.pes_manager.app_id
    # UserCommandLine
    user_command_line = UserCommandLineApp(setup_account, setup_pinata)
    user_command_line.process_PESManager(["connect", str(pes_manager_id)])
    assert user_command_line.pes_manager_user != None
    # Creates Box NFTManager
    user_command_line.process_PESManager(["CreateBox"])
    # Saves user command line
    pytest.user_command_line = user_command_line
    # Load algod client
    algod_client =  setup_algod_client
    # Looks for boxes on the app
    response = algod_client.application_boxes(pes_manager_id)
    assert len(response['boxes']) == 1
    box_name = response['boxes'][0]['name']
    assert convert_box_names(box_name) == setup_account.address
    box_value = (algod_client.application_box_by_name(pes_manager_id, decode_address(setup_account.address)))['value']
    box_value_decoded = ord((base64.b64decode(box_value)).decode('utf-8'))
    assert box_value_decoded == 0


def test_PES_Manager_opt_in2(setup_account2, setup_algod_client):
    # Loads pes_manager_command_line
    pes_manager_command_line = pytest.pes_manager_command_line
    pes_manager_id = pes_manager_command_line.pes_manager.app_id
    # Loads the user_command_line2
    user_command_line2 = pytest.user_command_line2
    # UserCommandLine
    user_command_line2.process_PESManager(["connect", str(pes_manager_id)])
    # Creates Box NFTManager
    user_command_line2.process_PESManager(["CreateBox"])
    # Saves user command line
    pytest.user_command_line2 = user_command_line2
    # Load algod client
    algod_client =  setup_algod_client
    # Looks for boxes on the app
    response = algod_client.application_boxes(pes_manager_id)
    assert len(response['boxes']) == 2
    box_name = response['boxes'][0]['name']
    box_name2 = response['boxes'][1]['name']
    assert (convert_box_names(box_name) == setup_account2.address or convert_box_names(box_name2) == setup_account2.address)
    box_value = (algod_client.application_box_by_name(pes_manager_id, decode_address(setup_account2.address)))['value']
    box_value_decoded = ord((base64.b64decode(box_value)).decode('utf-8'))
    assert box_value_decoded == 0


def test_create_PES_Scheme(setup_algod_client):
    # Loads user command line
    user_command_line2 = pytest.user_command_line2
    # Creates an NFT Seller
    pes_scheme_app_id = user_command_line2.process_PESManager(["CreatePESscheme", "1"])
    pytest.pes_scheme_app_id = pes_scheme_app_id
    assert pes_scheme_app_id != 0
    algod_client = setup_algod_client
    app_info = algod_client.application_info(pes_scheme_app_id)
    global_vars = get_global_variable(app_info)
    print(global_vars)
    # Verifies if the variables were stored correctly
    assert pytest.land_registry_address == convert_address(global_vars['Land_Registry_Address'])
    assert pytest.oracle_app_id == global_vars['Oracle_Id']
    assert user_command_line2.pes_manager_user.account.address == convert_address(global_vars['Seller_Address'])
    assert 0 == global_vars['State']
    pytest.user_command_line2 = user_command_line2
    print(user_command_line2)
    

def test_start_sale_PES_Scheme(setup_algod_client):
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
    # Loads sold_asset_id
    sold_asset_id = pytest.new_asset_id
    # The variables that are going to be used for the NFT
    decimals = 1
    name = "fractional_test_name"
    unit_name = "ftst"
    nft_price = 50
    period = 1
    pytest.period = period
    current_date = datetime.now()
    # Starts the sale
    user_command_line2 = pytest.user_command_line2
    print(user_command_line2)
    pes_scheme = user_command_line2.pes_schemes[pytest.pes_scheme_app_id]
    commands = ["start_sale", str(sold_asset_id), "pes_config.json"]
    created_asset_id = user_command_line2.process_PESScheme(commands, pes_scheme)
    assert created_asset_id != 0
    print(sold_asset_id)
    print(created_asset_id)
    pytest.fractional_asset_id = created_asset_id
    # Verifies if the Fraction NFTs were created
    algod_client = setup_algod_client
    created_asset_info = (algod_client.asset_info(created_asset_id))['params']
    assert created_asset_info['decimals'] == decimals
    assert created_asset_info['total'] == pow(10, decimals)
    assert created_asset_info['creator'] == pes_scheme.app_address
    # Verifies if the NFT Seller has the Fractional NFTs
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
    assert global_vars['Receive_Timestamp'] > current_date.timestamp()
    # Gets request
    oracle.request_list.append(SingleRequest(0, algod_client, pytest.pes_scheme_app_id, sold_asset_id, user_command_line2.account.address))
    oracle.get_requests(start_time, end_time)
    # Stores current number of requests
    end_requests = len(oracle.request_list)
    assert end_requests > start_request
    pytest.user_command_line2 = user_command_line2


def test_buy_NFTSeller(setup_algod_client, setup_account4, setup_pinata):

    # See the state of the seller and the asset before the buy
    seller_asset_info = (setup_algod_client.account_asset_info(get_app_address(pytest.pes_scheme_app_id), pytest.fractional_asset_id))['asset-holding']
    asset_info = setup_algod_client.asset_info(pytest.fractional_asset_id)
    assert seller_asset_info['amount'] == asset_info['params']['total']
    assert seller_asset_info['is-frozen'] == False
    # Creates a user_command_line 
    user_command_line4 = UserCommandLineApp(setup_account4, setup_pinata)
    pes_buyer = PESSchemeAssetUser(setup_account4, pytest.pes_scheme_app_id)
    # Buys the NFT
    quantity = 5
    user_command_line4.process_PESSchemeUser(["make_payment", str(quantity)], pes_buyer)
    # See the state of the buyer after the sale
    buyer_asset_info = (setup_algod_client.account_asset_info(setup_account4.address, pytest.fractional_asset_id))['asset-holding']
    assert buyer_asset_info['amount'] == quantity
    assert buyer_asset_info['is-frozen'] == True
    # See tshe state of the seller and the asset after the sale
    seller_asset_info = (setup_algod_client.account_asset_info(get_app_address(pytest.pes_scheme_app_id), pytest.fractional_asset_id))['asset-holding']
    asset_info = setup_algod_client.asset_info(pytest.fractional_asset_id)
    assert seller_asset_info['amount'] == asset_info['params']['total'] - quantity
    assert seller_asset_info['is-frozen'] == False
    pytest.user_command_line4 = user_command_line4


def test_buy_NFTSeller2(setup_algod_client, setup_account5, setup_pinata):
    # See the state of the seller and the asset before the buy
    seller_asset_info = (setup_algod_client.account_asset_info(get_app_address(pytest.pes_scheme_app_id), pytest.fractional_asset_id))['asset-holding']
    asset_info = setup_algod_client.asset_info(pytest.fractional_asset_id)
    assert seller_asset_info['amount'] != asset_info['params']['total']
    assert seller_asset_info['is-frozen'] == False
    # Creates a user_command_line 
    user_command_line5 = UserCommandLineApp(setup_account5, setup_pinata)
    pes_buyer = PESSchemeAssetUser(setup_account5, pytest.pes_scheme_app_id)
    # Buys the NFT
    quantity = 5
    user_command_line5.process_PESSchemeUser(["make_payment", str(quantity)], pes_buyer)
    # See the state of the buyer after the sale
    buyer_asset_info = (setup_algod_client.account_asset_info(setup_account5.address, pytest.fractional_asset_id))['asset-holding']
    assert buyer_asset_info['amount'] == quantity
    assert buyer_asset_info['is-frozen'] == True
    # See the state of the seller and the asset after the sale
    seller_asset_info = (setup_algod_client.account_asset_info(get_app_address(pytest.pes_scheme_app_id), pytest.fractional_asset_id))['asset-holding']
    asset_info = setup_algod_client.asset_info(pytest.fractional_asset_id)
    assert seller_asset_info['amount'] == 0
    assert seller_asset_info['is-frozen'] == False
    pytest.user_command_line5 = user_command_line5


def test_receive_positive_response(setup_algod_client, setup_account2):
    # Loads the Period
    period = pytest.period
    # Waits for the period to pass. Since period is in minutes and sleep's argument is in seconds, we need to multiply by 60
    sleep(period * 60)
    # Loads thhe Oracle
    oracle = pytest.oracle
    # Counts Start Responses and requests
    start_responses = len(oracle.response_list)
    print(oracle.response_list)
    start_requests = len(oracle.request_list)
    print(oracle.request_list)
    # Response positively to the request
    #oracle.respond_to_request(request = oracle.request_list[-1], answer = 1)
    oracle.give_responses(1)
    # Counts Current Responses and requests
    current_responses = len(oracle.response_list)
    current_requests = len(oracle.request_list)
    print(current_responses)
    print(current_requests)
    # Checks if response was added to list
    assert start_responses < current_responses
    # Checks if request was removed from the list
    assert current_requests < start_requests
    # Loads the algod client
    algod_client = setup_algod_client
    # Loads the global values
    app_info = algod_client.application_info(pytest.pes_scheme_app_id)
    global_vars = get_global_variable(app_info)
    # Verifies if the global state has been correctly changed
    assert global_vars['State'] == 3
    # Loads the app id of the NFT
    new_asset_id = pytest.new_asset_id
    account_asset_info = (algod_client.account_asset_info(setup_account2.address, new_asset_id))['asset-holding']
    # Verifies if the Land NFT was returned to the Seller
    assert account_asset_info['amount'] == 1
    assert account_asset_info['asset-id'] == new_asset_id
    # Verifies if the NFT Seller no longer has the Land NFT
    pes_scheme_assets = (algod_client.account_info(get_app_address(pytest.pes_scheme_app_id)))['assets']
    #pes_scheme_assets = (algod_client.account_info(pes_scheme.app_address))['assets']
    assert verify_in_assets(new_asset_id, pes_scheme_assets) == False


def test_give_refund(setup_account4, setup_algod_client):
    # Checks account balance before refund
    old_balance = setup_account4.get_balance()
    # Loads user command line
    user_command_line2 = pytest.user_command_line2
    # Loads NFT Seller
    pes_scheme = user_command_line2.pes_schemes[pytest.pes_scheme_app_id]
    # Gives refund
    user_command_line2.process_PESScheme(["give_refund", setup_account4.address],pes_scheme)
    # Checks account balance after refund
    new_balance = setup_account4.get_balance()
    # Calculates the difference
    balance_diff = new_balance - old_balance
    # Asserts
    assert balance_diff ==  2500 + 400 * (32 + 8)

def test_give_refund2(setup_account5, setup_algod_client):
    # Gets account balance before refund
    old_balance = setup_account5.get_balance()
    # Loads user command line
    user_command_line2 = pytest.user_command_line2
    # Loads NFT Seller
    pes_scheme = user_command_line2.pes_schemes[pytest.pes_scheme_app_id]
    # Gives refund
    user_command_line2.process_PESScheme(["give_refund", setup_account5.address],pes_scheme)
    # Checks account balance after refund
    new_balance = setup_account5.get_balance()
    # Calculates the difference
    balance_diff = new_balance - old_balance
    # Asserts
    assert balance_diff ==  2500 + 400 * (32 + 8)



def test_delete(setup_algod_client, setup_account2):
    # Gets balance before deletion
    old_balance = setup_account2.get_balance()
    # Loads User Command Line
    user_command_line2 = pytest.user_command_line2
    # Loads NFT Seller App Id
    pes_scheme_app_id = pytest.pes_scheme_app_id
    # Deletes NFT Seller
    user_command_line2.process_PESManager(["DeletePESscheme", pes_scheme_app_id])
    # Gets balance after deletion
    new_balance = setup_account2.get_balance()
    # Calculates the difference
    balance_diff = new_balance - old_balance
    sp = setup_algod_client.suggested_params()
    # Asserts
    assert new_balance > old_balance
    assert balance_diff == (428000 - 3 * sp.min_fee)


def test_delete2(setup_algod_client, setup_account2):
    # Loads User Command Line
    user_command_line2 = pytest.user_command_line2
    # Creates a New NFT Seller
    pes_scheme_app_id = user_command_line2.process_PESManager(["CreatePESscheme", str(1)])
    # Gets balance before deletion
    old_balance = setup_account2.get_balance()
    # Deletes NFT Seller
    user_command_line2.process_PESManager(["DeletePESscheme", pes_scheme_app_id])
    # Gets balance after deletion
    new_balance = setup_account2.get_balance()
    # Calculates the difference
    balance_diff = new_balance - old_balance
    sp = setup_algod_client.suggested_params()
    # Asserts
    assert new_balance > old_balance
    assert balance_diff == (428000 - 3 * sp.min_fee)


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
