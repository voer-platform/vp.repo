from django.contrib import admin
import models

class MaterialAdmin(admin.ModelAdmin):

    class Media:
        js = [
            '/s/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/s/grappelli/tinymce_setup/tinymce_setup.js',
        ]

#admin.site.register(models.Material)
admin.site.register(models.Material, MaterialAdmin)
admin.site.register(models.Category)
admin.site.register(models.Person)
admin.site.register(models.MaterialFile)
admin.site.register(models.OriginalID)
admin.site.register(models.MaterialComment)
admin.site.register(models.MaterialRating)
admin.site.register(models.MaterialViewCount)
