from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'pk', 'email',
        'first_name', 'last_name',
        'is_follow_count', 'is_recipe_count')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'

    @admin.display(description='Количество подписчиков')
    def is_follow_count(self, user):
        return user.following.count()

    @admin.display(description='Количество рецептов')
    def is_recipe_count(self, user):
        return user.recipe.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author',
    )
    empty_value_display = '-пусто-'
