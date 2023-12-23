from rest_framework.serializers import ModelSerializer, SerializerMethodField

from drf_extra_fields.fields import Base64ImageField

import base64

from django.core.files.base import ContentFile

from rest_framework import serializers
from users.models import User
from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient, Subscription, Favorites, ShoppingCart


class UserMeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

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
        return False


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password',
                  )

    # def get_is_subscribed(self, obj):
    #     if (self.context.get('request')
    #             and self.context['request'].user.is_authenticated):
    #         return Subscription.objects.filter(user=self.context['request'].user,
    #                                            author=obj).exists()
    #     return False

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
        extra_kwargs = {'name': {'required': True}}


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        # read_only_fields = (id,)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')
    author = UserSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

        read_only_fields = (
            'is_favorited',
            "is_in_shopping_cart",
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request:
            is_in_shopping_cart = request.query_params.get('is_in_shopping_cart', False)
            if is_in_shopping_cart:
                user = request.user if request.user.is_authenticated else None
                return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        if (self.context.get('request')
                and self.context['request'].user.is_authenticated):
            return Favorites.objects.filter(user=self.context['request'].user,
                                            recipe=obj).exists()
        return False

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

    def validate(self, data):
        image = data.get('image')
        # Проверка на пустое поле "image"
        if not image:
            raise serializers.ValidationError("Поле 'image' не может быть пустым.")

        cooking_time = data.get('cooking_time')
        # Проверка на пустое поле "cooking_time"
        if not cooking_time:
            raise serializers.ValidationError("Поле 'cooking_time' не может быть пустым.")

        tags_data = data.get('tags', [])
        # Проверка на пустое поле "tags"
        if not tags_data:
            raise serializers.ValidationError("Поле 'tags' не может быть пустым.")

        # Проверка на повторяющиеся теги
        tag_names = set()
        for tag_data in tags_data:
            tag_name = tag_data
            if tag_name in tag_names:
                raise serializers.ValidationError("Теги не могут повторяться.")
            tag_names.add(tag_name)

        ingredients_data = data.get('ingredients', [])
        # Проверка на пустое поле "ingredients"
        if not ingredients_data:
            raise serializers.ValidationError(" Поле 'ingredients' не может быть пустым.")

        # Проверка на количество ингредиентов
        if any(ingredient_data['amount'] < 1 for ingredient_data in ingredients_data):
            raise serializers.ValidationError("Количество ингредиентов должно быть больше или равно 1.")

        # Проверка на повторение ингредиентов
        ingredient_ids = set()
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['ingredient'].id
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError("Ингредиенты не могут повторяться в рецепте.")
            ingredient_ids.add(ingredient_id)
        return data

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
        recipes_limit = self.context.get('request').query_params.get('recipes_limit', None)
        recipes = obj.recipes.all()
        recipes = recipes[:int(recipes_limit)] if recipes_limit else recipes
        serializers = RecipePartialSerializer(recipes, many=True,
                                              context={'request': self.context.get('request')})
        return serializers.data

    def get_recipes_count(self, obj):
        recipes = obj.recipes.all()
        recipes_num = recipes.count()
        return recipes_num
