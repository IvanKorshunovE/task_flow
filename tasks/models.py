from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.urls import reverse


class Position(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "Positions"

    def __str__(self):
        return f"{self.name}"


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        related_name='workers'
    )

    class Meta:
        verbose_name = "Worker"
        verbose_name_plural = "Workers"


class TaskType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Task type"
        verbose_name_plural = "Task types"

    def __str__(self):
        return f"{self.name}"


class Task(models.Model):
    PRIORITY_CHOICES = (
        ('critical', 'Critical'),
        ('urgent', 'Urgent'),
        ('normal', 'Normal'),
    )

    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True, blank=True)
    deadline = models.DateField()
    is_completed = models.BooleanField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="normal",
    )
    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.SET_NULL,
        null=True
    )
    assignees = models.ManyToManyField(
        Worker,
        related_name="tasks",
    )

    class Meta:
        ordering = [models.Case(
            models.When(priority='critical', then=models.Value(1)),
            models.When(priority='urgent', then=models.Value(2)),
            models.When(priority='normal', then=models.Value(3)),
            default=models.Value(3),
            output_field=models.IntegerField(),
        )]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def get_absolute_url(self):
        return reverse("tasks:task-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.name}"
