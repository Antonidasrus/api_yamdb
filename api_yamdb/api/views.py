from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.serializers import RegisterDataSerializer, TokenSerializer

from rest_framework import viewsets

from api.serializers import (ReviewSerializer, CommentSerializer)
from reviews.models import User, Review, Comment


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterDataSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = get_object_or_404(User,
                             username=serializer.validated_data['username'])
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='YaMDb registration',
        message=f'Your confirmation code: {confirmation_code}',
        from_email=None,
        recipient_list=[user.email],
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User,
                             username=serializer.validated_data['username'])

    if default_token_generator.check_token(
        user, serializer.validated_data['confirmation_code']
    ):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Пользовательский класс разрешений, который проверяет, является ли пользователь автором объекта
# или модератором. Если это так, разрешается редактирование объекта.


class IsAuthorOrModeratorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Если метод запроса безопасен (например, GET), разрешить доступ
        if request.method in permissions.SAFE_METHODS:
            return True
        # Если пользователь автор объекта или модератор, разрешить доступ
        return obj.user == request.user or request.user.role == User.MODERATOR


# Представление для работы с отзывами
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrModeratorOrReadOnly]

    # Переопределение метода создания, чтобы автоматически присваивать пользователя
    # из текущего запроса как автора отзыва
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Представление для работы с комментариями
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrModeratorOrReadOnly]

    # Подобно предыдущему, автоматическое присваивание пользователя как автора комментария
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
