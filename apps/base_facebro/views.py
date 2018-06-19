from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'base_facebro/index.html')

def about(request):
    return render(request, 'base_facebro/about.html')