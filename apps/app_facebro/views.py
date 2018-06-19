from django.shortcuts import render, redirect

# Create your views here.

def index(request):
    if 'user_id' in request.session:
        return render(request, 'app_facebro/timeline.html')
    
    return render(request, 'app_facebro/index.html')