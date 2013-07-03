from django.contrib import admin
from models import Material, Category, Editor, MaterialFile, Person

admin.site.register(Material)
admin.site.register(Category)
admin.site.register(Editor)
admin.site.register(Person)
admin.site.register(MaterialFile)
