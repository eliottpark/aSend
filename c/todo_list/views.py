from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Task, Team, Email
from django.views.generic import DeleteView, UpdateView, ListView, DetailView, CreateView
from django.contrib.admin.widgets import AdminDateWidget
from django import forms
from django.forms import widgets
from django.forms import ModelForm
from .forms import DateTimeInput, TaskForm, TaskForm2, TeamTaskForm
from django.core.mail import send_mail
from django.db.models.query import EmptyQuerySet
import time
import copy
# Create your views here.

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Q




def emailer(request):

	emails = Email.objects.all()
	for email in emails:
			email.send()
	time.sleep(20)

	try:
		return redirect(request.META.get('HTTP_REFERER'))
	except:
		time.sleep(20)
		return redirect('todo_list-personal')
	#return redirect('email')


def personal(request):
	context = {
		'tasks': Task.objects.all(),
		'name': 'Personal Dashboard',
	}
	return render(request, 'todo_list/personal.html', context)

class TaskListView(LoginRequiredMixin, ListView):

	model = Task
	template_name = 'todo_list/personal.html'
	context_object_name = 'tasks'
	ordering = ['due']


	def get_context_data(self, **kwargs):
		tasks = Task.objects.all()
		for task in tasks:
			task.prioritize()
			task.save()

		context = super(TaskListView, self).get_context_data(**kwargs)
		todo = tasks.filter(status='TD').filter(assignee=self.request.user).filter(parent=None).order_by('due')
		context['late'] = todo.filter(priority='L')
		context['day'] = todo.filter(priority='T')
		context['week'] = todo.filter(priority='W')
		context['other'] = todo.filter(priority='D')
		context['done'] = Task.objects.filter(status='D').filter(assignee=self.request.user).filter(parent=None).order_by('finished')[:15]
		context['pend'] = Task.objects.filter(status='P').filter(assignee=self.request.user).order_by('due')
		context['width'] = '4'
		context['email'] = Email.objects.all().exists()
		return context

class TaskListViewA(LoginRequiredMixin, ListView):

	model = Task
	template_name = 'todo_list/manage.html'
	context_object_name = 'tasks'
	ordering = ['due']


	def get_context_data(self, **kwargs):
		tasks = Task.objects.all()
		for task in tasks:
			task.prioritize()
			task.save()

		context = super(TaskListViewA, self).get_context_data(**kwargs)
		todo = tasks.filter(status='TD').filter(assigner=self.request.user).filter(parent=None).order_by('due')
		context['late'] = todo.filter(priority='L')
		context['day'] = todo.filter(priority='T')
		context['week'] = todo.filter(priority='W')
		context['other'] = todo.filter(priority='D')
		context['done'] = Task.objects.filter(status='D').filter(assigner=self.request.user).filter(parent=None).order_by('finished')[:15]
		context['pend'] = Task.objects.filter(status='P').filter(assigner=self.request.user).order_by('due')
		context['width'] = '4'
		context['email'] = Email.objects.all().exists()
		return context


class UserTaskListView(LoginRequiredMixin, ListView):
	model = Task
	template_name = 'todo_list/user_tasks.html'
	ordering = ['due']
	
	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Task.objects.filter(assignee=user).filter(parent=None).order_by('due')

	def get_context_data(self, **kwargs):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		context = super(UserTaskListView, self).get_context_data(**kwargs)
		context['user'] = user
		context['tasks'] = Task.objects.filter(status='TD').filter(assignee=user).filter(parent=None).order_by('due')
		context['done'] = Task.objects.filter(status='D').filter(assignee=user).filter(parent=None).order_by('finished')[:15]
		context['pend'] = Task.objects.filter(status='P').filter(assignee=user).order_by('due')
		context['width'] = '4'
		context['email'] = Email.objects.all().exists()
		return context


def completeTodo(request, todo_id):
	task = Task.objects.get(pk=todo_id)
	due = task.get_due()
	if task.assignee == request.user:
		task.update_due()
		task.save()

		task = Task.objects.get(pk=todo_id)
		full = " "+ request.user.first_name +" "+ request.user.last_name
		subject = full + " has completed " + task.name
		details = task.name +"\n" + "_________________"+ "\n" + "Was Due: " + due + "\n" + "Completed: " + task.get_finished()  + "\n" 

		if not task.recurring == 'N':
			details += "Recurring " + task.get_recurring_display() + " until " + task.get_end() + "\n" + "Next Due Date: " + task.get_due()+ "\n"

		link = "See " + request.user.first_name + request.user.last_name+"'s " + "progress: " + request.build_absolute_uri(reverse('user-tasks', kwargs= {'username':request.user.username})) + "\n" 
		link += "See " + task.name + "  details: " +   request.build_absolute_uri(reverse('task-detail', kwargs= {'pk':task.id}))
		Email(subject =subject, content= details+link, reciever = task.assigner.email).save()
	url = 'todo_list-personal'
	return redirect(url)

def completeTodo2(request, todo_id, main_id):
	task = Task.objects.get(pk=todo_id)
	if task.assignee == request.user:
		task.update_due()
		task.save()

		task = Task.objects.get(pk=todo_id)
		full = " "+ request.user.first_name +" "+ request.user.last_name
		subject = full + " has completed " + task.name
		details = task.name +"\n" + "_________________"+ "\n" + "Was Due: " + due + "\n" + "Completed: " + task.get_finished()  + "\n" 

		if not task.recurring == 'N':
			details += "Recurring " + task.get_recurring_display() + " until " + task.get_end() + "\n" + "Next Due Date: " + task.get_due()+ "\n"

		link = "See " + request.user.first_name + request.user.last_name+"'s " + "progress: " + request.build_absolute_uri(reverse('user-tasks', kwargs= {'username':request.user.username})) + "\n" 
		link += "See " + task.name + "  details: " +   request.build_absolute_uri(reverse('task-detail', kwargs= {'pk':task.id}))
		Email(subject =subject, content= details+link, reciever = task.assigner.email).save()
	url = 'todo_list-personal'
	return redirect(url)

def acceptTodo(request, todo_id):
	task = Task.objects.get(pk=todo_id)
	if task.assignee == request.user:
		task.status = 'TD'
		task.save()

		task = Task.objects.get(pk=todo_id)
		full = " "+ request.user.first_name +" "+ request.user.last_name
		subject = full + " has accepted " + task.name
		details = task.name + "\n" + "Due: " +task.get_due()  + "\n" 
		if not task.recurring == 'N':
			details += "Recurring " + task.get_recurring_display() + " until " + task.get_end() + "\n" + "Next Due Date: " + task.get_due()+ "\n"

		link = "See " + request.user.first_name + request.user.last_name+"'s " + "progress: " + request.build_absolute_uri(reverse('user-tasks', kwargs= {'username':request.user.username})) + "\n" 
		link += "See " + task.name + "  details: " +   request.build_absolute_uri(reverse('task-detail', kwargs= {'pk':task.id}))
		Email(subject=subject, content= details+link, reciever = task.assigner.email).save()
	return redirect('todo_list-personal')

def doTodo(request, todo_id):
	task = Task.objects.get(pk=todo_id)
	if task.assignee == request.user:
		task.status = 'TD'
		task.save()

		task = Task.objects.get(pk=todo_id)
		full = " "+ request.user.first_name +" "+ request.user.last_name
		subject = full + " is still working on " + task.name
		details = task.name + "\n" + "Due: " + task.get_due() + "\n" + "Finished: " + task.get_finished() + "\n" 
		if not task.recurring == 'N':
			details += "Recurring " + task.get_recurring_display() + " until " + task.get_end() + "\n" + "Next Due Date: " + task.get_due()+ "\n"

		link = "See " + request.user.first_name + request.user.last_name+"'s " + "progress: " + request.build_absolute_uri(reverse('user-tasks', kwargs= {'username':request.user.username})) + "\n" 
		link += "See " + task.name + "  details: " +   request.build_absolute_uri(reverse('task-detail', kwargs= {'pk':task.id}))
		Email(subject=subject, content= details+link, reciever = task.assigner.email).save()

	return redirect('todo_list-personal')

def doTodo2(request, todo_id, main_id):
	task = Task.objects.get(pk=todo_id)
	if task.assignee == request.user:
		task.status = 'TD'
		task.save()

		task = Task.objects.get(pk=todo_id)
		full = " "+ request.user.first_name +" "+ request.user.last_name
		subject = full + " is still working on " + task.name
		details = task.name + "\n" + "Due: " + task.due.strftime('%m/%d/%Y %H:%M') + "\n" + "Finished: " + task.finished.strftime('%m/%d/%Y %H:%M') + "\n" 
		if not task.recurring == 'N':
			details += "Recurring " + task.get_recurring_display() + " until " + task.get_end() + "\n" + "Next Due Date: " + task.get_due()+ "\n"

		link = "See " + request.user.first_name + request.user.last_name+"'s " + "progress: " + request.build_absolute_uri(reverse('user-tasks', kwargs= {'username':request.user.username})) + "\n" 
		link += "See " + task.name + "  details: " +   request.build_absolute_uri(reverse('task-detail', kwargs= {'pk':task.id}))
		Email(subject=subject, content= details+link, reciever = task.assigner.email).save()

	return redirect('task-detail', main_id)


class TeamDetailView(LoginRequiredMixin, DetailView):
	model = Team
	context_object_name = 'team'
	template_name = 'todo_list/team_detail.html'


	
	def get_context_data(self, **kwargs):
		context = super(TeamDetailView, self).get_context_data(**kwargs)
		context['width'] = '4'
		context['email'] = Email.objects.all().exists()
		return context


class TaskDetailView(LoginRequiredMixin, DetailView):
	model = Task
	context_object_name = 'tasks'
	template_name = 'todo_list/task_detail.html'
	queryset = Task.objects.all()

	def get_context_data(self, **kwargs):
		context = super(TaskDetailView, self).get_context_data(**kwargs)
		context['main'] = self.get_object()
		print(Task.objects.filter(parent=self.get_object()).filter(status='TD').order_by('due').count())
		context['sub'] = Task.objects.filter(parent=self.get_object()).filter(status='TD').order_by('due')
		context['done'] = Task.objects.filter(parent=self.get_object()).filter(status='D').order_by('finished')[:15]
		context['width'] = '4'
		context['email'] = Email.objects.all().exists()
		return context

class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Task
	success_url = '/dashboard/manage/'
	def test_func(self):
		task = self.get_object()
		if self.request.user == task.assigner:
			return True
		return False

	def get_context_data(self, **kwargs):
		context = super(TaskDeleteView, self).get_context_data(**kwargs)
		context['width'] = '8'
		return context

class TeamDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Team
	success_url = '/dashboard/team/'
	def test_func(self):
		team = self.get_object()
		if self.request.user == team.leader:
			return True
		return False

	def get_context_data(self, **kwargs):
		context = super(TeamDeleteView, self).get_context_data(**kwargs)
		context['width'] = '8'
		return context

class TaskCreateView(LoginRequiredMixin, CreateView):
	model = Task
	form_class = TaskForm
	
	def form_valid(self, form):
		form.instance.assigner = self.request.user
		return super().form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(TaskCreateView, self).get_context_data(**kwargs)
		context['width'] = '8'
		return context

class TeamTaskCreateView(LoginRequiredMixin, CreateView):
	model = Task
	form_class = TeamTaskForm
	template_name = 'todo_list/team_task_form.html'
	
	
	def form_valid(self, form):
		form.instance.assigner = self.request.user
		return super().form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(TeamTaskCreateView, self).get_context_data(**kwargs)
		context['width'] = '8'
		return context
	def get_form_kwargs(self):
		kwargs = super(TeamTaskCreateView, self).get_form_kwargs()
		kwargs.update({'user': self.request.user})
		return kwargs

def assigner(request, task_id):
	task = Task.objects.get(pk=task_id)
	team = task.team
	
	full = " "+ task.assigner.first_name +" "+ task.assigner.last_name
	subject = full + " assigned " + task.name
	details = task.name + "\n" + "Due: " + task.due.strftime('%m/%d/%Y %H:%M') + "\n"
	if not task.recurring == 'N':
		details += "Recurring " + task.get_recurring_display() + " until " + task.get_end() + "\n" 
	link = "See " + task.name + "  details: " +   request.build_absolute_uri(reverse('task-detail', kwargs= {'pk':task.id}))
	
	for member in team.members.all():
		task = Task.objects.get(pk=task_id)
		task.pk = None
		task.assignee = member
		task.save()
		Email(subject=subject, content= details+link, reciever = task.assignee.email).save()

	return redirect('team-detail', team.id)


	#def get_form(self, form_class=None):
	#	form = super(TaskCreateView, self).get_form(form_class)
	#	form.fields['due'].widget = DateInput()
	#	return form

class TeamCreateView(LoginRequiredMixin, CreateView):
	model = Team
	fields = ['name', 'description', 'members']
	
	def form_valid(self, form):
		form.instance.leader = self.request.user
		return super().form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(TeamCreateView, self).get_context_data(**kwargs)
		context['width'] = '8'
		return context


def subtaskView(request, todo_id):
	task_parent = Task.objects.get(pk=todo_id)

	task_child = Task(name=None,status='P',due=task_parent.due, start=task_parent.start, end=task_parent.end, recurring=task_parent.recurring, assignee=task_parent.assignee, description= None, assigner=request.user, parent=task_parent)
	task_child.save()
	task_parent.subtasks = True
	task_parent.save()
	url = '/dashboard/task/'+ str(task_child.id) +'/update/'
	return redirect(url)

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Task
	form_class = TaskForm2
	
	def form_valid(self, form):
		form.instance.assigner = self.request.user
		return super().form_valid(form)

	def test_func(self):
		task = self.get_object()
		if self.request.user == task.assigner:
			return True
		return False

	def get_context_data(self, **kwargs):
		context = super(TaskUpdateView, self).get_context_data(**kwargs)
		context['width'] = '8'
		return context

class TeamUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Team
	fields = ['name', 'description', 'members']
	
	def form_valid(self, form):
		form.instance.leader = self.request.user
		return super().form_valid(form)

	def test_func(self):
		team = self.get_object()
		if self.request.user == team.leader:
			return True
		return False

	def get_context_data(self, **kwargs):
		context = super(TeamUpdateView, self).get_context_data(**kwargs)
		context['width'] = '8'
		return context

class TeamListView(LoginRequiredMixin, ListView):
	model = Team
	template_name = 'todo_list/team.html'
	context_object_name = 'teams'

	def get_queryset(self):
		return Team.objects.filter(leader=self.request.user)

	def get_context_data(self, **kwargs):
		context = super(TeamListView, self).get_context_data(**kwargs)
		context['width'] = '8'
		context['email'] = Email.objects.all().exists()
		return context


class ChartData(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None):
		labels = ["Done", "To Do"]
		print(request.user)
		day = [Task.objects.filter(status='D').count(), Task.objects.filter(status='TD').count()]
		week = day
		month= day
		data = {
				"labels": labels,
				"day": day,
				"week": week,
				"month": month,
		}
		return Response(data)





def assignmentEmail(request, id):
	task = Task.objects.get(pk=id)

	full = " "+ task.assigner.first_name +" "+ task.assigner.last_name
	subject = full + " assigned " + task.name
	details = task.name + "\n" + "Due: " + task.due.strftime('%m/%d/%Y %H:%M') + "\n"
	if not task.recurring == 'N':
		details += "Recurring " + task.get_recurring_display() + " until " + task.get_end() + "\n" 

	link = "See " + task.name + "  details: " +   request.build_absolute_uri(reverse('task-detail', kwargs= {'pk':task.id}))
	Email(subject=subject, content= details+link, reciever = task.assignee.email).save()

	return redirect("task-detail", id)




#########################################
class HomeView(View):
	def get(self, request, *args, **kwargs):
		return redirect('todo_list-personal')



def get_data(request,team_id=None, *args, **kwargs):
	labels = ["Done", "To Do", "Not Yet Accepted"]
	tasks = Task.objects.all()
	for task in tasks:
		task.prioritize()
		task.save()

	user = request.user
	tasks = Task.objects.all()
	myset = Team.objects.none()
	if team_id and not (team_id == -1):
		team = Team.objects.get(pk=team_id)
		for member in team.members.all():
			this = tasks.filter(assigner=user).filter(assignee=member).filter(parent=None)
			print(member)
			print(this)
			print(this.count())
			myset = myset | this
		day = [myset.filter(status='D').filter(priority='T').count() | myset.filter(status='D').filter(priority='L').count(), myset.filter(status='TD').filter(priority='T').count() | myset.filter(status='TD').filter(priority='L').count(), myset.filter(status='P').filter(priority='T').count()| myset.filter(status='P').filter(priority='L').count()]
		week = [myset.filter(status='D').filter(priority='W').count(), myset.filter(status='TD').filter(priority='W').count(),  myset.filter(status='P').filter(priority='W').count()]
		month= [myset.filter(status='D').filter(priority='D').count(), myset.filter(status='TD').filter(priority='D').count(),  myset.filter(status='P').filter(priority='D').count()]
		
	else:
		day = [Task.objects.filter(parent=None).filter(assigner=user).filter(status='D').filter(priority='T').count()| Task.objects.filter(parent=None).filter(assigner=user).filter(status='D').filter(priority='L').count(), Task.objects.filter(parent=None).filter(assigner=user).filter(status='TD').filter(priority='T').count()|Task.objects.filter(parent=None).filter(assigner=user).filter(status='TD').filter(priority='L').count(), Task.objects.filter(parent=None).filter(assigner=user).filter(status='P').filter(priority='T').count()| Task.objects.filter(parent=None).filter(assigner=user).filter(status='P').filter(priority='L').count()]
		week = [Task.objects.filter(parent=None).filter(assigner=user).filter(status='D').filter(priority='W').count(), Task.objects.filter(parent=None).filter(assigner=user).filter(status='TD').filter(priority='W').count(),  Task.objects.filter(parent=None).filter(assigner=user).filter(status='P').filter(priority='W').count()]
		month= [Task.objects.filter(parent=None).filter(assigner=user).filter(status='D').filter(priority='D').count(), Task.objects.filter(parent=None).filter(assigner=user).filter(status='TD').filter(priority='D').count(),  Task.objects.filter(parent=None).filter(assigner=user).filter(status='P').filter(priority='D').count()]
	backgroundColor = ['rgba(54, 162, 235, 0.8)','rgba(232, 42, 42, 0.8)', 'rgba(232, 182, 42, 0.8)']
	backgroundColor2 = ['rgba(54, 162, 235, 0.6)','rgba(232, 42, 42, 0.6)', 'rgba(232, 182, 42, 0.6)']
	backgroundColor3 = ['rgba(54, 162, 235, 0.4)','rgba(232, 42, 42, 0.4)', 'rgba(232, 182, 42, 0.4)']
	data = {
			"labels": labels,
			"day": day,
			"week": week,
			"month": month,
			"backgroundColor": backgroundColor,
			"backgroundColor2": backgroundColor2,
			"backgroundColor3": backgroundColor3,
	}

	
	return JsonResponse(data) # http response


def get_data2(request, *args, **kwargs):
	labels = ["Done", "To Do", "Not Yet Accepted"]
	tasks = Task.objects.all()
	for task in tasks:
		task.prioritize()
		task.save()

	user = request.user

	day = [Task.objects.filter(parent=None).filter(assigner=user).filter(status='D').filter(priority='T').count()| Task.objects.filter(parent=None).filter(assigner=user).filter(status='D').filter(priority='L').count(), Task.objects.filter(parent=None).filter(assigner=user).filter(status='TD').filter(priority='T').count()|Task.objects.filter(parent=None).filter(assigner=user).filter(status='TD').filter(priority='L').count(), Task.objects.filter(parent=None).filter(assigner=user).filter(status='P').filter(priority='T').count()| Task.objects.filter(parent=None).filter(assigner=user).filter(status='P').filter(priority='L').count()]
	week = [Task.objects.filter(parent=None).filter(assigner=user).filter(status='D').filter(priority='W').count(), Task.objects.filter(parent=None).filter(assigner=user).filter(status='TD').filter(priority='W').count(),  Task.objects.filter(parent=None).filter(assigner=user).filter(status='P').filter(priority='W').count()]
	month= [Task.objects.filter(parent=None).filter(assigner=user).filter(status='D').filter(priority='D').count(), Task.objects.filter(parent=None).filter(assigner=user).filter(status='TD').filter(priority='D').count(),  Task.objects.filter(parent=None).filter(assigner=user).filter(status='P').filter(priority='D').count()]
	backgroundColor = ['rgba(54, 162, 235, 0.8)','rgba(232, 42, 42, 0.8)', 'rgba(232, 182, 42, 0.8)']
	backgroundColor2 = ['rgba(54, 162, 235, 0.6)','rgba(232, 42, 42, 0.6)', 'rgba(232, 182, 42, 0.6)']
	backgroundColor3 = ['rgba(54, 162, 235, 0.4)','rgba(232, 42, 42, 0.4)', 'rgba(232, 182, 42, 0.4)']
	data = {
			"labels": labels,
			"day": day,
			"week": week,
			"month": month,
			"backgroundColor": backgroundColor,
			"backgroundColor2": backgroundColor2,
			"backgroundColor3": backgroundColor3,
	}

	
	return JsonResponse(data) # http response


