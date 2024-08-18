from rest_framework import status,generics,views
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *

from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django.db.models import Q


from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from datetime import timedelta
from django.utils import timezone



class SignupView(APIView):
    serializer_class = UserSerializer
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    # Save user ID and other relevant information in session
                    request.session['user_id'] = user.id
                    request.session['user_email'] = user.email
                    request.session['user_name'] = user.name
                    
                    return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class UserPagination(PageNumberPagination):
    page_size = 10  # Number of records per page
    page_size_query_param = 'page_size'
    max_page_size = 100



class UserSearchView(generics.ListAPIView):
    serializer_class = UserSearchSerializer
    pagination_class = UserPagination
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = '__all__'

    def get_queryset(self):
        query = self.request.query_params.get('search', '')
        if not query:
            return User.objects.none()  # Return empty queryset if no query

        # Search by exact email or partial name match
        if '@' in query:
            # Search by exact email
            queryset = User.objects.filter(email__iexact=query)
        else:
            # Search by partial name match
            queryset = User.objects.filter(name__icontains=query)

        return queryset
    


class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        sender_id = request.data.get('sender')
        receiver_id = request.data.get('receiver')

        if not receiver_id:
            return Response({"error": "Receiver ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver_id = int(receiver_id)
        except ValueError:
            return Response({"error": "Invalid receiver ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the receiver user instance
        receiver = get_object_or_404(User, id=receiver_id)
        sender = get_object_or_404(User, id=sender_id)

        if sender == receiver:
            return Response({"error": "You cannot send a friend request to yourself"}, status=status.HTTP_400_BAD_REQUEST)

        # Rate limiting: check how many requests were sent in the last minute
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(sender=sender, created_at__gte=one_minute_ago).count()

        if recent_requests >= 3:
            return Response({"error": "You can only send 3 friend requests per minute"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Check if a request already exists
        if FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
            return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new friend request
        friend_request = FriendRequest(sender=sender, receiver=receiver)
        friend_request.save()
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)
    




class RespondToFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    queryset = FriendRequest.objects.all()  # Provide the queryset attribute

    def patch(self, request, *args, **kwargs):
        request_id = kwargs.get('pk')
        status_update = request.data.get('status')

        if status_update not in ['accepted', 'rejected']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the friend request instance
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)

        if friend_request.status != 'pending':
            return Response({"error": "Friend request already handled"}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = status_update
        friend_request.save()

        if status_update == 'accepted':
            # Add logic to handle accepting the request, e.g., update relationships
            pass

        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_200_OK)
    

class FriendListView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve user information from the session
        user_id = request.session.get('user_id')
        user_email = request.session.get('user_email')
        user_name = request.session.get('user_name')

        # Fetch the User instance based on user_id
        user = get_object_or_404(User, id=user_id)

        friends = FriendRequest.objects.filter(
            models.Q(sender=user, status='accepted') |
            models.Q(receiver=user, status='accepted')
        ).values_list('sender', 'receiver')

        friend_ids = {f[1] if f[0] == user.id else f[0] for f in friends}
        friend_users = User.objects.filter(id__in=friend_ids)
        serializer = UserSearchSerializer(friend_users, many=True)
        return Response(serializer.data)


class PendingFriendRequestsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure that `user_id` is being correctly retrieved from the session
        user_id = request.session.get('user_id')
        
        if not user_id:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = get_object_or_404(User, id=user_id)

        pending_requests = FriendRequest.objects.filter(receiver=user, status='pending')
        serializer = FriendRequestSerializer(pending_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
