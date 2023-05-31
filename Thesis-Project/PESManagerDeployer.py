from Classes.Account import Account
from Classes.PESManager import PESManager
from Classes.PESManagerCommandLine import PESManagerCommandLine
from os.path import isfile, exists, split
from algosdk.v2client.algod import AlgodClient
from algosdk.mnemonic import to_private_key

# Constants

CURRENT_PATH = "Thesis-Project/"
ALGOD_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

PRIVATE_KEY2 = to_private_key("enter broccoli lawn dilemma silly easy explain mechanic unusual skate elder ecology eyebrow canyon wood million crush dune autumn roof base stumble innocent abandon pizza")
PUBLIC_KEY2 = "VB23U533V4IS2OS5WPAVAGCLUUMABQHE3ACXKY7O4JMYCGPYICBJD4CWVY"


if __name__ == "__main__":
    # Creates an algod client
    algod_client = AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

    # Loads keys and creates account
    account = Account(PRIVATE_KEY2, PUBLIC_KEY2, algod_client)

    # Verifies if account exists
    if not account.account_exists():
        print("Account " + account.address +
              " does not exist or does not have the minimum funding to function.")
        exit(1)

    # Creates the Command Line App
    command_line_app = PESManagerCommandLine(account)
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

        
