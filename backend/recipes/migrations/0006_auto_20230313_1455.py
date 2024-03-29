# Generated by Django 3.2.16 on 2023-03-13 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20230312_1333'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(db_index=True, related_name='recipe', to='recipes.Tag', verbose_name='Тег блюда'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(help_text='Укажите цвет тега', max_length=20, unique=True, verbose_name='Цвет тега'),
        ),
    ]
