from web3 import Web3, HTTPProvider
from dotenv import load_dotenv
from project.models.user_model import UserDoc
from project.service.enkripsi_service import DataEncryption
from eth_account.messages import encode_defunct
import os
import json

load_dotenv()
de = DataEncryption()


class EthereumService:
    def SetupW3(self):
        rpc_url = os.getenv("RPC_URL")
        default_account = os.getenv("DEFAULT_ACCOUNT")
        w3 = Web3(HTTPProvider(rpc_url))
        return w3

    def AccessContract(self):
        w3 = self.SetupW3()
        contract_file = open("project/smart-contract/Vote2Block.json")
        data = json.load(contract_file)
        abi = data["abi"]
        contract_address = os.getenv("CONTRACT_ADDRESS")
        contract = w3.eth.contract(address=contract_address, abi=abi)
        return contract

    def CreateWallet(self):
        key = os.getenv("SECRET_KEY")
        w3 = self.SetupW3()
        account = w3.eth.account.create(key)
        ethereum_access = de.Encrypting(account.privateKey)
        return account.address, ethereum_access
