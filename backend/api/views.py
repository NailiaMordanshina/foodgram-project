from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from django.db.models import Sum
from djoser.views import TokenCreateView

from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, generics

from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .filters import RecipeFilter

from recipes.models import Tag, Recipe, Ingredient, Subscription, Favorites, ShoppingCart, RecipeIngredient
from api.serializers import UserSerializer, TagSerializer, RecipeSerializer,\
    IngredientSerializer, RecipeCreateSerializer, UserSubscriptionSerializer, RecipePartialSerializer,\
    UserSerializer, UserMeSerializer

from users.models import User
from api.permissions import IsOwnerOrReadOnly


def index(request):
    return HttpResponse('index')


# class IsOwnerOrReadOnly(BasePermission):
#     def has_permission(self, request, view):
#         print(permissions.SAFE_METHODS)
#         return (request.method in permissions.SAFE_METHODS
#                 or request.user.is_authenticated)
#     """
#     Пользователи могут редактировать свои собственные объекты, но не могут редактировать чужие.
#     """
#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return obj.author == request.user


class CustomTokenCreateView(TokenCreateView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.status_code = 200
        return response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsOwnerOrReadOnly, )

    @action(methods=['get'], permission_classes=[IsAuthenticated],
            url_path='me', detail=False)
    def me(self, request):
        user = self.request.user
        serializer = UserMeSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)



    @action(detail=False,
            methods=['POST'])
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        if not self.request.user.check_password(current_password):
            return Response(
                {'detail': 'Неверный текущий пароль.'},
                status=status.HTTP_400_BAD_REQUEST
                )
        self.request.user.set_password(new_password)
        self.request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Подписаться, отписаться на пользователя."""
        user = request.user
        author_id = kwargs['pk']
        author_obj = get_object_or_404(User, id=author_id)
        serializer = UserSubscriptionSerializer(instance=author_obj,
                                                data=request.data,
                                                context={'request': request})
        if request.method == 'POST':
            if request.user == author_obj:
                raise serializers.ValidationError('Нельзя подписаться на самого себя.')
            subscription_exists = Subscription.objects.filter(author=author_obj, user=user).exists()
            if subscription_exists:
                return Response({'detail': 'Вы уже подписаны на этого автора.'},
                                status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, author_id=author_id)
            print("<>", serializer.is_valid(), serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription_exists = Subscription.objects.filter(author=author_obj, user=user).exists()
            if not subscription_exists:
                return Response({'detail': 'Вы не подписаны на этого автора.'},
                                status=status.HTTP_400_BAD_REQUEST)
            subscription_delete = get_object_or_404(Subscription, user=user, author_id=author_id).delete()
            if subscription_delete:
                return Response({'detail': 'Вы отписались от этого автора.'}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], permission_classes=[IsAuthenticated], detail=False)
    def subscriptions(self, request):
        subscription_data = User.objects.filter(followers__user=request.user)
        pages = self.paginate_queryset(subscription_data)
        serializer = UserSubscriptionSerializer(pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {'name': ['exact', 'startswith']}
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        print('Original queryset:', queryset)
        return queryset


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    # pagination_class = LimitOffsetPagination
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        """Добавить, удалить рецепт в избранное."""

        user = request.user
        recipe_id = kwargs.get('pk')
        if recipe_id is None:
            return Response({'detail': 'Некорректный идентификатор рецепта.'}, status=status.HTTP_400_BAD_REQUEST)
        recipe_id = kwargs['pk']
        try:
            recipe_obj = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            if request.method == 'DELETE':
                return Response({'detail': 'Рецепт не найден.'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'detail': 'Рецепт не найден.'}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            if request.user == recipe_obj.author:
                raise serializers.ValidationError('Нельзя добавить свой рецепт в избранное.')
            favorite_exists = Favorites.objects.filter(recipe=recipe_obj, user=user).exists()
            if favorite_exists:
                return Response({'detail': 'Рецепт уже в избранном.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipePartialSerializer(instance=recipe_obj)

            Favorites.objects.create(user=user, recipe_id=recipe_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite_exists = Favorites.objects.filter(recipe=recipe_obj, user=user).exists()
            if not favorite_exists:
                return Response({'detail': 'Рецепт не найден.'},
                                status=status.HTTP_400_BAD_REQUEST)
            favorite_delete = get_object_or_404(Favorites, user=user, recipe_id=recipe_id).delete()
            if favorite_delete:
                return Response({'detail': 'Рецепт удален из избранного.'}, status=status.HTTP_204_NO_CONTENT)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        from django.db import connection
        print(len(connection.queries))
        for q in connection.queries:
            return res

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        """Добавить, удалить рецепт в список покупок."""

        user = request.user
        recipe_id = kwargs.get('pk')
        if recipe_id is None:
            return Response({'detail': 'Некорректный идентификатор рецепта.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            recipe_obj = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            if request.method == 'DELETE':
                return Response({'detail': 'Рецепт не найден.'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'detail': 'Рецепт не найден.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RecipePartialSerializer(instance=recipe_obj)

        if request.method == 'POST':
            shoppingcart_exists = ShoppingCart.objects.filter(recipe=recipe_obj, user=user).exists()
            if shoppingcart_exists:
                return Response({'detail': 'Рецепт уже в списке покупок.'},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe_id=recipe_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            shoppingcart_exists = ShoppingCart.objects.filter(recipe=recipe_obj, user=user).exists()
            if not shoppingcart_exists:
                return Response({'detail': 'Рецепт не был добавлен.'},
                                status=status.HTTP_400_BAD_REQUEST)
            shoppingcart_delete = get_object_or_404(ShoppingCart, user=user, recipe_id=recipe_id).delete()
            if shoppingcart_delete:
                return Response({'detail': 'Рецепт удален из списка покупок.'}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        shopping_list = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).order_by(
                'ingredient__name'
            ).annotate(ingredient_value=Sum('amount'))
        )
        ingredient_list = f'Список покупок:\n'
        for ingredient in shopping_list:
            ingredient_list += (
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["ingredient_value"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )
        response = HttpResponse(ingredient_list, content_type='text/plain')
        return response
