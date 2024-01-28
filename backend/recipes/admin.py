from django.contrib import admin

from recipes.models import Tag, Recipe, Ingredient,\
    RecipeIngredient, Favorites, Subscription, ShoppingCart


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    list_display = ('author', 'name', 'recipes_in_favorites')
    search_fields = ('author', 'name', 'tags')
    list_filter = ('author', 'name', 'tags')

    def recipes_in_favorites(self, obj):
        return obj.favorites_recipe.count()

    recipes_in_favorites.short_description = 'Рецепты в избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass
