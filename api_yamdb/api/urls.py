from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'genres', views.GenreViewSet)
router.register(r'titles', views.TitleViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews',
                views.ReviewViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
                r'/comments', views.CommentViewSet, basename='comments')
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
#    path('v1/auth/signup/', views.register, name='register'),
    path('v1/auth/signup/', views.RegistrationView.as_view(), name='register'),
    path('v1/auth/token/', views.TokenView.as_view(), name='token')
]
