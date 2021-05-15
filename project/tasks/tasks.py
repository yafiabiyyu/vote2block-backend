from project import celery
from project.service.ethereum_service import EthereumService
from time import sleep
from dotenv import load_dotenv
import os

es = EthereumService()
load_dotenv()

@celery.task
def SavePetugasToContract(admin_address, signature,ketua_nonce):
    w3 = es.SetupW3()
    contract = es.AccessContract()
    main_acc_access = os.getenv("MAIN_ACCOUNT")
    main_acc_address = w3.eth.account.privateKeyToAccount(main_acc_access).address
    main_nonce = w3.eth.getTransactionCount(
        w3.toChecksumAddress(main_acc_address)
    )
    tx_hash = contract.functions.addPetugas(
        w3.toChecksumAddress(admin_address),
        ketua_nonce,
        signature
    ).buildTransaction({
        "chainId":5777,
        "gas":70000,
        "gasPrice":w3.toWei('1','gwei'),
        "nonce":main_nonce
    })
    sign_tx = w3.eth.account.sign_transaction(tx_hash,main_acc_access)
    w3.eth.sendRawTransaction(sign_tx.rawTransaction)
    return w3.toHex(w3.keccak(sign_tx.rawTransaction))

@celery.task
def RemovePetugasFromContract(admin_address, signature, ketua_nonce):
    w3 = es.SetupW3()
    contract = es.AccessContract()
    main_acc_access = os.getenv("MAIN_ACCOUNT")
    main_acc_address = w3.eth.account.privateKeyToAccount(main_acc_access).address
    main_nonce = w3.eth.getTransactionCount(main_acc_address)
    tx_hash = contract.functions.removePetugas(
        w3.toChecksumAddress(admin_address),
        ketua_nonce,
        signature
    ).buildTransaction({
        "chainId":5777,
        "gas":70000,
        "gasPrice":w3.toWei('1', 'gwei'),
        "nonce":main_nonce
    })
    sign_tx = w3.eth.account.sign_transaction(tx_hash, main_acc_access)
    w3.eth.sendRawTransaction(sign_tx.rawTransaction)
    return w3.toHex(w3.keccak(sign_tx.rawTransaction))

@celery.task
def SetVotingTimeStamp(register_start, register_finis, voting_start, voting_finis, signature):
    w3 = es.SetupW3()
    contract = es.AccessContract()
    main_acc_access = os.getenv("MAIN_ACCOUNT")
    main_acc_address = w3.eth.account.privateKeyToAccount(main_acc_access).address
    main_nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(main_acc_address))
    tx_hash = contract.functions.setVotingTimestampEvent(
        register_start,
        register_finis,
        voting_start,
        voting_finis,
        signature
    ).buildTransaction({
        "chainId":5777,
        "gas":70000,
        "gasPrice":w3.toWei('1','gwei'),
        "nonce":main_nonce
    })
    sign_tx = w3.eth.account.sign_transaction(tx_hash, main_acc_access)
    w3.eth.sendRawTransaction(sign_tx.rawTransaction)
    return w3.toHex(w3.keccak(sign_tx.rawTransaction))
