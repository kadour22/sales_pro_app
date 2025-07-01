from django.contrib import admin
from .models import SalesFile , SalesRecord , Profile

admin.site.register(SalesFile)
admin.site.register(Profile)
admin.site.register(SalesRecord)
