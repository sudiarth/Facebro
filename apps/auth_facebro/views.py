from django.shortcuts import render, redirect
from . import models as m

# Create your views here.

def index(request):
    return render(request, 'auth_facebro/index.html')

def signup(request):

    if request.method == 'POST':

        name = request.POST['html_name']
        email = request.POST['html_email']
        password = request.POST['html_password']
        confirm = request.POST['html_confirm']

    return redirect('app_facebro:index')

def signin(request):
    return redirect('app_facebro:index')

def signout(request):
    return redirect('auth_facebro:index')