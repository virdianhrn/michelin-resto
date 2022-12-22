from django.shortcuts import render
import rdflib
from main.forms import QueryForm
from main.query import getDetailOfRestaurant, queryProcessor
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

# Create your views here.
def home(request):
    print(request.GET)
    form = QueryForm(request.GET or None)
    if form.is_valid() and request.method == 'GET':
        query = form.cleaned_data['query']
        return redirect('main:search', query=query)
    context={'form':form}
    return render(request, 'main/home.html', context=context)

def search(request, query):
    list_result = queryProcessor(query)
    context = {'results' : list_result, 'query' : query}
    return render(request, 'main/result.html', context=context)

def detail(request, id):
    uri = rdflib.URIRef("http://www.semanticweb.org/stern/ontologies/2022/10/michelin-restaurant#"+id)
    restaurant_detail = getDetailOfRestaurant(uri)
    context = {
        'name' : restaurant_detail.name,
        'starRating' : restaurant_detail.starRating,
        'awardedYear' : restaurant_detail.awardedYear,
        'longitude' : restaurant_detail.longitude,
        'latitude' : restaurant_detail.latitude,
        'city' : restaurant_detail.city if restaurant_detail.city != None else "N/A",
        'region' : restaurant_detail.region,
        'zipcode' : restaurant_detail.zipcode if restaurant_detail.zipcode != None else " ",
        'cuisine' : restaurant_detail.cuisine if restaurant_detail.cuisine != None else "N/A",
        'price' : restaurant_detail.priceRange if restaurant_detail.priceRange != None else "N/A",
        'url' : restaurant_detail.url,
        'wikidataLink' : str(restaurant_detail.wikidataLink) if restaurant_detail.wikidataLink != None else "N/A",
        'director' : restaurant_detail.director if restaurant_detail.director != None else "N/A",
        'directorName' : restaurant_detail.directorName if restaurant_detail.directorName != None else "N/A",
        'maxCapacity' : restaurant_detail.maxCapacity if restaurant_detail.maxCapacity != None else "N/A",
    }

    return render(request, 'main/detail.html', context=context)