from squash.models import Project, Version, Issue
from django.contrib import admin

admin.site.register({Project, Version, Issue})
