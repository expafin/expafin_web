from django.shortcuts import render, get_object_or_404
from .models import Portfolio

# Create your views here.
def home(request):
    jobs = Portfolio.objects
    return render(request,'expafin/home.html', {'jobs': jobs})

def detail(request, port_id):
    port_detail = get_object_or_404(Portfolio, pk=port_id)
    return render(request,'expafin/detail.html', {'port_detail': port_detail})