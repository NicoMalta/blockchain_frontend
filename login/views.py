from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from web3 import Web3

from login.forms import BlockchainAccountForm
from django.shortcuts import render, redirect


def index_login(request):
    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('/')
    return render(request, 'login/login.html', {'form': form})


def logout_view(request):
    logout(request)


def registration(request):
    if request.method == 'POST':
        register_form = UserCreationForm(data=request.POST)
        address_form = BlockchainAccountForm(data=request.POST)

        if register_form.is_valid() * address_form.is_valid():
            user = register_form.save()
            blockchain_account = address_form.save(commit=False)

            account = create_blockchain_account(blockchain_account.address)
            blockchain_account.address = account
            blockchain_account.user = user

            blockchain_account.save()
            form = AuthenticationForm()
            return render(request, 'login/login.html', {'form': form})
    else:
        register_form = UserCreationForm()
        address_form = BlockchainAccountForm()
        return render(request, 'login/registration.html',
                      {'register_form': register_form, 'address_form': address_form})


def create_blockchain_account(address):
    my_provider = Web3.HTTPProvider('http://localhost:8545')
    w3 = Web3(my_provider)
    return w3.geth.personal.new_account(address)
