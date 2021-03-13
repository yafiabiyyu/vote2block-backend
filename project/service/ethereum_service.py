from web3 import Web3, HTTPProvider
from dotenv import load_dotenv
import os

load_dotenv()

class EthereumService:
    def setup(self):
        rpc_url = os.getenv("RPC_URL")
        w3 = Web3(HTTPProvider(rpc_url))
        return w3
    def CreateWallet(self):
        key = os.getenv("SECRET_KEY")
        w3 = self.setup()
        account = w3.eth.account.create(key)
        return account.privateKey, account.address