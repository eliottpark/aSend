# Generated by Django 2.2.2 on 2019-06-29 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_list', '0003_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('TD', 'To Do'), ('D', 'Done')], default='P', max_length=100),
        ),
    ]
