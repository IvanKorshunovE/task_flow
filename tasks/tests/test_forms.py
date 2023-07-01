from django.contrib.auth import get_user_model
from django.test import TestCase
from tasks.forms import (
    TaskSearchForm,
    WorkerSearchForm,
    WorkerCreationForm,
    TaskForm
)
from tasks.models import Position, TaskType


class FormTests(TestCase):
    def setUp(self):
        self.assignee = get_user_model().objects.create_user(
            username='test_user', password='test_pass'
        )
        self.position = Position.objects.create(
            name="test position"
        )
        self.task_type = TaskType.objects.create(
            name="test type"
        )

    def test_task_search_form_valid_data(self):
        form = TaskSearchForm(data={
            'search_field': 'Task 1',
            'priority': ['critical'],
            'assignee': self.assignee.id,
            'is_completed': True
        })
        self.assertTrue(form.is_valid())

    def test_task_search_form_empty_data(self):
        form = TaskSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_worker_search_form_valid_data(self):
        form = WorkerSearchForm(data={
            'search_field': 'worker1'
        })
        self.assertTrue(form.is_valid())

    def test_worker_search_form_empty_data(self):
        form = WorkerSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_worker_creation_form_valid_data(self):
        form = WorkerCreationForm(data={
            'username': 'new_worker',
            'password1': 'test_pass',
            'password2': 'test_pass',
            'position': self.position.id,
            'first_name': 'John',
            'last_name': 'Doe'
        })
        self.assertTrue(form.is_valid())

    def test_worker_creation_form_empty_data(self):
        form = WorkerCreationForm(data={})
        self.assertFalse(form.is_valid())

    def test_task_form_valid_data(self):
        form = TaskForm(data={
            'name': 'Task 1',
            'description': 'Test description',
            'deadline': '2023-06-20',
            'priority': 'normal',
            'task_type': self.task_type.pk,
            'assignees': [self.assignee.pk],
        })
        self.assertTrue(form.is_valid())

    def test_task_form_empty_data(self):
        form = TaskForm(data={})
        self.assertFalse(form.is_valid())
