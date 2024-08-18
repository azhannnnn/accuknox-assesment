from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-request/send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/respond/<int:pk>/', RespondToFriendRequestView.as_view(), name='respond-friend-request'),
    path('friends/', FriendListView.as_view(), name='list-friends'),
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='pending-requests'),
]
