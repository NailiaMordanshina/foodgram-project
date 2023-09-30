from rest_framework import routers
from django.urls import path, include


from api.views import index, UserViewSet, TagViewSet, RecipeViewSet, IngredientViewSet, UserSubscriptionViewSet

# app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)
# router.register('users/me/', CustomUserViewSet)
router.register('users/subscriptions', UserSubscriptionViewSet, basename='subscriptions')
router.register(r'users/(?P<user_id>\d+)/subscribe', UserSubscriptionViewSet, basename='subscribe')

router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)


urlpatterns = [
    path('index', index),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

