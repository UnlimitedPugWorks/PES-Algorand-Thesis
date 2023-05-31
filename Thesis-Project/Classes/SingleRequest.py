from algosdk.transaction import Transaction
from datetime import datetime
from algosdk.encoding import encode_address, checksum
from algosdk.v2client.algod import AlgodClient
from Classes.Request import Request
from Classes.SmartContract import get_app_address, get_global_variables, get_local_variables
import base64
import requests
import json



class SingleRequest(Request):

    def __init__(self, txid: int, algod_client: AlgodClient, sender_app_id: int, asset_id: int, seller_address: str):  
        super().__init__(txid, algod_client, sender_app_id, asset_id, seller_address)      
        if self.sender_app_id != 0:
            sender_global_variables = get_global_variables(self.sender_app_id, algod_client)
            self.asset_id = asset_id
            self.asset_info = get_asset_metadata(asset_id, algod_client)
            self.sender_app_address = get_app_address(self.sender_app_id)
            self.seller_address = seller_address
            self.nft_manager_app_id = sender_global_variables['NFT_Manager_Id']
            self.response_time = sender_global_variables['Receive_Timestamp']

    def __str__(self):
        return_str = "Id:" + str(self.txid) + "| "
        #return_str += "Sender:" + str(self.transaction) + "| "
        return_str += "Seller:"  + str(self.seller_address) + "| "
        return_str += "Response Time" + str(self.response_time)
        return return_str

    def __repr__(self):
        return_str = "Id:" + str(self.txid) + "| "
        #return_str += "Sender:" + str(self.transaction) + "| "
        return_str += "Seller:"  + str(self.seller_address) + "| "
        return_str += "Response Time" + str(self.response_time)
        return return_str

    def __eq__(self, o):
        return self.txid == o.txid
        #return self.transaction['id'] == o.transaction['id']

def get_asset_metadata(asset_id: int, algod_client: AlgodClient):
    asset_info = algod_client.asset_info(asset_id)
    print(asset_info)
    url = (asset_info)['params']['url']
    cid = url.removeprefix("ipfs://")
    ipfs_url = "https://ipfs.io/ipfs/" + cid
    response = requests.get(url= ipfs_url)
    response_json = json.loads(response.text)
    print(response_json)
    return response_json