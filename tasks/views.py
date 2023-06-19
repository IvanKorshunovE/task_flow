from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from tasks.forms import (
    TaskForm,
    WorkerCreationForm,
    WorkerSearchForm
)
from tasks.models import Task, Worker


def index(request):
    """View function for the home page of the site."""

    num_tasks = Task.objects.count()
    num_workers = Worker.objects.count()
    num_of_critical_tasks = Task.objects.filter(priority="critical").count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_tasks": num_tasks,
        "num_workers": num_workers,
        "num_of_critical_tasks": num_of_critical_tasks,
        "num_visits": num_visits + 1,
    }

    return render(request, "tasks/index.html", context=context)


def toggle_assign_to_task(request, pk):
    worker = Worker.objects.get(id=request.user.id)
    if (
        Task.objects.get(id=pk) in worker.tasks.all()
    ):
        worker.tasks.remove(pk)
    else:
        worker.tasks.add(pk)
    return HttpResponseRedirect(reverse_lazy("tasks:task-detail", args=[pk]))


class WorkerListView(
    # LoginRequiredMixin,
    generic.ListView
):
    model = Worker
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search_field = self.request.GET.get("search_field", "")
        context["search_form"] = WorkerSearchForm(
            initial={"search_field": search_field}
        )
        return context

    def get_queryset(self):
        queryset = Worker.objects.all()
        form = WorkerSearchForm(data=self.request.GET)
        if form.is_valid():
            search_query = form.cleaned_data["search_field"]
            return queryset.filter(
                Q(username__icontains=search_query)
                | Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
            )
        return queryset


class WorkerDetailView(
    # LoginRequiredMixin,
    generic.DetailView
):
    model = Worker


class WorkerCreateView(
    # LoginRequiredMixin,
    generic.CreateView
):
    model = Worker
    form_class = WorkerCreationForm
    success_url = reverse_lazy("tasks:worker-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "The new worker has been created.")
        return response


class WorkerUpdateView(
    # LoginRequiredMixin,
    generic.UpdateView
):
    model = Worker
    form_class = WorkerCreationForm

    def get_success_url(self):
        updated_worker = self.get_object()
        return updated_worker.get_absolute_url()

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, "Worker has been updated.")
        return response


class WorkerDeleteView(
    # LoginRequiredMixin,
    generic.DeleteView
):
    model = Worker
    success_url = reverse_lazy("tasks:worker-list")

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.warning(request, "Worker has been deleted.")
        return response


class TaskListView(
    # LoginRequiredMixin,
    generic.ListView
):
    model = Task
    paginate_by = 10


class TaskCreateView(
    # LoginRequiredMixin,
    generic.CreateView
):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tasks:task-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "The task has been created.")
        return response


class TaskDetailView(
    # LoginRequiredMixin,
    generic.DetailView
):
    model = Task


class TaskUpdateView(
    # LoginRequiredMixin,
    generic.UpdateView
):
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        updated_task = self.get_object()
        return updated_task.get_absolute_url()

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, "Task has been updated.")
        return response


class TaskDeleteView(
    # LoginRequiredMixin,
    generic.DeleteView
):
    model = Task
    success_url = reverse_lazy("tasks:task-list")

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.warning(request, "Task has been deleted.")
        return response
