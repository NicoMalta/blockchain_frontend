import json
from datetime import datetime

from django.shortcuts import render
from medical_story.models import Medicine
from django.contrib.auth.models import User
from login.models import BlockchainAccount
from django import template
from django.contrib.auth.models import Group

from solcx import compile_standard
from web3 import Web3
from medical_story.forms import HistoryForm

register = template.Library()


def index(request):
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
    if request.method == "POST":
        form = HistoryForm(request.POST)
        if form.is_valid():
            # patient = User.objects.filter(dni=form.dni)
            # patient_account = BlockchainAccount.objects.filter(user=patient)

            doctor_account = BlockchainAccount.objects.filter(user=request.user)
            submit_to_blockchain(form['dni'].value(), 12, "doctor_account.address", form['diagnostic'].value(),
                                 form['locality'].value())

    w3 = get_provider()
    w3.eth.defaultAccount = w3.eth.accounts[0]

    compiled_sol = get_compiled_medical_history()

    abi = json.loads(compiled_sol['contracts']['History.sol']['HistoryMedical']['metadata'])['output']['abi']

    history = w3.eth.contract(
        address="0x9f30617b9dAA71481E9B7ECB1F26E8Cb7d1B9640",
        abi=abi
    )

    histories = history.functions.getByPatient(2).call()
    history_form = HistoryForm()

    return render(request, 'medical/index_history.html', {'histories': histories, 'history_form': history_form})


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
                            string  patient;
                            string  doctor;
                            string  diagnostic;
                            string  place;
                            string  description;
                            string[]  medicines;
                            string date;
                        }
                        
   
                        History[] public submittedHistory;
                        mapping (string => History[]) public historyByPatient;
                        mapping (string => History[]) public historyByDoctor;
                    
                    
                        function submitHistory(string memory patient, string memory doctor, string memory diagnostic, string memory place, string memory description, string[] memory medicines, string memory date) public {
                            History memory history = History(patient, doctor, diagnostic, place, description, medicines, date);    
                            
                            submittedHistory.push(history);
                            
                            History[] storage allHistoryByPatient = historyByPatient[patient];
                            History[] storage allHistoryByDoctor = historyByDoctor[doctor];
                        
                            allHistoryByPatient.push(history);
                            allHistoryByDoctor.push(history);
                            
                            historyByPatient[patient] = allHistoryByPatient;
                            historyByDoctor[doctor] = allHistoryByDoctor;
                        }
                        
                        
                        function getSubmittedHistory() public view returns (History[] memory) {
                            return submittedHistory;
                        }
                        
                    
                        function getByPatient(string memory patient) public returns (History[] memory){
                            return historyByPatient[patient];
                        }
                        
                        function getByDoctor(string memory doctor) public returns (History[] memory){
                            return historyByDoctor[doctor];
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


def submit_to_blockchain(dni, patient_address, doctor_address, diagnostic, locality):
    w3 = get_provider()
    w3.eth.defaultAccount = w3.eth.accounts[0]

    compiled_sol = get_compiled_medical_history()

    abi = json.loads(compiled_sol['contracts']['History.sol']['HistoryMedical']['metadata'])['output']['abi']

    history = w3.eth.contract(
        address="0x9f30617b9dAA71481E9B7ECB1F26E8Cb7d1B9640",
        abi=abi
    )

    history.functions.submitHistory(2, 2, "probando", "probando", diagnostic, locality).transact()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.filter(name=group_name)
    if group:
        group = group.first()
        return group in user.groups.all()
    else:
        return False
