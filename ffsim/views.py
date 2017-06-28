from django.shortcuts import render
from .python import simulator
from django.http import JsonResponse
# Create your views here.
def index(request):
    return render(request, 'ffsim/index.html')

def contact(request):
    return render(request, 'ffsim/contact.html', {'content':['If you would like to contact me, please email me at ','ejnar123@gmail.com']})

def submit_local(request):
    if request.method == "GET":
        # print(request.GET)
        # print("Results requested")
        espn_url = request.GET.get("espn-url")
        resarr = simulator.run_simulation(espn_url)
        return render(request, 'ffsim/results.html', {'results': resarr})


def simcall(request):
    if request.method == "GET":
        print("GET Request Called: " + request.GET.get("espn-url"))
        url_string = request.GET.get("espn-url")
        resarr = simulator.run_simulation(url_string)
        return JsonResponse({'results': resarr})
