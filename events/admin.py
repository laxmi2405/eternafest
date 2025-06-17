from django.contrib import admin
from django import forms
from .models import Event


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'  # Use all fields from the Event model

        widgets = {
            # Customize the 'date' field to have a year range from 2000 to 2050
            'date': forms.SelectDateWidget(years=range(2000, 2051)),
            'time': forms.TimeInput(format='%H:%M',
                                    attrs={'type': 'time'}),
        }


class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm


class Media:
    js = ('events/admin_time_widget.js',)


admin.site.register(Event, EventAdmin)

admin.site.site_header = "EternaFest Admin Panel"
admin.site.site_title = "EternaFest Admin"
admin.site.index_title = "Welcome to EternaFest"
