from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'main/home.html')

def detail(request):
    context = {
        'name' : 'Alinea',
        'star' : 3,
        'year' : 2019,
        'longitude' : '-87.64798',
        'latitude' : '41.91328',
        'city' : 'Chicago',
        'region' : 'Chicago',
        'zipcode' : '60614',
        'cuisine' : 'Contemporary',
        'price' : '$$$',
        'url' : 'https://guide.michelin.com/us/en/illinois/chicago/restaurant/alinea'
    }

    return render(request, 'main/detail.html', context=context)