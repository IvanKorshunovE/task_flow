from django.db import models


class TaskType(models.Model):
    name = models.CharField(max_length=255)


class Task(models.Model):
    PRIORITY_CHOICES = (
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical'),
    )

    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    deadline = models.DateField()
    is_completed = models.BooleanField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL)