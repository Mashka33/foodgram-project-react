from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        'Email',
        unique=True,
        blank=False,
        help_text='Введите ваш email'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор рецепта',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_followings'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='not_yourself_follow'
            ),
        ]
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} follow to {self.author}'
