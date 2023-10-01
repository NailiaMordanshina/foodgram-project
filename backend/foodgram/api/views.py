from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.core.exceptions import ValidationError
from rest_framework import serializers

from recipes.models import Tag, Recipe, Ingredient, Subscription
from api.serializers import UserSerializer, TagSerializer, RecipeSerializer,\
    IngredientSerializer, RecipeCreateSerializer, UserSubscriptionSerializer, SubscriptionSerializer

from users.models import User


def index(request):
    return HttpResponse('index')

#
# class CustomUserViewSet(UserViewSet):
#     pass


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['get', 'patch'], permission_classes=[IsAuthenticated],
            url_path='me', detail=False)
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True,methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Подписаться на пользователя."""
        user = request.user
        # print('1????', kwargs, request.user)
        author_id = kwargs['pk']
        # print('2????', author_id)
        author_obj = get_object_or_404(User, id=author_id)
        serializer = UserSubscriptionSerializer(instance=author_obj,
                                                data=request.data,
                                                context={'request': request})
        print('3????', serializer)
        if request.method == 'POST':
            # print('4????')
            if request.user == author_obj:
                raise serializers.ValidationError('Нельзя подписаться на самого себя.')
            if Subscription.objects.filter(author=author_obj, user=user).exists():
                raise serializers.ValidationError('Вы уже подписаны.')
            # if serializer.is_valid():

            Subscription.objects.create(user=user, author_id=author_id)
            print("<>", serializer.is_valid(), serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(Subscription, user=user, author_id=author_id)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], permission_classes=[IsAuthenticated], detail=False)
    def subscriptions(self, request):
        print('5????')
        # user = request.user
        # queryset = User.objects.filter(author__user=user)
        subscription_data = User.objects.filter(followers__user=request.user)
        pages = self.paginate_queryset(subscription_data)
        serializer = UserSubscriptionSerializer(pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)

        from django.db import connection
        print(len(connection.queries))
        for q in connection.queries:
            print('>>>>', q['sql'])

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


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def subscribe_to_author(request):
#     print("qq")
#     author_username = request.data.get('author_username')
#     author = get_object_or_404(User, username=author_username)
#
#     # Проверяем, не подписан ли уже пользователь
#     subscription_exists = Subscription.objects.filter(follower=request.user, author=author).exists()
#
#     if subscription_exists:
#         return Response({'detail': 'Вы уже подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)
#
#     subscription = Subscription(follower=request.user, author=author)
#     subscription.save()
#
#     return Response({'detail': 'Подписка успешно создана.'}, status=status.HTTP_201_CREATED)





