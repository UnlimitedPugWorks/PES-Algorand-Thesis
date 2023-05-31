from Classes.SmartContract import SmartContract, get_app_address
from Classes.LandRegistryUser import LandRegistryUser
from Classes.PESScheme import PESScheme
from Classes.PESSchemeAsset import PESSchemeAsset
from Classes.PESSchemeNoAsset import PESSchemeNoAsset
from Classes.PESSchemeUser import PESSchemeUser
from Classes.PESSchemeAssetUser import PESSchemeAssetUser
from Classes.PESSchemeNoAssetUser import PESSchemeNoAssetUser
from Classes.PESManager import PESManager
from Classes.PESManagerUser import PESManagerUser
from Classes.Account import Account
from Classes.PinataSDK import PinataSDK
from Classes.CommandLineApp import CommandLineApp

class UserCommandLineApp(CommandLineApp):
    def __init__(self, account: Account, pinata: PinataSDK):
        self.account = account
        self.pes_manager_user = None
        self.land_registry_user = None
        self.pes_schemes = dict()
        self.pes_scheme_users = dict()


#==========================DISPLAY==========================================
    def display_commands(self):
        commands = "Choose a Smart Contract:\n"
        commands += "PES_manager - To interact with the PES Manager\n"
        commands += "land_registry  - To interact with the Land Registry\n"
        commands += "PES_scheme  - To interact with the PES Scheme\n"
        commands += "PES_scheme_user  - To interact with the PES Scheme User\n"
        commands += "exit  - To exit"
        print(commands)

    def display_LandRegistry_arguments(self):
        commands = "Choose an  operation:\n"
        commands += "AssetOptIn id  - Opts in to Land Registry Asset\n"
        commands += "AssetClose id  - Close out from Land Registry Asset\n"
        commands += "Assets - Shows Land Registry Assets\n"
        commands += "connect id - Connects to the PES Scheme"
        commands += "back  - To go back"
        print(commands)

    def display_PESManager_arguments(self):
        commands = "Choose an  operation:\n"
        commands += "CreatePESscheme - Creates an PES Scheme\n"
        commands += "CreateBox  - To create a box\n"
        commands += "DeletePESscheme id  - Deletes an PES Scheme\n"
        commands += "Connect id - Connects to the PES Scheme\n"
        commands += "SeePESschemes - Gets a list of existing PES Schemes"
        commands += "back  - To go back"
        print(commands)

    def display_PESScheme_arguments(self):
        commands = "Choose a operation:\n"
        commands += "start_sale name unit_name id - Starts the PES Scheme\n"
        commands += "give refund address - Gives a refund to an address\n"
        commands += "esbuyers - Lists all of the PES Scheme's ES Buyers\n"
        commands += "back - To go back"
        print(commands)

    def display_PESSchemeUser_arguments(self):
        commands = "Choose a operation:\n"
        commands += "make_payment quantity - Makes a payment to the PES Scheme\n"
        commands += "get_refund - Get a refund from the PES Scheme and/or deletes Box\n"
        commands += "CreateBox - Creates a box in the PES Scheme\n"
        commands += "back - To go back"
        print(commands)

#==========================COMMANDS=========================================

    def process_commands(self, commands: list) -> int:
        if len(commands) == 0:
            print("No command inserted")
            return 0
        command_type = commands[0]
        if (command_type == "exit"):
            print("Exiting...")
            return -1
        if (command_type == "PESmanger"):
            return self.enter_PESManager()
        elif (command_type == "landregistry"):
            return self.enter_LandRegistry()
        elif (command_type == "PESScheme"):
            return self.choose_PESScheme()
        elif (command_type == "PESSchemeUser"):
            return self.choose_PESSchemeUser()
        else:
            print(command_type + " is an Invalid Command")
            return 0


#===========================PES MANAGER USER=========================================== 

    def enter_PESManager(self) -> int:
        while True:
            self.display_PESManager_arguments()
            # Obtains the input
            line = input()
            # Splits the line into commands
            commands = line.split()
            command_return = self.process_PESManager(commands)
            if command_return == -1:
                break
        return 0

    def process_PESManager(self, commands: list):
        if len(commands) == 0:
            print("No command inserted")
            return 0
        command_type = commands[0]
        arguments = commands[1:]
        if (command_type == "back" and len(commands) == 1):
            return -1
        elif (command_type == "CreatePESscheme"):
            return self.process_CreatePESscheme(arguments)
        elif (command_type == "CreateBox"):
            return self.process_create_box(arguments)
        elif (command_type == "DeletePESscheme"):
            return self.process_DeletePESscheme(arguments)      
        elif (command_type == "connect"):
            return self.process_connect_pes_manager(arguments)  
        else:
            print(command_type + " is an Invalid Command")
            return 0

    def process_CreatePESscheme(self, arguments: list):
        if self.pes_manager_user == None:
            print("PES Scheme User hasn't been deployed.")
            return 0
        else:
            if len(arguments) != 1:
                return 0
            type = int(arguments[0])
            pes_scheme = self.pes_manager_user.create_PES_scheme(type)
            self.pes_schemes.update({pes_scheme.app_id: pes_scheme})
            return pes_scheme.app_id

    def process_create_box(self, arguments: list) -> int:
        if self.pes_manager_user == None:
            print("PES Manager hasn't been deployed.")
            return 0
        else:
            if len(arguments) != 0:
                return 0
            self.pes_manager_user.create_box_PESManager()
            return 1

    def process_DeletePESscheme(self, arguments: list) -> int:
        if self.pes_manager_user == None:
            print("PES Scheme User hasn't been deployed.")
            return 0
        else:
            if len(arguments) != 1:
                return 0
            pes_scheme_app_id = int(arguments[0])
            self.pes_manager_user.delete_PES_Scheme(pes_scheme_app_id)
            return 1  

    def process_SeePESschemes(self, arguments: list) -> int:
        if self.pes_manager_user == None:
            print("PES Scheme User hasn't been deployed.")
            return 0
        else:
            if len(arguments) != 0:
                return 0
            self.pes_manager_user.show_created_pes_Sellers()
            return 1      

    def process_connect_pes_manager(self, arguments: list) -> int:
        if self.pes_manager_user != None:
            print("PES Scheme User has been connected.")
            return 0
        else:
            if len(arguments) != 1:
                return 0
            pes_manager_app_id = int(arguments[0])
            self.pes_manager_user = PESManagerUser(self.account, pes_manager_app_id)
            return 1           

#===========================LAND REGISTRY USER==================================== 

    def process_LandRegistry(self, commands: list):
        if len(commands) == 0:
            print("No command inserted")
            return 0
        command_type = commands[0]
        arguments = commands[1:]
        if (command_type == "back" and len(commands) == 1):
            return -1
        elif (command_type == "connect"):
            return self.process_connect_land_registry(arguments)         
        elif (command_type == "AssetOptIn"):
            return self.process_opt_to_land(arguments) 
        elif (command_type == "AssetClose"):
            return self.process_close_to_land(arguments)
        elif (command_type == "Assets"):
            return self.process_assets(arguments)         
        else:
            print(command_type + " is an Invalid Command")
            return 0

    def process_connect_land_registry(self, arguments: list) -> int:
        if self.land_registry_user != None:
            print("Land Manager User has been connected.")
            return 0
        else:
            if len(arguments) != 1:
                return 0
            land_registry_app_id = int(arguments[0])
            self.land_registry_user = LandRegistryUser(self.account, land_registry_app_id)
            return 1   

    def process_opt_to_land(self, arguments: list) -> int:
        if self.land_registry_user == None:
            print("Land Manager User hasn't been connected.")
            return 0
        else:
            if len(arguments) != 1:
                return 0
            land_deed_app_id = int(arguments[0])
            self.account.opt_in_to_asset(land_deed_app_id)
            return 1       

    def process_close_to_land(self, arguments: list) -> int:
        if self.land_registry_user == None:
            print("Land Manager User hasn't been connected.")
            return 0
        else:
            if len(arguments) != 1:
                return 0
            land_deed_app_id = int(arguments[0])
            self.account.close_out_to_asset(land_deed_app_id, self.land_registry_user.app_id)
            return 1      

    def process_assets(self, arguments: list) -> int:
        if self.land_registry_user == None:
            print("Land Manager User hasn't been connected.")
            return 0
        else:
            if len(arguments) != 0:
                return 0
            land_deed_app_id = int(arguments[0])
            self.account.opt_in_to_asset(land_deed_app_id)
            return 1          

#===========================PES SCHEME=========================================== 
    def choose_PESScheme(self) -> int:
        while True:
            print("Choose an PES Scheme or choose back to return to previous menu")
            # Obtains the input
            line = input()
            # Splits the line into commands
            commands = line.split()
            if len(commands) == 1:
                if commands[0] == "back":
                    break 
                else:
                    id = int(commands[0])
                    if id not in self.pes_schemes.keys():
                        print("No PES Scheme found with id=" + id)
                    else:
                        pes_scheme = self.pes_schemes[id]
                        command_return = self.enter_PESScheme()
            else:
                print("Invalid number of arguments") 
        return 0

    def enter_PESScheme(self, pes_scheme: PESScheme) -> int:
        while True:
            pes_scheme.pes_scheme_info()
            self.dispaly_PESScheme_arguments()
            # Obtains the input
            line = input()
            # Splits the line into commands
            commands = line.split()
            command_return = self.process_PESScheme(commands, pes_scheme)
            if command_return == -1:
                break
        return 0

    def process_PESScheme(self, commands: list, pes_scheme: PESScheme) -> int:     
        if len(commands) == 0:
            print("No command inserted")
            return 0
        command_type = commands[0]
        arguments = commands[1:]
        if (command_type == "back" and len(commands) == 1):
            return -1
        elif (command_type == "start_sale"):
            return self.process_start_salePESScheme(arguments, pes_scheme)
        elif (command_type == "give_refund"):
            return self.process_give_refundPESScheme(arguments, pes_scheme)
        elif (command_type == "esbuyers"):
            return self.process_esbuyers(arguments, pes_scheme)        
        else:
            print(command_type + " is an Invalid Command")
            return 0

    def process_start_salePESScheme(self, arguments: list, pes_scheme: PESScheme) -> int:
        print(pes_scheme)
        if pes_scheme == None or pes_scheme.app_id not in self.pes_schemes.keys():
            print("PES Scheme doesn't exist.")
            return 0
        else:
            print(arguments)
            if len(arguments) != 2:
                print("Insufficient arguments")
                return 0
            asset_id = int(arguments[0])
            file_path = arguments[1]
            created_asset_id = pes_scheme.start_sale(asset_id, file_path)
            print(created_asset_id)
            return created_asset_id

    def process_give_refundPESScheme(self, arguments: list, pes_scheme: PESScheme) -> int:
        if pes_scheme == None:
            print("PES Scheme doesn't exist.")
            return 0
        else:
            if len(arguments) != 1:
                return 0
            refund_address = arguments[0]
            pes_scheme.give_refund(refund_address)
            return 1  

    def process_esbuyers(self, arguments: list, pes_scheme: PESScheme) -> int:
        if pes_scheme == None:
            print("PES Scheme doesn't exist.")
            return 0
        else:
            if len(arguments) != 0:
                return 0
            refund_address = arguments[0]
            pes_scheme.get_es_buyers()
            return 1  
  
#===========================PES Scheme User=========================================== 
    def choose_PESSchemeUser(self) -> int:
        while True:
            print("Choose an PES Scheme User or choose back to return to previous menu")
            # Obtains the input
            line = input()
            # Splits the line into commands
            commands = line.split()
            if len(commands) == 1:
                if commands[0] == "back":
                    break 
                else:
                    id = int(commands[0])
                    if id not in self.pes_scheme_users.keys():
                        print("No PES Scheme User found with id=" + id)
                    else:
                        pes_scheme_user = self.pes_scheme_users[id]
                        command_return = self.enter_PESSchemeUser()
            else:
                print("Invalid number of arguments") 
        return 0

    def enter_PESSchemeUser(self, pes_scheme_user: PESSchemeUser) -> int:
        while True:
            pes_scheme_user.pes_scheme_info()
            self.dispaly_PESSchemeUser_arguments()
            # Obtains the input
            line = input()
            # Splits the line into commands
            commands = line.split()
            command_return = self.process_PESSchemeUser(commands[1:], pes_scheme_user)
            if command_return == -1:
                break
        return 0

    def process_PESSchemeUser(self, commands: list, pes_scheme_user: PESSchemeUser) -> int:     
        if len(commands) == 0:
            print("No command inserted")
            return 0
        command_type = commands[0]
        arguments = commands[1:]
        if (command_type == "back" and len(commands) == 1):
            return -1
        elif (command_type == "make_payment"):
            return self.process_buy_pes(arguments, pes_scheme_user)
        elif (command_type == "get_refund"):
            return self.process_get_refund(arguments, pes_scheme_user)
        elif (command_type == "create_box"):
            return self.process_create_boxPESSchemeUser(arguments, pes_scheme_user)
        else:
            print(command_type + " is an Invalid Command")
            return 0

    def process_buy_pes(self, arguments: list, pes_scheme_user: PESSchemeUser) -> int:
        if pes_scheme_user == None:
            print("PES Scheme User doesn't exist.")
            return 0
        else:
            if len(arguments) != 1:
                return 0
            quantity = int(arguments[0])
            pes_scheme_user.buy_NFT(quantity)
            return 1          

    def process_get_refund(self, arguments: list, pes_scheme_user: PESSchemeUser) -> int:
        if pes_scheme_user == None:
            print("PES Scheme User doesn't exist.")
            return 0
        else:
            if len(arguments) != 0:
                return 0
            pes_scheme_user.get_refund()
            return 1   

    def process_create_boxPESSchemeUser(self, arguments: list, pes_scheme_user: PESSchemeUser) -> int:
        if pes_scheme_user == None:
            print("PES Scheme User doesn't exist.")
            return 0
        else:
            if len(arguments) != 0:
                return 0
            pes_scheme_user.create_box()
            return 1   

    def __str__(self):
        account_str = "Account: " + str(self.account) + "\n"
        user_pes_manager = "pes_MANAGER_USER: " + " Id: "+ str(self.pes_manager_user.app_id) +  " Account: " + str(self.pes_manager_user.account) + "\n"
        pes_schemes = ""
        for pes_scheme in self.pes_schemes.keys():
            pes_schemes += "pes_scheme: " +  str(pes_scheme) + " Account: " + str(self.pes_schemes[pes_scheme].account) +"\n"
        return (account_str + user_pes_manager + pes_schemes)
        