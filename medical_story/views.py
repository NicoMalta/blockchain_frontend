import json
from datetime import datetime

from django.shortcuts import render
from medical_story.models import Medicine
from django.contrib.auth.models import User

from solcx import compile_standard
from web3 import Web3


def index(request):
    # Solidity source code
    # compile_sol = compile_source_file('tender/tender.json')

    # print(greeter.functions.submiteOffer("probando").call())
    # tx_hash = events.functions.addEvent("prueba2", deadline).transact()
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    # print(events.functions.listEvents(0, 2).call())

    return render(request, 'medical/index_medical.html')


def create_medicine(request):
    medicine = request.POST.get('medicine')
    if medicine is not None:
        new_medicine = Medicine()
        new_medicine.name = medicine.name
        new_medicine.description = medicine.description
        new_medicine.category = medicine.category

        new_medicine.save()

    return render(request, 'medical/index_medical.html')


def medicine_index(request):
    medicines = Medicine.objects.all()

    return render(request, 'medical/index_medicine.html', {'medicines': medicines})


def patient_index(request):
    patients = User.objects.filter(groups__name='Patients')

    return render(request, 'medical/index_patient.html', {'patients': patients})


def history_index(request):
    submit_to_blockchain()

    w3 = get_provider()
    w3.eth.defaultAccount = w3.eth.accounts[0]

    compiled_sol = get_compiled_medical_history()

    abi = json.loads(compiled_sol['contracts']['History.sol']['HistoryMedical']['metadata'])['output']['abi']

    history = w3.eth.contract(
        address="0x9f30617b9dAA71481E9B7ECB1F26E8Cb7d1B9640",
        abi=abi
    )

    histories = history.functions.getByPatient(1).call()

    return render(request, 'medical/index_history.html', {'histories': histories})


def profile_index(request):
    return render(request, 'medical/index_profile.html')


def get_compiled_medical_history():
    return compile_standard({

        "language": "Solidity",
        "sources": {
            "History.sol": {
                "content": '''
                    pragma solidity >=0.0.0;
                    pragma experimental ABIEncoderV2;
                    
                    contract HistoryMedical {
                        
                        struct History {
                            int  patient;
                            int  doctor;
                            string  diagnostic;
                            string  place;
                            string  description;
                            string  receta;
                        }
                        
                        
                        History[] public submittedHistory;
                        mapping (int => History[]) public historyByPatient;
                    
                    
                        function submitHistory( int  patient,  int  doctor, string memory diagnostic,  string memory place, string memory description, string memory receta) public {
                            History memory history = History(patient, doctor, diagnostic, place, description, receta);    
                            
                            submittedHistory.push(history);
                            
                            History[] storage allHistory = historyByPatient[patient];
                            allHistory.push(history);
                            
                            historyByPatient[patient] = allHistory;
                        }
                        
                        
                        function getSubmittedHistory() public view returns (History[] memory) {
                            return submittedHistory;
                        }
                        
                    
                        function getByPatient(int patient) public returns (History[] memory){
                            return historyByPatient[patient];
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


def submit_to_blockchain():
    w3 = get_provider()
    w3.eth.defaultAccount = w3.eth.accounts[0]

    compiled_sol = get_compiled_medical_history()

    abi = json.loads(compiled_sol['contracts']['History.sol']['HistoryMedical']['metadata'])['output']['abi']

    history = w3.eth.contract(
        address="0x9f30617b9dAA71481E9B7ECB1F26E8Cb7d1B9640",
        abi=abi
    )

    #history.functions.submitHistory(2, 123, "probando", "probando", "probando", "probando").transact()

    #print(history.functions.getSubmittedHistory().call())

    #print(history.functions.getByPatient(1).call())

