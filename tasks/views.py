from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic, View

from tasks.forms import (
    TaskForm,
    WorkerCreationForm,
    WorkerSearchForm,
    TaskSearchForm,
)
from tasks.models import (
    Task,
    Worker,
)


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        """View function for the home page of the site."""
        num_tasks = Task.objects.count()
        num_workers = Worker.objects.count()
        num_of_critical_tasks = Task.objects.filter(
            priority="critical"
        ).count()
        num_tasks_not_completed = Task.objects.filter(
            is_completed=False
        ).count()

        num_visits = request.session.get(
            "num_visits", 0
        )
        request.session["num_visits"] = num_visits + 1

        context = {
            "num_tasks": num_tasks,
            "num_workers": num_workers,
            "num_of_critical_tasks": num_of_critical_tasks,
            "num_tasks_not_completed": num_tasks_not_completed,
            "num_visits": num_visits + 1,
        }

        return render(
            request,
            "tasks/index.html",
            context=context
        )


class ToggleCompleteTaskView(LoginRequiredMixin, View):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.is_completed = not task.is_completed
        task.save()
        return redirect(reverse(
            "tasks:task-detail",
            kwargs={"pk": pk})
        )


class ToggleAssignToTaskView(LoginRequiredMixin, View):
    def get(self, request, pk):
        worker = get_object_or_404(
            Worker,
            id=request.user.id
        )
        task = get_object_or_404(Task, id=pk)

        if task in worker.tasks.all():
            worker.tasks.remove(task)
        else:
            worker.tasks.add(task)

        source = request.GET.get("source")
        worker_id = request.GET.get("worker_id")

        if source == "worker-detail":
            return HttpResponseRedirect(
                reverse(
                    "tasks:worker-detail",
                    args=[worker_id]
                )
            )
        elif source == "task-detail":
            return HttpResponseRedirect(
                reverse(
                    "tasks:task-detail",
                    args=[pk]
                )
            )

        return HttpResponseRedirect(
            reverse(
                "tasks:task-detail",
                args=[pk]
            )
        )


class WorkerListView(
    LoginRequiredMixin,
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
    LoginRequiredMixin,
    generic.DetailView
):
    model = Worker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        my_tasks = Task.objects.filter(assignees=user)
        context["my_tasks"] = my_tasks
        return context


class WorkerCreateView(
    LoginRequiredMixin,
    generic.CreateView
):
    model = Worker
    form_class = WorkerCreationForm
    success_url = reverse_lazy("tasks:worker-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "The new worker has been created."
        )
        return response


class WorkerUpdateView(
    LoginRequiredMixin,
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
    LoginRequiredMixin,
    generic.DeleteView
):
    model = Worker
    success_url = reverse_lazy("tasks:worker-list")

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.warning(request, "Worker has been deleted.")
        return response


class TaskListView(
    LoginRequiredMixin,
    generic.ListView
):
    model = Task
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search_field = self.request.GET.get("search_field", "")
        priority = self.request.GET.getlist("priority")
        assignee = self.request.GET.get("assignee", "")
        is_completed = self.request.GET.get("is_completed")
        if not priority:
            priority = TaskSearchForm().fields["priority"].initial
        context["search_form"] = TaskSearchForm(
            initial={
                "search_field": search_field,
                "priority": priority,
                "assignee": assignee,
                "is_completed": is_completed,
            }
        )
        return context

    def get_queryset(self):
        queryset = Task.objects.all()
        form = TaskSearchForm(data=self.request.GET)
        if form.is_valid():
            search_query = form.cleaned_data["search_field"]
            priority = form.cleaned_data["priority"]
            is_completed = form.cleaned_data["is_completed"]
            if not is_completed:
                queryset = queryset.filter(is_completed=False)
            if priority:
                queryset = queryset.filter(priority__in=priority)
            assignee = form.cleaned_data["assignee"]
            if assignee:
                queryset = queryset.filter(
                    assignees__username__icontains=assignee
                )
            return queryset.filter(
                Q(name__icontains=search_query)
            )
        return queryset


class TaskCreateView(
    LoginRequiredMixin,
    generic.CreateView
):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tasks:task-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "The task has been created."
        )
        return response


class TaskDetailView(
    LoginRequiredMixin,
    generic.DetailView
):
    model = Task


class TaskUpdateView(
    LoginRequiredMixin,
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
    LoginRequiredMixin,
    generic.DeleteView
):
    model = Task
    success_url = reverse_lazy("tasks:task-list")

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.warning(request, "Task has been deleted.")
        return response
