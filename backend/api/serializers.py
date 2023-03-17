from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import User, Follow


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'username', 'id', 'email',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        return (request and request.user.is_authenticated and
                author.following.filter(user=request.user).exists())


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message=('Вы уже подписаны на этот аккаунт')
            ),
        ]

    def validate_following(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return value


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(method_name='get_recipe')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipe_count'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_request(self):
        return self.context.get('request')

    def get_is_subscribed(self, obj):
        return obj.following.filter(
            user=self.get_request().user
        ).exists()

    def get_recipe(self, obj):
        limit = self.get_request().GET.get('recipes_limit')
        recipes = obj.author.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(recipes, many=True,
                                     context={'request': self.get_request()}
                                     ).data

    def get_recipe_count(self, obj):
        return obj.author.all().count()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(source='ingredient_in_recipe',
                                               read_only=True, many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author',
            'image', 'ingredients',
            'text', 'tags', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_request(self, obj, model):
        request = self.context.get('request')
        # if request is None or request.user.is_anonymous:
        #     return False
        return(request and request.user.is_authenticated
               and model.objects.filter(
                    user=request.user, recipe=obj).exists())

    def get_is_favorited(self, obj):
        return self.get_request(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_request(obj, ShoppingCart)


class AddRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def validate_ingredient(self, value):
        ingredient = value
        if not ingredient:
            raise serializers.ValidationError(
                'Заполните поле ингредиентов'
            )
        ingredients_list = []
        for item in ingredient:
            ingredients = get_object_or_404(Ingredient, id=item['id'])
            if ingredients in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться'
                )
            if int(item['amount']) <= 1:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше одного'
                )
            ingredients_list.append(ingredients)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise serializers.ValidationError(
                'Заполните поле тега'
            )
        tag_list = []
        for tag in tags:
            if tag in tag_list:
                raise serializers.ValidationError(
                    'Тег должен быть уникальным'
                )
            tag_list.append(tag)
        return value

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError(
                'Время приготовление не меньше минуты'
            )
        return data

    def to_representation(self, instance):
        return RecipeSerializer(instance).data

    @transaction.atomic
    def create_ingredients(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount'),
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        instance.tags.clear()
        instance.tags.set(tags)
        return super().update(instance, validated_data)
