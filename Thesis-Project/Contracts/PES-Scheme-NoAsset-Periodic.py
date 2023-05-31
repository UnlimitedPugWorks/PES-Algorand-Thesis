from pyteal import *
from pyteal_helpers import program
from base64 import b64decode
from algosdk.v2client.algod import AlgodClient 

TEAL_PATH = "Thesis-Project/TEAL/"

ALGOD_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def approval():

    # Has a box containing the number of successes in preservation.
    # This box contains 1 or 2 Bytes, with a bit for each preservation succession, having from 1 to 12 bits
    # The periodicy for payments has to be a divisor of 12, throug Mod(12, Periodcy) == 0

    # GLOBAL - App Create
    #Minimum-Balance = 100000 + (28500) * 9 + (50000) * 3 = 485000 = 4,85 * MIN_BALANCE

    # Local - App OptIn
    #Minimum-Balance = 100000 + (28500) * 0 + (50000) * 0 = 100000 =  MIN_BALANCE

    # Global Int 
    global_success = Bytes("Success")

    # Global Int
    global_money = Bytes("Funds")

    # Global Int
    global_oracle_app_id = Bytes("Oracle_Id")

    # Global Int
    global_number_of_payments = Bytes("Number_of_Payments")

    # Global Int
    global_asset_id = Bytes("Asset_Id")

    # Global Byte
    global_ES_provider_address = Bytes("Seller_Address")

    # Global Byte
    global_land_registry_address = Bytes("Land_Registry_Address")

    # Global Int
    global_PES_goal = Bytes("NFT_Price")

    # Global Int
    global_start_timestamp = Bytes("Start_Timestamp")

    # Global Int
    global_pes_manager_id = Bytes("NFT_Manager_Id")

    # Global Int
    global_state = Bytes("State")

    # Global Int
    global_number_of_boxes = Bytes("Number_of_Offers")

    # LOCAL

    # CONSTANTS
    # The state constants:
    SaleNotStarted = Int(0)
    FinalState = App.globalGet(global_number_of_payments) + Int(1)
    
    responseState = App.globalGet(global_state)

    secondsYear = Int(31536000)

    # Represents the local reputation of each smart contract user.

    # OPERATIONS

    # The operation responsible for starting the sale
    op_start_sale = Bytes("Start_Sale")

    # The operation responsible for buying the NFTs
    op_make_payment = Bytes("Buy_NFT")

    # The operation responsible for receiving a positive response from the oracle
    op_receive_positive_response = Bytes("receive_positive_response")

    # The operation responsible for receiving a positive response from the oracle
    op_receive_negative_response = Bytes("receive_negative_response")

    # The operation responsible for getting a refund
    op_get_refund = Bytes("Get_Refund")

    # The operation responsible for giving a refund
    op_give_refund = Bytes("Give_Refund")

    # The operation responsible for creating boxes
    op_create_box = Bytes("Create_Box")

    # SUBROUTINES
    @Subroutine(TealType.none)
    def defaultTransactionChecks(txnId):
        return Seq([
            Assert(txnId < Global.group_size()),
            Assert(Gtxn[txnId].rekey_to() == Global.zero_address()),
            Assert(Gtxn[txnId].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[txnId].asset_close_to() == Global.zero_address())
        ])

    @Subroutine(TealType.bytes)
    def app_id_to_address(appId):
        return Seq(Sha512_256(Concat(Bytes("appID"), Itob(appId))))

    # Verifies if WaitingForResponse
    @Subroutine(TealType.none)
    def isWaitingForResponse():
        return Seq(
            Assert(App.globalGet(global_state) >= Int(1)),
            Assert(App.globalGet(global_state) <= App.globalGet(global_number_of_payments)),
        )
 
    @Subroutine(TealType.none)
    def isLandRegistryToken(asset):
        assetCreator = AssetParam.creator(asset)
        return Seq(
            assetCreator,
            Assert(assetCreator.hasValue()),
            Assert(assetCreator.value() == App.globalGet(global_land_registry_address)),
        )


    @Subroutine(TealType.uint64)
    def box_minimum_balance(box_name, box_size):
        return Add(Int(2500), Mul(Int(400), Add(box_size, Len(box_name))))


    @Subroutine(TealType.uint64)
    def get_refunds(box_name):
        return Btoi(App.box_extract(box_name, Int(0), Int(8)))

    @Subroutine(TealType.uint64)
    def get_ts(box_name):
        return Btoi(App.box_extract(box_name, Int(8), Int(1)))   

    @Subroutine(TealType.none)
    def set_refunds(box_name, refund):
        return Seq(
            App.box_replace(box_name, Int(0), refund)
        )

    @Subroutine(TealType.none)
    def set_ts(box_name, ts):
        return Seq(
            App.box_replace(box_name, Int(8), ts)
        )


    
    # CALLS

    # nft_seller_init receives the following accounts:
    # 1. Seller_Address - Address of the Seller
    # 2. Land_Registry_Address - Address of the Land_Registry
    # nft_seller_init recieves the following apps:
    # 1. Oracle App Id - The App Id of the Oracle
    # nft_seller_init recieves the following arguments:
    # 0. Description
    nft_seller_init = Seq(
        # Security Checks
        defaultTransactionChecks(Int(0)),
        # Verifies the length of the accounts
        Assert(Txn.accounts.length() == Int(2)),
        # Verifies the length of the apps
        Assert(Txn.applications.length() == Int(1)),
        # Stores the Oracle ID
        App.globalPut(global_oracle_app_id, Txn.applications[1]),
        # Stores the Seller Address
        App.globalPut(global_ES_provider_address, Txn.accounts[1]),
        # Stores the Land Registry Address
        App.globalPut(global_land_registry_address, Txn.accounts[2]),
        # Stores the state of the seller 
        App.globalPut(global_state, SaleNotStarted),
        # Stores the NFT Manager Id
        App.globalPut(global_pes_manager_id , Global.caller_app_id()),
        # Initializes the number of offers
        App.globalPut(global_number_of_boxes, Int(0)),
        # Stores global money
        App.globalPut(global_money, Int(0)),
        # Stores success 
        App.globalPut(global_success, Itob(Int(0))),
        # Approves  
        Approve(),
    )
    


    # The start_sale function receives a group of three transactions
    # 1. A Payment Transactions to fund the smart contract
    # 2. An Application Call Transaction
    # 3. A Asset Transfer Transactions that sends the NFT
    # The start_sale function receives the foloowing arguments:
    # 0. Start_Sale
    # 1. PES_GOAL
    # 2. Number of Payments

    start_sale = Seq(
        # Verifies if the Sale hasn't started yet
        Assert(App.globalGet(global_state) == SaleNotStarted),
        # Security Checks
        defaultTransactionChecks(Int(0)),
        defaultTransactionChecks(Int(1)),
        defaultTransactionChecks(Int(2)),
        # Verifies if the first transaction is a Payment
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        # Verifies if the third transaction is a ApplicationCallTransfer
        Assert(Gtxn[1].type_enum() == TxnType.ApplicationCall),
        # Verifies if the second transaction is a AssetTransfer
        Assert(Gtxn[2].type_enum() == TxnType.AssetTransfer),
        # Verifies if the seller is the one starting the sale
        Assert(Gtxn[0].sender() == App.globalGet(global_ES_provider_address)),
        Assert(Gtxn[1].sender() == App.globalGet(global_ES_provider_address)),
        Assert(Gtxn[2].sender() == App.globalGet(global_ES_provider_address)),
        # Verifies if the ammount payed is large enough to pay the transaction fees.
        Assert(Gtxn[0].amount() >= Mul(Int(8), Global.min_txn_fee())),
        # Verifies if the number of payments is a divisor of 12
        Assert(Mod(Int(12), Btoi(Gtxn[1].application_args[2])) == Int(0)),
        # Creates a Inner Transaction Group to send to the Oracle Account
        InnerTxnBuilder.Begin(),
        # Starts with a Payment Transaction
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.sender: Global.current_application_address(),
                TxnField.receiver: Gtxn[1].accounts[1],
                TxnField.amount: (Mul(Int(3), Global.min_txn_fee())),
                TxnField.fee: Int(0),
            }
        ),
        # Continues to the next Transaction
        InnerTxnBuilder.Next(),
        # Continues with an ApplicationCall to the Oracle
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.ApplicationCall,
                TxnField.sender: Global.current_application_address(),
                TxnField.application_id: Gtxn[1].applications[1],
                TxnField.application_args: [Bytes("Receive_Request")],
                TxnField.accounts: [Gtxn[1].accounts[2]],
                TxnField.applications: [Gtxn[1].applications[0]],
                TxnField.fee: Int(0),
            }
        ),
        # Submits the transaction
        InnerTxnBuilder.Submit(),
        # Creates an Inner Transaction to opt in to the asset that will be received
        InnerTxnBuilder.Begin(),
        # Creates opt in transaction
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum : TxnType.AssetTransfer,
                TxnField.asset_receiver: Global.current_application_address(),
                TxnField.xfer_asset: Gtxn[2].xfer_asset(),
                TxnField.fee: Int(0),                
            }
        ),
        # Submits the Inner Transaction
        InnerTxnBuilder.Submit(),
        # Verifies if the asset's transfered comes from the Land Registry
        isLandRegistryToken(Gtxn[2].xfer_asset()),
        # Stores the sent Asset Id
        App.globalPut(global_asset_id ,Gtxn[2].xfer_asset()),
        # Stores the number of payments
        App.globalPut(global_number_of_payments,  Btoi(Txn.application_args[2])),
        # Starts the sale
        App.globalPut(global_state, Int(1)),
        # Stores the nft price
        App.globalPut(global_PES_goal, Btoi(Txn.application_args[1])),
        # Stores the current timestamp
        App.globalPut(global_start_timestamp, Global.latest_timestamp()),
        # Approves
        Approve(),
    )


    refund_ammount = ScratchVar(TealType.uint64)
    state_byte = ScratchVar(TealType.bytes)

    # Called in the No_Op
    # The make_payment function receives a group of arguments:
    # 0. make_payment
    # 1. The quantity of NFT bought
    # The make_payment function receives a group of transactions:
    # 1. A payment transfer which is the offer
    # 2. A Application Call to call the Smart Contract
    make_payment = Seq(
        # Verifies if has the NFT Seller is awaiting response
        isWaitingForResponse(),
        # Verifies if the group of transactions contains only two transactions
        Assert(Global.group_size() == Int(2)),
        # Verifies if the first transaction is an Payment Transfer
        Assert(Gtxn[0].type_enum() == TxnType.Payment),    
        # Verifies if the receiver of the payment transaction is the smart contract
        Assert(Gtxn[0].receiver() == Global.current_application_address()),
        # Verifies if the second transaction is a Application Call
        Assert(Gtxn[1].type_enum() == TxnType.ApplicationCall),
        # Verifies if the caller and the payer are the same
        Assert(Gtxn[1].sender() == Gtxn[0].sender()),
        # Verifies default transaction checks
        defaultTransactionChecks(Int(0)),
        defaultTransactionChecks(Int(1)),
        # Loads box
        boxint := App.box_get(Gtxn[0].sender()),
        # Verifies if it exists
        Assert(boxint.hasValue()),    
        # Verifies if ts != 0
        Assert(get_ts(Gtxn[0].sender()) == Int(0)),    
        # Increments the payment on the account, minus the minimum transaction fee
        # Saves the donation
        refund_ammount.store(Gtxn[0].amount() / (App.globalGet(global_number_of_payments) - App.globalGet(global_state) + Int(1))),
        # Sets
        set_refunds(Gtxn[0].sender(), Itob(refund_ammount.load())),
        # Global Money
        App.globalPut(global_money, App.globalGet(global_money) + refund_ammount.load()),
        # Gets state byte
        state_byte.store(Itob(App.globalGet(global_state))),
        # Saves the ts
        #set_ts(Gtxn[0].sender(), GetByte(state_byte.load(), Int(0))),
        #set_ts(Gtxn[0].sender(), Substring(Itob(GetByte(state_byte.load(), Int(0))), Int(0), Int(1))), 
        set_ts(Gtxn[0].sender(), Substring(state_byte.load(), Int(7), Int(8))),
        #set_ts(Gtxn[0].sender(), Substring(Itob(GetByte(state_byte.load(), Int(0))), Int(0), Int(1))),
        # Approves
        Approve()
    )

    # Called in the No_Op.
    # Environmental Conditionality was guaranteed and therefore the seller can receive the money.
    # Received apps
    # 1. The oracle app
    # Received accounts
    # 1. The seller account, which will also be used to access the box array
    # 2. The NFT-Seller address
    # Received assets
    # 0. The Land Registry NFT
    receive_negative_response = Seq(
        # Verifies if has the NFT Seller is awaiting response
        isWaitingForResponse(),
        # Verifies if the period time has passed
        # Assert(Global.latest_timestamp() >= App.globalGet(global_start_timestamp) + (secondsYear/responseState)),
        # Security Checks
        defaultTransactionChecks(Int(0)),
        # Verifies if the message was sent by the oracle.
        Assert(Txn.sender() == app_id_to_address(App.globalGet(global_oracle_app_id))),
        # Stores feedback in success
        # App.globalPut(global_success, SetBit(App.globalGet(global_success), App.globalGet(global_state) - Int(1), Int(0))),
        # Updates state
        App.globalPut(global_state, App.globalGet(global_state) + Int(1)),
        # Verifies if it has reached final state
        If(App.globalGet(global_state) == FinalState)
        .Then(
            Seq(
                # Returns the NFT to the owner
                InnerTxnBuilder.Begin(),
                # Creates an AssetTransfer transaction
                InnerTxnBuilder.SetFields({
                    TxnField.type_enum: TxnType.AssetTransfer,
                    TxnField.asset_receiver: Txn.accounts[1], # The Seller Account
                    TxnField.asset_amount: Int(1),
                    TxnField.xfer_asset: Txn.assets[0], # Must be in the assets array sent as part of the application call
                    TxnField.asset_close_to: Txn.accounts[1],
                    TxnField.fee:Int(0),
                }),
                InnerTxnBuilder.Next(),
                # Creates a Payment transaction that returns the MBR increase from the Land Deed Token
                InnerTxnBuilder.SetFields(
                    {
                        TxnField.type_enum:  TxnType.Payment,
                        TxnField.sender: Global.current_application_address(),
                        TxnField.receiver: Txn.accounts[1],
                        TxnField.amount: Int(100000),
                        TxnField.fee:Int(0),
                    }
                ),
                # Submits the transaction
                InnerTxnBuilder.Submit(),
            )
        ),
        # Approves
        Approve(),
    )

    # Called in the No_Op.
    # Environmental Conditionality was guaranteed and therefore the seller can receive the money.
    # Received apps
    # 1. The oracle app
    # Received accounts
    # 1. The seller account, which will also be used to access the box array
    # 2. The NFT-Seller address
    # Received assets
    # 0. The Land Registry NFT
    # Total cost: 4 * Min_Fee
    receive_positive_response = Seq(
        # Verifies if has the NFT Seller is awaiting response
        isWaitingForResponse(),
        # Verifies if the period time has passed 
        #Assert(Global.latest_timestamp() >= App.globalGet(global_start_timestamp) + (secondsYear/responseState)),
        # Security Checks
        defaultTransactionChecks(Int(0)),
        # Verifies if the message was sent by the oracle.
        Assert(Txn.sender() == app_id_to_address(App.globalGet(global_oracle_app_id))),
        # Verifies if the first account received is the seller address
        Assert(App.globalGet(global_ES_provider_address) == Txn.accounts[1]),
        # Stores feedback in success
        App.globalPut(global_success, SetBit(App.globalGet(global_success), App.globalGet(global_state) - Int(1), Int(1))),
        # Updates the state
        App.globalPut(global_state, App.globalGet(global_state) + Int(1)),
        # If final state
        If(App.globalGet(global_state) == FinalState)
        .Then(
            Seq(
                InnerTxnBuilder.Begin(),
                # Creates an AssetTransfer transaction
                InnerTxnBuilder.SetFields({
                    TxnField.type_enum: TxnType.AssetTransfer,
                    TxnField.asset_receiver: Txn.accounts[1], # Seller Address
                    TxnField.asset_amount: Int(1),
                    TxnField.xfer_asset: Txn.assets[0], # Must be in the assets array sent as part of the application call
                    TxnField.asset_close_to: Txn.accounts[1],
                    TxnField.fee:Int(0),
                }),
                # Continues transaction group
                InnerTxnBuilder.Next(),
                # Makes Payment Transaction
                InnerTxnBuilder.SetFields(
                    {
                    TxnField.type_enum:  TxnType.Payment,
                    TxnField.sender: Global.current_application_address(),
                    TxnField.receiver: Txn.accounts[1],
                    TxnField.amount:  App.globalGet(global_money) + Int(100000),
                    TxnField.fee:Int(0),
                    }
                ),
                # Submits
                InnerTxnBuilder.Submit(),
            )
        )
        # If not final state
        .Else(
            Seq(
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields(
                    {
                        TxnField.type_enum:  TxnType.Payment,
                        TxnField.sender: Global.current_application_address(),
                        TxnField.receiver: Txn.accounts[1],
                        TxnField.amount: App.globalGet(global_money),
                        TxnField.fee:Int(0),
                    }
                ),
                InnerTxnBuilder.Submit(),
            ),
        ),
        # Approves
        Approve()
    )

    i = ScratchVar(TealType.uint64)
    refund_counter = ScratchVar(TealType.uint64)
    box_deleted = ScratchVar(TealType.uint64)

    get_refund = Seq(
        # Security Checks
        defaultTransactionChecks(Int(0)),
        # Loads box
        boxint := App.box_get(Txn.sender()),
        # Verifies if it exists
        Assert(boxint.hasValue()),
        # Initializes scratches
        refund_counter.store(Int(0)),
        box_deleted.store(Int(0)),
        # If it exists gets ts
        For(i.store((get_ts(Txn.sender()))), i.load() < App.globalGet(global_state), i.store(i.load() + Int(1)))
        .Do(
            Seq(
                # If the environmental conditionality wasn't guaranteed
                If(GetBit(App.globalGet(global_success), App.globalGet(global_state) - i.load() - Int(1)) == Int(0))
                .Then(
                    # Adds to available refunds
                    refund_counter.store(refund_counter.load() + get_refunds(Txn.sender())),
                ),
            )
        ),
        # Updates user timpestamp
        set_ts(Txn.sender(), Substring(Itob(App.globalGet(global_state)), Int(7), Int(8))),
        # Verifies if its a final state
        If(App.globalGet(global_state) == FinalState)
        .Then(
            # Deletes the box
            Seq(
                Pop(App.box_delete(Txn.sender())),
                box_deleted.store(Int(1)),
                App.globalPut(global_number_of_boxes, App.globalGet(global_number_of_boxes) - Int(1)),
            )
        ),
        # Verifies if there's money to be refunded
        If(Or(refund_counter.load() > Int(0), box_deleted.load() == Int(1)))
        .Then(
            # Creates an InnerTransactions to send to refund to the buyer
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum:  TxnType.Payment,
                    TxnField.sender: Global.current_application_address(),
                    TxnField.receiver: Txn.sender(),
                    TxnField.amount: refund_counter.load() + box_minimum_balance(Txn.sender(), Int(9)) * box_deleted.load(),
                    TxnField.fee: Int(0),
                }
            ),
            # Submits the transaction
            InnerTxnBuilder.Submit(),
        ),
        # Approves
        Approve(),
    )

    refund = ScratchVar(TealType.uint64)

    delete_NFT_Seller = Seq(
        # Verifies if has received a response from the Oracle
        Assert(Or(App.globalGet(global_state) == SaleNotStarted, App.globalGet(global_state) == FinalState)),
        # Verifies the default transaction checks
        defaultTransactionChecks(Int(0)),
        # Verifies if the Seller Address is the one sending the request
        Assert(App.globalGet(global_ES_provider_address) == Txn.accounts[1]),
        # Verifies if there are no refunds left to be granted
        Assert(App.globalGet(global_number_of_boxes) == Int(0)),
        # Approves
        Approve(),
    )

    hasBox = App.box_get(Gtxn[1].sender())

    create_box = Seq(
        # Boxes can only be created in the WaitingForResponse state
        Assert(
            And(
                App.globalGet(global_state) != SaleNotStarted,
                App.globalGet(global_state) != FinalState,
                )
            ),
        isWaitingForResponse(),
        # Verifies if the group of transactions contains only two transactions
        Assert(Global.group_size() == Int(2)),
        # Verifies default transaction checks
        defaultTransactionChecks(Int(0)),
        defaultTransactionChecks(Int(1)),
        # Verifies if the sender of both transaction is the same
        Assert(Gtxn[0].sender() == Gtxn[1].sender()),
        # Verifies if the first transaction is a Payment
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        # Verifies if the amount sent is enough to cover the minimum balance
        Assert(Gtxn[0].amount() >= box_minimum_balance(Gtxn[1].sender(), Int(9))),
        # Verifies if the second transaction is an Application Call
        Assert(Gtxn[1].type_enum() == TxnType.ApplicationCall),
        # Obtains hasBox
        hasBox,
        # If box does not exist then creates box
        If(hasBox.hasValue() == Int(0))
        .Then( 
        Seq(
            # Creates Box
            Pop(App.box_create(Gtxn[1].sender(), Int(9))),
            # Puts 0 in the box
            set_refunds(Gtxn[1].sender(), Itob(Int(0))),
            set_ts(Gtxn[1].sender(), Bytes(b'\x00')),
            # Increments number of boxes
            App.globalPut(global_number_of_boxes, App.globalGet(global_number_of_boxes)  + Int(1)),
            # Approves
            Approve(),
            ) 
        )
        .Else(
        # If box exists then rejects it
        Reject()
        ),
    )

    give_refund = Seq(
        # Refunds can only be given if its on final state
        Assert(App.globalGet(global_state) == FinalState),
        # Verifies if the seller is the sender
        Assert(Txn.sender() == App.globalGet(global_ES_provider_address)),
        # Security Checks
        defaultTransactionChecks(Int(0)),
        # Loads box
        boxint := App.box_get(Txn.accounts[1]),
        # Verifies if it exists
        Assert(boxint.hasValue()),
        # Initializes scratches
        refund_counter.store(Int(0)),
        box_deleted.store(Int(0)),
        # If it exists gets ts
        For(i.store(get_ts(Txn.accounts[1])), i.load() < App.globalGet(global_state), i.store(i.load() + Int(1)))
        .Do(
            Seq(
                # If the environmental conditionality wasn't guaranteed
                If(GetBit(App.globalGet(global_success), i.load() - Int(1)) == Int(0))
                .Then(
                    # Adds to available refunds
                    refund_counter.store(refund_counter.load() + get_refunds(Txn.accounts[1])),
                ),
            )
        ),
        # Updates user timpestamp
        set_ts(Txn.accounts[1], Substring(Itob(App.globalGet(global_state)), Int(7), Int(8))),
        # Verifies if its a final state
        If(App.globalGet(global_state) == FinalState)
        .Then(
            # Deletes the box
            Seq(
                Pop(App.box_delete(Txn.accounts[1])),
                box_deleted.store(Int(1)),
                App.globalPut(global_number_of_boxes, App.globalGet(global_number_of_boxes) - Int(1)),
            )
        ),
        # Verifies if there's money to be refunded
        If(Or(refund_counter.load() > Int(0), box_deleted.load() == Int(1)))
        .Then(
            # Creates an InnerTransactions to send to refund to the buyer
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum:  TxnType.Payment,
                    TxnField.sender: Global.current_application_address(),
                    TxnField.receiver: Txn.accounts[1],
                    TxnField.amount: refund_counter.load() + box_minimum_balance(Txn.accounts[1], Int(9)) * box_deleted.load(),
                    TxnField.fee: Int(0),
                }
            ),
            # Submits the transaction
            InnerTxnBuilder.Submit(),
        ),
        # Approves
        Approve(),  
    )

    return program.event(
        init=nft_seller_init,
        no_op=Cond(
            [Txn.application_args[0] == op_start_sale, start_sale],
            [Txn.application_args[0] == op_make_payment, make_payment],
            [Txn.application_args[0] == op_receive_negative_response,
                receive_negative_response],
            [Txn.application_args[0] == op_receive_positive_response,
                receive_positive_response],
            [Txn.application_args[0] == op_get_refund, get_refund],
            [Txn.application_args[0] == op_give_refund, give_refund],
            [Txn.application_args[0] == op_create_box, create_box],
        ),
        opt_in=Reject(),
        close_out=get_refund,
        delete=delete_NFT_Seller,
        update=Reject(),
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

    algod_client = AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

    approval_file = open(TEAL_PATH + 'NFT-Seller-approval-periodic.teal', 'w')
    approval_file.write(approval_program())

    approval_result = algod_client.compile(approval_program())

    approval_bytes = b64decode(approval_result["result"])

    print(approval_bytes)
    approval_file.close()

    clear_file = open(TEAL_PATH + 'NFT-Seller-clear-periodic.teal', 'w')
    clear_file.write(clear_state_program())

    clear_result = algod_client.compile(clear_state_program())

    clear_bytes = b64decode(clear_result["result"])

    print(clear_bytes)

    clear_file.close()

    print("success")