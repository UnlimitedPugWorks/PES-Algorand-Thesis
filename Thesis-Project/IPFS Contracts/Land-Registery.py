from pyteal import *
from pyteal import compileTeal
from pyteal_helpers import program


# The trusted third party will have a multisignature account to give it an extra layer of security.

TEAL_PATH = "Thesis-Project/TEAL/"


def approval():


    # GLOBAL - App Create
    #Minimum-Balance = 100000 = MIN_BALANCE

    # Local - App OptIn
    #Minimum-Balance = 100000 = MIN_BALANCE

    # GLOBAL

    # LOCAL

    # OPERATIONS

    # Registers land in the smart contract
    op_register_land = Bytes("Register_Land")

    # Transfers the registered land to a user(presumably the owner of the land)
    op_transfer_registered_land = Bytes("Transfer_Registered_Land")

    # Since human mistakes can happen, the 3rd party might need to clawback those land NFT.
    op_land_clawback = Bytes("Land_Clawback")

    # CONSTANTS

    # The min_balance is the minimum balance required to own an asset.
    # It is equal to 100000 microalgos, which corresponds to 0.1 Algo, which corresponds to approximately 0.03 euros
    min_balance = Int(100000)

    # SUBROUTINES
    asset_name_len = ScratchVar(TealType.uint64)

    @Subroutine(TealType.none)
    def checkNFTBalance(account, assetId):
        bal = AssetHolding.balance(account, assetId)
        return Seq(
            bal,
            Assert(bal.hasValue()),
            Assert(bal.value() == Int(1)),
        )

    @Subroutine(TealType.none)
    def checkAssetOptIn(account, assetId):
        bal = AssetHolding.balance(account, assetId)
        return Seq(
            bal,
            Assert(bal.hasValue()),
            Assert(bal.value() >= Int(0)),
        )


    @Subroutine(TealType.none)
    def checkNFTCreator(account, assetId):

        param = AssetParam().creator(assetId)

        return Seq(
            param,
            Assert(param.hasValue()),
            Assert(param.value() == account),
        )

    @Subroutine(TealType.none)
    def defaultTransactionChecks(txnId):
        return Seq([
            Assert(txnId < Global.group_size()),
            Assert(Gtxn[txnId].rekey_to() == Global.zero_address()),
            Assert(Gtxn[txnId].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[txnId].asset_close_to() == Global.zero_address())
        ])

    # In this function, the application_args
    # Txn.application_args[1] = URL of the Asset
    # Txn.application_args[2] = Hash of the metadata
    # Txn.application_args[3] = Name of the Asset
    # Txn.application_args[4] = Unit Name of the Asset
    # This function also receives a group of transactions where:
    # 0 - Payment Transaction which funds the Land-Registery so that it has the minimal balance to hold the NFT
    # 1 - Application Call
    register_land = Seq(
        # Verifies if the size of the transaction group is 2
        Assert(Global.group_size() == Int(2)),
        # Verifies if the number of arguments in the args is equal to intended 5
        Assert(Txn.application_args.length() == Int(5)),
        # Saves the length of the Asset's name
        # asset_name_len.store(Len(Txn.application_args[3])),
        # Assert(
        #    And(
        #        # Verifies if the sender of the transaction is the creator of the App
        #        Txn.sender() == Global.creator_address(),
        #        # Verifies if the length of the asset's name is larger than 4
        #        asset_name_len.load() > Int(4),
        #        # Verifies if the asset name ends with @arc3
        #        Substring(Txn.application_args[3], asset_name_len.load(
        #        ) - Int(5), asset_name_len.load() - Int(1)) == Bytes("@arc3"),
        #    )
        # ),
        InnerTxnBuilder.Begin(),
        # Builds the transaction
        InnerTxnBuilder.SetFields(
            {
                # We will config(create) an Asset
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_name: Txn.application_args[3],
                TxnField.config_asset_unit_name: Txn.application_args[4],
                TxnField.config_asset_url: Txn.application_args[1],
                TxnField.config_asset_metadata_hash: Txn.application_args[2],
                TxnField.config_asset_decimals: Int(0),
                TxnField.config_asset_total: Int(1),
                TxnField.config_asset_manager: Global.current_application_address(),
                TxnField.config_asset_freeze: Global.current_application_address(),
                TxnField.config_asset_clawback: Global.current_application_address(),
                TxnField.fee: Int(0),
            }
        ),
        # Sends the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    transfer_registered_land = Seq(
        # In this function, the application_args
        # Txn.account[1] = Receiver of the NFT
        # Txn.assets[0] = Id of the Asset
        # Verifies if the size of the transaction group is 1
        Assert(Global.group_size() == Int(1)),
        # Verifies if the number of arguments in the args is equal to intended (1)
        Assert(Txn.application_args.length() == Int(1)),
        # Verifies if the number of accounts in the accounts is equal to intended (1)
        Assert(Txn.accounts.length() == Int(1)),
        # Verifies if the number of arguments in the assets is equal to intended (1)
        Assert(Txn.assets.length() == Int(1)),
        # Verifies if the sender of the transaction is the creator of the App
        Assert(Txn.sender() == Global.creator_address()),
        # Verifies if the person the NFT is going to be sent to is opted in to the asset
        # Assert(App.optedIn(Txn.accounts[1], Global.current_application_id())),
        checkAssetOptIn(Txn.accounts[1], Txn.assets[0]),
        # Checks if the Smart Contract has the NFT that is going to be transfered, otherwise it should fail
        checkNFTBalance(Global.current_application_address(), Txn.assets[0]),
        # Builds the transaction
        InnerTxnBuilder.Begin(),
        # Builds an AssetTransfer
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_receiver: Txn.accounts[1],
                TxnField.asset_amount: Int(1),
                TxnField.xfer_asset: Txn.assets[0],
                TxnField.fee: Int(0),
            }
        ),
        # Submits the transaction
        InnerTxnBuilder.Submit(),
        # Approves
        Approve(),
    )

    land_clawback = Seq(
        # In this function, the application_args
        # Txn.accounts[1] = Receiver of the NFT
        # Txn.assets[0] = Id of the Asset
        # Verifies if the size of the transaction group is 1
        Assert(Global.group_size() == Int(1)),
        # Verifies if the number of accounts in the accounts is equal to intended (1)
        Assert(Txn.accounts.length() == Int(1)),
        # Verifies if the number of arguments in the assets is equal to intended (1)
        Assert(Txn.assets.length() == Int(1)),
        # Verifies if the sender of the transaction is the creator of the App
        Assert(Txn.sender() == Global.creator_address()),
        # Checks if the Smart Contract has the NFT that is going to be transfered, otherwise it should fail
        checkNFTBalance(Txn.accounts[1], Txn.assets[0]),
        # Builds the transaction
        InnerTxnBuilder.Begin(),
        # Clawbacks
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_receiver: Global.current_application_address(),
                TxnField.asset_sender: Txn.accounts[1],
                TxnField.asset_amount: Int(1),
                TxnField.xfer_asset: Txn.assets[0],
                TxnField.fee: Int(0),
            }
        ),
        # Submits the transaction
        InnerTxnBuilder.Submit(),
        Approve(),
    )

    return program.event(
        # Only approves when the application is created
        init=Approve(),
        # Router for the different ops
        no_op=Cond(
            [Txn.application_args[0] == op_register_land, register_land],
            [Txn.application_args[0] == op_transfer_registered_land,
                transfer_registered_land],
            [Txn.application_args[0] == op_land_clawback, land_clawback],
        ),
        # Opting in results in an approve. Opting in is only used for the user to be able to own the land.
        opt_in=Approve(),
    )


def clear():
    return Approve()


def approval_program():
    program = approval()
    # Mode.Application specifies that this is a smart contract
    return compileTeal(program, Mode.Application, version=8)


def clear_state_program():
    program = clear()
    # Mode.Application specifies that this is a smart contract
    return compileTeal(program, Mode.Application, version=8)


if __name__ == "__main__":
    approval_file = open(TEAL_PATH + 'Land-Registery-approval.teal', 'w')
    approval_file.write(approval_program())
    approval_file.close()

    clear_file = open(TEAL_PATH + 'Land-Registery-clear.teal', 'w')
    clear_file.write(clear_state_program())
    clear_file.close()
    
    print("success")
