from django.contrib import admin
from tasks.models import Position, Worker, TaskType, Task

admin.site.register(Position)
admin.site.register(Worker)
admin.site.register(TaskType)
admin.site.register(Task)
