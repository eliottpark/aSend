


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.views.generic import DeleteView, UpdateView, ListView, DetailView, CreateView
from django import forms
from django.forms import widgets
from django.forms import ModelForm

# Create your views here.

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Q

from .models import Entry, Category
from django.db.models import Max

from django.conf import settings
from django.conf.urls import url,include
from django.conf.urls.static import static

# Create your views here.
class EntryListView(ListView):

	model = Entry
	template_name = 'asend/home.html'
	context_object_name = 'entries'
	ordering = ['value']
	def get_context_data(self, **kwargs):
		c = Category.objects.all()[:1].get()
		d = Category.objects.all()[1:2].get()
		e = Category.objects.all()[2:3].get()
		context = super(EntryListView, self).get_context_data(**kwargs)
		context['first'] = Entry.objects.all().filter(category=c).order_by('-value').first()
		context['second'] = Entry.objects.all().filter(category=d).order_by('-value').first()
		context['third'] = Entry.objects.all().filter(category=e).order_by('-value').first()
		return context

class CategoryDetailView(LoginRequiredMixin, DetailView):
	model = Category
	context_object_name = 'category'
	template_name = 'asend/category_detail.html'
	ordering = ['value']
	
	def get_context_data(self, **kwargs):
		c = Category.objects.all().get(pk=self.object.pk)
		context = super(CategoryDetailView, self).get_context_data(**kwargs)
		context['entries'] = Entry.objects.all().filter(category=c).order_by('-value')
		return context

class EntryDetailView(LoginRequiredMixin, DetailView):
	model = Entry
	context_object_name = 'object'
	template_name = 'asend/entry_detail.html'



class EntryCreateView(LoginRequiredMixin, CreateView):
	model = Entry
	fields = ['category','value','video','description']

	def form_valid(self, form):
		form.instance.creator = self.request.user
		form.instance.metric = form.instance.category.metric
		form.instance.category.updateRank()
		return super().form_valid(form)

class CategoryCreateView(LoginRequiredMixin, CreateView):
	model = Category
	fields = ['name','metric', 'description']

	def form_valid(self, form):
		form.instance.creator = self.request.user
		return super().form_valid(form)

def updater(request, cat_id):
	category = Category.objects.all().get(pk=cat_id)
	categoryEntries = Entry.objects.all().filter(category=category).order_by("-value")

	for i,e in enumerate(categoryEntries):
		e.rank = i+1
		e.save()

	return redirect('category-detail', category.id)



class UserEntries(LoginRequiredMixin, ListView):
	model = Entry
	template_name = 'asend/user_entries.html'
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
	
