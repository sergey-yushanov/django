from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from catalogs.models import PumpUnit, Pump, Motor, CurvePointMixin, CurveMixin, Vfd, SoftStarter

import uuid


INSTANCE_STATE = (
	("OLD", "Существующий"),
	("NEW", "Новый"),
)

TRUE_FALSE_CHOICES = (
    (True, 'Да'),
    (False, 'Нет')
)

class PumpInstance(models.Model):
    #pump = models.ForeignKey(Pump, on_delete=models.SET_NULL, null=True, verbose_name=Pump._meta.verbose_name)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Уникальный ID для каждого насоса")
    instance_code = models.CharField("название", max_length=50, default="")
    instance_state = models.CharField("состояние", max_length=3, choices=INSTANCE_STATE, default="OLD")
    prod_date = models.DateField("производен")
    #install_date = models.DateField("установлен")
    is_impeller_mod = models.BooleanField("обточка рабочего колеса", choices=TRUE_FALSE_CHOICES, default=False)
    impeller_dia = models.FloatField("диаметр рабочего колеса, м", null=True, blank=True, validators=[MinValueValidator(0.0)])

    def __str__(self):
        return self.instance_code

    class Meta:
        verbose_name = "Экземпляр насоса"
        verbose_name_plural = "Экземпляры насосов"
        db_table = "project_pump_instance"

    def get_absolute_url(self):
        return reverse('pump-instance-detail', args=[str(self.id)])


class CurveInstance(CurveMixin):
    pump_instance = models.ForeignKey(PumpInstance, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Коэффициенты полиномов характеристик насоса"
        verbose_name_plural = "Коэффициенты полиномов характеристик насосов"
        db_table = "project_curve_instance"


class CurvePointInstance(CurvePointMixin):
    pump_instance = models.ForeignKey(PumpInstance, on_delete=models.SET_NULL, null=True, related_name="curve_points_instance_set")

    def __str__(self):
        return ''

    class Meta:
        verbose_name = "Точки характеристических кривых"
        verbose_name_plural = "Точки характеристических кривых"
        ordering = ['flow']
        db_table = "project_curve_point_instance"


class MotorInstance(models.Model):
    #motor = models.ForeignKey(Motor, on_delete=models.SET_NULL, null=True, verbose_name=Motor._meta.verbose_name)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Уникальный ID для каждого электродвигателя")
    instance_code = models.CharField("название", max_length=50, default="")
    instance_state = models.CharField("состояние", max_length=3, choices=INSTANCE_STATE, default="OLD")
    prod_date = models.DateField("производен")
    #install_date = models.DateField("установлен")
    is_wire_mod = models.BooleanField("перемотаны обмотки", choices=TRUE_FALSE_CHOICES, default=False)

    def __str__(self):
        return self.instance_code

    class Meta:
        verbose_name = "Экземпляр электродвигателя"
        verbose_name_plural = "Экземпляры электродвигателей"
        db_table = "project_motor_instance"

    def get_absolute_url(self):
        return reverse('motor-instance-detail', args=[str(self.id)])


class PumpUnitInstance(models.Model):

    CONTROL_TYPE = (
		("VFD", "Частотно-регулируемый привод"),
		("SFT", "Плавный пуск"),
		("DIR", "Прямой пуск"),
	)

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Уникальный ID для каждого насосного агрегата")
    pump_unit = models.ForeignKey(PumpUnit, on_delete=models.SET_NULL, null=True, verbose_name=PumpUnit._meta.verbose_name)
    pump_instance = models.ForeignKey(PumpInstance, on_delete=models.SET_NULL, null=True, verbose_name=PumpInstance._meta.verbose_name)
    motor_instance = models.ForeignKey(MotorInstance, on_delete=models.SET_NULL, null=True, verbose_name=MotorInstance._meta.verbose_name)
    control_type = models.CharField("управление", max_length=3, choices=CONTROL_TYPE, default="VFD")
    instance_state = models.CharField("состояние", max_length=3, choices=INSTANCE_STATE, default="OLD")
    vfd = models.ForeignKey(Vfd, on_delete=models.SET_NULL, null=True, verbose_name=Vfd._meta.verbose_name)
    soft_starter = models.ForeignKey(SoftStarter, on_delete=models.SET_NULL, null=True, verbose_name=SoftStarter._meta.verbose_name)

    class Meta:
        verbose_name = "Экземпляр насосного агрегата"
        verbose_name_plural = "Экземпляры насосных агрегатов"
        db_table = "project_pump_unit_instance"


class AddressModelMixin(models.Model):
    name = models.CharField("название", max_length=1024)
    address1 = models.CharField("адрес", max_length=1024)
    address2 = models.CharField("адрес 2", max_length=1024, blank=True, null=True)
    zip_code = models.CharField("индекс", max_length=12)
    city = models.CharField("город", max_length=1024)

    class Meta:
        abstract = True


class Object(AddressModelMixin):
    OBJECT_TYPE = (
		("ВНС", "Водопроводная насосная станция"),
		("КНС", "Канализационная насосная станция"),
		("ТС", "Насосная станция тепловой сети"),
	)
    object_code = models.CharField("краткое название", max_length=50)
    object_type = models.CharField("тип", max_length=3, choices=OBJECT_TYPE, default="ВНС")
    object_desc = models.TextField("описание", null=True, blank=True)

    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"
        db_table = "project_object"


class Scheme(models.Model):
    scheme_name = models.CharField("название", max_length=50)
    scheme_code = models.CharField("краткое название", max_length=20)
    scheme_desc = models.TextField("описание", null=True, blank=True)
    template = models.ImageField("шаблон", upload_to="schemes", null=True, blank=True)

    class Meta:
        verbose_name = "Технологическая схема"
        verbose_name_plural = "Технологические схемы"
        db_table = "project_scheme"


class SchemeInstance(models.Model):
    scheme = models.ForeignKey(Scheme, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Технологическая схема"
        verbose_name_plural = "Технологические схемы"
        db_table = "project_scheme_instance"


class SchemeItem(models.Model):

    SCHEME_ITEM_TYPE = (
        ("PU", "Насосный агрегат"),
        ("VLV", "Задвижка (клапан)"),
        ("CHK_VLV", "Обратный клапан"),
	)

    class Meta:
        verbose_name = "Элемент технологической схемы"
        verbose_name_plural = "Элементы технологической схемы"
        db_table = "project_scheme_item"
