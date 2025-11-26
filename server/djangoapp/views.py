from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json

from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    """Handle sign-in requests."""
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']

    user = authenticate(username=username, password=password)
    response_data = {"userName": username}
    if user is not None:
        login(request, user)
        response_data = {
            "userName": username,
            "status": "Authenticated"
        }
    return JsonResponse(response_data)


def logout_request(request):
    """Handle sign-out requests."""
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)


@csrf_exempt
def registration(request):
    """Handle sign-up requests."""
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    username_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except Exception as err:
        logger.debug("%s is new user: %s", username, err)

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
        )
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    else:
        return JsonResponse({"userName": username, "error": "Already Registered"})


def get_cars(request):
    """Return car models; populate demo data if empty."""
    count = CarMake.objects.filter().count()
    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = [
        {"CarModel": car_model.name, "CarMake": car_model.car_make.name}
        for car_model in car_models
    ]
    return JsonResponse({"CarModels": cars})


def get_dealerships(request, state="All"):
    """Return list of dealerships (optionally filtered by state)."""
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"

    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    """Return reviews for a dealer with sentiment analysis added."""
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint) or []

        for review_detail in reviews:
            review_text = review_detail['review']
            response = analyze_review_sentiments(review_text)
            sentiment = None
            if isinstance(response, dict):
                sentiment = response.get('sentiment')
            review_detail['sentiment'] = sentiment

        return JsonResponse({"status": 200, "reviews": reviews})

    return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_details(request, dealer_id):
    """Return details for a single dealer."""
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})

    return JsonResponse({"status": 400, "message": "Bad Request"})


def add_review(request):
    """Submit a review (authenticated users only)."""
    if not request.user.is_anonymous:
        data = json.loads(request.body)

        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception as err:
            logger.error(
                "Error posting review: %s", err
            )
            return JsonResponse({
                "status": 401,
                "message": "Error in posting review"
            })

    return JsonResponse({"status": 403, "message": "Unauthorized"})
