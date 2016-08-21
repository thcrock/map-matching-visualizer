from django.shortcuts import render


def index(request):
    return render(request, 'cta_dump_viewer/index.html')
