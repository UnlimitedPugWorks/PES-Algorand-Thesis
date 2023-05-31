import sys
sys.path.append('c:\\Users\\migue\\PES V2\\Thesis-Project')

import pytest
import base64
from Classes.PinataSDK import PinataSDK
from Classes.Account import Account
from Classes.LandRegistry import LandRegistry, get_app_address
from algosdk.v2client.algod import AlgodClient
from algosdk.mnemonic import to_private_key



#=========================Algod_Setup=================================================#

@pytest.fixture
def setup_algod_client():
    # Algod_client_constants
    ALGOD_ADDRESS = "http://localhost:4001"
    ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    # # Creates an algod client
    algod_client = AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    return algod_client

#=========================Account_Setup=================================================#

@pytest.fixture
def setup_account(setup_algod_client):
    #PRIVATE AND PUBLIC KEY
    # RELEASE NETWORK KEYS
    #PRIVATE_KEY = to_private_key("fiction minor vote eager neck lady chalk reject dress jungle behave depth faculty fruit into myth muffin develop use cherry tip venue general able energy")
    #PUBLIC_KEY =  "GSBQOCBC6D6JOVMI7YWQYGOVD46XVN2BS4J22MDONNONIX3J6SPYW2OW5Q"
    # DEV NETWORK KEYS
    PRIVATE_KEY = to_private_key("adjust ready swamp spell hat account hair bottom high snack stand mutual practice hour answer junior wink manual wild skate version force slogan abstract vital")
    PUBLIC_KEY = "D4WUBPYPVOSCEI6LHD7T3G3IZGJCEQYJAWBLW36QCIKXS2YP5NB57R5ZYU"
    account = Account(PRIVATE_KEY, PUBLIC_KEY, setup_algod_client)
    return account

@pytest.fixture
def setup_accountDEV(setup_algod_client):
    #PRIVATE AND PUBLIC KEY
    # RELEASE NETWORK KEYS
    #PRIVATE_KEY = to_private_key("fiction minor vote eager neck lady chalk reject dress jungle behave depth faculty fruit into myth muffin develop use cherry tip venue general able energy")
    #PUBLIC_KEY =  "GSBQOCBC6D6JOVMI7YWQYGOVD46XVN2BS4J22MDONNONIX3J6SPYW2OW5Q"
    # DEV NETWORK KEYS
    PRIVATE_KEY = to_private_key("adjust ready swamp spell hat account hair bottom high snack stand mutual practice hour answer junior wink manual wild skate version force slogan abstract vital")
    PUBLIC_KEY = "D4WUBPYPVOSCEI6LHD7T3G3IZGJCEQYJAWBLW36QCIKXS2YP5NB57R5ZYU"
    account = Account(PRIVATE_KEY, PUBLIC_KEY, setup_algod_client)
    return account

@pytest.fixture
def setup_account2(setup_algod_client):
    #PRIVATE AND PUBLIC KEY2
    # RELEASE NETWORK KEYS
    #PRIVATE_KEY2 = to_private_key("decrease where minimum airport message beyond inquiry evidence solar duty advance tip fitness pet tragic banner era oven census coil celery prefer shiver ability panda")
    #PUBLIC_KEY2 = "GGFFDGMKL6QYZNGNIGHAAHWKTLAUOZ5A5WKEEI4762SVW6MGK6T4JXWP74"
    # DEV NETWORK KEYS
    PRIVATE_KEY2 = to_private_key("enter broccoli lawn dilemma silly easy explain mechanic unusual skate elder ecology eyebrow canyon wood million crush dune autumn roof base stumble innocent abandon pizza")
    PUBLIC_KEY2 = "VB23U533V4IS2OS5WPAVAGCLUUMABQHE3ACXKY7O4JMYCGPYICBJD4CWVY"
    account = Account(PRIVATE_KEY2, PUBLIC_KEY2, setup_algod_client)
    return account

@pytest.fixture
def setup_account2DEV(setup_algod_client):
    #PRIVATE AND PUBLIC KEY2
    # RELEASE NETWORK KEYS
    #PRIVATE_KEY2 = to_private_key("decrease where minimum airport message beyond inquiry evidence solar duty advance tip fitness pet tragic banner era oven census coil celery prefer shiver ability panda")
    #PUBLIC_KEY2 = "GGFFDGMKL6QYZNGNIGHAAHWKTLAUOZ5A5WKEEI4762SVW6MGK6T4JXWP74"
    # DEV NETWORK KEYS
    PRIVATE_KEY2 = to_private_key("enter broccoli lawn dilemma silly easy explain mechanic unusual skate elder ecology eyebrow canyon wood million crush dune autumn roof base stumble innocent abandon pizza")
    PUBLIC_KEY2 = "VB23U533V4IS2OS5WPAVAGCLUUMABQHE3ACXKY7O4JMYCGPYICBJD4CWVY"
    account = Account(PRIVATE_KEY2, PUBLIC_KEY2, setup_algod_client)
    return account

@pytest.fixture
def setup_account3(setup_algod_client):
    #PRIVATE AND PUBLIC KEY3
    # RELEASE NETWORK KEYS
    #PRIVATE_KEY3 = to_private_key("tiger bean size pass click north harsh legend share radio leopard patient blur deputy adapt organ rescue enable october order relief label race abstract already")
    #PUBLIC_KEY3 = "NKWJZM723TPBJRWWODMP5OID7HQTJ7RYXISZYNEUMQYD6F3BZ6M7VBC7NM"
    # DEV NETWORK KEYS
    PRIVATE_KEY3 = to_private_key("ill elite accident aunt laptop dice traffic grass protect coffee guide marble panic start bracket glove tornado stove breeze drip rifle viable artist above fruit")
    PUBLIC_KEY3 = "WGEIHXPK7C6WV2WBMXXHMLAXTXT6EH6JWJDRAYXL7R26V6M66PK3GRQ62E"
    account = Account(PRIVATE_KEY3, PUBLIC_KEY3, setup_algod_client)
    return account

@pytest.fixture
def setup_account3DEV(setup_algod_client):
    #PRIVATE AND PUBLIC KEY3
    # RELEASE NETWORK KEYS
    #PRIVATE_KEY3 = to_private_key("tiger bean size pass click north harsh legend share radio leopard patient blur deputy adapt organ rescue enable october order relief label race abstract already")
    #PUBLIC_KEY3 = "NKWJZM723TPBJRWWODMP5OID7HQTJ7RYXISZYNEUMQYD6F3BZ6M7VBC7NM"
    # DEV NETWORK KEYS
    PRIVATE_KEY3 = to_private_key("ill elite accident aunt laptop dice traffic grass protect coffee guide marble panic start bracket glove tornado stove breeze drip rifle viable artist above fruit")
    PUBLIC_KEY3 = "WGEIHXPK7C6WV2WBMXXHMLAXTXT6EH6JWJDRAYXL7R26V6M66PK3GRQ62E"
    account = Account(PRIVATE_KEY3, PUBLIC_KEY3, setup_algod_client)
    return account

@pytest.fixture
def setup_account4(setup_algod_client, setup_account):
    #PRIVATE AND PUBLIC KEY4
    PRIVATE_KEY4 = to_private_key("genuine burger urge heart spot science vague guess timber rich olympic cheese found please then snack nice arrest coin seminar pyramid adult flip absorb apology")
    PUBLIC_KEY4 = "7LQ7U4SEYEVQ7P4KJVCHPJA5NSIFJTGIEXJ4V6MFS4SL5FMDW6MYHL2JXM"
    account = Account(PRIVATE_KEY4, PUBLIC_KEY4, setup_algod_client)
    if not account.account_exists():
        funding_account = setup_account
        application_info = funding_account.get_account_info()
        print(application_info)
        fund_ammount = application_info['amount']/2
        print(fund_ammount)
        print(type(fund_ammount))
        funding_account.fund(PUBLIC_KEY4, int(fund_ammount))
    return account

@pytest.fixture
def setup_account4DEV(setup_algod_client, setup_accountDEV):
    #PRIVATE AND PUBLIC KEY4
    PRIVATE_KEY4 = to_private_key("genuine burger urge heart spot science vague guess timber rich olympic cheese found please then snack nice arrest coin seminar pyramid adult flip absorb apology")
    PUBLIC_KEY4 = "7LQ7U4SEYEVQ7P4KJVCHPJA5NSIFJTGIEXJ4V6MFS4SL5FMDW6MYHL2JXM"
    account = Account(PRIVATE_KEY4, PUBLIC_KEY4, setup_algod_client)
    if not account.account_exists():
        funding_account = setup_account
        application_info = funding_account.get_account_info()
        print(application_info)
        fund_ammount = application_info['amount']/2
        print(fund_ammount)
        print(type(fund_ammount))
        funding_account.fund(PUBLIC_KEY4, int(fund_ammount))
    return account

@pytest.fixture
def setup_account5(setup_algod_client, setup_account2):
    #PRIVATE AND PUBLIC KEY5
    PRIVATE_KEY5 = to_private_key("loan journey alarm garage bulk olympic detail pig edit other brisk sense below when false ripple cute buffalo tissue again boring manual excuse absent injury")
    PUBLIC_KEY5 = "6EVZZTWUMODIXE7KX5UQ5WGQDQXLN6AQ5ELUUQHWBPDSRTD477ECUF5ABI"
    account = Account(PRIVATE_KEY5, PUBLIC_KEY5, setup_algod_client)
    if not account.account_exists():
        funding_account = setup_account2
        application_info = funding_account.get_account_info()
        print(application_info)
        fund_ammount = application_info['amount']/2
        print(fund_ammount)
        print(type(fund_ammount))
        funding_account.fund(PUBLIC_KEY5, int(fund_ammount))
    return account

@pytest.fixture
def setup_account5DEV(setup_algod_client, setup_account2DEV):
    #PRIVATE AND PUBLIC KEY5
    PRIVATE_KEY5 = to_private_key("loan journey alarm garage bulk olympic detail pig edit other brisk sense below when false ripple cute buffalo tissue again boring manual excuse absent injury")
    PUBLIC_KEY5 = "6EVZZTWUMODIXE7KX5UQ5WGQDQXLN6AQ5ELUUQHWBPDSRTD477ECUF5ABI"
    account = Account(PRIVATE_KEY5, PUBLIC_KEY5, setup_algod_client)
    if not account.account_exists():
        funding_account = setup_account2
        application_info = funding_account.get_account_info()
        print(application_info)
        fund_ammount = application_info['amount']/2
        print(fund_ammount)
        print(type(fund_ammount))
        funding_account.fund(PUBLIC_KEY5, int(fund_ammount))
    return account

@pytest.fixture
def setup_account6(setup_algod_client, setup_account3):
    #PRIVATE AND PUBLIC KEY6
    PRIVATE_KEY6 = "BwWsnRdikG9RgKLarja+Pn7tavTseR8pRSmztb8w6BgMhberskbTOIq6LVlwROafuv6lECv2KsQgrvz03gCUDg=="
    PUBLIC_KEY6 = "BSC3PK5SI3JTRCV2FVMXARHGT65P5JIQFP3CVRBAV36PJXQASQHMKT6MOI"
    account = Account(PRIVATE_KEY6, PUBLIC_KEY6, setup_algod_client)
    if not account.account_exists():
        funding_account = setup_account3
        application_info = funding_account.get_account_info()
        print(application_info)
        fund_ammount = application_info['amount']/2
        print(fund_ammount)
        print(type(fund_ammount))
        funding_account.fund(PUBLIC_KEY6, int(fund_ammount))
    return account

@pytest.fixture
def setup_account6DEV(setup_algod_client, setup_account3DEV):
    #PRIVATE AND PUBLIC KEY6
    PRIVATE_KEY6 = "BwWsnRdikG9RgKLarja+Pn7tavTseR8pRSmztb8w6BgMhberskbTOIq6LVlwROafuv6lECv2KsQgrvz03gCUDg=="
    PUBLIC_KEY6 = "BSC3PK5SI3JTRCV2FVMXARHGT65P5JIQFP3CVRBAV36PJXQASQHMKT6MOI"
    account = Account(PRIVATE_KEY6, PUBLIC_KEY6, setup_algod_client)
    if not account.account_exists():
        funding_account = setup_account3
        application_info = funding_account.get_account_info()
        print(application_info)
        fund_ammount = application_info['amount']/2
        print(fund_ammount)
        print(type(fund_ammount))
        funding_account.fund(PUBLIC_KEY6, int(fund_ammount))
    return account

#=========================Land_Registry================================================#


#=========================Pinata_Setup=================================================#

@pytest.fixture
def setup_pinata():
    key = "701eb0b47f41e945a859"
    secret = "caf08886c4b2dde12a3946b5ffebf94677cc941ca8b4cf414364da6570057c81"
    pinata = PinataSDK(key, secret)
    assert pinata.test() == 200
    return pinata

#========================Auxiliary_Methods=============================================#

def verify_in_created_assets(new_asset_id, created_assets):
    for asset in created_assets:
        if asset['index'] == new_asset_id:
            return True
    return False
    
def verify_in_assets(new_asset_id, assets):
    for asset in assets:
        if asset['asset-id'] == new_asset_id:
            return True
    return False

def hasAsset(new_asset_id, assets):
    for asset in assets:
        if asset['asset-id'] == new_asset_id and asset['amount'] >= 1:
            return True
    return False

def noAsset(new_asset_id, assets):
    for asset in assets:
        if asset['asset-id'] == new_asset_id and asset['amount'] == 0:
            return True
    return False

def get_global_variable(app_info):
    global_variables = dict()
    for variable in app_info['params']['global-state']:
        bytes_key = base64.b64decode(variable['key'])
        key = bytes_key.decode("utf-8")
        if(variable['value']['type'] == 2):
            global_variables[key] = variable['value']['uint']
        else:
            global_variables[key] = variable['value']['bytes']
    return global_variables

def get_local_variables(app_info):
    local_variables = dict()
    for variable in app_info['app-local-state']['key-value']:
        bytes_key = base64.b64decode(variable['key'])
        key = bytes_key.decode("utf-8")
        if(variable['value']['type'] == 2):
            local_variables[key] = variable['value']['uint']
        else:
            local_variables[key] = variable['value']['bytes']
    return local_variables