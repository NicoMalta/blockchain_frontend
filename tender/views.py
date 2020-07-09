import pprint

from django.shortcuts import render
import json

from web3 import Web3, HTTPProvider
from solcx import compile_source, compile_standard
from web3.contract import ConciseContract


def compile_source_file(file_path):
    with open(file_path, 'r') as f:
        source = f.read()

    return compile_source(source)


def deploy_contract(w3, contract_interface):
    tx_hash = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']).constructor().transact()

    address = w3.eth.getTransactionReceipt(tx_hash)['contractAddress']
    return address


# Create your views here.
def index(request):
    # Solidity source code
    # compile_sol = compile_source_file('tender/tender.json')
    compiled_sol = compile_standard({

        "language": "Solidity",
        "sources": {
            "Greeter.sol": {
                "content": '''
                     pragma solidity >0.0.0;
    
                     contract Greeter {
                       string public greeting;
    
                       constructor() public {
                           greeting = 'Hello';
                       }
    
                       function setGreeting(string memory _greeting) public {
                           greeting = _greeting;
                       }
    
                       function greet() view public returns (string memory) {
                           return greeting;
                       }
                     }
                   '''
            }
        },
        "settings":
            {
                "outputSelection": {

                    "*": {

                        "*": [
                            "metadata", "evm.bytecode"
                            , "evm.bytecode.sourceMap"
                        ]
                    }
                }
            }
    })

    # web3.py instance
    my_provider = Web3.HTTPProvider('http://localhost:8545')
    w3 = Web3(my_provider)

    # set pre-funded account as sender
    w3.eth.defaultAccount = w3.eth.accounts[0]

    # get bytecode
    bytecode = compiled_sol['contracts']['Greeter.sol']['Greeter']['evm']['bytecode']['object']

    # get abi
    abi = json.loads(compiled_sol['contracts']['Greeter.sol']['Greeter']['metadata'])['output']['abi']

    Greeter = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Submit the transaction that deploys the contract
    #  tx_hash = Greeter.constructor().transact()

    # Wait for the transaction to be mined, and get the transaction receipt
    #  tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    greeter = w3.eth.contract(
        address='0x266Ba82e0271546108C7601468F5D282842e7FaB',
        abi=abi
    )

    print(greeter.functions.greet().call())
    tx_hash = greeter.functions.setGreeting('Nihao').transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(greeter.functions.greet().call())

    return render(request, 'tender/index_tender.html')


def erase(request):
    my_provider = Web3.HTTPProvider('http://localhost:8545')
    w3 = Web3(my_provider)

    truffleFile = json.load(
        open('/Users/nmaltagliatt/Documents/blockchain/blockchain_backend/build/contracts/Tender.json'))

    abi = truffleFile['abi']
    contractAddress = "0xB64e2fEcd5c6D91a6471318c2E6AbDD8ef39c05C"
    fContract = w3.eth.contract(address=contractAddress, abi=abi)

    print(fContract.caller.submittedOffers)

# a = w3.eth.getTransaction('0xc64fe06bbb355c2b568612036906af4c33c4ce0b87e0ce235bd9f0fff81c6cd5')
# a = w3.eth.getBlock('latest')
# print(a)
