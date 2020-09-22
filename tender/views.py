import datetime

from django.shortcuts import render
import json
import hashlib

from web3 import Web3
from solcx import compile_source, compile_standard
from tender.models import TenderFile
from login.models import BlockchainAccount


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


def index(request):
    account = request.user

    if request.method == 'POST':
        submit_offer(request)
    return render(request, 'tender/index_tender.html')


def submit_offer(request):
    file_hash = hashlib.sha1()
    file = request.FILES['file']
    while chunk := file.read(8192):
        file_hash.update(chunk)

    tender = TenderFile()
    tender.hash = file_hash.hexdigest()
    tender.offer = file
    tender.save()


def submit_to_blockchain(file_hash, address):
    # Solidity source code
    # compile_sol = compile_source_file('tender/tender.json')
    compiled_sol = compile_standard({

        "language": "Solidity",
        "sources": {
            "Tender.sol": {
                "content": '''
                pragma solidity ^0.6.11;
                pragma experimental ABIEncoderV2;
                
                contract Tender {
                    struct Offer {
                        address bidder;
                        string offerHash;
                        uint256 timestamp;
                    }
                
                    uint public offersCount;
                    Offer[] public submittedOffers;
                    mapping (address => uint) public bidderToIndex; // to check who already submitted offers
                    uint256 public dateEnd;
                
                    event OfferSubmitted(address indexed _bidder, string _offerHash);
                
                    constructor(uint256 _dateEnd) public {
                        dateEnd = _dateEnd;
                        offersCount = 0;
                    }
                
                    function submitOffer(string memory offerHash) public {
                        require(now < dateEnd);
                
                        offersCount++;
                        bidderToIndex[msg.sender] = offersCount;
                        submittedOffers.push(Offer(msg.sender, offerHash, now));
                
                        emit OfferSubmitted(msg.sender, offerHash);
                    }
                
                    function getSubmittedOffers() public view returns (Offer[] memory) {
                        return submittedOffers;
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
    Web3.WebsocketProvider
    my_provider = Web3.HTTPProvider('http://localhost:8545')
    w3 = Web3(my_provider)

    # set pre-funded account as sender
    w3.eth.defaultAccount = address

    # get bytecode
    bytecode = compiled_sol['contracts']['Tender.sol']['Tender']['evm']['bytecode']['object']

    # get abi
    abi = json.loads(compiled_sol['contracts']['Tender.sol']['Tender']['metadata'])['output']['abi']

    Tender = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Creating a datetime object so we can test.
    deadline = datetime.datetime.now() + datetime.timedelta(days=1, hours=3)

    # Converting a to string in the desired format (YYYYMMDD) using strftime
    # and then to int.
    deadline = int(deadline.strftime('%Y%m%d%H%M%S'))

    # Submit the transaction that deploys the contract
    # tx_hash = Tender.constructor(deadline).transact()

    # Wait for the transaction to be mined, and get the transaction receipt
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    tender = w3.eth.contract(
        address="0x415CEB2d87309889971C7745DD370237c268673A",
        abi=abi
    )

    # print(greeter.functions.submiteOffer("probando").call())
    # tx_hash = tender.functions.submitOffer("tinchito").transact()
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(tender.functions.getSubmittedOffers().call())


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
