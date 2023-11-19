from rest_framework.serializers import ModelSerializer, SerializerMethodField

# from drf_extra_fields.fields import Base64ImageField
import base64

from django.core.files.base import ContentFile

from rest_framework import serializers
from users.models import User
from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient, Subscription, Favorites, ShoppingCart


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password',
                  'is_subscribed',
                  )

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
                and self.context['request'].user.is_authenticated):
            return Subscription.objects.filter(user=self.context['request'].user,
                                               author=obj).exists()

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class RecipePartialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')
    author = UserSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    # image = Base64ImageField()


    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

        read_only_fields = (
            'is_favorited',
            "is_in_shopping_cart",
        )


    def get_is_in_shopping_cart(self, obj):
        if (self.context.get('request')
                and self.context['request'].user.is_authenticated):
            return ShoppingCart.objects.filter(user=self.context['request'].user,
                                            recipe=obj).exists()

    def get_is_favorited(self, obj):
        if (self.context.get('request')
                and self.context['request'].user.is_authenticated):
            return Favorites.objects.filter(user=self.context['request'].user,
                                            recipe=obj).exists()

    def get_ingredients(self, instance):
        return RecipeIngredientSerializer(
            instance.recipe_ingredients.all(),
            many=True
        ).data


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)

        for ingredient_data in ingredients:
            RecipeIngredient(
                recipe_id=instance.id,
                ingredient_id=ingredient_data['ingredient'].id,
                amount=ingredient_data['amount']
            ).save()
        return instance

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        instance.image = validated_data.get('image', instance.image)
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)

        for ingredient_data in ingredients:
            RecipeIngredient(
                recipe_id=instance.id,
                ingredient_id=ingredient_data['ingredient'].id,
                amount=ingredient_data['amount']
            ).save()
        return instance

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        serializer = RecipeSerializer(
            instance=instance,
            context=context
        )
        return serializer.data


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
                and self.context['request'].user.is_authenticated):
            return Subscription.objects.filter(user=self.context['request'].user,
                                               author=obj).exists()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        serializers = RecipePartialSerializer(recipes, many=True,
                                              context={'request': self.context.get('request')})
        return serializers.data

    def get_recipes_count(self, obj):
        recipes = obj.recipes.all()
        recipes_num = recipes.count()
        return recipes_num
