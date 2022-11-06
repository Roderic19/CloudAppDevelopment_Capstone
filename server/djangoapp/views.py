from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf
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
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = 'https://us-south.functions.appdomain.cloud/api/v1/web/49869738-0262-464d-9ade-9e7fddfc5646/dealership-package/get-review'
        context = {"reviews":  get_dealer_reviews_from_cf(url, dealer_id)}
        return HttpResponse(context["reviews"])

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/49869738-0262-464d-9ade-9e7fddfc5646/dealership-package/get-review"
        context = {
            "cars": CarModel.objects.all(),
            "dealers": get_dealer_reviews_from_cf(url, dealer_id),
        }
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == "POST":
        if request.user.is_authenticated:
            json_payload = dict()
            json_payload["name"] = request.user.username
            ## A REVOIR
            json_payload["id"] = dealer_id

            json_payload["dealership"] = dealer_id
            json_payload["review"] = request.POST["content"]
            json_payload["purchase"] = request.POST["purchasecheck"]
            if json_payload["purchase"]:
                json_payload["purchase_date"] = datetime.strptime(request.POST["purchasedate"], "%m/%d/%Y").isoformat()
                car_id = request.POST["car"]
                car = CarModel.objects.get(pk=car_id)
                json_payload["car_make"] = car.car_make.name
                json_payload["car_model"] = car.name
                json_payload["car_year"] = int(car.year.strftime("%Y"))
                json_payload["another"] == "field"
            json_payload = {"review": review}
            url = "https://us-south.functions.cloud.ibm.com/api/v1/namespaces/rod_deploy_cloud_app_djangoserver-space/actions/dealership-package/post-review"
            restapis.post_request(url, json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            return redirect("/djangoapp/login")

