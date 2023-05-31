# IMPORTS

import json
import base64
import requests
from hashlib import sha256
from algosdk.v2client import algod, indexer
from algosdk import transaction
from algosdk.transaction import LogicSigAccount, StateSchema, ApplicationCreateTxn, ApplicationOptInTxn, PaymentTxn, ApplicationCallTxn, ApplicationDeleteTxn
from algosdk.encoding import encode_address, checksum, decode_address
from algosdk.atomic_transaction_composer import *
from algosdk import account, mnemonic, constants
from Classes.Account import Account
from Classes.PESScheme import PESScheme
from Classes.PESSchemeAsset import PESSchemeAsset
from Classes.PESSchemeNoAsset import PESSchemeNoAsset
from Classes.PESSchemePeriodic import PESSchemePeriodic
from Classes.SmartContract import SmartContract, get_global_variables, convert_address, convert_box_names, GLOBAL_BYTE_PRICE, GLOBAL_INT_PRICE, MIN_BALANCE, deploy_cost

# CONSTANTS
CURRENT_PATH = "TEAL/"
NFT_MANAGER_PREFIX = "NFT-Manager-"
APPROVAL_PATH = CURRENT_PATH + NFT_MANAGER_PREFIX + "approval.teal"
CLEAR_PATH = CURRENT_PATH + NFT_MANAGER_PREFIX + "clear.teal"
CREATE_NFT_SELLER = "create_NFT_seller"
DELETE_NFT_SELLER = "delete_NFT_seller"
CREATE_BOX = "create_box"
seller_state = ['SaleNotStarted', 'WaitingForResponse', 'NegativeResponse', 'PositiveResponse']

class PESManagerUser(SmartContract):

    def __init__(self, account: Account, app_id: int):
        super().__init__(account, app_id)
        
        global_vars = get_global_variables(app_id, self.account.algod_client)
        self.oracle_app_id = global_vars['oracle_app_id']
        self.land_registry_address = convert_address(global_vars['land_registry_address'])


    def create_box_PESManager(self):
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        address_length = len(decode_address(address))

        # Suggested params
        sp = algod_client.suggested_params()

        sp.fee = 2 * sp.min_fee

        sp.flat_fee = True

        # Creates an atomic transaction composer
        atc = AtomicTransactionComposer()

        signer = AccountTransactionSigner(private_key)

        # The box ammount
        ammount = 2500 + 400 * (address_length + 1)

        ptxn = PaymentTxn(
            address, sp, self.app_address, ammount)

        sp.fee = 0
        sp.flat_fee = True

        # Creates the applicationOptInTxn
        #atxn = ApplicationOptInTxn(address, sp, self.app_id, boxes=[[self.app_id, decode_address(address)]])
        #atxn = ApplicationOptInTxn(address, sp, self.app_id, boxes=[[self.app_id, decode_address(address)]])
        atxn = ApplicationCallTxn(address, sp, self.app_id, on_complete=transaction.OnComplete.NoOpOC, app_args=[CREATE_BOX.encode()], boxes=[[self.app_id, decode_address(address)]])

        atc.add_transaction(TransactionWithSigner(ptxn, signer))

        atc.add_transaction(TransactionWithSigner(atxn, signer))

        result = atc.execute(algod_client, 4)


    # Funds spent
    # 449500 - Minimum Balance requirement for creating an NFT Seller
    # Min_Txn_Fee - For the createApplication Transaction
    # 2* Min_Txn_Fee - To pay for both the ApplicationCall and Payment Transaction
    # 449500 + 3.Min_Txn_Fee
    def create_PES_scheme(self, type: int):
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        # Suggested params
        sp = algod_client.suggested_params()

        #sp.fee = sp.min_fee
        sp.fee = 3 * sp.min_fee

        sp.flat_fee = True

        # Creates an atomic transaction composer
        atc = AtomicTransactionComposer()

        signer = AccountTransactionSigner(private_key)

        # To pay the minimum balance to create the PES Scheme
        #ammount =  MIN_BALANCE + (GLOBAL_INT_PRICE) * 8 + (GLOBAL_BYTE_PRICE) * 4
        if type == 2:
            ammount =  deploy_cost(9, 3)
        else:
            ammount = deploy_cost(8, 2) if type else deploy_cost(7, 2)

        ptxn = PaymentTxn(address, sp, self.app_address, ammount)

        sp.fee = 0
        sp.flat_fee = True

        atxn = ApplicationCallTxn(address, sp, self.app_id, transaction.OnComplete.NoOpOC, app_args=[CREATE_NFT_SELLER.encode(), type], boxes=[[self.app_id, decode_address(address)]], foreign_apps=[0, self.oracle_app_id], accounts=[self.land_registry_address])

        atc.add_transaction(TransactionWithSigner(ptxn, signer))

        atc.add_transaction(TransactionWithSigner(atxn, signer))

        result = atc.execute(algod_client, 4)

        created_app_id = (algod_client.pending_transaction_info(result.tx_ids[1]))['inner-txns'][0]['application-index']

        print(created_app_id)

        if type == 2:
           return PESSchemePeriodic(self.account, created_app_id, self.oracle_app_id, self.land_registry_address, address)
        else:
            return PESSchemeAsset(self.account, created_app_id, self.oracle_app_id, self.land_registry_address, address) if type else PESSchemeNoAsset(self.account, created_app_id, self.oracle_app_id, self.land_registry_address, address)


    def delete_PES_Scheme(self, pes_scheme_app_id: int):
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        # Suggested params
        sp = algod_client.suggested_params()

        sp.fee = 3 * sp.min_fee

        # Test Flat Fee
        sp.flat_fee = True   

        unsigned_txn = ApplicationCallTxn(sender=address, sp=sp, index=self.app_id, on_complete=transaction.OnComplete.NoOpOC, app_args=[DELETE_NFT_SELLER.encode()], foreign_apps=[pes_scheme_app_id, self.oracle_app_id])

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

        


    def show_created_NFT_Sellers(self):
        address = self.account.get_address()
        algod_client = self.account.get_algod_client()
        created_apps = algod_client.account_info(self.app_address)['created-apps']
        for app in created_apps:
            app_global_state = get_app_global_variables(app['params']['global-state'])
            if app_global_state['State'] == 0:
                continue
            print(self.print_nft_seller(app_global_state, app['id']))

    def get_asset_description(self, asset_id: int):
        algod_client = self.account.algod_client
        asset_info = algod_client.asset_info(asset_id)
        print(asset_info)
        url = (asset_info)['params']['url']
        cid = url.removeprefix("ipfs://")
        ipfs_url = "https://ipfs.io/ipfs/" + cid
        response = requests.get(url= ipfs_url)
        response_json = json.loads(response.text)
        return response_json['description']

    def print_nft_seller(self, app_global_state: dict, app_id: int) -> str:
        return_str = str(app_id) + " | " 
        #description = (base64.b64decode(app_global_state['Description'])).decode("utf-8")
        #return_str += description + " | "
        seller_address = encode_address(base64.b64decode(app_global_state['Seller_Address']))
        return_str += seller_address + " | "
        state = app_global_state['State']
        return_str += seller_state[state]
        return return_str

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


def get_app_global_variables(app_global_state: dict) -> dict:
    app_global_variables = dict()
    for variable in app_global_state:
        bytes_key = base64.b64decode(variable['key'])
        key = bytes_key.decode("utf-8")
        if(variable['value']['type'] == 2):
            app_global_variables[key] = variable['value']['uint']
        else:
            app_global_variables[key] = variable['value']['bytes']
    return app_global_variables

'''
if __name__ == "__main__":

    # Algod_client
    ALGOD_ADDRESS = "http://localhost:4001"
    ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    # Creates an algod client
    algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

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
'''