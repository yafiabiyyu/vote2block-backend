from eth_account import account
from web3 import Web3, HTTPProvider, WebsocketProvider
from dotenv import load_dotenv
from project.service.enkripsi_service import DataEnkripsi
import json, os

load_dotenv()
de = DataEnkripsi()


class EthereumService:
    def SetupW3(self):
        rpc_url = os.getenv("RPC_URL")
        w3 = Web3(HTTPProvider(rpc_url))
        w3.eth.defaultAccount = w3.eth.account.privateKeyToAccount(
            os.getenv("MAIN_ACCOUNT")
        ).address
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
        w3 = self.SetupW3()
        key = os.getenv("SECRET_KEY")
        account = w3.eth.account.create(key)
        ethereum_access = de.Enkripsi(account.privateKey)
        return account.address, ethereum_access
