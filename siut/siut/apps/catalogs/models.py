from django.db import models
from django_countries.fields import CountryField

from django.core.validators import MaxValueValidator, MinValueValidator

from django.utils.translation import gettext_lazy as _
#from model_utils import Choices



IP_CODE_CHOICES = (
    ("IP20", "IP20"),
    ("IP23", "IP23"),
    ("IP54", "IP54"),
    ("IP55", "IP55"),
    ("IP65", "IP65"),
    ("IP68", "IP68"),
)

class DimMassModelMixin(models.Model):
    length = models.FloatField("длина, м", null=True, blank=True, validators=[MinValueValidator(0.0)])
    width = models.FloatField("ширина, м", null=True, blank=True, validators=[MinValueValidator(0.0)])
    height = models.FloatField("высота, м", null=True, blank=True, validators=[MinValueValidator(0.0)])
    weight = models.FloatField("масса, кг", null=True, blank=True, validators=[MinValueValidator(0.0)])

    class Meta:
        abstract = True


class Manufacturer(models.Model):
    manufacturer_name = models.CharField("название", max_length=50)
    manufacturer_code = models.CharField("краткое название", max_length=20)
    manufacturer_desc = models.TextField("описание", null=True, blank=True)
    manufacturer_logo = models.ImageField("лого", upload_to="logos", null=True, blank=True)
    manufacturer_url = models.URLField("сайт", null=True, blank=True)
    manufacturer_country = CountryField("страна", null=True, blank=True)

    def __str__(self):
        return self.manufacturer_code

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"
        ordering = ['manufacturer_code']
        db_table = "catalog_manufacturer"

    def get_absolute_url(self):
        return reverse('manufacturer-detail', args=[str(self.id)])


class Pump(DimMassModelMixin):
    
    class PumpType(models.TextChoices):
        CENTRIFUGAL = "CEN", _("Центробежный")
        IMPELLER = "IMP", _("Импеллерный (ламельный)")
        LAMELLAR = "LAM", _("Пластинчатый (шиберный)")
        WATER_RING = "WAT", _("Водокольцевой")
        GEAR = "GEA", _("Шестерённый")
        AXIAL_PLUNGER = "AXI", _("Аксиально-плунжерный")
        RADIAL_PLUNGER = "RAD", _("Радиально-плунжерный")
        DISK = "DIS", _("Центробежно-шнековый (дисковый, оседиагональный)")
        SCREW = "SCR", _("Винтовой (шнековый)")
        PISTON = "PIS", _("Поршневой")
        VORTEX = "VOR", _("Вихревой")
        ROTARY = "ROT", _("Роторный")
        JET = "JET", _("Струйный")
        SINUSOIDAL = "SIN", _("Синусоидальный")
        PERISTALTIC = "PER", _("Перистальтический")
        MEMBRANE = "MEM", _("Мембранный")
        ABSORPTION = "ABS", _("Абсорбционный")
        HYDRAULIC_RAM = "HYD", _("Гидротаранный")
        MAGNETIC_DISCHARGE = "MAG", _("Магниторазрядный")

    PUMP_ACCURACY = (
		("1B", "1B"),
        ("1E", "1E"),
        ("1U", "1U"),
        ("2B", "2B"),
        ("2U", "2U"),
        ("3B", "3B"),
	)

    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=Manufacturer._meta.verbose_name)
    pump_accuracy = models.CharField("класс точности", max_length=2, choices=PUMP_ACCURACY, null=True, blank=True, default="2B")
    pump_type = models.CharField("тип", max_length=3, choices=PumpType.choices, default=PumpType.CENTRIFUGAL)
    pump_name = models.CharField("название", max_length=100)
    pump_code = models.CharField("артикул", max_length=50)
    flow_min = models.FloatField("производительность (мин.), м3/ч", null=True, blank=True, validators=[MinValueValidator(0.0)])
    flow_max = models.FloatField("производительность (макс.), м3/ч", null=True, blank=True, validators=[MinValueValidator(0.0)])
    eff_bep = models.FloatField("КПД (макс.), %", null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(100)])
    flow_bep = models.FloatField("производительность (макс. КПД), м3/ч", null=True, blank=True, validators=[MinValueValidator(0.0)])
    temp_max = models.PositiveSmallIntegerField("температура (макс.), \xb0C", null=True, blank=True, validators=[MinValueValidator(0.0)])
    head_max = models.FloatField("напор (макс.), м", null=True, blank=True, validators=[MinValueValidator(0.0)])
    rpm = models.PositiveSmallIntegerField("об/мин", null=True, blank=True)
    impeller_dia = models.FloatField("диаметр рабочего колеса, м", null=True, blank=True, validators=[MinValueValidator(0.0)])
    ip_code = models.CharField("степень защиты IP", max_length=4, choices=IP_CODE_CHOICES, default="IP20")

    def __str__(self):
        return self.pump_code

    class Meta:
        verbose_name = "Насос"
        verbose_name_plural = "Насосы"
        db_table = "catalog_pump"

    def get_absolute_url(self):
        return reverse('pump-detail', args=[str(self.id)])


class CurveMixin(models.Model):

    CURVE_TYPE = (
        ("HQ", "Напорно-расходная характеристика"),
        ("PQ", "Характеристика мощности"),
        ("EQ", "Характеристика КПД"),
	)

    curve_type = models.CharField("тип кривой", max_length=2, choices=CURVE_TYPE, default="HQ")
    p0 = models.FloatField(null=True, blank=True)
    p1 = models.FloatField(null=True, blank=True)
    p2 = models.FloatField(null=True, blank=True)
    p3 = models.FloatField(null=True, blank=True)
    p4 = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.curve_type.__str__

    class Meta:
        abstract = True


class Curve(CurveMixin):
    pump = models.ForeignKey(Pump, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Коэффициенты полиномов характеристик насоса"
        verbose_name_plural = "Коэффициенты полиномов характеристик насосов"
        db_table = "catalog_curve"


class CurvePointMixin(models.Model):
    flow = models.FloatField("расход, м3/ч", null=True, blank=True, validators=[MinValueValidator(0.0)])
    head = models.FloatField("напор, м", null=True, blank=True, validators=[MinValueValidator(0.0)])
    power = models.FloatField("мощность, кВт", null=True, blank=True, validators=[MinValueValidator(0.0)])
    eff = models.FloatField("КПД, %", null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    class Meta:
        abstract = True


class CurvePoint(CurvePointMixin):
    pump = models.ForeignKey(Pump, on_delete=models.SET_NULL, null=True, related_name="curve_points_set")

    def __str__(self):
        return ''

    class Meta:
        verbose_name = "Точки характеристических кривых"
        verbose_name_plural = "Точки характеристических кривых"
        ordering = ['flow']
        db_table = "catalog_curve_point"


class Motor(DimMassModelMixin):

    MOTOR_TYPE = (
        ("AS", "Асинхронный"),
        ("SY", "Синхронный"),
        ("LI", "Линейный"),
        ("ST", "Шаговый"),
        ("SE", "Серводвигатель"),
    )

    MOTOR_EFF_CLASS = (
        ("IE1", "IE1 - Стандартный класс"),
        ("IE2", "IE2 - Высокий класс"),
        ("IE3", "IE3 - Сверхвысокий класс"),
        ("IE4", "IE4 - Максимально высокий класс"),
	)

    MOTOR_INSULATION_CLASS = (
        ("A", "A (105 \xb0C)"),
        ("E", "E (120 \xb0C)"),
        ("B", "B (130 \xb0C)"),
        ("F", "F (155 \xb0C)"),
        ("H", "H (180 \xb0C)"),
	)

    MOTOR_DUTY_TYPE = (
        ("S1", "S1 - Продолжительный режим"),
        ("S2", "S2 - Кратковременный режим"),
        ("S3", "S3 - Повторно-кратковременный режим"),
        ("S4", "S4 - Повторно-кратковременный режим с влиянием пусковых процессов"),
        ("S5", "S5 - Повторно-кратковременный режим с электрическим торможением"),
        ("S6", "S6 - Перемежающийся режим"),
        ("S7", "S7 - Перемежающийся режим с электрическим торможением и влиянием пусковых процессов"),
        ("S8", "S8 - Перемежающийся режим с разными частотами вращения (2 или более)"),
	)

    MOTOR_POLES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
	)

    MOTOR_PHASES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
	)

    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, verbose_name=Manufacturer._meta.verbose_name)
    motor_type = models.CharField("тип", max_length=2, choices=MOTOR_TYPE, default="AS")
    motor_code = models.CharField("артикул", max_length=50)
    phases = models.PositiveSmallIntegerField("количество фаз", choices=MOTOR_PHASES, default=3, null=True, blank=True)
    poles = models.PositiveSmallIntegerField("число пар полюсов", choices=MOTOR_POLES, default=1, null=True, blank=True)
    eff_100 = models.FloatField("КПД, %", validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    eff_75 = models.FloatField("КПД (нагрузка - 75%), %", validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    eff_50 = models.FloatField("КПД (нагрузка - 50%), %", validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    eff_class = models.CharField("класс энергоэффективности", max_length=3, choices=MOTOR_EFF_CLASS, default="IE2")
    duty_type = models.CharField("режим работы", max_length=2, choices=MOTOR_DUTY_TYPE, default="S1")
    ip_code = models.CharField("степень защиты IP", max_length=4, choices=IP_CODE_CHOICES, default="IP54")
    insulation_class = models.CharField("класс изоляции", max_length=1, choices=MOTOR_INSULATION_CLASS, default="F")

    def __str__(self):
        return '%s (%s)' % (self.motor_code, self.manufacturer.manufacturer_code)

    class Meta:
        verbose_name = "Электродвигатель"
        verbose_name_plural = "Электродвигатели"
        db_table = "catalog_motor"

    def get_absolute_url(self):
        return reverse('motor-detail', args=[str(self.id)])


class MotorCircuitMixin(models.Model):

    class MotorVoltage(models.TextChoices):
        MV_220d = "220 \u0394", _("220 \u0394")
        MV_380s = "380 \u03A5", _("380 \u03A5")
        MV_380d = "380 \u0394", _("380 \u0394")
        MV_660s = "660 \u03A5", _("660 \u03A5")
        MV_230d = "230 \u0394", _("230 \u0394")
        MV_400s = "400 \u03A5", _("400 \u03A5")
        MV_400d = "400 \u0394", _("400 \u0394")
        MV_690s = "690 \u03A5", _("690 \u03A5")
        MV_240d = "240 \u0394", _("240 \u0394")
        MV_415s = "415 \u03A5", _("415 \u03A5")
        MV_415d = "415 \u0394", _("415 \u0394")
        MV_440s = "440 \u03A5", _("440 \u03A5")
        MV_500s = "500 \u03A5", _("500 \u03A5")
        MV_500d = "500 \u0394", _("500 \u0394")

    MOTOR_FREQ = (
        (50, "50"),
        (60, "60"),
	)

    voltage = models.CharField("напряжение, В", max_length=5, choices=MotorVoltage.choices, default=MotorVoltage.MV_380s)
    current = models.FloatField("ток, А", validators=[MinValueValidator(0.0)])
    freq = models.PositiveSmallIntegerField("частота, Гц", choices=MOTOR_FREQ, default=50)
    rpm = models.PositiveSmallIntegerField("об/мин")
    power = models.FloatField("мощность, кВт", validators=[MinValueValidator(0.0)])
    cos_phi = models.FloatField("cos(phi)", validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    def __str__(self):
        return '%s (%s) - %s' % (self.motor.motor_code, self.motor.manufacturer.manufacturer_code, self.voltage)

    class Meta:
        abstract = True


class MotorCircuit(MotorCircuitMixin):
    motor = models.ForeignKey(Motor, on_delete=models.SET_NULL, null=True, related_name="circuits")
    
    class Meta:
        verbose_name = "Электрическая характеристика"
        verbose_name_plural = "Электрические характеристики"
        db_table = "catalog_motor_circuit"


class Vfd(DimMassModelMixin):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, verbose_name=Manufacturer._meta.verbose_name)
    vfd_code = models.CharField("артикул", max_length=50)
    freq_min = models.PositiveSmallIntegerField("частота (мин.), Гц", validators=[MinValueValidator(0.0)])
    freq_max = models.PositiveSmallIntegerField("частота (макс.), Гц", validators=[MinValueValidator(0.0)])
    current_min = models.FloatField("ток (мин.), А", validators=[MinValueValidator(0.0)])
    current_max = models.FloatField("ток (макс.), А", validators=[MinValueValidator(0.0)])
    voltage_min = models.FloatField("напряжение (мин.), В", validators=[MinValueValidator(0.0)])
    voltage_max = models.FloatField("напряжение (макс.), В", validators=[MinValueValidator(0.0)])
    power_min = models.FloatField("мощность (мин.), кВт", validators=[MinValueValidator(0.0)])
    power_max = models.FloatField("мощность (макс.), кВт", validators=[MinValueValidator(0.0)])
    eff = models.FloatField("КПД, %", validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    ip_code = models.CharField("степень защиты оболочки", max_length=4, choices=IP_CODE_CHOICES, default="IP20")

    def __str__(self):
        return self.vfd_code

    class Meta:
        verbose_name = "Частотно-регулируемый привод"
        verbose_name_plural = "Частотно-регулируемые приводы"
        db_table = "catalog_vfd"

    def get_absolute_url(self):
        return reverse('vfd-detail', args=[str(self.id)])


class SoftStarter(DimMassModelMixin):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, verbose_name=Manufacturer._meta.verbose_name)
    soft_starter_code = models.CharField("артикул", max_length=50)
    current = models.FloatField("ток, А", validators=[MinValueValidator(0.0)])
    voltage = models.FloatField("напряжение, В", validators=[MinValueValidator(0.0)])
    power = models.FloatField("мощность, кВт", validators=[MinValueValidator(0.0)])
    eff = models.FloatField("КПД, %", validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    ip_code = models.CharField("степень защиты оболочки", max_length=4, choices=IP_CODE_CHOICES, default="IP20")

    def __str__(self):
        return self.soft_starter_code

    class Meta:
        verbose_name = "Плавный пуск"
        verbose_name_plural = "Плавные пуски"
        db_table = "catalog_soft_starter"

    def get_absolute_url(self):
        return reverse('soft-starter-detail', args=[str(self.id)])


class PumpUnit(DimMassModelMixin):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, verbose_name=Manufacturer._meta.verbose_name)
    pump_unit_code = models.CharField("артикул", max_length=50)
    pump = models.ForeignKey(Pump, on_delete=models.SET_NULL, null=True, verbose_name=Pump._meta.verbose_name)
    motor = models.ForeignKey(Motor, on_delete=models.SET_NULL, null=True, verbose_name=Motor._meta.verbose_name)

    def __str__(self):
        return self.pump_unit_code

    class Meta:
        verbose_name = "Насосный агрегат"
        verbose_name_plural = "Насосные агрегаты"
        db_table = "catalog_pump_unit"

    def get_absolute_url(self):
        return reverse('pump-unit-detail', args=[str(self.id)])