from django import forms
from django.forms import ModelForm
from django.forms import widgets

from .models import Task, Team

class DateTimeInput(forms.DateTimeInput):
	input_type = 'date'
	

class TaskForm(ModelForm):
	
	class Meta:
		model = Task
		fields = ['name', 'assignee', 'description', 'due', 'recurring', 'start', 'end']
		widgets = {
			'due': DateTimeInput(),
			'start': DateTimeInput(),
			'end': DateTimeInput(),
		}


class TeamTaskForm(ModelForm):
	
	class Meta:
		model = Task
		fields = ['name', 'team', 'description', 'due', 'recurring', 'start', 'end']
		widgets = {
			'due': DateTimeInput(),
			'start': DateTimeInput(),
			'end': DateTimeInput(),
		}
	#self.fields['team'].queryset = (Team.objects.filter(leader=request.user))


	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')  # To get request.user. Do not use kwargs.pop('user', None) due to potential security hole

		super(TeamTaskForm, self).__init__(*args, **kwargs)

		# If the user does not belong to a certain group, remove the field
		self.fields['team'].queryset = (Team.objects.filter(leader=self.user))


class TaskForm2(ModelForm):

	class Meta:
		model = Task
		fields = ['name', 'assignee', 'description', 'due', 'recurring', 'start', 'end']
		widgets = {
			'due': forms.widgets.DateTimeInput(format="%m/%d/%Y %H:%M"),
			'start': forms.widgets.DateTimeInput(format="%m/%d/%Y %H:%M"),
			'end': forms.widgets.DateTimeInput(format="%m/%d/%Y %H:%M"),
		}