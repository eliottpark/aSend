from django.contrib import admin
from .models import Task, Team, Email

admin.site.register(Task)  
admin.site.register(Team)
admin.site.register(Email)