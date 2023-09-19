from djoser.serializers import UserSerializer

from rest_framework import serializers
from users.models import User
from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient


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
                  'is_subcribed',
                  )

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


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
        # fields = ('id', 'name', 'color', 'slug', 'recipes')
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):

    # tags = TagSerializer(many=True)
    # tags = serializers.StringRelatedField(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')

    class Meta:

        fields = ('id', 'tags', 'ingredients', 'name', 'text', 'cooking_time')
        model = Recipe

    def create(self, validated_data):
        # Уберем список достижений из словаря validated_data и сохраним его
        # tags = self.initial_data.pop('tags')
        tags_data = validated_data.pop('tags')
        # print(tags_data);
        recipe = Recipe.objects.create(**validated_data)
        # for tag_id in tags_data:
        #     tag = Tag.objects.get(pk=tag_id)
        #     recipe.tags.add(tag_id)

        recipe.tags.set(tags_data)

        return recipe


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


# class RecipeCreateSerializer(serializers.ModelSerializer):
#     # author = UserSerializer(read_only=True)
#     tags = serializers.PrimaryKeyRelatedField(
#         queryset=Tag.objects.all(), many=True)
#     ingredients = RecipeIngredientCreateSerializer(many=True)
#
#     class Meta:
#         model = Recipe
#         fields = ('id', 'tags', 'ingredients', 'name', 'text', 'cooking_time')
#
#     def create(self, validated_data):
#         ingredients = validated_data.pop('ingredients')
#         tags = validated_data.pop('tags')
#         recipe = Recipe.objects.create(**validated_data)
#         return self.validated_data

