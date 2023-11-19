from rest_framework import routers
from django.urls import path, include

from api.views import index, UserViewSet, TagViewSet, RecipeViewSet, IngredientViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('index', index)
]

