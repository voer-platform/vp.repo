from django.contrib import admin
import models

admin.site.register(models.Material)
admin.site.register(models.Category)
admin.site.register(models.Person)
admin.site.register(models.MaterialFile)
admin.site.register(models.OriginalID)
admin.site.register(models.MaterialComment)
admin.site.register(models.MaterialRating)
admin.site.register(models.MaterialViewCount)
