import re

from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import CONST
from api import serializers
from api.filters import TitlesFilter
from api.mixins import ListCreateDestroyMixin
from api.permissions import (IsAuthenticatedAdmin,
                             IsAuthenticatedAndAdminOrReadOnly,
                             IsAuthenticatedAdminModeratorOwnerOrReadOnly)

from reviews.models import Category, Genre, Review, Title, User


METHODS = ('get', 'post', 'head', 'delete', 'patch', 'options')

PATTERN_USERNAME = re.compile(r'^[\w.@+-]+\Z')
PATTERN_EMAIL = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+$')


# Представление для работы с категориями
class CategoryViewSet(ListCreateDestroyMixin):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = (IsAuthenticatedAndAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


# Представление для работы с жанрами
class GenreViewSet(ListCreateDestroyMixin):
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = (IsAuthenticatedAndAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


# Представления для работы с тайтлами
class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    ).order_by('name')
    serializer_class = serializers.TitleSerializer
    permission_classes = (IsAuthenticatedAndAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter
    http_method_names = METHODS

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return serializers.ReadOnlyTitleSerializer
        return serializers.TitleSerializer


class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        errors = {}

        if not username or not PATTERN_USERNAME.match(username):
            errors['username'] = ['Invalid username format']

        if not email or not PATTERN_EMAIL.match(email):
            errors['email'] = ['Invalid email format']
        if errors:
            return Response(errors,
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()

        if user and user.username != username:
            return Response(
                {'detail': 'Email is already in use by another user.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user and user.username == username:
            confirmation_code = default_token_generator.make_token(user)
            self.send_confirmation_email(user, confirmation_code)
            return Response({'detail': 'Confirmation code sent again.'},
                            status=status.HTTP_200_OK)

        serializer = serializers.RegisterDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = get_object_or_404(
            User, username=serializer.validated_data['username'])
        confirmation_code = default_token_generator.make_token(user)
        self.send_confirmation_email(user, confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def send_confirmation_email(self, user, confirmation_code):
        send_mail(
            subject='YaMDb registration',
            message=f'Your confirmation code: {confirmation_code}',
            from_email=CONST['FROM_EMAIL'],
            recipient_list=[user.email],
        )


class TokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = serializers.TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )

        if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
        ):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Представление для работы с пользователями
class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = METHODS

    @action(
        methods=['get', 'patch', ],
        detail=False,
        url_path='me',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=serializers.UserEditSerializer,
    )
    def users_own_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(user,
                                             data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        username = request.data.get('username')

        if email is None or username is None:
            return Response(
                {'error': 'Email and username are required fields.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not PATTERN_USERNAME.match(username):
            return Response({'username': ['Invalid username format']},
                            status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)


# Представление для работы с отзывами
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAuthenticatedAdminModeratorOwnerOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


# Представление для работы с комментариями
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    permission_classes = [IsAuthenticatedAdminModeratorOwnerOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)
