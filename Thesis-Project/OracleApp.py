import json
from random import randint
from time import sleep
from algosdk.v2client.algod import AlgodClient
from Classes.Oracle import Oracle, timestamp_to_rfc3339, rfc3339_step
from Classes.Account import Account
from algosdk.mnemonic import to_private_key

# Algod_client_constants
ALGOD_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# Account Private Key and Public Key
PRIVATE_KEY3 = to_private_key("ill elite accident aunt laptop dice traffic grass protect coffee guide marble panic start bracket glove tornado stove breeze drip rifle viable artist above fruit")
PUBLIC_KEY3 = "WGEIHXPK7C6WV2WBMXXHMLAXTXT6EH6JWJDRAYXL7R26V6M66PK3GRQ62E"


def load_account():
    # # Creates an algod client
    algod_client = AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    account = Account(PRIVATE_KEY3, PUBLIC_KEY3, algod_client)
    return account

def test_get_last_round(account: Account):
    algod_client = account.algod_client
    status_node = algod_client.status()
    print(status_node['last-round'])

if __name__ == "__main__":
    # Loads account
    oracle_account = load_account()
    # Deploys the Oracle
    oracle = Oracle(oracle_account)
    # Shows oracle id
    print("Oracle deployed with App Id = " + str(oracle.app_id))
    # Stores the start_time
    start_time = timestamp_to_rfc3339()
    # Indicates that will sleep
    print("Will sleep for 3 seconds")
    # Sleeps for 30 seconds
    sleep(3)
    # getblock
    test_get_last_round(oracle_account)
    # Stores the end_time
    end_time = timestamp_to_rfc3339()
    while (True):
        # Indicates that time has passed
        print("Will search for requests")
        # Obtains most recent requests
        oracle.get_requests(start_time, end_time)
        # Calculates a Random Response 
        answer = randint(0, 1)
        # Verifies if there is any response to be given
        oracle.give_responses(answer)
        # Updates start_time
        start_time = end_time
        # Indicates that will sleep
        print("Will sleep for 30 seconds")
        # Sleeps for a minute
        sleep(3)
        # getblock
        test_get_last_round(oracle_account)
        # Updates end_time
        end_time = timestamp_to_rfc3339()


