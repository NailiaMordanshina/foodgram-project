import django_filters
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag, User, Ingredient


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'tags', 'author',
                  'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if self.request.user.is_anonymous:
            return queryset.none()
        if value:
            return queryset.filter(favorites_recipe__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if self.request.user.is_anonymous:
            return queryset.none()
        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset
