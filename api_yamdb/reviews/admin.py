from django.contrib import admin

from reviews.models import (Category, Comment, Genre,
                            GenreTitle, Review, Title, User)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
