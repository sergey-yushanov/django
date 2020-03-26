from django.contrib.postgres.forms import SimpleArrayField
from django import forms
from django.forms.fields import CharField
from django.forms.widgets import Textarea
from .models import MotorCircuit


class MotorCircuitForm(forms.ModelForm):
    
    volt = SimpleArrayField(CharField(), delimiter='|', widget=Textarea())
    
    #def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        #self.fields['volt'].delimiter = '|'  # Or whichever other character you want.
        

    class Meta:
        model = MotorCircuit
        fields = '__all__'