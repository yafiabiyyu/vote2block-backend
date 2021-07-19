from project import celery
from project.service.ethereum_service import EthereumService
from dotenv import load_dotenv
import os, time


es = EthereumService()
load_dotenv()


@celery.task
def GetTimeDataTask():
    contract = es.AccessContract()
    result = contract.functions.GetVotingTimeData().call()
    return result


@celery.task
def GetKandidatTotalDataTask():
    contract = es.AccessContract()
    result = contract.functions.GetTotalKandidat().call()
    return result


@celery.task
def GetKandidatData(kandidatId):
    contract = es.AccessContract()
    result = contract.functions.GetKandidatData(kandidatId).call()
    return result


@celery.task
def GetPemilihDataTask(addressPemilih):
    w3 = es.SetupW3()
    contract = es.AccessContract()
    result = contract.functions.GetPemilihData(
        w3.toChecksumAddress(addressPemilih)
    ).call()
    return result


@celery.task
def SetupTimestampTask(
    registerstart,
    registerfinis,
    votingstart,
    votingfinis,
    nonce,
    signature,
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
    tx_hash = contract.functions.SetupTimedata(
        registerstart,
        registerfinis,
        votingstart,
        votingfinis,
        nonce,
        signature,
    ).buildTransaction(
        {
            "gas": 1000000,
            "gasPrice": w3.toWei("25", "gwei"),
            "nonce": main_account_nonce,
        }
    )
    sign_tx = w3.eth.account.sign_transaction(
        tx_hash, main_account_access
    )
    try:
        w3.eth.sendRawTransaction(sign_tx.rawTransaction)
        return w3.toHex(w3.keccak(sign_tx.rawTransaction))
    except Exception:
        return "Gagal"


@celery.task
def RegisterKandidatTask(
    kandidatID, kandidatNameBytes, nonce, signature
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
    livetime = int(time.time())
    tx_hash = contract.functions.KandidatRegister(
        kandidatID, nonce, livetime, kandidatNameBytes, signature
    ).buildTransaction(
        {
            "gas": 1000000,
            "gasPrice": w3.toWei("25", "gwei"),
            "nonce": main_account_nonce,
        }
    )
    sign_tx = w3.eth.account.sign_transaction(
        tx_hash, main_account_access
    )
    try:
        w3.eth.sendRawTransaction(sign_tx.rawTransaction)
        return w3.toHex(w3.keccak(sign_tx.rawTransaction))
    except Exception as e:
        print(e)
        return "Gagal"


@celery.task
def RegisterPemilihTask(pemilihAddress, nonce, signature):
    w3 = es.SetupW3()
    contract = es.AccessContract()
    main_account_access = os.getenv("MAIN_ACCOUNT")
    main_account_address = w3.eth.account.privateKeyToAccount(
        main_account_access
    ).address
    main_account_nonce = w3.eth.getTransactionCount(
        main_account_address
    )
    livetime = int(time.time())
    tx_hash = contract.functions.PemilihRegister(
        pemilihAddress, nonce, livetime, signature
    ).buildTransaction(
        {
            "gas": 1000000,
            "gasPrice": w3.toWei("25", "gwei"),
            "nonce":main_account_nonce
        }
    )
    sign_tx = w3.eth.account.sign_transaction(
        tx_hash, main_account_access
    )
    try:
        w3.eth.sendRawTransaction(sign_tx.rawTransaction)
        return w3.toHex(w3.keccak(sign_tx.rawTransaction))
    except Exception:
        return "Gagal"


@celery.task
def VotingTask(kandidatID, nonce, signature):
    w3 = es.SetupW3()
    contract = es.AccessContract()
    main_account_access = os.getenv("MAIN_ACCOUNT")
    main_account_address = w3.eth.account.privateKeyToAccount(
        main_account_access
    ).address
    main_account_nonce = w3.eth.getTransactionCount(
        main_account_address
    )
    livetime = int(time.time())
    tx_hash = contract.functions.Voting(
        kandidatID, nonce, livetime, signature
    ).buildTransaction(
        {
            "gas": 1000000,
            "gasPrice": w3.toWei("25", "gwei"),
            "nonce":main_account_nonce
        }
    )
    sign_tx = w3.eth.account.sign_transaction(
        tx_hash, main_account_access
    )
    try:
        w3.eth.sendRawTransaction(sign_tx.rawTransaction)
        return w3.toHex(w3.keccak(sign_tx.rawTransaction))
    except Exception:
        return "Gagal"


@celery.task
def KandidatTerpilihTask():
    contract = es.AccessContract()
    livetime = int(time.time())
    try:
        result = contract.functions.KandidatTerpilih(livetime).call()
        return result
    except Exception:
        return "Gagal"
