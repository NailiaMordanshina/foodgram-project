from djoser.serializers import UserSerializer
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from rest_framework import serializers
from users.models import User
from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient, Subscription

#
# class CustomUserSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name', )


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


class RecipePartialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = "id", "name", "image", "cooking_time"
        read_only_fields = ("__all__",)


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


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')
    author = UserSerializer(read_only=True)
    # is_favorited = SerializerMethodField()
    # is_in_shopping_cart = SerializerMethodField()
    # image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'text', 'cooking_time')

        # read_only_fields = (
        #     "is_favorite",
        #     "is_shopping_cart",
        # )


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
    # tags = serializers.PrimaryKeyRelatedField(
    #     queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        print('1>>>>', validated_data)
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
        print("1<><><>", context)
        serializer = RecipeSerializer(
            instance=instance,
            context=context
        )
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):

    is_subcribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subcribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name',
                  'last_name', 'is_subcribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj: User) -> bool:
        user = self.context.get("request").user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscriptions.filter(author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
            recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return RecipePartialSerializer(recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeUserSerializer(serializers.ModelSerializer):
    print('2[][][]')
    follower = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
    )
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('follower', 'author')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['follower', 'author'],
                message='Вы уже подписаны'
            )
        ]

    # def validate(self, data):
    #     print('3[][][]', data)
    #     request = self.context['request']
    #     print('5[][][]', request.user)
    #
    #     if request.user == data['author']:
    #         raise serializers.ValidationError(
    #             'Нельзя подписаться на самого себя.')
    #     return data

    def validate(self, value):
        print('3[][][]', value)
        user_value = self.context.get('request').user.username
        print('5[][][]', user_value)
        if str(value) == str(user_value):
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return value

    def to_representation(self, instance):
        print('4[][][]')
        request = self.context.get('request')
        print("1<><><>", request)
        return SubscriptionSerializer(
            instance.author, context={'request': request}
        ).data