
from os import getcwd, chdir
from Classes.CommandLineApp import CommandLineApp
from Classes.PinataSDK import PinataSDK
from Classes.PESManager import PESManager
from Classes.Account import Account
from algosdk.v2client import algod
from Classes.SmartContract import get_app_address

class PESManagerCommandLine(CommandLineApp):
    def __init__(self, account: Account):
        self.account = account
        self.pes_manager = None

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
            return self.process_deploy(arguments)
        elif (command_type == 'reputation'):
            return self.process_reputation()
        elif (command_type == 'reputation_user'):
            return self.process_reputation_user(arguments)
        else:
            print(command_type + " is an Invalid Command")
            return 0

    # Displays the commands supported by the console app
    def display_commands(self):
        print("This console application supports the following commands:")
        print("exit - Exits the application")
        print("deploy - Deploys the PES Manager Smart Contract.")
        self.display_deploy_arguments()
        print("reputation - Shows the reputation of each user on the PES Manager")
        print("reputation_user ADDRESS - Shows the reputation of a user on the PES Manager")
        self.display_reputation_user_arguments()
        print("Enter the command")  

    # Displays the arguments of the transfer command
    def display_deploy_arguments(self) -> None:
        print("1 - oracle_app_id - App Id of the Oracle Smart Contract")
        print("2 - land_registry_app_id - App Id of the Land Registry")

    # Displays the arguments of the transfer command
    def display_reputation_user_arguments(self) -> None:
        print("1 - address - The User's Address")

    def process_reputation(self) -> int:
        if self.pes_manager == None:
            print("PES Manager hasn't been deployed.")
            return 0   
        else:
            self.pes_manager.get_reputations()
            return 1

    def process_reputation_user(self, arguments) -> int:
        if self.pes_manager == None:
            print("PES Manager hasn't been deployed.")
            return 0   
        else:
            if len(arguments) != 1:
                self.display_reputation_user_arguments()
                return
            user_address = arguments[0]
            self.pes_manager.get_user_reputation(user_address)
            return 1

    def process_deploy(self, arguments):
        if self.pes_manager != None:
            print("PES Manager has been deployed.")
            return 0 
        else:
            if len(arguments) != 2:
                print("Invalid Arguments! The arguments supported for Deploy are:")
                self.display_deploy_arguments()
                return
            oracle_app_id = int(arguments[0])
            land_registry_app_id = int(arguments[1])
            self.pes_manager = PESManager(self.account, 0, oracle_app_id, get_app_address(land_registry_app_id))