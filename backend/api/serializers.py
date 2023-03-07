from django.shortcuts import get_object_or_404
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from backend.recipes.models import (Recipe, Ingredient, IngredientInRecipe,
                                    Tag, Favorite, ShoppingCart)
from rest_framework.validators import UniqueTogetherValidator
from backend.users.serializers import CustomUserSerializer
from django.db import transaction


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement = serializers.ReadOnlyField(source='ingredient.measurement')

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id', 'name', 'measurement', 'amount'
        )
    validators = [
        UniqueTogetherValidator(
            queryset=IngredientInRecipe.objects.all(),
            fields=('ingredient', 'recipe')
        ),
    ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientAddSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = IngredientAddSerializer(many=True)
    image = Base64ImageField()
    is_favorite = serializers.SerializerMethodField(
        method_name='get_is_favorite')
    is_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author',
            'image', 'ingredients',
            'text', 'tag', 'cooking_time',
            'pub_date', 'is_favorite', 'is_shopping_cart'
        )

    def get_list(self, obj, model):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return model.obj.filter(user=request.user, recipe=obj).exists()

    def get_is_favorite(self, obj):
        return self.get_list(obj, Favorite)

    def get_is_shopping_cart(self, obj):
        return self.get_list(obj, ShoppingCart)


class AddRecipeSerializer(serializers.ModelSerializer):
    tag = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    ingredient = IngredientAddSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('tag', 'ingredient', 'name',
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

    def validate_tag(self, value):
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

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    @transaction.atomic
    def create_ingredient(self, ingredient, recipe):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredients=Ingredient.objects.get(id=ingredients['id']),
                recipe=recipe,
                amount=ingredients['amount']
            ) for ingredients in ingredient]
        )

    @transaction.atomic
    def create(self, validated_data):
        tag = validated_data.pop('tag')
        ingredient = validated_data.pop('ingredient')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tag.set(tag)
        recipe.save()
        self.create_ingredient(ingredient, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredient = validated_data.pop('ingredient')
        tag = validated_data.pop('tag')
        instance.ingredient.clear()
        self.create_ingredient(ingredient, instance)
        instance.tags.clear()
        instance.tags.set(tag)
        return super().update(instance, validated_data)
