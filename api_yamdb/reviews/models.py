from django.db import models
from django.contrib.auth.models import AbstractUser


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


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    ]

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        null=True,
        unique=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=ROLES,
        default=USER,
    )
    info = models.TextField(
        verbose_name='Информация',
        null=True,
        blank=True,
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR
    
    @property
    def is_admin(self):
        return self.role == self.ADMIN
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_is_not_me'
            )
        ]
