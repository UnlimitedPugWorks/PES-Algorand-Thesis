from algosdk.v2client.algod import AlgodClient
from algosdk.transaction import ApplicationOptInTxn, wait_for_confirmation, AssetOptInTxn, PaymentTxn, AssetCloseOutTxn
import base64

class Account:

    def __init__(self, private_key, address, algod_client: AlgodClient):
        self.private_key = private_key
        self.address = address
        self.algod_client = algod_client

    def get_address(self):
        return self.address

    def get_private_key(self):
        return self.private_key

    def get_algod_client(self):
        return self.algod_client

    def account_exists(self) -> bool:
        response = self.algod_client.account_info(self.address)
        return (response['min-balance'] < response['amount'])

    def get_min_balance(self) -> int:
        response = self.algod_client.account_info(self.address)
        return response['min-balance']

    def get_balance(self) -> int:
        response = self.algod_client.account_info(self.address)
        return response['amount']

    def get_account_info(self):
        response = self.algod_client.account_info(self.address)
        return response

    def get_created_apps(self):
        response = self.algod_client.account_info(self.address)
        return response['created-apps']

    def get_assets(self):
        response = self.algod_client.account_info(self.address)

    def get_local_variables_for_app(self, app_id):
        response = self.algod_client.account_info(self.address)
        apps_local_state = response['apps-local-state']
        local_variables = dict()
        for app in apps_local_state:
            if app['id'] == app_id:
                app_variables = app['key-value']
                for variable in app_variables:
                    byte_key = base64.b64decode(variable['key'])
                    key = byte_key.decode("utf-8")
                    if(variable['value']['type'] == 2):
                        local_variables[key] = variable['value']['uint']
                    else:
                        local_variables[key] = variable['value']['bytes']
        return local_variables

    def opt_in_to_smart_contract(self, app_id: int):

        # Suggested params
        sp = self.algod_client.suggested_params()

        sp.fee = sp.min_fee

        sp.flat_fee = True

        # Creates the applicationOptInTxn
        unsigned_txn = ApplicationOptInTxn(self.address, sp, app_id)

        # Sign transaction
        signed_txn = unsigned_txn.sign(self.private_key)

        # Send transaction
        txid = self.algod_client.send_transaction(signed_txn)

        # Wait for result
        try:
            confirmed_txn = wait_for_confirmation(
                self.algod_client, txid, 4)
            print(confirmed_txn)
        except Exception as err:
            print(err)

    def opt_in_to_asset(self, asset_id: int):

        # Suggested params
        sp = self.algod_client.suggested_params()

        sp.fee = sp.min_fee

        sp.flat_fee = True

        # Creates the applicationOptInTxn
        unsigned_txn = AssetOptInTxn(self.address, sp, asset_id)

        # Sign transaction
        signed_txn = unsigned_txn.sign(self.private_key)

        # Send transaction
        txid = self.algod_client.send_transaction(signed_txn)

        # Wait for result
        try:
            confirmed_txn = wait_for_confirmation(
                self.algod_client, txid, 4)
            #print(confirmed_txn)
        except Exception as err:
            print(err)

    def close_out_to_asset(self, asset_id: int, receiver: str):

        # Suggested params
        sp = self.algod_client.suggested_params()

        sp.fee = sp.min_fee

        sp.flat_fee = True

        # Creates the applicationOptInTxn
        unsigned_txn = AssetCloseOutTxn(self.address, sp, receiver, asset_id)

        # Sign transaction
        signed_txn = unsigned_txn.sign(self.private_key)

        # Send transaction
        txid = self.algod_client.send_transaction(signed_txn)

        # Wait for result
        try:
            confirmed_txn = wait_for_confirmation(
                self.algod_client, txid, 4)
            #print(confirmed_txn)
        except Exception as err:
            print(err)

    def fund(self, receiver: str, payment_amount: int):

        # Suggested params
        sp = self.algod_client.suggested_params()

        # Creates the applicationOptInTxn
        unsigned_txn = PaymentTxn(self.address, sp, receiver, payment_amount)

        # Sign transaction
        signed_txn = unsigned_txn.sign(self.private_key)

        # Send transaction
        txid = self.algod_client.send_transaction(signed_txn)

        # Wait for result
        try:
            confirmed_txn = wait_for_confirmation(
                self.algod_client, txid, 4)
            #print(confirmed_txn)
        except Exception as err:
            print(err)


    def is_opted_in(self, app_id: int):
        response = self.algod_client.account_info(self.address)
        opted_in_apps = response['apps-local-state']
        for app in opted_in_apps:
            if app['id'] == app_id:
                return True
        return False

    def is_opted_in_to_asset(self, asset_id):
        response = self.algod_client.account_info(self.address)
        opted_in_assets = response['assets']
        for asset in opted_in_assets:
            if asset['asset-id'] == asset_id:
                return True
        return False

    def __str__(self):
        return "Address: " + str(self.address) + " Private Key: " + str(self.private_key)

