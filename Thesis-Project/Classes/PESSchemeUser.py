import json
import base64
from hashlib import sha256
from algosdk.v2client import algod, indexer
from algosdk import transaction
from algosdk.transaction import LogicSigAccount, StateSchema, ApplicationCreateTxn, PaymentTxn, ApplicationCallTxn
from algosdk.encoding import encode_address, checksum, decode_address
from algosdk.atomic_transaction_composer import *
from algosdk import account, mnemonic, constants
from Classes.Account import Account
from Classes.PinataSDK import PinataSDK
from Classes.SmartContract import SmartContract, get_global_variables, get_app_address, convert_box_names

BUY_NFT = "Buy_NFT"
GET_REFUND  = "Get_Refund"
CREATE_BOX = "Create_Box"

class PESSchemeUser(SmartContract):

    def __init__(self, account: Account, app_id: int):
        super().__init__(account, app_id)

    def get_refund(self):
        # Takes the variables from account
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        # Obtains the suggested params
        sp = algod_client.suggested_params()

        sp.fee = 2 * sp.min_fee

        sp.flat_fee = True

        # Bytes Args
        bytes_args = [GET_REFUND.encode()]

        # Creates Transaction
        unsigned_txn = transaction.ApplicationCallTxn(address, sp, self.app_id, transaction.OnComplete.NoOpOC, app_args=bytes_args, boxes=[[self.app_id, decode_address(address)]])

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

    def create_box(self):
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

        # To pay the minimum fee of the Answer Request + pay the minimum fee
        ammount = 2500 + 400 * (address_length + 8)

        print(ammount)

        ptxn = PaymentTxn(
            address, sp, self.app_address, ammount)

        sp.fee = 0

        sp.flat_fee = True

        # Creates the applicationOptInTxn
        atxn = ApplicationCallTxn(address, sp, self.app_id, on_complete=transaction.OnComplete.NoOpOC, app_args=[CREATE_BOX.encode()], boxes=[[self.app_id, decode_address(address)]])

        atc.add_transaction(TransactionWithSigner(ptxn, signer))

        atc.add_transaction(TransactionWithSigner(atxn, signer))

        result = atc.execute(algod_client, 4)

        print(result)

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

