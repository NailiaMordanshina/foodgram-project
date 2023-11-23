from rest_framework import routers
from django.urls import path, include

from api.views import index, UserViewSet, TagViewSet, RecipeViewSet, IngredientViewSet, CustomTokenCreateView

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/create/', CustomTokenCreateView.as_view(), name='token_create'),
    path('auth/', include('djoser.urls.authtoken')),
    path('index', index)
]
