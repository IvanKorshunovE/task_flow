from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import DateInput

from tasks.models import Task, Worker


class WorkerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "position",
            "first_name",
            "last_name",
        )

    def clean_username(self):
        # Skip uniqueness validation if the form is used for updating an existing worker
        if self.instance.pk and self.cleaned_data.get('username') == self.instance.username:
            return self.cleaned_data.get('username')

        # Otherwise, perform the default uniqueness validation
        username = self.cleaned_data.get('username')
        try:
            Worker.objects.get(username=username)
        except Worker.DoesNotExist:
            return username
        raise ValidationError("A user with that username already exists.")


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
        fields = "__all__"
