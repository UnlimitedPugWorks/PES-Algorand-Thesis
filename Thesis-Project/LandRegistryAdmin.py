from Classes.Account import Account
from Classes.PinataSDK import PinataSDK
from Classes.LandRegistry import LandRegistry
from Classes.LandRegistryCommandLineApp import LandRegistryCommandLineApp
from os.path import isfile, exists, split
from algosdk.v2client.algod import AlgodClient
from algosdk.mnemonic import to_private_key

# Constants

CURRENT_PATH = "Thesis-Project/"
ALGOD_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

def verifies_asset(land_registry: LandRegistry, asset_id: int, algod_client: AlgodClient):
    response = algod_client.account_info(
        land_registry.app_address)
    assets_list = response["assets"]
    return asset_id in assets_list


def verifies_minimal_balance(receiver_address: str, land_registry: LandRegistry, algod_client: AlgodClient):
    response = algod_client.account_info(receiver_address)
    return response['min-balance'] + 1000 < response['amount']

# Loads the cryptographic keys for the Algorand Account


def load_cryptographic_keys(file: str):
    #keys = open(file, "r")
    keys = open(CURRENT_PATH + file, "r")
    address = keys.readline()
    private_key = keys.readline()
    keys.close()
    return to_private_key(private_key[:-1]), address[:-1]

# Loads the API key and Secret for Pinata


def load_pinata_api_keys(file: str):
    #keys = open(file, "r")
    keys = open(CURRENT_PATH + file, "r")
    API_key = keys.readline()
    API_secret = keys.readline()
    keys.close()
    return API_key[:-1], API_secret[:-1]


if __name__ == "__main__":
    # Creates an algod client
    algod_client = AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

    # Loads keys and creates account
    private_key, address = load_cryptographic_keys("keys.txt")
    account = Account(private_key, address, algod_client)

    # Verifies if account exists
    if not account.account_exists():
        print("Account " + account.address +
              " does not exist or does not have the minimum funding to function.")
        exit(1)

    # Creates the Command Line App
    command_line_app = LandRegistryCommandLineApp(account)
    # While the exit flag hasn't been raised
    while True:
        # Displays the available commands
        command_line_app.display_commands()
        # Obtains the input
        line = input()
        # Splits the line into commands
        commands = line.split()
        # Processes the command
        command_return = command_line_app.process_commands(commands)
        # Verifies if exited
        if command_return == -1:
            # Exits
            break

        
