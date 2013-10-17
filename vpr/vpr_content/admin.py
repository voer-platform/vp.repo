from django.contrib import admin
from models import Material, Category, MaterialFile, Person, OriginalID

admin.site.register(Material)
admin.site.register(Category)
admin.site.register(Person)
admin.site.register(MaterialFile)
admin.site.register(OriginalID)
