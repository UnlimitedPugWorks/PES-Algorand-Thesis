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
from Classes.PESSchemeUser import PESSchemeUser


BUY_NFT = "Buy_NFT"
GET_REFUND  = "Get_Refund"
CREATE_BOX = "Create_Box"

class PESSchemeNoAssetUser(PESSchemeUser):

    def __init__(self, account: Account, app_id: int):

        super().__init__(account, app_id)
        
        algod_client = self.account.algod_client

        response = algod_client.application_boxes(app_id)
        found_box = False
        for box in response['boxes']:
            if convert_box_names(box['name']) == account.address:
                found_box = True
                break

        if found_box == False:
            self.create_box()

    def buy_NFT(self, quantity: int):
        # Takes the variables from account
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        # Obtains the suggested params
        sp = algod_client.suggested_params()

        sp.fee = 2 * sp.min_fee

        sp.flat_fee = True

        atc = AtomicTransactionComposer()

        signer = AccountTransactionSigner(private_key)

        # The application args
        bytes_args = [BUY_NFT.encode(), quantity]

        amount = quantity

        ptxn = transaction.PaymentTxn(
            address, sp, self.app_address, amount)

        sp.fee = 0

        sp.flat_fee = True

        ctxn = transaction.ApplicationCallTxn(address, sp, self.app_id, transaction.OnComplete.NoOpOC, app_args=bytes_args, boxes=[[self.app_id, decode_address(address)]])


        atc.add_transaction(TransactionWithSigner(ptxn, signer))

        atc.add_transaction(TransactionWithSigner(ctxn, signer))

        result = atc.execute(algod_client, 4)

        for tx_id in result.tx_ids:
            print(algod_client.pending_transaction_info(tx_id))
