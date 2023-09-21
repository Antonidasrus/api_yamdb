from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'genres', views.GenreViewSet)
router.register(r'titles', views.TitleViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', views.register, name='register'),
    path('v1/auth/token/', views.get_token, name='token')
]
