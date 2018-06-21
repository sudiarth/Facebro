import os, uuid
from django.shortcuts import render, redirect
from django.contrib import messages

from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.db.models import Q
from django.http import HttpRequest
from apps.auth_facebro.models import User
from . import models as m

def index(request):
    if 'user_id' in request.session:
        return redirect('app_facebro:timeline', user_id=request.session['user_id'])
    
    return render(request, 'app_facebro/index.html')

def timeline(request, user_id):
    if 'user_id' not in request.session:
        return redirect('auth_facebro:timeline', user_id=request.session['user_id'])

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
            'followed' : followed,
            'posts' : []
        }

    return render(request, 'app_facebro/timeline.html', context)

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

    context = {
        'user': user
    }

    return render(request, 'app_facebro/setting.html', context)

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
    if request.method == 'POST' and request.FILES['file']:
        
        myfile = request.FILES['file']
        caption = request.POST['caption']
        user_id = request.session['user_id']

        print(uuid.uuid4())

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

            return redirect('app_facebro:timeline', user_id=user_id)

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

    if request.method == 'POST':

        return redirect('app_facebro:results', query=request.POST['html_query'])

    return redirect('app_facebro:timeline')

def results(request, query):

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