from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated


from recipes.models import Tag, Recipe
from api.serializers import UserSerializer, TagSerializer, RecipeSerializer

from users.models import User


def index(request):
    return HttpResponse('index')


class CustomUserViewSet(UserViewSet):
    pass


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    # def get_serializer_class(self):
    #     if self.action == 'create':
    #         return RecipeCreateSerializer
    #     return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

