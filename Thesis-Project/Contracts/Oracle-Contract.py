from pyteal import *
from pyteal_helpers import program

TEAL_PATH = "Thesis-Project/TEAL/"


def approval():

    # This Smart Contract works as an interface to an oracle. NFT-Seller Smart Contracts comunicate with this smart contract
    # to obtain updates about the ecosystem services. An oracle program will deploy this smart contract and after the contract
    # is deployed will use indexer to read the transactions received by the contract and algod to send transactions to
    # interact with the blockchain.

    # GLOBAL - App Create
    #Minimum-Balance = 100000 = MIN_BALANCE

    # GLOBAL

    global_pes_scheme_state = Bytes("State")

    global_number_of_payments = Bytes("Number_of_Payments")

    # CONSTANTS 

    # The state constants:
    SaleNotStarted = Int(0)
    WaitingForResponse = Int(1)
    NegativeResponse = Int(2)
    PositiveResponse = Int(3)
 
    # OPERATIONS

    # Receives a request
    op_receive_request = Bytes("Receive_Request")

    # Answers a request
    op_answer_request = Bytes("Answer_Request")

    # The operation responsible for receiving a positive response from the oracle
    op_receive_positive_response = Bytes("receive_positive_response")

    # The operation responsible for receiving a positive response from the oracle
    op_receive_negative_response = Bytes("receive_negative_response")

    # SUBROUTINES
    @Subroutine(TealType.none)
    def defaultTransactionChecks(txnId):
        return Seq([
            Assert(txnId < Global.group_size()),
            Assert(Gtxn[txnId].rekey_to() == Global.zero_address()),
            Assert(Gtxn[txnId].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[txnId].asset_close_to() == Global.zero_address())
        ])


    # Receives a request and stores the note on the blockchain
    # This function receives a group of transactions that consists of:
    # 1 A Payment transaction to fund the minimum transaction fees of the response
    # 2 An ApplicationCall transaction that calls the application, is detected by the indexer and changes the local state of the smart Contract
    receive_request = Seq(
        # Verifies if the group of transactions contains only two transaction
        Assert(Global.group_size() == Int(2)),
        # Verifies if this transaction is the second transaction in the group
        Assert(Txn.group_index() == Int(1)),
        # Verifies default transaction checks
        defaultTransactionChecks(Int(0)),
        defaultTransactionChecks(Int(1)),
        # Verifies if the first transaction is an Payment Transfer
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        # Verifies if the minimum fee was payed
        Assert(Gtxn[0].amount() >= Mul(Int(3), Global.min_txn_fee())),
        # Verifies if the second transaction is a Application Call
        Assert(Gtxn[1].type_enum() == TxnType.ApplicationCall),
        # Verifies if the length of application_arguments is 1
        Assert(Gtxn[1].application_args.length() == Int(1)),
        # Loads the PES Scheme's state
        PES_state := App.globalGetEx(Gtxn[1].applications[1], global_pes_scheme_state),
        # Verifies if it exists
        Assert(PES_state.hasValue() == Int(1)),
        # Verifies if the PES Scheme if the PES Scheme hasn't started
        Assert(PES_state.value() == SaleNotStarted),
        # Sends the oracle account the funds
        InnerTxnBuilder.Begin(),
        # Through a Payment Transaction
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.sender: Global.current_application_address(),
                TxnField.receiver: Gtxn[1].accounts[1],
                TxnField.amount: Mul(Int(2),Global.min_txn_fee()),
                TxnField.fee: Int(0),
            }
        ),
        InnerTxnBuilder.Submit(),
        # Approves
        Approve()
    )

    response_type = ScratchVar(TealType.bytes)
    

    # Answers request
    # This function receives the following application arguments:
    # 0 Response
    # 1 True or False
    # Accounts
    # 1. The Seller Account
    # 2. The nft seller Account
    # Assets
    # 0. Land Registry NFT
    # Applications
    # 0. Oracle App Id
    # 1. Nft Manager App Id
    # 2. Nft Seller App Id
    answer_request = Seq(
        # Verifies if the group of transaction contains only one transaction
        Assert(Global.group_size() == Int(1)),
        # Verifies if this transaction is the first transaction in the group
        Assert(Txn.group_index() == Int(0)),
        # Verifies default transaction checks
        defaultTransactionChecks(Int(0)),
        # Verifies if the  transaction is a Application Call
        Assert(Txn.type_enum() == TxnType.ApplicationCall),
        # Verifies if the response sender is the oracle account who created the smart contract
        Assert(Txn.sender() == Global.creator_address()),
        # PES Scheme's state
        PES_state2 := App.globalGetEx(Txn.applications[2], global_pes_scheme_state),
        # Verifies if it exists
        Assert(PES_state2.hasValue() == Int(1)),
        # Verifies if Periodic PES
        PES_num_payments := App.globalGetEx(Txn.applications[2], global_number_of_payments),
        # Tests if Periodic
        If(PES_num_payments.hasValue() == Int(1))
        .Then(
            Seq(
                # If PERIODIC
                # Verifies if it can receive a response
                Assert(PES_state2.value() <= PES_num_payments.value()),
                Assert(PES_state2.value() != Int(0)),
            )
        )
        .Else(
            Seq(
                # If NOT PERIODIC
                # Verifies if the PES Scheme is waiting for response
                Assert(PES_state2.value() ==  WaitingForResponse),
            )
        ),

        # Verifies the type of response
        If(Btoi(Txn.application_args[1]) == Int(1),
        response_type.store(op_receive_positive_response),
        response_type.store(op_receive_negative_response)),
        # Creates the Inner Transactions that will be sended
        InnerTxnBuilder.Begin(),
        # An Application Call that will be sent to the address of the arguments
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.ApplicationCall,
                TxnField.application_id: Txn.applications[2], # NFT Seller AP ID
                TxnField.application_args: [response_type.load()],
                TxnField.accounts: [Txn.accounts[1]], # Seller Address, NFT Seller Address
                TxnField.applications: [Txn.applications[0]], # Oracle ID
                TxnField.assets: [Txn.assets[0]], # Land Registry Asset
                TxnField.fee: Int(0),
            }
        ),
        # 
        InnerTxnBuilder.Next(),
        InnerTxnBuilder.SetFields(
            {
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.application_id: Txn.applications[1], # NFT Manager AP ID
            TxnField.application_args: [response_type.load()],
            TxnField.accounts: [Txn.accounts[1]], #NFT Seller
            TxnField.fee: Int(0),
            }
        ),
        InnerTxnBuilder.Submit(),
        # Approves
        Approve()
    )

    return program.event(
        # Init just approves
        init=Approve(),
        no_op=Cond(
            # Receives a request to the oracle that will be detected by the indexer
            [Txn.application_args[0] == op_receive_request, receive_request],
            # Answers a request by the oracle that will be sent by the algod
            [Txn.application_args[0] == op_answer_request, answer_request],
        ),
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
    approval_file = open(TEAL_PATH + 'Oracle-approval.teal', 'w')
    approval_file.write(approval_program())
    approval_file.close()

    clear_file = open(TEAL_PATH + 'Oracle-clear.teal', 'w')
    clear_file.write(clear_state_program())
    clear_file.close()

    print("success")
