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
    patients = User.objects.all()

    return render(request, 'medical/index_patient.html', {'patients': patients})


def history_index(request):

    return render(request, 'medical/index_history.html')
