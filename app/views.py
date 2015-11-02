from django.shortcuts import render
from django.core.cache import cache
import requests
from .forms import URLForm
from utils import analyze, untar


def index(request):
    form = URLForm()
    return render(request, 'index.html', {'form': form})


def result(request):
    url = request.POST.get('url')
    cached = cache.get(url)
    if cached:
        response = cached
    else:
        try:
            response = requests.get(url=url)
            cache.set(url, response)
        except:
            message = {"errorMessage": "Invalid URL"}
            return render(request, 'error.html', message)
    try:
        analyze(untar(response))
        return render(request, 'result.html')
    except RuntimeError as output:
        return render(request, 'error.html', {"errorMessage": output})
