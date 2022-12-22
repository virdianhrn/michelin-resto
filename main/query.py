import rdflib
from collections import namedtuple

g = rdflib.Graph()

def extractParams(query):
  query = query.lower()
  priceRange, starRating, cuisine, city, region = None, None, None, None, None

  checkForLocation = query.split(' in ', 1)
  if len(checkForLocation) > 1:
    location = checkForLocation[1]
    if 'region' in location:
      region = location.replace(' region', '').strip()
    else:
      city = location.strip()

  starRatingIdx = query.find('-star')
  if starRatingIdx != -1:
    starRating = query[starRatingIdx-1]

  keywords = {
    'very cheap' : '$',
    'very expensive' : '$$$$$',
    'cheap' : '$$',
    'affordable' : '$$$',
    'expensive' : '$$$$'
  }
  
  for keyword in keywords.keys():
    if keyword in query:
      priceRange = keywords[keyword]
      query = query.split(keyword, 1)[1]
      break
  
  query = query.split('restaurants')[0]
  if starRating != None and len(query) > 1: query = query.split('star')[1]
  cuisine = query.strip() if query.strip() else None

  return priceRange, starRating, cuisine, city, region

def getRestaurantByName(name):
  query_restaurant_by_name = """
  PREFIX ex: <http://www.semanticweb.org/stern/ontologies/2022/10/michelin-restaurant#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  SELECT DISTINCT ?restaurant ?label ?region WHERE {
      SERVICE <http://localhost:9999/bigdata/sparql> {
          ?restaurant a ex:Restaurant ;
            rdfs:label ?label ;
            ex:locatedInRegion/rdfs:label ?region ;
      }
  """
  query_restaurant_by_name += f"FILTER (lcase(?label) = '{name.lower()}')"
  query_restaurant_by_name += "}"

  qres = g.query(query_restaurant_by_name)
  
  for row in qres:
    restaurant, name, region = row
  return (restaurant, name, region)



def priceRangeFilterQuery(priceRange):
  query = f'ex:hasPriceRange/rdfs:label "{priceRange}" ;'
  return query

def starRatingFilterQuery(starRating):
  query = f'ex:hasStarRating "{starRating}"^^xsd:int ;'
  return query

def cuisineFilterQuery(cuisine):
  query = f'ex:hasCuisine/rdfs:label ?cuisine ;'
  query_filter = f"FILTER (lcase(?cuisine) = '{cuisine.lower()}')"
  return query, query_filter

def cityFilterQuery(city):
  query = f'ex:locatedInCity/rdfs:label ?city ;'
  query_filter = f"FILTER (lcase(?city) = '{city.lower()}')"
  return query, query_filter

def regionFilterQuery(region):
  query = ''
  query_filter = f"FILTER (lcase(?region) = '{region.lower()}')"
  return query, query_filter



def createQueryFromParams(params):
  priceRange, starRating, cuisine, city, region = extractParams(params)
  query = """
  PREFIX ex: <http://www.semanticweb.org/stern/ontologies/2022/10/michelin-restaurant#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  SELECT DISTINCT ?restaurant ?label ?region WHERE {
      SERVICE <http://localhost:9999/bigdata/sparql> {
          ?restaurant a ex:Restaurant ;
            rdfs:label ?label ;
            ex:locatedInRegion/rdfs:label ?region ;
  """
  filters = ''
  if priceRange is not None: query += priceRangeFilterQuery(priceRange)
  if starRating is not None: query += starRatingFilterQuery(starRating)
  if cuisine is not None: 
    cuisine_query, query_filter = cuisineFilterQuery(cuisine)
    query += cuisine_query
    filters += query_filter
  if city is not None: 
    city_query, query_filter = cityFilterQuery(city)
    query += city_query
    filters += query_filter
  if region is not None:
    region_query, query_filter = regionFilterQuery(region)
    query += region_query
    filters += query_filter

  query += '}' + filters + '}'

  return query

def getRestaurantsByParams(params):
  query_restaurants_by_param = createQueryFromParams(params)

  qres = g.query(query_restaurants_by_param)
  restaurants = []
  for row in qres:
      restaurants.append((row.restaurant, str(row.label), str(row.region)))
  return restaurants



def detailQueryBuilder(optional):
  query = """
  PREFIX ex: <http://www.semanticweb.org/stern/ontologies/2022/10/michelin-restaurant#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

  SELECT DISTINCT * WHERE {
      SERVICE <http://localhost:9999/bigdata/sparql> {
          ?restaurant a ex:Restaurant ;
  """
  query += optional + '}} LIMIT 1'
  return query

def nameOptionalQuery():
  return detailQueryBuilder('OPTIONAL {?restaurant rdfs:label ?name}')

def awardedYearOptionalQuery():
  return detailQueryBuilder('OPTIONAL {?restaurant ex:awardedYear ?year}')

def cuisineOptionalQuery():
  return detailQueryBuilder('OPTIONAL {?restaurant ex:hasCuisine/rdfs:label ?cuisine}')

def latitudeOptionalQuery():
  return detailQueryBuilder('OPTIONAL {?restaurant ex:hasLatitude ?latitude}')

def longitudeOptionalQuery():
  return detailQueryBuilder('OPTIONAL {?restaurant ex:hasLongitude ?longitude}')

def cityOptionalQuery():
  return detailQueryBuilder('OPTIONAL {?restaurant ex:locatedInCity/rdfs:label ?city}')

def regionOptionalQuery():
  return detailQueryBuilder('OPTIONAL {?restaurant ex:locatedInRegion/rdfs:label ?region}')

def starRatingOptionalQuery():
  return detailQueryBuilder('OPTIONAL {?restaurant ex:hasStarRating ?starRating}')

def urlOptionalQuery():
  return detailQueryBuilder('OPTIONAL {?restaurant ex:hasURL ?url}')

def zipCodeOptionalQuery():
  return detailQueryBuilder('OPTIONAL {?restaurant ex:hasZipCode ?zipCode}')

def priceRangeOptionalQuery():
  return detailQueryBuilder('OPTIONAL {?restaurant ex:hasPriceRange/rdfs:label ?priceRange}')

def autoconvert(s):
    for fn in (int, float, str):
        try:
            return fn(s) if s is not None else None
        except ValueError:
            pass
    return s

def extractLiteralFromQuery(query, uri):
  qres = g.query(query, initBindings={'restaurant' : uri})
  node = None
  for row in qres:
    node = row[0] if isinstance(row[0], rdflib.term.Literal) else row[-1]
  literal = autoconvert(node)
  return literal

def getDetailsFromWikidata(name):
  query_wikidata = """
  PREFIX wd: <http://www.wikidata.org/entity/>
  PREFIX wdt: <http://www.wikidata.org/prop/direct/>

  SELECT DISTINCT ?restaurant ?director ?maxCapacity ?directorName WHERE{  
    SERVICE <https://query.wikidata.org/sparql> {
      ?restaurant ?label ?restaurantName;  
        wdt:P31 wd:Q11707 .
      OPTIONAL {
        ?restaurant wdt:P1037 ?director .
        ?director rdfs:label ?directorName .
        FILTER (langMatches( lang(?directorName), "EN" ) )
      }
      OPTIONAL {
        ?restaurant wdt:P1083 ?maxCapacity
      }
    }
  }
  LIMIT 1
  """

  qres = g.query(query_wikidata, 
                initBindings={
                  'restaurantName': rdflib.Literal(name, lang='en')
                })

  restaurant, director, directorName, maxCapacity = None, None, None, None
  for row in qres:
      restaurant = row.restaurant
      director = row.director
      directorName = autoconvert(row.directorName)
      maxCapacity = autoconvert(row.maxCapacity)
  return restaurant, director, directorName, maxCapacity


def getDetailOfRestaurant(uri):
  DetailRestaurant = namedtuple("DetailRestaurant", 
    """
    name awardedYear cuisine latitude longitude city region starRating 
    url zipcode priceRange wikidataLink director directorName maxCapacity
    """
  )
  name_query = nameOptionalQuery()
  name = extractLiteralFromQuery(name_query, uri)

  awardedYear_query = awardedYearOptionalQuery()
  awardedYear = extractLiteralFromQuery(awardedYear_query, uri)

  cuisine_query = cuisineOptionalQuery()
  cuisine = extractLiteralFromQuery(cuisine_query, uri)

  latitude_query = latitudeOptionalQuery()
  latitude = extractLiteralFromQuery(latitude_query, uri)

  longitude_query = longitudeOptionalQuery()
  longitude = extractLiteralFromQuery(longitude_query, uri)

  city_query = cityOptionalQuery()
  city = extractLiteralFromQuery(city_query, uri)

  region_query = regionOptionalQuery()
  region = extractLiteralFromQuery(region_query, uri)

  starRating_query = starRatingOptionalQuery()
  starRating = extractLiteralFromQuery(starRating_query, uri)

  url_query = urlOptionalQuery()
  url = extractLiteralFromQuery(url_query, uri)

  zipCode_query = zipCodeOptionalQuery()
  zipCode = extractLiteralFromQuery(zipCode_query, uri)

  priceRange_query = priceRangeOptionalQuery()
  priceRange = extractLiteralFromQuery(priceRange_query, uri)
  
  wikidataLink, director, directorName, maxCapacity = getDetailsFromWikidata(name)

  detail = DetailRestaurant(name, awardedYear, cuisine, latitude,  
         longitude, city, region, starRating, url, zipCode, priceRange,
         wikidataLink, director, directorName, maxCapacity)

  return detail


def queryClassifier(query):
  query = query.lower()
  if 'restaurants' in query:
    return getRestaurantsByParams(query)
  else:
    return getRestaurantByName(query)


res = queryClassifier('The French Laundry')
# print(queryClassifier('NoMad'))
# res = queryClassifier('affordable 1-star french contemporary restaurants in taipei region')
# print(getDetailOfRestaurant(res[0][0]))
# print(queryClassifier('expensive contemporary restaurants in new york'))

print(getDetailOfRestaurant(res[0]))
# print(getDetailOfRestaurant('NoMad'))