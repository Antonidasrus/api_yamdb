import re

from api_yamdb.settings import Const
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User
from users.validators import validate_username, validate_email

PATTERN_USERNAME = re.compile(r'^[\w.@+-]+\Z')
PATTERN_EMAIL = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+$')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'review', 'author', 'text', 'pub_date')
        model = Comment


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class RegisterDataSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=Const.USERNAME_MAX_LENGTH,
        validators=[
            RegexValidator(PATTERN_USERNAME, 'Invalid username format.')
        ]
    )
    email = serializers.EmailField(
        max_length=Const.EMAIL_MAX_LENGTH,
        validators=[
            RegexValidator(PATTERN_EMAIL, 'Invalid email format.')
        ]
    )

    def validate_username(self, value):
        # Using the custom validator
        value = validate_username(value)

        if value.lower() == Const.USERNAME_VALIDATED:
            raise serializers.ValidationError('Username "me" is not valid')
        if len(value) > Const.USERNAME_MAX_LENGTH:
            msg = f'Max username length is {Const.USERNAME_MAX_LENGTH}.'
            raise serializers.ValidationError(msg)
        return value

    def validate_email(self, value):
        # Using the custom validator
        value = validate_email(value)

        if len(value) > Const.EMAIL_MAX_LENGTH:
            msg = f'Max email length is {Const.EMAIL_MAX_LENGTH}'
            raise serializers.ValidationError(msg)
        return value

    class Meta:
        fields = ('username', 'email')
        model = User


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method != 'POST':
            return data

        if not Review.objects.filter(title=title, author=author).exists():
            return data

        raise ValidationError('Вы не можете добавить более одного'
                              'отзыва на произведение')

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=Const.USERNAME_MAX_LENGTH,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(PATTERN_USERNAME, 'Invalid username format.')
        ],
        required=True,
    )
    email = serializers.EmailField(
        max_length=Const.EMAIL_MAX_LENGTH,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(PATTERN_EMAIL, 'Invalid email format.')
        ]
    )

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User
        read_only_fields = ('role',)
