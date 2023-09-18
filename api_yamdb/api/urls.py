from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import get_token, register, ReviewViewSet, CommentViewSet


router = DefaultRouter()
router.register(r'reviews', ReviewViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', register, name='register'),
    path('v1/auth/token/', get_token, name='token')
]
