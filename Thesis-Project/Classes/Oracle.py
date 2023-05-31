import base64
import pytest
import pytz
from pyrfc3339 import generate, parse
from algosdk.v2client import algod, indexer
from datetime import datetime, timedelta, timezone
from Classes.Request import Request
from Classes.PeriodicRequest import PeriodicRequest
from Classes.SingleRequest import SingleRequest
from Classes.Account import Account
from Classes.SmartContract import SmartContract, get_app_address, var_to_base64, MIN_BALANCE, get_global_variables
from algosdk.transaction import StateSchema, ApplicationNoOpTxn, ApplicationCreateTxn, PaymentTxn
from algosdk import transaction
from algosdk.encoding import encode_address, checksum, decode_address
from itertools import filterfalse


INDEXER_ADDRESS = "http://localhost:8980"
INDEXER_TOKEN = ""

CURRENT_PATH = "TEAL/"
ORACLE_PREFIX = "Oracle-"
APPROVAL_PATH = CURRENT_PATH + ORACLE_PREFIX + "approval.teal"
CLEAR_PATH = CURRENT_PATH + ORACLE_PREFIX + "clear.teal"
ANSWER_REQUEST = "Answer_Request"
RECEIVE_REQUEST = "Receive_Request"
START_SALE = "Start_Sale"

class Oracle(SmartContract):

    def __init__(self, account: Account):
        # Creates the indexer client
        self.indexer_client = indexer.IndexerClient(
            INDEXER_TOKEN, INDEXER_ADDRESS)
        # Create Request List
        self.request_list = list()
        # Creates a Response List
        self.response_list = list()
        # If the Oracle doesn't exist yet
        self.deploy_oracle_smart_contract(account)


    def get_requests(self, start_time: str, end_time: str) -> None:
        # Creates variables to deal with paginated results
        nexttoken = ""
        numtxn = 1

        # Obtains the Oracle's address
        oracle_address = self.app_address

        # Obtains the indexer client
        indexer_client = self.indexer_client

        # Since Indexer returns paginated results, a while loop is needed to get all the requests.
        # The loop is mantained until we get an empty page.
        while (numtxn > 0):
            # Obtains requests for the oracle after a certain time
            #response = indexer_client.search_transactions_by_address(
            #    address=oracle_address, start_time=start_time, next_page=nexttoken)
            response = indexer_client.search_transactions(start_time=start_time, end_time=end_time, application_id=self.app_id, next_page=nexttoken)
            # Obtains the transactions from the response
            transactions = response['transactions']
            # Obtains the number of transactions
            numtxn = len(transactions)
            # If there are stil transactions on this page, then search the next page
            if (numtxn > 0):
                # Obtains token for the next page
                nexttoken = response['next-token']
                # Converts the transactions into requests
                for transaction in transactions:
                    if 'application-transaction' in transaction:
                        # Creates a new Request from the transaction
                        application_args = transaction['application-transaction']['application-args']
                        if(len(application_args) == 0):
                            continue
                        print(transaction)
                        PES_scheme_app_id = transaction['application-transaction']['application-id']
                        asset_id = transaction['application-transaction']['foreign-assets'][0]
                        seller_address = transaction['sender']
                        appliction_call_type = application_args[0]
                        if appliction_call_type.encode() == var_to_base64(START_SALE):
                            innerTxns = transaction['inner-txns']
                            if(len(innerTxns) != 5):
                                continue
                            application_args = innerTxns[2]['application-transaction']['application-args']
                            print(application_args)
                            appliction_call_type = application_args[0]
                            if appliction_call_type.encode() == var_to_base64(RECEIVE_REQUEST):
                                global_vars = get_global_variables(app_id, self.account.algod_client)
                                request = None
                                if "Number_of_Payments" not in global_vars.keys():
                                    request = SingleRequest(transaction['id'], self.account.algod_client, PES_scheme_app_id, asset_id, seller_address)
                                else:
                                    request = PeriodicRequest(transaction['id'], self.account.algod_client, PES_scheme_app_id, asset_id, seller_address)
                                # Adds the request to the request list if it's there
                                if request not in self.request_list:
                                    print("Received the request: " + str(request))
                                    self.request_list.append(request)

    # Verifies if the time to respond has come
    def give_responses(self, answer: int) -> None:
        # Calculates the current time
        current_time = datetime.now()
        # For each request, verify if it can be responded to
        for request in self.request_list:
            if request.ready_to_respond(current_time):
                self.respond_to_request(request, answer)
                self.response_list.append(request)
        # Removes the already responded requests
        self.request_list = list(filter(lambda x: x.ready_to_delete(current_time) == False, self.request_list))

    def respond_to_request(self, request: Request, answer:int) -> None:

        #print(request)
        # Takes the variables from oracle account
        address = self.account.get_address()
        private_key = self.account.get_private_key()
        algod_client = self.account.get_algod_client()

        node_status = algod_client.status()
        
        print(node_status)

        # Takes the variables from the requests
        # The applications array
        oracle_app_id = self.app_id
        nft_manager_app_id = request.nft_manager_app_id
        nft_seller_app_id = request.sender_app_id
        applications = [nft_manager_app_id, nft_seller_app_id]

        print("Applications = " + str(applications))

        # To accounts
        seller_address = request.seller_address
        nft_seller = request.sender_app_address
        accounts = [seller_address, nft_seller]
        #accounts = [seller_address]
        print("Accounts = " + str(accounts))

        # To assets
        land_registry_nft = request.asset_id
        assets = [land_registry_nft]

        print("Assets = " + str(assets))

        # To boxes
        boxes = [[nft_manager_app_id, decode_address(seller_address)]]
        #boxes = [[nft_manager_app_id, nft_seller]]
        print("Boxes = " + str(boxes))

        # Args
        args=[ANSWER_REQUEST.encode(), answer]

        # Suggested params
        sp = algod_client.suggested_params()

        sp.fee = 5 * sp.min_fee
        sp.flat_fee = True

        # Creates the applicationNoOpTxn
        unsigned_txn = ApplicationNoOpTxn(address, sp, self.app_id, app_args=args, foreign_assets=assets, accounts=accounts, foreign_apps=applications, boxes=boxes)

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

    

    def deploy_oracle_smart_contract(self, account: Account):
        # Takes the variables from oracle account
        address = account.get_address()
        private_key = account.get_private_key()
        algod_client = account.get_algod_client()

        # build transaction
        params = algod_client.suggested_params()

        # comment out the next two (2) lines to use suggested fees
        #params.flat_fee = constants.MIN_TXN_FEE
        #params.fee = 1000

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
        local_schema = StateSchema(2, 0)

        # Create unsigned transaction that will create App
        unsigned_txn = ApplicationCreateTxn(
            address, params, 0, approval_bytes, clear_bytes, global_schema, local_schema)

        # Sign transaction
        signed_txn = unsigned_txn.sign(private_key)

        # Send transaction
        txid = algod_client.send_transaction(signed_txn)

        # Wait for result
        try:
            confirmed_txn = transaction.wait_for_confirmation(
                algod_client, txid, 4)
            self.app_id = confirmed_txn["application-index"]
            created_app_id = confirmed_txn["application-index"]
            super().__init__(account, created_app_id)
        except Exception as err:
            print(err)
            super().__init__(account, 0)

        unsigned_txn = PaymentTxn(address, params, get_app_address(self.app_id) , MIN_BALANCE)
        # Sign transaction
        signed_txn = unsigned_txn.sign(private_key)

        # Send transaction
        txid = algod_client.send_transaction(signed_txn)

        # Wait for result
        try:
            confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
        except Exception as err:
            print(err)

def timestamp_to_rfc3339():
    return generate(datetime.now(timezone.utc).replace(tzinfo=pytz.utc))

def rfc3339_step():
    return generate((datetime.now(timezone.utc) + timedelta(minutes=1)).replace(tzinfo=pytz.utc))