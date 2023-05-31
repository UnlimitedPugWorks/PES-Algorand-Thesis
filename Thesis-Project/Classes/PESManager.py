# IMPORTS

import json
import base64
from hashlib import sha256
from algosdk.v2client import algod, indexer
from algosdk import transaction
from algosdk.transaction import LogicSigAccount, StateSchema, ApplicationCreateTxn, PaymentTxn
from algosdk.encoding import encode_address, checksum, decode_address
from algosdk.atomic_transaction_composer import *
from algosdk import account, mnemonic, constants
from Classes.Account import Account
from Classes.SmartContract import SmartContract, get_app_address, convert_box_names, MIN_BALANCE

# CONSTANTS
CURRENT_PATH = "TEAL/"
NFT_MANAGER_PREFIX = "NFT-Manager-"
APPROVAL_PATH = CURRENT_PATH + NFT_MANAGER_PREFIX + "approval.teal"
CLEAR_PATH = CURRENT_PATH + NFT_MANAGER_PREFIX + "clear.teal"

class PESManager(SmartContract):

    def __init__(self, account: Account, app_id: int, oracle_app_id: int, land_registry_address: str):

        if (app_id <= 0):

            # Takes the variables from account
            address = account.get_address()
            private_key = account.get_private_key()
            algod_client = account.get_algod_client()

            # build transaction
            params = algod_client.suggested_params()
            params.fee = params.min_fee
            params.flat_fee = True

            # Loads approval program
            approval_file = open(APPROVAL_PATH, "r")

            approval_result = algod_client.compile(approval_file.read())

            approval_bytes = base64.b64decode(approval_result["result"])

            approval_file.close()

            # Loads clear program
            clear_file = open(CLEAR_PATH, "r")

            clear_result = algod_client.compile(clear_file.read())

            clear_bytes = base64.b64decode(clear_result["result"])

            clear_file.close()

            # Global Schema
            global_schema = StateSchema(1, 2)

            # Local Schema
            local_schema = StateSchema(0, 0)

            # Create unsigned transaction that will create App
            unsigned_txn = ApplicationCreateTxn(address, params, 0, approval_bytes, clear_bytes, global_schema, local_schema, foreign_apps=[oracle_app_id], accounts=[land_registry_address], extra_pages=2)

            # Sign transaction
            signed_txn = unsigned_txn.sign(private_key)

            # Send transaction
            txid = algod_client.send_transaction(signed_txn)

            # Wait for result
            try:
                confirmed_txn = transaction.wait_for_confirmation(
                    algod_client, txid, 4)
                created_app_id = confirmed_txn["application-index"]
                super().__init__(account, created_app_id) 
            except Exception as err:
                print(err)
                super().__init__(account, 0)

            
            # Creates transaction to fullfill Minimum Balance
            unsigned_txn = PaymentTxn(address, params, get_app_address(self.app_id) , MIN_BALANCE)
            # Sign transaction
            signed_txn = unsigned_txn.sign(private_key)

            # Send transaction
            txid = algod_client.send_transaction(signed_txn)

            # Wait for result
            try:
                confirmed_txn = transaction.wait_for_confirmation(
                    algod_client, txid, 4)
            except Exception as err:
                print(err)
        else:
            # If the app_id is higher than 0, then it means that the Land Registry has already been deployed
            super().__init__(account, app_id)

    def get_reputations(self):
        # Takes the algod_client from account
        algod_client = account.get_algod_client()    
        application_boxes = algod_client.application_boxes(self.app_id)
        users_list = []
        for box in application_boxes['boxes']:
            users_list.append(convert_box_names(box['name']))
        reputation_list = []
        for user in users_list:
            reputation = (algod_client.application_box_by_name(self.app_id, decode_address(user)))['value']
            reputation_value = ord((base64.b64decode(reputation)).decode('utf-8'))
            reputation_list.append({user:reputation_value})
        for reputation in reputation_list:
            print(reputation)
    
    def get_user_reputation(self, user_address: str):
        # Takes the variables from account
        algod_client = account.get_algod_client()    
        application_boxes = algod_client.application_boxes(self.app_id)
        users_list = []
        for box in application_boxes['boxes']:
            users_list.append(convert_box_names(box['name']))     
        if user_address in users_list:
            reputation = (algod_client.application_box_by_name(self.app_id, decode_address(user_address)))['value']
            reputation_value = ord((base64.b64decode(reputation)).decode('utf-8'))
            print({user_address:reputation_value})
        else:
            print("User has no box created on NFT Manager")  
    
    