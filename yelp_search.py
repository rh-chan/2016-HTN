from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
import json

YOUR_CONSUMER_KEY = 'HDyhHceN3yjdlbc3bASndQ'
YOUR_CONSUMER_SECRET = 'Hjc0xotojyVptO1odiH47HhoYT0'
YOUR_TOKEN = 'wpkyi9lsCzmoUY6z6ycrOAJeZ-AYTXvV'
YOUR_TOKEN_SECRET = 'WGu1usC9b4vNebdeha6cGVlJmJA'

auth = Oauth1Authenticator(
    consumer_key=YOUR_CONSUMER_KEY,
    consumer_secret=YOUR_CONSUMER_SECRET,
    token=YOUR_TOKEN,
    token_secret=YOUR_TOKEN_SECRET
)

client = Client(auth)

def return_search(search_string, location):
    params1 = {
        'term': search_string,
        'location': location,
        'category_filter': 'restaurants'
    }
    response = client.search(**params1)
    businesses = response.businesses
    data = []
    for business in businesses:
        business_dict = {}
        business_dict['name'] = business.name
        business_dict['location_address'] = business.location.address
        business_dict['location_city'] = business.location.city
        business_dict['id'] = business.id
        business_dict['rating'] = business.rating
        cord = business.location.coordinate
        business_dict['cord'] = "lat:"+str(cord.latitude)+"long:"+str(cord.longitude)
        data.append(business_dict)
    json_data = json.dumps(data)
    return json_data

return_search('panino', 'waterloo')
