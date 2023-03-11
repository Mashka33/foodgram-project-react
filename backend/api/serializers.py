from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import (UserCreateSerializer, UserSerializer,
                                PasswordSerializer, CurrentPasswordSerializer)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import User, Follow


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )

    def validate(self, obj):
        if obj.get('username') == 'me':
            raise serializers.ValidationError(
                'Пользователь не может иметь такое имя')

        if User.objects.filter(email=obj.get('email')).exists():
            raise serializers.ValidationError(
                'Пользователь с такой почтой уже существует')

        if User.objects.filter(username=obj.get('username')).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует')
        return obj


class CustomUserSerializer(UserSerializer):
    is_follow = serializers.SerializerMethodField(
        method_name='get_is_follow'
    )

    class Meta:
        model = User
        fields = (
            'username', 'id', 'email',
            'first_name', 'last_name', 'is_follow'
        )

    def get_is_follow(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, athor=obj).exists()


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
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_follow = serializers.SerializerMethodField(
        method_name='get_is_follow'
    )
    recipe = serializers.SerializerMethodField(method_name='get_recipe')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipe_count'
    )

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_follow',
            'recipes',
            'recipes_count'
        )

    def get_request(self):
        return self.context.get('request')

    def get_is_follow(self, obj):
        return Follow.objects.filter(
            user=self.get_request().user, author=obj.author).exists

    def get_recipe(self, obj):
        limit = self.get_request().GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(recipes, many=True, read_only=True).data

    def get_recipe_count(self, obj):
        return obj.author.recipe.count()


class CustomPasswordRetypeSerializer(
    PasswordSerializer, CurrentPasswordSerializer
):
    pass


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id', 'name', 'amount', 'measurement_unit'
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


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tag = TagSerializer(many=True, read_only=True)
    ingredient = IngredientInRecipeSerializer(
        source='ingredient_in_recipe', many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorite')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author',
            'image', 'ingredient',
            'text', 'tag', 'cooking_time',
            'pub_date', 'is_favorited', 'is_in_shopping_cart'
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
    ingredient = IngredientInRecipeSerializer(many=True)

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

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredient = validated_data.pop('ingredient')
        tag = validated_data.pop('tag')
        instance.ingredient.clear()
        self.create_ingredient(ingredient, instance)
        instance.tags.clear()
        instance.tags.set(tag)
        return super().update(instance, validated_data)
