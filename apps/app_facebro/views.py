import os, uuid
from django.shortcuts import render, redirect
from django.contrib import messages

from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.db.models import Q
from django.http import HttpRequest
from apps.auth_facebro.models import User, Profile
from apps.auth_facebro import utilities as util

from . import models as m

def index(request):
    if 'user_id' in request.session:
        return redirect('app_facebro:wall', user_id=request.session['user_id'])
    
    return render(request, 'app_facebro/index.html')

def timeline(request):
    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    try:
        posts = m.Post.objects.filter(Q(following_id=request.session['user_id']) | Q(user_id=request.session['user_id'])).order_by('-created_at')
    except:
        pass

    context = {
        'user': User.objects.get(id=request.session['user_id']),
        'posts': posts
    }

    return render(request, 'app_facebro/timeline.html', context)

def wall(request, user_id):
    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    try:

        followed = []

        if 'user_id' in request.session:
            for following in m.Friend.objects.filter(Q(following_id=request.session['user_id']) | Q(user_id=request.session['user_id'])):
                followed.append(following.following_id)

        user = User.objects.get(id=user_id)
        posts = m.Post.objects.filter(Q(user_id=user_id) | Q(following_id=user_id)).order_by('-created_at')

        context = {
            'user' : user,
            'followed' : followed,
            'posts' : posts
        }

    except:

        context = {
            'user' : [],
            'followed' : [],
            'posts' : []
        }

    return render(request, 'app_facebro/wall.html', context)

def comment_post(request, post_id):
    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':

        try:
            comment = m.Comment()
            comment.content = request.POST['html_content']
            comment.post_id = post_id
            comment.user_id = request.session['user_id']
            comment.save()
        except:
            pass

    return redirect(url)

def comment_delete(request, comment_id):
    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    url = request.META.get('HTTP_REFERER')

    try:
        comment = m.Comment.objects.get(id=comment_id)
        comment.delete()
    except:
        pass

    return redirect(url)

def setting(request):
    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    user = User.objects.get(id=request.session['user_id'])
    photos = Profile.objects.filter(user_id=request.session['user_id'])

    context = {
        'user': user,
        'photos': photos
    }

    return render(request, 'app_facebro/setting.html', context)

def profile_upload(request):

    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    if request.method == 'POST' and request.FILES['file']:
        
        myfile = request.FILES['file']

        fs = FileSystemStorage()
        filename = fs.save(str(uuid.uuid4())+'.'+myfile.name.split('.')[-1], myfile)
        uploaded_file_url = fs.url(filename)

        try:
            request.session['error'] = ''

            profile = Profile()
            profile.image = uploaded_file_url
            profile.is_active = 1
            profile.user_id = request.session['user_id']
            profile.save()

            request.session['error'] = 'profile_upload'

            messages.error(request, 'Profile photo uploaded')

            return redirect('app_facebro:setting')
        except:
            messages.error(request, 'Profile upload error')

    return redirect('app_facebro:setting')

def profile_update(request):

    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    if request.method == 'POST':

        request.session['error'] = ''

        name = request.POST['html_name']
        email = request.POST['html_email']

        errors = []
        errors += util.is_blank('name', name)
        errors += util.is_blank('email', email)

        if not util.EMAIL_REGEX.match(email):
            errors.append('Email formated error')

        for error in errors:
            messages.error(request, error)

        request.session['error'] = 'profile_update'

        if len(errors) == 0:

            try:
            
                user = User.objects.get(id=request.session['user_id'])
                user.name = name
                user.email = email
                user.save()

                request.session['user_id'] = user.id
                request.session['name'] = user.name

                messages.error(request, 'Update profile success')

            except:

                messages.error(request, 'Update profile error')

    return redirect('app_facebro:setting')

def password_update(request):

    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    if request.method == 'POST':

        request.session['error'] = ''

        password = request.POST['html_password']
        confirm = request.POST['html_confirm']

        errors = []

        errors += util.is_blank('password', password)
        errors += util.is_blank('confirm', confirm)

        if password != confirm:
            errors.append('Password doesn\'t match')
        if len(password) < 6:
            errors.append('Password too short')

        for error in errors:
            messages.error(request, error)

        request.session['error'] = 'password_update'

        if len(errors) == 0:

            try:
            
                user = User.objects.get(id=request.session['user_id'])
                user.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                user.save()

                messages.error(request, 'Update profile success')

            except:

                messages.error(request, 'Update profile error')

    return redirect('app_facebro:setting')

def follower(request, user_id):

    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    user = User.objects.get(id=user_id)

    followed = []

    if 'user_id' in request.session:
        for following in m.Friend.objects.filter(user_id=request.session['user_id']):
            followed.append(following.following_id)

    try:
        context = {
            'user': user,
            'followed' : followed,
            'follower' : m.Friend.objects.filter(following_id=user_id)
        }
    except:
        
        context = {
            'user': user,
            'followed' : [],
            'follower' : []
        }

    return render(request, 'app_facebro/follower.html', context)

def following(request, user_id):

    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    user = User.objects.get(id=user_id)

    followed = []

    if 'user_id' in request.session:
        for following in m.Friend.objects.filter(user_id=request.session['user_id']):
            followed.append(following.following_id)

    try:
        context = {
            'user': user,
            'followings': m.Friend.objects.filter(user_id=user_id),
            'followed': followed
        }
    except:
        
        context = {
            'user': user,
            'followings': [],
            'followd': []
        }

    return render(request, 'app_facebro/following.html', context)

def follow(request, email):

    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    url = request.META.get('HTTP_REFERER')

    try:
        user = User.objects.get(email=email)

        friend = m.Friend()
        friend.following_id = user.id
        friend.user_id = request.session['user_id']
        friend.save()
    except:
        pass

    return redirect(url)

def unfollow(request, user_id):

    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    url = request.META.get('HTTP_REFERER')

    try:
        friend = m.Friend.objects.filter(following_id=user_id, user_id=request.session['user_id'])
        friend.delete()
    except:
        pass

    return redirect(url)

def photo(request, user_id):

    followed = []

    if 'user_id' in request.session:
        for following in m.Friend.objects.filter(Q(following_id=request.session['user_id']) | Q(user_id=request.session['user_id'])):
            followed.append(following.following_id)

    context = {
        'followed': followed,
        'user' : User.objects.get(id=user_id),
        'photos' : m.Photo.objects.filter(user_id=user_id).order_by('-created_at')
    }

    return render(request, 'app_facebro/photos.html', context)

def photo_create(request):
    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    if request.method == 'POST' and request.FILES['file']:
        
        myfile = request.FILES['file']
        caption = request.POST['caption']
        user_id = request.session['user_id']

        fs = FileSystemStorage()
        filename = fs.save(str(uuid.uuid4())+'.'+myfile.name.split('.')[-1], myfile)
        uploaded_file_url = fs.url(filename)

        try:
            photo = m.Photo()
            photo.caption = caption
            photo.src = uploaded_file_url
            photo.user_id = user_id
            photo.save()
        except:
            pass

    return redirect('app_facebro:photo', user_id=user_id)

def photo_delete(request, photo_id):
    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')
    
    try:
        photo = m.Photo.objects.get(id=photo_id)
        photo.delete()
        os.remove(settings.MEDIA_ROOT+photo.src)
    except:
        raise

    return redirect('app_facebro:photo', user_id=request.session['user_id'])

def post_create(request, user_id):
    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    if request.method == 'POST':

        request.session['error'] = ''

        try:
            
            post = m.Post()
            post.content = request.POST['html_content']
            post.user_id = request.session['user_id']
            post.following_id = user_id
            post.save()

            return redirect('app_facebro:wall', user_id=user_id)

        except:
            messages.error(request, 'Create post error')

    return redirect('app_facebro:timeline', user_id=user_id)

def post_delete(request, post_id):
    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    url = request.META.get('HTTP_REFERER')

    try:
        post = m.Post.objects.get(id=post_id)
        post.delete()
    except:
        pass

    return redirect(url)

def search(request):

    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    if request.method == 'POST':

        return redirect('app_facebro:results', query=request.POST['html_query'])

    return redirect('app_facebro:wall')

def results(request, query):

    if 'user_id' not in request.session:
        return redirect('auth_facebro:index')

    results = User.objects.filter(Q(name__icontains=query) | Q(email__icontains=query)).exclude(id=request.session['user_id']).all()
    user = User.objects.get(id=request.session['user_id'])

    followed = []

    if 'user_id' in request.session:
        for following in m.Friend.objects.filter(user_id=request.session['user_id']):
            followed.append(following.following_id)

    context = {
        'user' : user,
        'query' : query,
        'results' : results,
        'followed' : followed
    }

    return render(request, 'app_facebro/search.html', context)