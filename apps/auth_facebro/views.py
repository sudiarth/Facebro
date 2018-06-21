import bcrypt
from django.shortcuts import render, redirect
from django.contrib import messages
from . import models as m
from . import utilities as util

def index(request):
    if 'user_id' in request.session:
        return redirect('app_facebro:timeline', user_id=request.session['user_id'])
    return render(request, 'auth_facebro/index.html')

def signup(request):

    if 'user_id' in request.session:
        return redirect('app_facebro:timeline', user_id=request.session['user_id'])

    if request.method == 'POST':

        request.session['error'] = ''

        name = request.POST['html_name']
        email = request.POST['html_email']
        password = request.POST['html_password']
        confirm = request.POST['html_confirm']

        errors = []

        errors += util.is_blank('name', name)
        errors += util.is_blank('email', email)
        errors += util.is_blank('password', password)
        errors += util.is_blank('confirm', confirm)

        if password != confirm:
            errors.append('Password doesn\'t match')
        if len(password) < 6:
            errors.append('Password too short')
        if not util.EMAIL_REGEX.match(email):
            errors.append('Email formated error')

        for error in errors:
            messages.error(request, error)

        request.session['error'] = 'signup'

        if len(errors) == 0:

            try:
                m.User.objects.get(email=email)
                messages.error(request, 'Email already exist')
            except:
                user = m.User()
                user.name = name
                user.email = email
                user.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                user.save()

                request.session['user_id'] = user.id
                request.session['name'] = user.name

                return redirect('app_facebro:index')

    return render(request, 'auth_facebro/index.html')

def signin(request):

    if 'user_id' in request.session:
        return redirect('app_facebro:timeline', user_id=request.session['user_id'])

    if request.method == 'POST':

        request.session['error'] = ''

        email = request.POST['html_email']
        password = request.POST['html_password']

        errors = []

        errors += util.is_blank('email', email)
        errors += util.is_blank('password', password)

        request.session['error'] = 'signin'

        try:
            user = m.User.objects.get(email=email)
            
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                request.session['user_id'] = user.id
                request.session['name'] = user.name
                return redirect('app_facebro:timeline', user_id=request.session['user_id'])
            else:
                messages.error(request, 'Password not match')

        except:
            messages.error(request, 'Invalid login')
    
    return render(request, 'auth_facebro/index.html')

def signout(request):
    request.session.clear()
    return redirect('auth_facebro:index')

