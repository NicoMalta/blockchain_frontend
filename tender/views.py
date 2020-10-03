from datetime import datetime

from django.shortcuts import render
import json
import hashlib

from web3 import Web3
from solcx import compile_source, compile_standard
from tender.models import TenderFile
from login.models import User


def index(request):
    offers = []
    for offer in get_offers(request):
        user = User.objects.filter(blockchainaccount__address=offer[0])[0].username
        file = TenderFile.objects.filter(hash=offer[1])[0].offer
        submitted_date = datetime.fromtimestamp(offer[2])
        offers.append([user, file, submitted_date])
    if request.method == 'POST':
        submit_offer(request)
    return render(request, 'tender/index_tender.html', {'offers': offers})


def open_tendering(request):
    return render(request, 'tender/open_tendering.html')


def submit_offer(request):
    file_hash = hashlib.sha1()
    file = request.FILES['file']

    tender = TenderFile()
    tender.hash = file_hash.hexdigest()
    tender.offer = file
    tender.save()

    account = request.user
    submit_to_blockchain(tender.hash, account.blockchainaccount.address)


def submit_to_blockchain(file_hash, address):
    w3 = get_provider()
    w3.eth.defaultAccount = w3.eth.accounts[0]

    compiled_sol = get_compiled_tender()

    # get abi
    abi = json.loads(compiled_sol['contracts']['Tender.sol']['Tender']['metadata'])['output']['abi']

    # Tender = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Creating a datetime object so we can test.
    # deadline = datetime.datetime.now() + datetime.timedelta(days=1, hours=3)

    # Converting a to string in the desired format (YYYYMMDD) using strftime
    # and then to int.
    # deadline = int(deadline.strftime('%Y%m%d%H%M%S'))

    # Submit the transaction that deploys the contract
    # tx_hash = Tender.constructor(deadline).transact()

    # Wait for the transaction to be mined, and get the transaction receipt
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    tender = w3.eth.contract(
        address="0x2644f95f8D779d44f90668c586FbF51827A5d1fa",
        abi=abi
    )

    # print(greeter.functions.submiteOffer("probando").call())
    tx_hash = tender.functions.submitOffer(address, file_hash).transact()
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(tender.functions.getSubmittedOffers().call())


def get_offers(request):
    w3 = get_provider()
    w3.eth.defaultAccount = w3.eth.accounts[0]

    compiled_sol = get_compiled_tender()
    abi = json.loads(compiled_sol['contracts']['Tender.sol']['Tender']['metadata'])['output']['abi']

    tender = w3.eth.contract(
        address="0x2644f95f8D779d44f90668c586FbF51827A5d1fa",
        abi=abi
    )

    return tender.functions.getSubmittedOffers().call()


def get_compiled_tender():
    return compile_standard({

        "language": "Solidity",
        "sources": {
            "Tender.sol": {
                "content": '''
                    pragma solidity >=0.0.0;
                    pragma experimental ABIEncoderV2;

                    contract Tender {
                        struct Offer {
                            string bidder;
                            string offerHash;
                            uint256 timestamp;
                        }

                        uint public offersCount;
                        Offer[] public submittedOffers;
                        mapping (string => uint) public bidderToIndex; // to check who already submitted offers
                        uint256 public dateEnd;

                        event OfferSubmitted(string indexed _bidder, string _offerHash);

                        constructor(uint256 _dateEnd) public {
                            dateEnd = _dateEnd;
                            offersCount = 0;
                        }

                        function submitOffer(string memory bidder, string memory offerHash) public {
                            require(now < dateEnd);

                            offersCount++;
                            bidderToIndex[bidder] = offersCount;
                            submittedOffers.push(Offer(bidder, offerHash, now));

                            emit OfferSubmitted(bidder, offerHash);
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


def get_provider():
    my_provider = Web3.HTTPProvider('http://localhost:8545')
    return Web3(my_provider)
