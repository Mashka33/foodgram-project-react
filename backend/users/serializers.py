# from rest_framework import serializers
# from djoser.serializers import UserCreateSerializer, UserSerializer, PasswordSerializer, CurrentPasswordSerializer
# from .models import User, Follow
# from rest_framework.validators import UniqueTogetherValidator
# from api.serializers import RecipeShortSerializer
#
#
# class CustomUserCreateSerializer(UserCreateSerializer):
#     class Meta:
#         model = User
#         fields = tuple(User.REQUIRED_FIELDS) + (
#             User.USERNAME_FIELD,
#             'password',
#         )
#
#     def validate(self, obj):
#         if obj.get('username') == 'me':
#             raise serializers.ValidationError(
#                 'Пользователь не может иметь такое имя')
#
#         if User.objects.filter(email=obj.get('email')).exists():
#             raise serializers.ValidationError(
#                 'Пользователь с такой почтой уже существует')
#
#         if User.objects.filter(username=obj.get('username')).exists():
#             raise serializers.ValidationError(
#                 'Пользователь с таким именем уже существует')
#         return obj
#
#
# class CustomUserSerializer(UserSerializer):
#     is_follow = serializers.SerializerMethodField(
#         method_name='get_is_follow'
#     )
#
#     class Meta:
#         model = User
#         fields = (
#             'username', 'id', 'email',
#             'first_name', 'last_name', 'is_followed'
#         )
#
#     def get_is_follow(self, obj):
#         user = self.context.get('request').user
#         if user.is_anonymous:
#             return False
#         return Follow.objects.filter(user=user, athor=obj).exists()
#
#
# class FollowedSerializer(serializers.ModelSerializer):
#
#     user = serializers.SlugRelatedField(
#         read_only=True,
#         slug_field='username',
#         default=serializers.CurrentUserDefault()
#     )
#     following = serializers.SlugRelatedField(
#         slug_field='username',
#         queryset=User.objects.all()
#     )
#
#     class Meta:
#         model = Follow
#         fields = ('user', 'author')
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Follow.objects.all(),
#                 fields=('user', 'author'),
#                 message=('Вы уже подписаны на этот аккаунт')
#             ),
#         ]
#
#     def validate_following(self, value):
#         if self.context['request'].user == value:
#             raise serializers.ValidationError(
#                 'Нельзя подписываться на самого себя!'
#             )
#         return value
#
#
# class FollowSerializer(serializers.ModelSerializer):
#     email = serializers.ReadOnlyField()
#     username = serializers.ReadOnlyField()
#     first_name = serializers.ReadOnlyField()
#     last_name = serializers.ReadOnlyField()
#     is_follow = serializers.SerializerMethodField(
#         method_name='get_is_follow'
#     )
#     recipe = serializers.SerializerMethodField(method_name='get_recipe')
#     recipes_count = serializers.SerializerMethodField(
#         method_name='get_recipe_count'
#     )
#
#     class Meta:
#         model = Follow
#         fields = (
#             'email',
#             'id',
#             'username',
#             'first_name',
#             'last_name',
#             'is_subscribed',
#             'recipes',
#             'recipes_count'
#         )
#
#     def get_request(self):
#         return self.context.get('request')
#
#     def get_is_follow(self, obj):
#         return Follow.objects.filter(
#             user=self.get_request().user, author=obj.author).exists
#
#     def get_recipe(self, obj):
#         limit = self.get_request().GET.get('recipes_limit')
#         recipes = obj.recipes.all()
#         if limit:
#             recipes = recipes[:int(limit)]
#         return RecipeShortSerializer(recipes, many=True, read_only=True).data
#
#     def get_recipe_count(self, obj):
#         return obj.author.recipe.count()
#
#
# class CustomPasswordRetypeSerializer(
#     PasswordSerializer, CurrentPasswordSerializer
# ):
#     pass
