from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import DateInput

from tasks.models import Task, Worker


class TaskSearchForm(forms.Form):
    search_field = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search the name of the task",
                "class": "form-control;",
                "style": "width: 300px",
                "type": "text",
            }
        )
    )
    priority = forms.MultipleChoiceField(
        choices=(
            ('critical', 'Critical'),
            ('urgent', 'Urgent'),
            ('normal', 'Normal'),
        ),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
            }
        ),
        label="",
        initial=("critical", "urgent", "normal")
    )
    assignee = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width: 300px",
                "placeholder": "Search by assignee username"
            }
        ),
        label="",
    )
    is_completed = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
        label="Include completed tasks"
    )


class WorkerSearchForm(forms.Form):
    search_field = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by username, first name, last name",
                "class": "form-control;",
                "style": "width: 400px",
                "type": "text",
            }
        )
    )


class WorkerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "position",
            "first_name",
            "last_name",
        )

    def clean_username(self):
        if (self.instance.pk and self.cleaned_data.get('username') ==
                self.instance.username):
            return self.cleaned_data.get('username')
        username = self.cleaned_data.get('username')
        try:
            Worker.objects.get(username=username)
        except Worker.DoesNotExist:
            return username
        raise ValidationError(
            "A user with that username already exists."
        )


class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    deadline = forms.DateField(
        widget=DateInput(
            attrs={
                'type': 'date'
            }
        )
    )

    class Meta:
        model = Task
        exclude = ['is_completed']
