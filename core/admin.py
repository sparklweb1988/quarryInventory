from django.contrib import admin
from .models import Material, Stock, Quarry, TruckIn, TruckOut,Project, Task,Company


# Register your models here.

admin.site.register(Material)
admin.site.register(Stock)
admin.site.register(Quarry)
admin.site.register(TruckIn)
admin.site.register(TruckOut)

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Company)