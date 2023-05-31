# Imports
import sys

import json
import base64
from hashlib import sha256
from algosdk.v2client import algod, indexer
from algosdk import transaction
from algosdk.transaction import LogicSigAccount, StateSchema, PaymentTxn
from algosdk.encoding import encode_address, checksum
from algosdk.atomic_transaction_composer import *
from algosdk import account, mnemonic, constants
from Classes.Account import Account
from Classes.PinataSDK import PinataSDK
from os import getcwd
from base64 import b32encode
from Classes.SmartContract import SmartContract, get_app_address, MIN_BALANCE

# CONSTANTS

CURRENT_PATH = "TEAL/"
LAND_REGISTRY_PREFIX = "Land-Registery-"
APPROVAL_PATH = CURRENT_PATH + LAND_REGISTRY_PREFIX + "approval.teal"
CLEAR_PATH = CURRENT_PATH + LAND_REGISTRY_PREFIX + "clear.teal"
REGISTER_LAND = "Register_Land"
TRANSFER_LAND = "Transfer_Registered_Land"
CLAWBACK_LAND = "Land_Clawback"


class LandRegistry(SmartContract):

    def __init__(self, account: Account, app_id: int):

        self.created_assets_id = list()

        if (app_id <= 0):

            # Takes the variables from account
            address = account.get_address()
            private_key = account.get_private_key()
            algod_client = account.get_algod_client()

            # Shows the address and account balance of that address
            #print("My address: {}".format(address))
            account_info = algod_client.account_info(address)
            #print("Account balance: {} microAlgos".format(account_info.get('amount')))

            # build transaction
            params = algod_client.suggested_params()

            params.fee = params.min_fee
        
            params.flat_fee = True

            #print(getcwd())

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
            global_schema = StateSchema(0, 0)

            # Local Schema
            local_schema = StateSchema(0, 0)

            # Create unsigned transaction that will create App
            unsigned_txn = transaction.ApplicationCreateTxn(
                address, params, 0, approval_bytes, clear_bytes, global_schema, local_schema)

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

            params.fee = params.min_fee
        
            params.flat_fee = True

            # Creates transaction to fullfill Minimum Balance
            unsigned_txn = transaction.PaymentTxn(address, params, get_app_address(self.app_id) , MIN_BALANCE)
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

    def register_land(self, name, description, unit_name, file_name, file_path, pinata):

        # Takes the variables from creator account
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        # Pins the file using Pinata
        ipfs_file = pinata.pin_file(file_name, file_path)

        # Opens the file that is needed for the metadata json
        file = open(file_path, "rb")

        # Reads the file
        filestr = file.read()

        # Builds the metadata json that will be sent to the smart contract to create the NFT
        metadata_json = build_metadata_json(
            name, description, file_name, ipfs_file, filestr)

        #print(metadata_json)

        # Closes the file
        file.close()

        # Creates a sha256 hash of the metadata_json
        metadata_json_hash = sha256(
            metadata_json.encode()).digest()

        # Pins the json of the file
        ipfs_json = pinata.pin_json(name + ".json", metadata_json)

        ipfs_json_link = "ipfs://" + ipfs_json["IpfsHash"] + "#arc3"

        sp = algod_client.suggested_params()

        args = [REGISTER_LAND, ipfs_json_link,
                metadata_json_hash, name, unit_name]

        #print("args = " + str(args))

        bytes_args = []

        for x in args:
            if x != metadata_json_hash:
                bytes_args.append(x.encode())
            else:
                bytes_args.append(metadata_json_hash)

        #print("bytes_args = " + str(bytes_args))

        atc = AtomicTransactionComposer()

        signer = AccountTransactionSigner(private_key)

        sp.fee = sp.min_fee * 3
        sp.flat_fee = True

        ptxn = transaction.PaymentTxn(
            address, sp, self.app_address, MIN_BALANCE)

        sp.fee = 0
        
        sp.flat_fee = True

        atxn = transaction.ApplicationCallTxn(
            address, sp, self.app_id, transaction.OnComplete.NoOpOC, app_args=bytes_args)

        atc.add_transaction(TransactionWithSigner(ptxn, signer))

        atc.add_transaction(TransactionWithSigner(atxn, signer))

        result = atc.execute(algod_client, 4)

        '''
        for id in result.tx_ids:
            print(algod_client.pending_transaction_info(id))
        '''

        asset_id = algod_client.pending_transaction_info(result.tx_ids[1])['inner-txns'][0]['asset-index']

        '''
        print(asset_id)
        '''

        self.created_assets_id.append(asset_id)

        return asset_id

    def transfer_land(self, receiver_address, asset_id):

        # Takes the variables from creator account
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        # Suggest params
        sp = algod_client.suggested_params()
        sp.fee = sp.min_fee * 2
        sp.flat_fee = True

        # Encrypts the bytes
        bytes_args = [TRANSFER_LAND.encode()]

        #bytes_accounts = [address, receiver_address]
        bytes_accounts = [receiver_address]

        # Creates unsigned txn
        unsigned_txn = transaction.ApplicationCallTxn(
            address, sp, self.app_id, transaction.OnComplete.NoOpOC, app_args=bytes_args, foreign_assets=[asset_id], accounts=bytes_accounts)

        # Sign transaction
        signed_txn = unsigned_txn.sign(private_key)

        # Send transaction
        txid = algod_client.send_transaction(signed_txn)

        # Wait for result
        try:
            confirmed_txn = transaction.wait_for_confirmation(
                algod_client, txid, 4)
            print(confirmed_txn)
        except Exception as err:
            print(err)

    def clawback_land(self, sender_add, asset_id):

        # Takes the variables from creator account
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        # Suggest params
        sp = algod_client.suggested_params()

        sp.fee = sp.min_fee * 2
        sp.flat_fee = True

        # Encrypts the bytes
        bytes_args = [CLAWBACK_LAND.encode()]

        #bytes_accounts = [address, receiver_address]
        bytes_accounts = [sender_add]

        # Creates unsigned txn
        unsigned_txn = transaction.ApplicationCallTxn(
            address, sp, self.app_id, transaction.OnComplete.NoOpOC, app_args=bytes_args, foreign_assets=[asset_id], accounts=bytes_accounts)

        # Sign transaction
        signed_txn = unsigned_txn.sign(private_key)

        # Send transaction
        txid = algod_client.send_transaction(signed_txn)

        # Wait for result
        try:
            confirmed_txn = transaction.wait_for_confirmation(
                algod_client, txid, 4)
            print(confirmed_txn)
        except Exception as err:
            print(err)



def build_metadata_json(name: str, description: str, file_name: str, ipfs_json: dict, file: str) -> str:
    metadata_json = dict()
    metadata_json["name"] = name
    metadata_json["description"] = description
    metadata_json["image"] = "ipfs://" + ipfs_json["IpfsHash"]
    metadata_json["image_integrity"] = "sha-256-" + sha256(file).hexdigest()
    metadata_json["image_mimetype"] = "image/png"
    metadata_json["properties"] = dict()
    metadata_json["properties"]["file_url"] = file_name
    metadata_json["properties"]["file_url_integrity"] = "sha-256-" + \
        sha256(file).hexdigest()
    metadata_json["properties"]["file_url_mimetype"] = "image/png"
    return json.dumps(metadata_json)

