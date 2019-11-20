from django.contrib import admin

from testapp.models import SetTest

@admin.register(SetTest)
class SetTestAdmin(admin.ModelAdmin):
	list_display = ['text_value', 'int_value']
	list_filter = ['text_value', 'int_value']
