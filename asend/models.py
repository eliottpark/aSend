from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
import calendar


# Create your models here.
class Entry(models.Model):
	value = models.IntegerField()
	creator = models.ForeignKey(User, max_length=100, on_delete=models.CASCADE, null=True, blank=True)
	category = models.ForeignKey('Category',max_length=100, on_delete=models.CASCADE)
	video =  models.CharField(max_length=100, null=True, blank=True)
	metric = models.CharField(max_length=100, null=True, blank=True)
	description = models.CharField(max_length=100, null=True, blank=True)
	rank = models.IntegerField(null=True, blank=True)
	
	def get_absolute_url(self):
		return reverse('update', kwargs={'cat_id': self.category.pk})

	def __str__(self):
		return str(self.category.name+": " + self.creator.first_name)





class Category(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	creator = models.CharField(max_length=100)
	metric = models.CharField(max_length=100, null=True, blank=True)
	def get_absolute_url(self):
		return reverse('category-detail', kwargs={'pk': self.pk})

	def __str__(self):
		return str(self.name)

	def updateRank(self):
		e = Entry.objects.all().filter(category=self).order_by('-value')
		for i in range(e.count()):
			e[i].rank = i+1
			e[i].save()





