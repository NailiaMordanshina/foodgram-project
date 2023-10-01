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

    @action(methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            detail=True)
    def subscribe(self, request, **kwargs):
        """Подписаться на пользователя."""
        user = request.user
        # print('1????', kwargs, request.user)
        author_id = kwargs['pk']
        # print('2????', author_id)

        author_obj = get_object_or_404(User, id=author_id)

        serializer = SubscriptionSerializer(instance=author_obj,
                                                data=request.data,
                                                context={'request': request})
        print('3????', serializer)

        if request.method == 'POST':
            # print('4????')

            if request.user == author_obj:
                raise ValidationError('Нельзя подписаться на самого себя.')
            if Subscription.objects.filter(author=author_obj, user=user).exists():
                raise ValidationError('Вы уже подписаны.')

            # if serializer.is_valid():
            print('5????')
            Subscription.objects.create(user=user, author_id=author_id)
            print("<>", serializer.is_valid(), serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(Subscription, user=user, author_id=author_id)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # def delete_subscribe(self, request, **kwargs):
    #     """Отписать на пользователя."""
    #     user = request.user
    #     author_id = kwargs['id']
    #
    #     if get_object_or_404(
    #             Subscriptions,
    #             user=user,
    #             author_id=author_id
    #     ).delete():
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #
    #     return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], permission_classes=[IsAuthenticated], detail=False)
    def subscription(self, request):
        user = request.user
        queryset = User.objects.filter(author__user=user)
        pages = self.paginate_queryset(queryset)
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


# class ListSubscriptionViewSet(generics.ListAPIView):
#     """Вывод списка подписчиков пользователя"""
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = ListSubscriptionSerializer
#
#     def get_queryset(self):
#         return Subscription.objects.filter(user_id=self.request.user.id)
    # def post(self, request, user_id):
    #     print('111[][][]', request, user_id)
    #     author = get_object_or_404(User, id=user_id)
    #     serializer = SubscribeUserSerializer(
    #         data={'user': request.user.id, 'author': author.id}, context={'request': request}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    #
    # def delete(self, request, user_id):
    #     author = get_object_or_404(User, id=user_id)
    #     if not Subscription.objects.filter(user=request.user, author=author).exists():
    #         return Response(
    #             {'errors': 'Вы не подписаны на этого пользователя'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #
    #     Subscription.objects.get(user=request.user.id, author=user_id).delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)



# class AddSubscriptionView(views.APIView):
#     print("111")
#
#     """Добавление в подписчики"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, id):
#         print("222")
#
#         user = User.objects.filter(id=id)
#         if user.exists():
#             Subscription.objects.create(author=request.user, user=user)
#             return response.Response(status=201)
#         return response.Response(status=404)
#
#     def delete(self, request, id):
#         print("333")
#
#         try:
#             sub = Subscription.objects.get(author=request.user, user_id=id)
#         except Subscription.DoesNotExist:
#             return response.Response(status=404)
#         sub.delete()
#         return response.Response(status=204)

