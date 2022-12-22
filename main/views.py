from django.shortcuts import render
import rdflib
from main.query import getDetailOfRestaurant, getRestaurantByName, queryClassifier
from django.http import HttpResponseRedirect

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

def detail(request, id):
    uri = rdflib.URIRef("http://www.semanticweb.org/stern/ontologies/2022/10/michelin-restaurant#"+id)
    restaurant_detail = getDetailOfRestaurant(uri)
    context = {
        'name' : restaurant_detail.name,
        'starRating' : restaurant_detail.starRating,
        'awardedYear' : restaurant_detail.awardedYear,
        'longitude' : restaurant_detail.longitude,
        'latitude' : restaurant_detail.latitude,
        'city' : restaurant_detail.city ,
        'region' : restaurant_detail.region,
        'zipcode' : restaurant_detail.zipcode if isinstance(restaurant_detail.zipcode, int) else " ",
        'cuisine' : restaurant_detail.cuisine if restaurant_detail.cuisine != None else "N/A",
        'price' : restaurant_detail.priceRange if restaurant_detail.priceRange != None else "N/A",
        'url' : restaurant_detail.url,
        'wikidataLink' : str(restaurant_detail.wikidataLink) if restaurant_detail.wikidataLink != None else "N/A",
        'director' : restaurant_detail.director if restaurant_detail.director != None else "N/A",
        'directorName' : restaurant_detail.directorName if restaurant_detail.directorName != None else "N/A",
        'maxCapacity' : restaurant_detail.maxCapacity if restaurant_detail.maxCapacity != None else "N/A",
    }

    return render(request, 'main/detail.html', context=context)