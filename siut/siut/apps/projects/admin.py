from django.contrib import admin

from .models import PumpInstance, PumpUnitInstance, MotorInstance

# Register your models here.
admin.site.register(PumpUnitInstance)
admin.site.register(PumpInstance)
admin.site.register(MotorInstance)