from datetime import datetime

from django.utils import timezone
from django.shortcuts import render, redirect
import json

from web3 import Web3
from solcx import compile_standard
from tender.models import TenderFile, OpenTendering
from login.models import User
from tender.forms import OpenTenderingForm


def index(request):
    offers = []
    last_tender = OpenTendering.objects.last()
    for offer in get_offers(request, last_tender.contract_address):
        user = User.objects.filter(blockchainaccount__address=offer[0])[0].username
        file = TenderFile.objects.filter(hash=str(offer[1]))[0].offer
        submitted_date = datetime.fromtimestamp(offer[2])
        offers.append([user, file, submitted_date])
    if request.method == 'POST':
        submit_offer(request, last_tender.contract_address)
    return render(request, 'tender/index_tender.html', {'offers': offers, 'open_tender': last_tender})


def open_tendering(request):
    open_tendering_form = OpenTenderingForm()
    last_tender = OpenTendering.objects.last()
    if not last_tender:
        if last_tender.due_date > timezone.now():
            open_tendering_form.fields['name'].disabled = True
            open_tendering_form.fields['description'].disabled = True
            open_tendering_form.fields['due_date'].disabled = True
    if request.method == 'POST':
        open_tendering_form = OpenTenderingForm(data=request.POST)
        if open_tendering_form.is_valid():
            w3 = get_provider()
            w3.eth.defaultAccount = w3.eth.accounts[0]

            compiled_sol = get_compiled_tender()

            bytecode = compiled_sol['contracts']['Tender.sol']['Tender']['evm']['bytecode']['object']
            abi = json.loads(compiled_sol['contracts']['Tender.sol']['Tender']['metadata'])['output']['abi']

            tender = w3.eth.contract(abi=abi, bytecode=bytecode)

            deadline = open_tendering_form.cleaned_data['due_date']
            deadline = int(deadline.strftime('%Y%m%d%H%M%S'))

            tx_hash = tender.constructor(deadline).transact()

            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

            model = OpenTendering()
            model.name = open_tendering_form.cleaned_data['name']
            model.description = open_tendering_form.cleaned_data['description']
            model.due_date = open_tendering_form.cleaned_data['due_date']
            model.contract_address = tx_receipt.contractAddress
            model.save()

            return redirect('/tender')
    return render(request, 'tender/open_tendering.html', {'form': open_tendering_form})


def submit_offer(request, contract_address):
    file = request.FILES['file']

    tender = TenderFile()
    tender.offer = file
    tender.save()

    account = request.user
    submit_to_blockchain(tender.hash, account.blockchainaccount.address, contract_address)


def submit_to_blockchain(file_hash, address, contract_address):
    w3 = get_provider()
    w3.eth.defaultAccount = w3.eth.accounts[0]

    compiled_sol = get_compiled_tender()

    # get abi
    abi = json.loads(compiled_sol['contracts']['Tender.sol']['Tender']['metadata'])['output']['abi']

    tender = w3.eth.contract(
        address=contract_address,
        abi=abi
    )

    # print(greeter.functions.submiteOffer("probando").call())
    tx_hash = tender.functions.submitOffer(address, str(file_hash)).transact()
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(tender.functions.getSubmittedOffers().call())


def get_offers(request, contract_address):
    w3 = get_provider()
    w3.eth.defaultAccount = w3.eth.accounts[0]

    compiled_sol = get_compiled_tender()
    abi = json.loads(compiled_sol['contracts']['Tender.sol']['Tender']['metadata'])['output']['abi']

    tender = w3.eth.contract(
        address=contract_address,
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
