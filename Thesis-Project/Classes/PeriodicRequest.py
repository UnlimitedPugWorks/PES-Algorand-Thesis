from algosdk.transaction import Transaction
from datetime import datetime
from algosdk.encoding import encode_address, checksum
from algosdk.v2client.algod import AlgodClient
from Classes.SmartContract import get_app_address, get_global_variables, get_local_variables
from Classes.Request import Request, get_asset_metadata
import base64
import requests
import json


class PeriodicRequest(Request):

    def __init__(self, txid: int, algod_client: AlgodClient, sender_app_id: int, asset_id: int, seller_address: str):
        super().__init__(txid, algod_client, sender_app_id, asset_id, seller_address)
        if self.sender_app_id != 0:
            sender_global_variables = get_global_variables(self.sender_app_id, algod_client)
            self.asset_info = get_asset_metadata(asset_id, algod_client)
            self.sender_app_address = get_app_address(self.sender_app_id)
            self.nft_manager_app_id = sender_global_variables['NFT_Manager_Id']
            print(sender_global_variables)
            self.start_time = sender_global_variables["Start_Timestamp"]
            number_of_payments = sender_global_variables["Number_of_Payments"]
            self.response_times = []
            for num in range(1, number_of_payments + 1):
                payment_date = self.start_time + (31536000/number_of_payments) * num
                self.response_times.append(payment_date)

    def ready_to_respond(self, current_date: datetime) -> bool:
        # If current response is available
        if current_date.timestamp() > self.response_times[0]:
            # Deletes current timestamp
            self.response_times.pop(0)
            return True
        else:
            return False

    def ready_to_delete(self, current_date) -> bool:
        return len(current_date.timestamp()) == 0


    def __str__(self):
        return_str = "Id:" + str(self.txid) + "| "
        #return_str += "Sender:" + str(self.transaction) + "| "
        return_str += "Seller:"  + str(self.seller_address) + "| "
        return_str += "Response Time" + str(self.start_time)
        return return_str

    def __repr__(self):
        return_str = "Id:" + str(self.txid) + "| "
        #return_str += "Sender:" + str(self.transaction) + "| "
        return_str += "Seller:"  + str(self.seller_address) + "| "
        return_str += "Response Time" + str(self.start_time)
        return return_str
