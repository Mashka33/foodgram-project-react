from django.urls import include, path

from api.views import FollowView, SubscriptionViewSet, SetPasswordRetypeView

urlpatterns = [
    path('users/subscriptions/', SubscriptionViewSet.as_view()),
    path('users/set_password/', SetPasswordRetypeView.as_view()),
    path('users/<int:pk>/subscribe/', FollowView.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
