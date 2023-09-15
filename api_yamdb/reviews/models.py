from django.db import models


class Category(models.Model):
    '''Категории (типы) произведений: «Фильм», «Книга», «Музыка».'''
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)


class Genre(models.Model):
    '''Жанры произведений: «Детектив», «Рок», «Артхаус».'''
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)


class Title(models.Model):
    '''
    Произведения, к которым пишут отзывы (определённый фильм, книга или песня).
    Одно произведение может быть привязано:
        - только к одной категории
        - к нескольким жанрам.
    '''
    name = models.CharField(max_length=256)
    year = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, null=True,
        related_name='category')
    genre = models.ManyToManyField(
        Genre,
        related_name='genres')
