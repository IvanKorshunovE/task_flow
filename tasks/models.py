from django.contrib.auth.models import AbstractUser
from django.db import models


class Position(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "Positions"


class Worker(AbstractUser):
    position = models.ForeignKey(Position, on_delete=models.SET_NULL)


class TaskType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Task type"
        verbose_name_plural = "Task types"

    def __str__(self):
        return f"{self.name}"


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

    class Meta:
        ordering = ["-priority"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"{self.name}"
