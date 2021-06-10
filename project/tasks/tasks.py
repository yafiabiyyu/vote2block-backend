from project import celery
from project.service.ethereum_service import EthereumService
from dotenv import load_dotenv
import os, time

es = EthereumService()
load_dotenv()


@celery.task
def SavePetugasTask(petugas_address, signature, ketua_nonce):
    w3 = es.SetupW3()
    contract = es.AccessContract()
    main_account_access = os.getenv("MAIN_ACCOUNT")
    main_account_address = w3.eth.account.privateKeyToAccount(
        main_account_access
    ).address
    main_account_nonce = w3.eth.getTransactionCount(
        main_account_address
    )
    tx_hash = contract.functions.addPetugas(
        w3.toChecksumAddress(petugas_address), ketua_nonce, signature
    ).buildTransaction({"nonce": main_account_nonce})
    sign_tx = w3.eth.account.sign_transaction(
        tx_hash, main_account_access
    )
    try:
        w3.eth.sendRawTransaction(sign_tx.rawTransaction)
        return w3.toHex(w3.keccak(sign_tx.rawTransaction))
    except Exception:
        return "Gagal"


@celery.task
def RemovePetugasTask(petugas_address, signature, ketua_nonce):
    w3 = es.SetupW3()
    contract = es.AccessContract()
    main_account_access = os.getenv("MAIN_ACCOUNT")
    main_accout_address = w3.eth.account.privateKeyToAccount(
        main_account_access
    ).address
    main_account_nonce = w3.eth.getTransactionCount(main_accout_address)
    tx_hash = contract.functions.removePetugas(
        w3.toChecksumAddress(petugas_address),
        ketua_nonce,
        signature,
    ).buildTransaction({"nonce": main_account_nonce})
    sign_tx = w3.eth.account.sign_transaction(
        tx_hash, main_account_access
    )
    try:
        w3.eth.sendRawTransaction(sign_tx.rawTransaction)
        return w3.toHex(w3.keccak(sign_tx.rawTransaction))
    except Exception:
        return "Gagal"


@celery.task
def SetupTimeAppTask(
    registerstart, registerfinis, votingstart, votingfinis, signature
):
    w3 = es.SetupW3()
    contract = es.AccessContract()
    main_account_access = os.getenv("MAIN_ACCOUNT")
    main_account_address = w3.eth.account.privateKeyToAccount(
        main_account_access
    ).address
    main_account_nonce = w3.eth.getTransactionCount(
        main_account_address
    )
    tx_hash = contract.functions.setVotingTimestampEvent(
        registerstart,
        registerfinis,
        votingstart,
        votingfinis,
        signature,
    ).buildTransaction({"nonce": main_account_nonce})
    sign_tx = w3.eth.account.sign_transaction(
        tx_hash, main_account_access
    )
    try:
        w3.eth.sendRawTransaction(sign_tx.rawTransaction)
        return w3.toHex(w3.keccak(sign_tx.rawTransaction))
    except Exception:
        return "Gagal"


# Petugas Peneyelenggara Task
@celery.task
def RegisterKandidatTask(
    kandidatID, petugas_nonce, bytes_name_kandidat, signature
):
    w3 = es.SetupW3()
    contract = es.AccessContract()
    main_account_access = os.getenv("MAIN_ACCOUNT")
    main_account_address = w3.eth.account.privateKeyToAccount(
        main_account_access
    ).address
    main_account_nonce = w3.eth.getTransactionCount(
        main_account_address
    )
    unixtimestamp = int(time.time())
    tx_hash = contract.functions.registerKandidat(
        int(kandidatID),
        petugas_nonce,
        unixtimestamp,
        bytes_name_kandidat,
        signature,
    ).buildTransaction({"nonce": main_account_nonce})
    sign_tx = w3.eth.account.sign_transaction(
        tx_hash, main_account_access
    )
    try:
        w3.eth.sendRawTransaction(sign_tx.rawTransaction)
        return w3.toHex(w3.keccak(sign_tx.rawTransaction))
    except Exception:
        return "Gagal"


@celery.task
def RegisterPemilihTask(petugas_nonce, pemilih_address, signature):
    w3 = es.SetupW3()
    contract = es.AccessContract()
    main_account_access = os.getenv("MAIN_ACCOUNT")
    main_account_address = w3.eth.account.privateKeyToAccount(
        main_account_access
    ).address
    main_account_nonce = w3.eth.getTransactionCount(
        main_account_address
    )
    unixtimestamp = int(time.time())
    tx_hash = contract.functions.registerPemilih(
        w3.toChecksumAddress(pemilih_address),
        petugas_nonce,
        unixtimestamp,
        signature,
    ).buildTransaction({"nonce": main_account_nonce})
    sign_tx = w3.eth.account.sign_transaction(
        tx_hash, main_account_access
    )
    try:
        w3.eth.sendRawTransaction(sign_tx.rawTransaction)
        return w3.toHex(w3.keccak(sign_tx.rawTransaction))
    except Exception:
        return "Gagal"

# Register and Voting Timestamp Task
@celery.task
def GetTimestampDataTask():
    contract = es.AccessContract()
    result = contract.functions.getTimestampData().call()
    return result

# Get Pemilih data dari smart-contract
@celery.task
def GetPemilihDataTask(pemilih_address):
    contract = es.AccessContract()
    result = contract.functions.getPemilihData(pemilih_address).call()
    return result