from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from recipes.models import Tag, Recipe, Ingredient, Subscription
from api.serializers import UserSerializer, TagSerializer, RecipeSerializer,\
    IngredientSerializer, RecipeCreateSerializer, SubscriptionSerializer, SubscribeUserSerializer

from users.models import User


def index(request):
    return HttpResponse('index')

#
# class CustomUserViewSet(UserViewSet):
#     pass


class UserViewSet(ModelViewSet):
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
def subscribe_to_author(request):
    print("qq")
    author_username = request.data.get('author_username')
    author = get_object_or_404(User, username=author_username)

    # Проверяем, не подписан ли уже пользователь
    subscription_exists = Subscription.objects.filter(follower=request.user, author=author).exists()

    if subscription_exists:
        return Response({'detail': 'Вы уже подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)

    subscription = Subscription(follower=request.user, author=author)
    subscription.save()

    return Response({'detail': 'Подписка успешно создана.'}, status=status.HTTP_201_CREATED)

class UserSubscriptionViewSet(ModelViewSet):
    print('?????')
    serializer_class = SubscribeUserSerializer
    print('[][][]')

    def post(self, request, user_id):
        print('111[][][]', request, user_id)
        author = get_object_or_404(User, id=user_id)
        serializer = SubscribeUserSerializer(
            data={'user': request.user.id, 'author': author.id}, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        if not Subscription.objects.filter(user=request.user, author=author).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.get(user=request.user.id, author=user_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(methods=['get'], permission_classes=[IsAuthenticated],
    #         # url_path='subscription',
    #         detail=False)
    # def subscription(self, request):
    #     user = request.user
    #     queryset = User.objects.filter(author__user=user)
    #     pages = self.paginate_queryset(queryset)
    #     serializer = SubscriptionSerializer(pages, many=True, context={'request': request})
    #     return self.get_paginated_response(serializer.data)

# class SubscriptionViewSet(ModelViewSet):
#     # http_method_names = ['get', 'post']
#     permission_classes = [IsAuthenticated]
#     serializer_class = SubscriptionSerializer
#     # filter_backends = [filters.SearchFilter]
#     search_fields = ['user__username', 'author__username']
#
#     def get_queryset(self):
#         print("!!")
#         user = get_object_or_404(
#             User, username=self.request.user.username
#         )
#         return user.author
#
#     def perform_create(self, serializer):
#         print("!!")
#         serializer.save(user=self.request.user, author=self.request.user)

