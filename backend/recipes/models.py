from django.core.validators import MaxValueValidator, MinValueValidator
from colorfield.fields import ColorField
from django.utils import timezone
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название',
    )
    color = ColorField(
        unique=True,
        verbose_name='Цветовой код',
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Slug',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        default='г',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )

    name = models.CharField(
        max_length=200,
        verbose_name='Название блюда',
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        null=True,
        default=None,
        verbose_name='Изображение блюда',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
        verbose_name='Ингредиенты для приготовления блюда',
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, 'Время приготовления не может быть меньше 1 минуты!'
            ),
            MaxValueValidator(
                180, 'Время приготовления не может быть более 3 часов!'
            )
        ],
        default=1,
        verbose_name='Время приготовления',
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                1, 'Количество ингредиентов не может быть меньше 1!'
            ),
            MaxValueValidator(
                1000, 'Количество ингредиентов не может быть больше 1000!'
            )
        ],
        default=1,
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Кол-во ингредиентов'
        verbose_name_plural = 'Кол-во ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe',
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE, related_name='favorites_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE, related_name='favorites_recipe',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorites')]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь',
        help_text='Пользователь',
        default=None
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Избранный автор',
        help_text='Избранный автор',
    )

    class Meta:
        verbose_name = 'Избранный автор'
        verbose_name_plural = 'Избранные авторы'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_subscribe'
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.author}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_user',
        verbose_name='Пользователь', help_text='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='Рецепт в списке покупок', help_text='Рецепт в списке покупок',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
