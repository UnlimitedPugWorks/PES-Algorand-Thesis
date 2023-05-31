from abc import ABC, abstractclassmethod
from Classes.Account import Account
from algosdk.encoding import encode_address, checksum
from algosdk.v2client.algod import AlgodClient
import base64
import json
import requests

GLOBAL_INT_PRICE = 28500
GLOBAL_BYTE_PRICE = 50000
LOCAL_INT_PRICE = 28500
LOCAL_BYTE_PRICE = 50000
MIN_BALANCE = int(1e5)

class SmartContract():

    def __init__(self, account: Account, app_id: int):
        self.app_id = app_id
        self.account = account
        if app_id != 0:
            self.app_address = get_app_address(app_id)
        else:
            self.app_address = None


def get_app_address(app_id: int) -> str:
    return encode_address(checksum(b'appID'+(app_id).to_bytes(8, 'big')))

def get_global_variables(app_id: int, algod_client: AlgodClient) -> dict:
    app_info = algod_client.application_info(app_id)
    global_variables = dict()
    for variable in app_info['params']['global-state']:
        bytes_key = base64.b64decode(variable['key'])
        key = bytes_key.decode("utf-8")
        if(variable['value']['type'] == 2):
            global_variables[key] = variable['value']['uint']
        else:
            global_variables[key] = variable['value']['bytes']
    return global_variables

def get_local_variables(account_address: str, app_id: int, algod_client: AlgodClient) -> dict:
    app_info = algod_client.account_application_info(account_address, app_id)
    local_variables = dict()
    for variable in app_info['app-local-state']['key-value']:
        bytes_key = base64.b64decode(variable['key'])
        key = bytes_key.decode("utf-8")
        if(variable['value']['type'] == 2):
            local_variables[key] = variable['value']['uint']
        else:
            local_variables(app_info)[key] = variable['value']['bytes']
    return local_variables

def box_cost(key: str, size: int) -> int:
    return (2500 + 400 * (len(key) + size))

def deploy_cost(global_ints: int, global_bytes: int) -> int:
    return MIN_BALANCE + global_ints * GLOBAL_INT_PRICE + global_bytes * GLOBAL_BYTE_PRICE

def local_storage_cost(global_ints: int, global_bytes: int) -> int:
    return MIN_BALANCE + global_ints * GLOBAL_INT_PRICE + global_bytes * GLOBAL_BYTE_PRICE

def var_to_base64(var_key: str) -> bytes:
    return base64.b64encode(var_key.encode())

def convert_address(b64_address:str):
    bytes_address = base64.b64decode(b64_address)
    str_address = encode_address(bytes_address)
    return str_address

def convert_box_names(b64_box_name:str):
    bytes_box_name = base64.b64decode(b64_box_name)
    str_box_name = encode_address(bytes_box_name)
    return str_box_name

def get_asset_json(algod_client: AlgodClient, asset_id: int) -> dict:
    asset_info = algod_client.asset_info(asset_id)
    print(asset_info)
    url = (asset_info)['params']['url']
    cid = url.removeprefix("ipfs://")
    ipfs_url = "https://ipfs.io/ipfs/" + cid
    response = requests.get(url= ipfs_url)
    response_json = json.loads(response.text)
    return response_json