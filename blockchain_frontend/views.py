from django.shortcuts import render


def prehome(request):
    return render(request, 'prehome.html')
