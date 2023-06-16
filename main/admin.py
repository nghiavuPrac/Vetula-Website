from django.contrib import admin
from .models import Topic, DB_Recipe,Profile


admin.site.register(DB_Recipe)
admin.site.register(Topic)
admin.site.register(Profile)