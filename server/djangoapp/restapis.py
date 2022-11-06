import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

def get_request(url, api_key=False, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    response = None
    try:
        # Call get method of requests library with URL and parameters
        if api_key:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs,
                                        auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        # If any error occurs
        print("Network exception occurred")


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    json_obj = json_payload["review"]
    print(kwargs)
    try:
        response = requests.post(url, json=json_obj, params=kwargs)
    except:
        print("Something went wrong")
    print(response)
    return response


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            dealer_doc = dealer["docs"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    json_result = get_request(url, dealerId = dealerId)
    # Retrieve the dealer data from the response
    dealers = json_result["data"]["docs"]
    # For each dealer in the response
    for dealer in dealers:
        dealer_obj = DealerReview(name=dealer["name"], dealership=dealer["dealership"], review=dealer["review"], purchase=dealer["purchase"],
                                purchase_date=dealer["purchase_date"], car_make=dealer["car_make"],
                               car_model=dealer["car_model"],
                               car_year=dealer["car_year"], sentiment=analyze_review_sentiments(dealer["review"]), id=dealer["id"])
        results.append(dealer_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):

    url = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/37cbf468-e05f-4687-98d8-75d5a6909a66'
    version = '2021-08-01'
    authenticator = IAMAuthenticator('LqnsYlWX-aQZx0Joh_mavQb9DtIeNc3CkLScmyGPTnv_')
    nlu = NaturalLanguageUnderstandingV1(
        version=version, authenticator=authenticator)
    nlu.set_service_url(url)
    try:
        response = nlu.analyze(text=text, features=Features(
            sentiment=SentimentOptions())).get_result()
        sentiment_label = response["sentiment"]["document"]["label"]
    except:
        sentiment_label = "neutral"
    return sentiment_label


