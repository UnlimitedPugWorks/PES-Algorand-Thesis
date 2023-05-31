import json
import base64
from hashlib import sha256
from algosdk.v2client import algod, indexer
from algosdk import transaction
from algosdk.transaction import LogicSigAccount, StateSchema, ApplicationCreateTxn
from algosdk.encoding import encode_address, checksum, decode_address
from algosdk.atomic_transaction_composer import *
from algosdk import account, mnemonic, constants
from Classes.Account import Account
from Classes.PinataSDK import PinataSDK
from Classes.SmartContract import SmartContract, get_app_address, get_global_variables, MIN_BALANCE , LOCAL_BYTE_PRICE, LOCAL_INT_PRICE
from Classes.PESScheme import PESScheme



# CONSTANTS
CURRENT_PATH = "TEAL/"
NFT_SELLER_PREFIX = "NFT-Seller-"
STATELESS_PREFIX = "-no-local"
APPROVAL_PATH = CURRENT_PATH + NFT_SELLER_PREFIX + "approval.teal"
CLEAR_PATH = CURRENT_PATH + NFT_SELLER_PREFIX + "clear.teal"
#APPROVAL_PATH = CURRENT_PATH + NFT_SELLER_PREFIX + STATELESS_PREFIX + "approval.teal"
#CLEAR_PATH = CURRENT_PATH + NFT_SELLER_PREFIX + STATELESS_PREFIX + "clear.teal"
START_SALE = "Start_Sale"
GIVE_REFUND = "Give_Refund"
seller_state = ['SaleNotStarted', 'WaitingForResponse', 'NegativeResponse', 'PositiveResponse']


class PESSchemeNoAsset(PESScheme):

    def __init__(self, account: Account, app_id: int, oracle_app_id: int, land_registry_address: str, es_provider: str):
        super().__init__(account, app_id, oracle_app_id, land_registry_address, es_provider)

    def start_sale(self, asset_id: int, pes_goal: int, period: int):        
        print("Entrei aqui")
        # Takes the variables from creator account
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        bytes_args = [START_SALE.encode(), pes_goal, period]

        atc = AtomicTransactionComposer()

        signer = AccountTransactionSigner(private_key)

        sp = algod_client.suggested_params()

        #ammount = 3 * sp.min_fee + MIN_BALANCE * (pow(10, decimals) + 3) + oracle_opt_in_price 
        ammount = 3 * sp.min_fee + 2 * MIN_BALANCE

        #print(ammount)

        sp = algod_client.suggested_params()

        sp.fee = 7 * sp.min_fee

        sp.flat_fee = True

        ptxn = transaction.PaymentTxn(
            address, sp, self.app_address, ammount)

        sp.fee = 0
        
        sp.flat_fee = True

        ctxn = transaction.ApplicationCallTxn(
            address, sp, self.app_id, transaction.OnComplete.NoOpOC, app_args=bytes_args, foreign_assets=[asset_id], accounts=[get_app_address(self.oracle_app_id), self.oracle_creator], foreign_apps=[self.oracle_app_id])

        atxn = transaction.AssetTransferTxn(
            address, sp, self.app_address, 1, asset_id)

        atc.add_transaction(TransactionWithSigner(ptxn, signer))

        atc.add_transaction(TransactionWithSigner(ctxn, signer))

        atc.add_transaction(TransactionWithSigner(atxn, signer))

        result = atc.execute(algod_client, 4)

        print(result)


    def give_refund(self, refund_address: str):
        # Takes the variables from account
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        # Obtains the suggested params
        sp = algod_client.suggested_params()

        sp.fee = 2 * sp.min_fee

        sp.flat_fee = True

        # Bytes Args
        bytes_args = [GIVE_REFUND.encode()]

        # Creates Transaction
        #unsigned_txn = transaction.ApplicationCallTxn(address, sp, self.app_id, transaction.OnComplete.NoOpOC, app_args=bytes_args)
        unsigned_txn = transaction.ApplicationCallTxn(address, sp, self.app_id, transaction.OnComplete.NoOpOC, app_args=bytes_args, boxes=[[self.app_id, decode_address(refund_address)]], accounts=[refund_address])

        # Sign transaction
        signed_txn = unsigned_txn.sign(private_key)

        # Send transaction
        txid = algod_client.send_transaction(signed_txn)

        # Wait for result
        try:
            confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
            print(confirmed_txn)
        except Exception as err:
            print(err)      


    def nft_seller_info(self):
        # Takes the variables from account
        algod_client = self.account.get_algod_client()

        global_variables = get_global_variables(self.app_id, algod_client)

        state = global_variables["State"]
    
        info_str = ""
        info_str += "Seller: " + global_variables["Seller_Address"] + "|"
        if seller_state[state] != SaleNotStarted:
            info_str += "State: " + seller_state[state] + "|"
            info_str += "End Date: " + global_variables["Receive_Timestamp"] + "|"
            info_str += "Number of Boxes: " + global_variables["Number_of_Offers"] + "|"
        print(info_str)

def build_metadata_json(name: str, description: str, file_name: str, ipfs_json: dict, file: str) -> str:
    metadata_json = dict()
    metadata_json["name"] = name + "@arc3"
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

def get_app_creator_address(algod_client, app_id):
    # Response
    response = algod_client.application_info(app_id)
    return response['params']['creator']

def validate_json(config_json: dict) -> bool:
    if "nft_name" not in config_json.keys():
        print("Asset name is missing!")
        return False
    elif "nft_unit_name" not in config_json.keys():
        print("Unit name is missing!")
        return False
    elif "decimals" not in config_json.keys():
        print("Decimals is missing!")
        return False
    elif "nft_price" not in config_json.keys():
        print("NFT Price is missing!")
        return False
    elif "period" not in config_json.keys():
        print("Period is missing!")
        return False   
    return True 


    
