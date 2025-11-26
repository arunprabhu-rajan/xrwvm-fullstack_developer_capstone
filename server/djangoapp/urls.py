from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'

urlpatterns = [
    # path for registration

    # path for login/logout/register
    path('login', views.login_user, name='login'),
    path('logout', views.logout_request, name='logout'),
    path('register', views.registration, name='register'),
    path('get_cars', views.get_cars, name='getcars'),

    # dealer endpoints
    path(
        'get_dealers/',
        views.get_dealerships,
        name='get_dealers'
    ),
    path(
        'get_dealers/<str:state>',
        views.get_dealerships,
        name='get_dealers_by_state'
    ),
    path(
        'dealer/<int:dealer_id>',
        views.get_dealer_details,
        name='dealer_details'
    ),
    path(
        'reviews/dealer/<int:dealer_id>',
        views.get_dealer_reviews,
        name='dealer_details'
    ),

    # add review
    path('add_review', views.add_review, name='add_review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
