from django.shortcuts import render
from web3 import Web3


# Create your views here.
def index(request):
    my_provider = Web3.HTTPProvider('http://localhost:8545')
    w3 = Web3(my_provider)
    a = w3.eth.getBlock('latest')
    print(a)
    return render(request, 'tender/index_tender.html')
