from django.contrib import admin

from .models import Motor, Pump, Manufacturer, MotorCircuit, CurvePoint, PumpUnit
#from .forms import MotorCircuitForm

#admin.site.register(PumpType)
#admin.site.register(PumpAccuracy)


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('manufacturer_name', 'manufacturer_code', 'manufacturer_url', 'manufacturer_country')

admin.site.register(Manufacturer, ManufacturerAdmin)


class PumpUnitAdmin(admin.ModelAdmin):
    list_display = ('pump_unit_code', 'manufacturer', 'pump', 'motor')

admin.site.register(PumpUnit, PumpUnitAdmin)


# Pump
class CurvePointInline(admin.TabularInline):
    model = CurvePoint
    extra = 0


@admin.register(Pump)
class PumpAdmin(admin.ModelAdmin):
    list_display = ('pump_code', 'manufacturer', 'pump_type', 'eff_bep', 'flow_bep', 'head_max')
    list_filter = ('manufacturer', 'pump_type')
    fieldsets = (
        (None, {
            'fields': ('pump_code', 'manufacturer','pump_type', 'ip_code')
        }),
        ('Габариты, масса', {
            'fields': ('length', 'width', 'height', 'weight')
        }),
    )
    inlines = [
        CurvePointInline,
    ]

#admin.site.register(Motor)
class MotorCircuitInline(admin.TabularInline):
    model = MotorCircuit
    extra = 0


@admin.register(Motor)
class MotorAdmin(admin.ModelAdmin):
    list_display = ('motor_code', 'manufacturer', 'motor_type', 'eff_class', 'eff_100')
    list_filter = ('manufacturer', 'motor_type', 'eff_class')
    fieldsets = (
        (None, {
            'fields': ('motor_code', 'manufacturer','motor_type', 'duty_type', 'ip_code', 'insulation_class')
        }),
        ('Характеристики эффективности', {
            'fields': ('eff_class', 'eff_100', 'eff_75', 'eff_50')
        }),
        ('Габариты, масса', {
            'fields': ('length', 'width', 'height', 'weight')
        }),
    )
    inlines = [
        MotorCircuitInline,
    ]



#admin.site.register(MotorCircuit)

#admin.site.register(Drive)


#class MotorCircuitAdmin(admin.ModelAdmin):
    #form = MotorCircuitForm

#admin.site.register(Curve)
