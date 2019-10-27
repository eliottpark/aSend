from django.contrib import admin
from .models import Task, Team, Email
from asend.models import Entry, Category

admin.site.register(Task)  
admin.site.register(Team)
admin.site.register(Email)
admin.site.register(Entry)
admin.site.register(Category)