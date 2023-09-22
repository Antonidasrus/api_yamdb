from django.contrib import admin

from reviews import models

admin.site.register(models.Category)
admin.site.register(models.Comment)
admin.site.register(models.Genre)
admin.site.register(models.GenreTitle)
admin.site.register(models.Review)
admin.site.register(models.Title)
admin.site.register(models.User)
