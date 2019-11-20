from django.db import models
from setfield import SetField

class SetTest(models.Model):
    text_value=SetField(models.TextField(choices=(('RED', 'red'), ('GREEN', 'green'), ('BLUE', 'blue'))), null=True, blank=True)
    int_value=SetField(models.PositiveIntegerField(), default=list)
