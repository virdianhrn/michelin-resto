from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'main/home.html')

def search(request):
    list_result = []
    list_result.append({ 'id' : 'id1' , 'name' : 'Alinea '})
    list_result.append({ 'id' : 'id2' , 'name' : 'Alinea 2'})
    query = 'expensive 3-star restaurants'
    context = {'results' : list_result, 'query' : query}
    return render(request, 'main/result.html', context=context)

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