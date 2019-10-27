from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from django.core.mail import send_mail


def get_first_name(self):
    return (self.first_name+' '+self.last_name)

User.add_to_class("__str__", get_first_name)

def add_one_month(orig_date):
    # advance year and month by one month
    new_year = orig_date.year
    new_month = orig_date.month + 1
    # note: in datetime.date, months go from 1 to 12
    if new_month > 12:
        new_year += 1
        new_month -= 12

    last_day_of_month = calendar.monthrange(new_year, new_month)[1]
    new_day = min(orig_date.day, last_day_of_month)

    return orig_date.replace(year=new_year, month=new_month, day=new_day)

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

class Email(models.Model):
	subject = models.CharField(max_length=1000)
	content = models.CharField(max_length=1000)
	sender =  models.CharField(max_length=1000, default = 'taskmanageraravind@gmail.com')
	reciever = models.CharField(max_length=1000)

	def send(self):
		send_mail(self.subject, self.content, self.sender, [self.reciever,])
		self.delete()

class Team(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)
	leader = models.ForeignKey(User, related_name='leader', on_delete=models.CASCADE,null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	members = models.ManyToManyField(User, related_name='memebers')

	def get_absolute_url(self):
		return reverse('team-detail', kwargs={'pk': self.pk})

	def __str__(self):
		return str(self.name)

class Task(models.Model):
	team = models.ForeignKey(Team, related_name='Team', on_delete=models.CASCADE, null=True, blank=True)
	name = models.CharField(max_length=100, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	due = models.DateTimeField(default=(timezone.now() + timezone.timedelta(minutes = 330)))
	assignee = models.ForeignKey(User, related_name='Assigned_To', on_delete=models.CASCADE, null=True, blank=True)
	assigner = models.ForeignKey(User, related_name='Assigned_By', on_delete=models.CASCADE, null=True, blank=True)
	STATUSES = (
		('P', "Pending"),
		('TD', "To Do"),
		('D', "Done"),
		)
	status = models.CharField(max_length=100, choices=STATUSES, default='P')
	parent = models.ForeignKey('Task', related_name='Parent', on_delete=models.CASCADE, null=True, blank=True)
	RECUR = (
		('N', "Never"),
		('D', "Daily"),
		('W', "Weekly"),
		('M', "Monthly"),
		('Y', "Yearly"),
		)

	recurring = models.CharField(max_length=100, choices=RECUR, default='N')
	start = models.DateTimeField(null=True, blank=True, default=(timezone.now() + timezone.timedelta(minutes = 330)))
	end = models.DateTimeField(null=True, blank=True, default=(timezone.now() + timezone.timedelta(minutes = 330))+timezone.timedelta(days=99999) )
	subtasks = models.BooleanField(default=False)
	finished =  models.DateTimeField(null=True, blank=True)

	PRIORITY = (

			('L', 'Late'),
			('T', 'Today'),
			('W', 'Week'),
			('D', 'Default')
			)

	priority = models.CharField(max_length=100, choices=PRIORITY, default='D')


	def prioritize(self):
		if self.due is None:
			self.due = (timezone.now() + timezone.timedelta(minutes = 330))

		dif = self.due - (timezone.now() + timezone.timedelta(minutes = 330))
		if dif < timezone.timedelta(minutes = 1):
			self.priority = 'L'
		elif dif < timezone.timedelta(days = 1):
			self.priority = 'T'
		elif dif < timezone.timedelta(days = 7):
			self.priority = 'W'
		else:
			self.priority = 'D'

	def update_due(self):
		r = self.recurring
		d = self.due
		if self.end is None:
			self.end = (timezone.now() + timezone.timedelta(minutes = 330))+timezone.timedelta(days=99999)
		if self.start is None:
			self.start = (timezone.now() + timezone.timedelta(minutes = 330))
		if self.due is None:
			self.due = (timezone.now() + timezone.timedelta(minutes = 330))

		r = self.recurring
		d = self.due
		if r == 'N' or self.end==None or self.start==None:
			self.status = 'D'
			self.finished = (timezone.now() + timezone.timedelta(minutes = 330))
		elif r == 'D':
			d = d + timezone.timedelta(days=1)
		elif r == 'W':
			d = d + timezone.timedelta(days=7)
		elif r == 'M':
			d = add_one_month(d)
		else:
			d = d + relativedelta(years=1)

		if d > self.end:
			self.status = 'D'
		else:
			self.due = d

	def get_due(self):
		if self.due:
			return self.due.strftime('%m/%d/%Y %H:%M')
		return "-"

	def get_finished(self):
		if self.finished:
			return self.finished.strftime('%m/%d/%Y %H:%M')
		return "-"

	def get_end(self):
		if self.end:
			return self.end.strftime('%m/%d/%Y %H:%M')
		return "-"

	def __str__(self):
		return str(self.name)
	
	def get_absolute_url(self):
		if self.parent:
			return reverse('assign-email', kwargs={'id': self.parent.pk})
		if self.team:
			return reverse('team-assigner', kwargs={'task_id': self.id})
		return reverse('assign-email', kwargs={'id': self.id})
		#return reverse('task-detail', kwargs={'pk': self.pk})

	def __str__(self):
		return str(self.name)

