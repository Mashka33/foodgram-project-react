from django.urls import include, path

from api.views import FollowView, SubscriptionView


urlpatterns = [
    path('users/subscriptions/', SubscriptionView.as_view()),
    path('users/<int:pk>/subscribe/', FollowView.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
