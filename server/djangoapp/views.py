from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    print("Logging out `{}`...".format(request.user.username))
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        password = request.POST['psw']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            user.is_superuser = True
            user.is_staff=True
            user.save()  
            login(request, user)
            return redirect("djangoapp:index")
        else:
            messages.warning(request, "The user already exists.")
            return redirect("djangoapp:registration")

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/rod_deploy_cloud_app_djangoserver-space/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context = {"dealership_list": dealerships}
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = 'https://us-south.functions.appdomain.cloud/api/v1/web/rod_deploy_cloud_app_djangoserver-space/dealership-package/get-review'
        dealer_reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context = {
            "reviews":  dealer_reviews, 
            "dealer_id": dealer_id
        }

        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/rod_deploy_cloud_app_djangoserver-space/dealership-package/get-dealership?id={0}".format(dealer_id)
        #url = "https://us-south.functions.appdomain.cloud/api/v1/web/rod_deploy_cloud_app_djangoserver-space/dealership-package/get-dealership"
        context = {
            "cars": CarModel.objects.filter(dealer_id=dealer_id),
            "dealer": get_dealers_from_cf(url)[0],
        }
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == "POST":
        if request.user.is_authenticated:
            json_payload = dict()
            json_payload["id"] = 1454
            json_payload["name"] = request.user.username
            json_payload["dealership"] = dealer_id
            json_payload["review"] = request.POST["content"]
            json_payload["another"] = "field"
            if ("purchasecheck" in request.POST) and (request.POST["purchasecheck"] == "on"):
                
                json_payload["purchase"] = True
                json_payload["purchase_date"] = request.POST["purchasedate"]
                car_id = request.POST["car"]
                car = CarModel.objects.get(pk=car_id)
                json_payload["car_make"] = car.car_make.name
                json_payload["car_model"] = car.name
                json_payload["car_year"] = int(car.year.strftime("%Y"))
            else:
                json_payload["purchase"] = False
                json_payload["purchase_date"] = "01/01/0000"
                car_id = 0
                json_payload["car_make"] = "None"
                json_payload["car_model"] = "None"
                json_payload["car_year"] = 0000
            json_payload = {"review": json_payload}
            url = "https://us-south.functions.appdomain.cloud/api/v1/web/rod_deploy_cloud_app_djangoserver-space/dealership-package/post-review"
            post_request(url, json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            return redirect("/djangoapp/login")

