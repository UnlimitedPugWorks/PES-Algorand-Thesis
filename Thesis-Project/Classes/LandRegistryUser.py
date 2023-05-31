# Imports
import sys

import json
import base64
from hashlib import sha256
from algosdk.v2client import algod, indexer
from algosdk import transaction
from algosdk.transaction import LogicSigAccount, StateSchema, PaymentTxn, ApplicationCallTxn
from algosdk.encoding import encode_address, checksum
from algosdk.atomic_transaction_composer import *
from algosdk import account, mnemonic, constants
from Classes.Account import Account
from Classes.PinataSDK import PinataSDK
from os import getcwd
from base64 import b32encode
from Classes.SmartContract import SmartContract, get_app_address, get_global_variables, MIN_BALANCE, GLOBAL_BYTE_PRICE, GLOBAL_INT_PRICE

# CONSTANTS

CURRENT_PATH = "TEAL/"


class LandRegistryUser(SmartContract):

    def __init__(self, account: Account, app_id: int):
        super().__init__(account, app_id) 

    

