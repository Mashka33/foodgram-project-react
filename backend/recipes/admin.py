from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (Favorite, Ingredient, IngredientInRecipe,
                     Recipe, ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    fields = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient')
    list_filter = ('recipe', 'ingredient')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientInRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipeInline,)
    list_display = ('pk', 'name', 'author', 'text',
                    'cooking_time', 'is_favorited',
                    'ingredients_in_recipe')
    fields = ('name', 'text',
              'author', 'image',
              'tags', 'cooking_time')
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    readonly_fields = ('is_favorited',)

    def is_favorited(self):
        return self.favorite.count()

    def ingredients_in_recipe(self, obj):
        return (', '.join([
            ingredient.name for ingredient in obj.ingredients.all()
        ]))


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name'
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name'
    )


admin.site.unregister(Group)
