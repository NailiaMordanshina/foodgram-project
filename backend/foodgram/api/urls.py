from rest_framework import routers
from django.urls import path, include


from api.views import index, UserViewSet, TagViewSet, RecipeViewSet, CustomUserViewSet

# app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)
# router.register('users/me/', CustomUserViewSet)

router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('index', index),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

