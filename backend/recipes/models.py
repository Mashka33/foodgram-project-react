from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.template.defaultfilters import slugify

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        unique=True,
        max_length=settings.MAX_LENGTH_1,
        db_index=True,
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.MAX_LENGTH_1,
        help_text='Введите единицу измерения'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_measurement_unit')
        ]
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} --- {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        unique=True,
        max_length=settings.MAX_LENGTH_1,
        help_text='Введите тег'
    )
    color = models.CharField(
        'Цвет тега',
        unique=True,
        max_length=settings.MAX_LENGTH_2,
        help_text='Укажите цвет тега'
    )
    slug = models.SlugField(
        'Слаг тега',
        unique=True,
        max_length=settings.MAX_LENGTH_1
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Recipe(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=settings.MAX_LENGTH_1,
        help_text='Введите название рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор рецепта'
    )
    image = models.ImageField(
        'Фото блюда',
        upload_to='recipe/',
        help_text='Загрузите фото блюда'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты блюда'
    )
    text = models.TextField(
        'Описание блюда',
        help_text='Напишите ваш рецепт здесь'
    )
    tags = models.ManyToManyField(
        Tag,
        db_index=True,
        verbose_name='Тег блюда',
        related_name='recipe'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(settings.MIN_VALUE)]
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Рецепты'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_list',
        verbose_name='Ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['ingredient', 'recipe'],
            name='unique_ingredient')
        ]
        verbose_name = 'Колличество ингредиента'
        verbose_name_plural = 'Колличество ингредиентов'

    def __str__(self):
        return (f'{self.recipe.name}: '
                f'{self.ingredient.name} - '
                f'{self.amount} '
                f'{self.ingredient.measurement_unit}')


class FavoriteShopping(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Favorite(FavoriteShopping):
    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite')
        ]
        default_related_name = 'favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(FavoriteShopping):
    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping')
        ]
        default_related_name = 'shopping_cart'
        verbose_name = 'Покупки'
        verbose_name_plural = 'Покупки'
