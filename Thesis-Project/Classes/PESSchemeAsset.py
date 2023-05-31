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
START_SALE = "Start_Sale"
GIVE_REFUND = "Give_Refund"
seller_state = ['SaleNotStarted', 'WaitingForResponse', 'NegativeResponse', 'PositiveResponse']


class PESSchemeAsset(PESScheme):

    def __init__(self, account: Account, app_id: int, oracle_app_id: int, land_registry_address: str, es_provider: str):
        super().__init__(account, app_id, oracle_app_id, land_registry_address, es_provider)

    '''
    def start_sale(self, asset_id: int, nft_name: str, nft_unit_name: str, file_name:str, file_path:str, description:str, decimals: int, nft_price: int, period: int, pinata):        
        print("Entrei aqui")
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
            nft_name, description, file_name, ipfs_file, filestr)

        #print(metadata_json)

        # Closes the file
        file.close()

        # Creates a sha256 hash of the metadata_json
        metadata_json_hash = sha256(
            metadata_json.encode()).digest()

        # Pins the json of the file
        ipfs_json = pinata.pin_json(nft_name + ".json", metadata_json)

        ipfs_json_link = "ipfs://" + ipfs_json["IpfsHash"]


        args = [START_SALE, nft_name, nft_unit_name, ipfs_json_link,
                metadata_json_hash]

        bytes_args = []

        for x in args:
            if x != metadata_json_hash:
                bytes_args.append(x.encode())
            else:
                bytes_args.append(metadata_json_hash)

        bytes_args.append(decimals)
        bytes_args.append(nft_price)
        bytes_args.append(period)

        #print("bytes_args = " + str(bytes_args))

        atc = AtomicTransactionComposer()

        signer = AccountTransactionSigner(private_key)

        sp = algod_client.suggested_params()

        oracle_opt_in_price = MIN_BALANCE + (LOCAL_INT_PRICE) * 2 + (LOCAL_BYTE_PRICE) * 0

        #ammount = 3 * sp.min_fee + MIN_BALANCE * (pow(10, decimals) + 3) + oracle_opt_in_price 
        ammount = 3 * sp.min_fee + 3 * MIN_BALANCE + oracle_opt_in_price 

        #print(ammount)

        sp = algod_client.suggested_params()

        sp.fee = 9 * sp.min_fee

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

        created_asset_id = (algod_client.pending_transaction_info(result.tx_ids[1]))['inner-txns'][-1]['asset-index']

        for id in result.tx_ids:
            print(algod_client.pending_transaction_info(id))

        return created_asset_id
    '''

    def start_sale(self, asset_id: int, file_path: str):        
        print("Entrei aqui")
        # Takes the variables from creator account
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        # Opens the file that is needed for the metadata json
        f = open(file_path, "r")

        json_str = f.read()

        print(json_str)

        # Reads the Json
        pes_json = json.loads(json_str)

        print(pes_json)

        # Validate JSON
        if validate_json(pes_json) == False:
            print("Error with configuration file")
            return -1

        # Loads NFT Name from the JSON
        nft_name = pes_json['nft_name']

        # Loads NFT Unit name from the JSON
        nft_unit_name = pes_json['nft_unit_name']
        
        args = [START_SALE, nft_name, nft_unit_name]

        bytes_args = []

        for x in args:
            bytes_args.append(x.encode())

        # Loads decimals from the JSON
        decimals = pes_json['decimals']

        bytes_args.append(decimals)

        # Loads NFT Price from the JSON
        nft_price = pes_json['nft_price']

        bytes_args.append(nft_price)

        # Loads the Period from the JSON
        period = pes_json['period']

        bytes_args.append(period)

        #print("bytes_args = " + str(bytes_args))

        atc = AtomicTransactionComposer()

        signer = AccountTransactionSigner(private_key)

        sp = algod_client.suggested_params()

        #ammount = 3 * sp.min_fee + MIN_BALANCE * (pow(10, decimals) + 3) + oracle_opt_in_price 
        ammount = 3 * sp.min_fee + 3 * MIN_BALANCE

        #print(ammount)

        sp = algod_client.suggested_params()

        sp.fee = 8 * sp.min_fee

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

        created_asset_id = (algod_client.pending_transaction_info(result.tx_ids[1]))['inner-txns'][-1]['asset-index']

        '''
        for id in result.tx_ids:
            print(algod_client.pending_transaction_info(id))
        '''

        return created_asset_id

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


    
