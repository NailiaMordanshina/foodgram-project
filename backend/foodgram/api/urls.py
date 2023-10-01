from rest_framework import routers
from django.urls import path, include


from api.views import index, UserViewSet, TagViewSet, RecipeViewSet, IngredientViewSet

# app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)
# router.register('users/me/', CustomUserViewSet)
# router.register('users/subscriptions', ListSubscriptionViewSet.as_view())
# router.register(r'users/(?P<user_id>\d+)/subscribe', AddSubscriptionView.as_view())

router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    # path('users/<user_id>/subscribe', AddSubscriptionView.as_view()),
    # path('users/subscriptions', ListSubscriptionViewSet.as_view()),
    path('index', index)
]

