
from os import getcwd, chdir
from Classes.CommandLineApp import CommandLineApp
from Classes.PinataSDK import PinataSDK
from Classes.LandRegistry import LandRegistry
from Classes.Account import Account
from algosdk.v2client import algod

# Algod_client_constants
ALGOD_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# Pinata secrets
API_key = "701eb0b47f41e945a859"
API_secret = "caf08886c4b2dde12a3946b5ffebf94677cc941ca8b4cf414364da6570057c81"

class LandRegistryCommandLineApp(CommandLineApp):

    def __init__(self, account: Account):
        self.account = account
        self.pinataSDK = PinataSDK(API_key, API_secret)
        self.land_registry = None
        print(getcwd())
        chdir("C:\\Users\\migue\\PES V2\\Thesis-Project")

    def process_commands(self, commands: list) -> int:
        if len(commands) == 0:
            print("No command inserted")
            return 0
        command_type = commands[0]
        arguments = commands[1:]
        if (command_type == "exit"):
            print("Exiting...")
            return -1
        if (command_type == "deploy"):
            print(getcwd())
            return self.process_deploy()
        elif (command_type == "register"):
            return self.process_register(arguments)
        elif (command_type == 'transfer'):
            return self.process_transfer(arguments)
        elif (command_type == 'clawback'):
            return self.process_clawback(arguments)
        elif (command_type == 'assets'):
            return self.process_assets()
        else:
            print(command_type + " is an Invalid Command")
            return 0

    # Displays the commands supported by the console app
    def display_commands(self):
        print("This console application supports the following commands:")
        print("exit - Exits the application")
        print("deploy - Deploys the Land Registry Smart Contract.")
        print("register - Registers an Land Document NFT on the Algorand Blockchain. Has the following arguments:")
        self.display_register_arguments()
        print("transfer - Transfers a Land Document NFT to an address on the Algorand Blockchain. Has the following arguments:")
        self.display_transfer_arguments()
        print("clawback - Confiscates a Land Document NFT from an address on the Algorand Blockchain. Has the following arguments:")
        self.display_clawback_arguments()
        print("assets - Shows all assets created by the Land Registry")
        print("Enter the command")

    # Displays the arguments of the register command
    def display_register_arguments(self) -> None:
        print("1 - name - name of the Land NFT")
        print("2 - description - description of the Land NFT")
        print("3 - unit_name - unit name of the Land NFT")
        print("4 - file_path - path to the file on the metadata JSON")

    # Displays the arguments of the transfer command
    def display_transfer_arguments(self) -> None:
        print("1 - receiver_address - Address that will receive the NFT")
        print("2 - asset_id - Id of the Asset")

    # Displays the arguments of the transfer command
    def display_clawback_arguments(self) -> None:
        print("1 - sender_address - Address that will lose the NFT")
        print("2 - asset_id - Id of the Asset")

    # Processes the Land Registry Deployment
    def process_deploy(self) -> int:
        if self.land_registry == None:
            self.land_registry = LandRegistry(self.account, 0)
            print("Deployed Land Registry with App Id = " + str(self.land_registry.app_id))
        else:
            print("Land Registry has already been deployed.")
        return self.land_registry.app_id

    def process_transfer(self, arguments: list) -> int:
        if self.land_registry == None:
            print("Land Registry hasn't been deployed.")
            return 0
        else:
            if len(arguments) != 2:
                print("Invalid Arguments! The arguments supported for Transfer are:")
                self.display_transfer_arguments()
                return
            receiver_address = arguments[0]
            asset_id = int(arguments[1])
            self.land_registry.transfer_land(receiver_address, asset_id)
            return 1
    
    def process_register(self, arguments: list) -> int:
        if self.land_registry == None:
            print("Land Registry hasn't been deployed.")
            return 0
        else:
            if len(arguments) != 5:
                print("Invalid Arguments! The arguments supported for Register are:")
                self.display_register_arguments()
                return 0
            name = arguments[0]
            description = arguments[1]
            unit_name = arguments[2]
            file_name = arguments[3]
            file_path = arguments[4]
            return self.land_registry.register_land(name, description, unit_name, file_name, file_path, self.pinataSDK)

    def process_clawback(self, arguments: list) -> int:
        if self.land_registry == None:
            print("Land Registry hasn't been deployed.")
            return 0
        else:
            if len(arguments) != 2:
                print("Invalid Arguments! The arguments supported for Clawback are:")
                display_register_arguments()
                return 0
            sender_add = arguments[0]
            asset_id = int(arguments[1])
            self.land_registry.clawback_land(sender_add, asset_id)
            return 1

    def process_assets(self) -> int:
        if self.land_registry == None:
            print("Land Registry hasn't been deployed.")
            return 0
        else:
            algod_client = self.account.algod_client
            account_info = algod_client.account_info(self.land_registry.app_address)
            created_assets = (account_info)['created-assets']
            assets = (account_info)['assets']
            for asset in assets:
                print("AssetId: " + str(asset['asset-id']) + " | " + "Owned: " + has_asset(asset['amount']) + " | "  + "Frozen: " + has_asset(asset['is-frozen']))
            return 1

def has_asset(amount: int) -> str:
    return "yes" if amount != 0 else "no"

if __name__ == "__main__":
    pass
