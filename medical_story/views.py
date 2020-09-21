import json
from datetime import datetime

from django.shortcuts import render

# Create your views here.
from solcx import compile_standard
from web3 import Web3


def index(request):
    # Solidity source code
    # compile_sol = compile_source_file('tender/tender.json')
    compiled_sol = compile_standard({

        "language": "Solidity",
        "sources": {
            "Events.sol": {
                "content": '''
                    pragma solidity >0.0.0;
                    pragma experimental ABIEncoderV2;
                    
                    contract EventManager {
                    
                        struct Event {
                            string name;
                            uint time;
                        }
                    
                        uint totalEvents;
                    
                        mapping(uint => Event) EventList;
                    
                        event EventAdded(address indexed _senderAddress, uint _eventId);
                    
                        function addEvent(string memory _name, uint _time) public returns(uint eventId) {
                            eventId = totalEvents++;
                            EventList[eventId] = Event(_name, _time);
                            emit EventAdded(msg.sender, eventId);
                        }
                    
                        function listEvents(uint _start, uint _count) public view returns(uint[] memory eventIds, string[] memory eventNames, uint[] memory eventTimes) {
                    
                            uint maxIters = _count;
                            if( (_start+_count) > totalEvents) {
                                maxIters = totalEvents - _start;
                            }
                    
                            eventIds = new uint[](maxIters);
                            eventNames = new string[](maxIters);
                            eventTimes = new uint[](maxIters);
                    
                            for(uint i=0;i<maxIters;i++) {
                                uint eventId = _start + i;
                    
                                Event memory e = EventList[eventId];
                                eventIds[i] = eventId;
                                eventNames[i] = e.name;
                                eventTimes[i] = e.time;
                            }
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
    bytecode = compiled_sol['contracts']['Events.sol']['EventManager']['evm']['bytecode']['object']

    # get abi
    abi = json.loads(compiled_sol['contracts']['Events.sol']['EventManager']['metadata'])['output']['abi']

    Events = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Creating a datetime object so we can test.
    deadline = datetime.now()

    # Converting a to string in the desired format (YYYYMMDD) using strftime
    # and then to int.
    deadline = int(deadline.strftime('%Y%m%d'))

    # Submit the transaction that deploys the contract
    #tx_hash = Events.constructor().transact()

    # Wait for the transaction to be mined, and get the transaction receipt
    #tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    events = w3.eth.contract(
        address="0x7760580c182a2e076C362a2Ad05C084C7d12A24c",
        abi=abi
    )

    # print(greeter.functions.submiteOffer("probando").call())
   # tx_hash = events.functions.addEvent("prueba2", deadline).transact()
   # tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
   # print(events.functions.listEvents(0, 2).call())

    return render(request, 'medical/index_medical.html')
