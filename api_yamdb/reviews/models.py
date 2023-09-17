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

    @property
    def average_rating(self):
        # Вычисляем средний рейтинг для всех отзывов этого произведения.
        # Если отзывов нет, возвращаем 0.
        return self.reviews.aggregate(models.Avg('score'))['score__avg'] or 0


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


class Review(models.Model):
    '''
    Отзыв на произведение. Отзыв привязан к определённому произведению.
    Пользователь может оставить только один отзыв на одно произведение.
    '''
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    score = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 11)])
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['title', 'user']
        ordering = ['-pub_date']


class Comment(models.Model):
    '''
    Комментарий к отзыву. Комментарий привязан к определённому отзыву.
    '''
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
