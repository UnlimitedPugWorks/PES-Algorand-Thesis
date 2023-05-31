from Classes.Account import Account
from Classes.PinataSDK import PinataSDK
from os.path import isfile, exists, split
from algosdk.v2client.algod import AlgodClient
from algosdk.mnemonic import to_private_key
from algosdk.account import address_from_private_key
from Classes.UserCommandLineApp import UserCommandLineApp

# Constants

KEYS_PATH = "Thesis-Project/keys/"
ALGOD_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# Loads the cryptographic keys for the Algorand Account

'''
def load_cryptographic_keys(file: str):
    keys = open(KEYS_PATH + file, "r")
    address = keys.readline()
    private_key = keys.readline()
    keys.close()
    return private_key[:-1], address[:-1]
'''

PRIVATE_KEY4 = to_private_key("genuine burger urge heart spot science vague guess timber rich olympic cheese found please then snack nice arrest coin seminar pyramid adult flip absorb apology")
PUBLIC_KEY4 = "7LQ7U4SEYEVQ7P4KJVCHPJA5NSIFJTGIEXJ4V6MFS4SL5FMDW6MYHL2JXM"

if __name__ == "__main__":

    # Creates an algod client
    algod_client = AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

    # Loads keys and creates account
    #print("Enter file where the keys are present")
    #file = input()
    account = Account(PRIVATE_KEY4, PUBLIC_KEY4, algod_client)

    # Verifies if account exists
    if not account.account_exists():
        print("Account " + account.address +
              " does not exist or does not have the minimum funding to function.")
        exit(1)

    usercommandline = UserCommandLineApp(account, pinata)    

    command_line_return = 0
    while command_line_return != -1:
        usercommandline.display_commands()
        # Obtains the input
        line = input()
        # Splits the line into commands
        commands = line.split()
        command_line_return = usercommandline.process_commands(commands)