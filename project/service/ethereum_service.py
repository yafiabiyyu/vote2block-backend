from web3 import Web3, HTTPProvider
from dotenv import load_dotenv
import os
import json

load_dotenv()

class EthereumService:
    def setup(self):
        rpc_url = os.getenv("RPC_URL")
        w3 = Web3(HTTPProvider(rpc_url))
        return w3

    def AccessContract(self):
        w3 = self.setup()
        contract_file = open('project/smart-contract/Vote2Block.json')
        data = json.load(contract_file)
        abi = data['abi']
        contract_address = os.getenv("CONTRACT_ADDRESS")
        contract = w3.eth.contract(
            address=w3.toChecksumAddress(contract_address),
            abi=abi
        )
        return contract
    
    def CreateWallet(self):
        key = os.getenv("SECRET_KEY")
        w3 = self.setup()
        account = w3.eth.account.create(key)
        return account.privateKey, account.address
    
    def AddAdminPetugas(self, admin_address, ketua_address):
        w3 = self.setup()
        contract = self.AccessContract()
        user_nonce = w3.eth.get_transaction_count(ketua_address)
        addAdmin_tx = contract.functions.addAdminPetugas(
            w3.toChecksumAddress(admin_address)
        ).buildTransaction({
            'chainId':5777,
            'gas':70000,
            'gasPrice':w3.toWei('1', 'gwei'),
            'nonce':user_nonce
        })
        print(addAdmin_tx)
        return addAdmin_tx