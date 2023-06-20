from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from tasks.forms import WorkerSearchForm
from tasks.models import Worker, Position, Task, TaskType
from tasks.views import WorkerListView


WORKERS_URL = reverse("tasks:worker-list")
TASKS_URL = reverse("tasks:task-list")


class PublicWorkerTests(TestCase):
    def test_login_required(self):
        response = self.client.get(WORKERS_URL)
        self.assertNotEquals(response.status_code, 200)


class PublicTaskTests(TestCase):
    def test_login_required(self):
        response = self.client.get(TASKS_URL)
        self.assertNotEquals(response.status_code, 200)


class PrivateWorkerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user', password='test_pass'
        )
        self.client.force_login(self.user)
        self.worker1 = Worker.objects.create(
            username='worker1', first_name='John', last_name='Doe'
        )
        self.worker2 = Worker.objects.create(
            username='worker2', first_name='Jane', last_name='Smith'
        )
        self.worker3 = Worker.objects.create(
            username='worker3', first_name='Bob', last_name='Johnson'
        )
        self.factory = RequestFactory()

    def test_retrieve_worker_list(self):
        response = self.client.get(WORKERS_URL)
        workers = Worker.objects.all()

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.worker2.username)
        self.assertEquals(
            list(response.context_data["worker_list"]),
            list(workers)
        )
        self.assertTemplateUsed(
            response,
            "tasks/worker_list.html"
        )

    def test_search_box_filter_worker_list(self):
        response = self.client.get(WORKERS_URL, {"search_field": "worker1"})
        response_last_name = self.client.get(WORKERS_URL, {"search_field": "Johnson"})
        manufacturers = Worker.objects.filter(username__icontains="worker1")

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.worker1.username)
        self.assertContains(response_last_name, self.worker3.last_name)
        self.assertNotContains(response, self.worker2.username)
        self.assertNotContains(response_last_name, self.worker2.last_name)
        self.assertNotContains(response, self.worker3.username)
        self.assertEqual(len(response.context_data["worker_list"]), 1)
        self.assertEqual(
            len(response_last_name.context_data["worker_list"]),
            1
        )
        self.assertEqual(
            list(response.context_data["worker_list"]),
            list(manufacturers)
        )

    def test_get_queryset_without_search(self):
        request = self.factory.get(WORKERS_URL)
        view = WorkerListView()
        view.setup(request)
        queryset = view.get_queryset()
        self.assertQuerysetEqual(queryset, Worker.objects.all())

    def test_worker_list_view_context(self):
        url = reverse('tasks:worker-list')
        request = self.factory.get(url)
        request.user = self.user
        request.GET = {'search_field': 'Smith'}
        response = WorkerListView.as_view()(request)
        self.assertIn('search_form', response.context_data)
        search_form = response.context_data['search_form']
        self.assertIsInstance(search_form, WorkerSearchForm)
        queryset = response.context_data["object_list"]
        self.assertEqual(len(queryset), 1)
        self.assertIn(self.worker2, queryset)
        self.assertNotIn(self.worker1, queryset)
        self.assertNotIn(self.worker1, queryset)
        self.assertNotIn(self.user, queryset)

    def test_worker_list_view_queryset(self):
        url = reverse('tasks:worker-list')
        request = self.factory.get(
            url, data={'search_field': 'John'}
        )
        request.user = self.user
        response = WorkerListView.as_view()(request)
        expected_workers = [self.worker1, self.worker3]
        returned_workers = list(response.context_data['object_list'])

        self.assertEqual(len(returned_workers), len(expected_workers))
        for worker in expected_workers:
            self.assertIn(worker, returned_workers)

    def test_worker_list_view_pagination(self):
        url = reverse('tasks:worker-list')
        request = self.factory.get(url)
        request.user = self.user
        response = WorkerListView.as_view()(request)

        self.assertEqual(response.context_data['paginator'].per_page, 10)
        self.assertEqual(len(response.context_data['page_obj']), 4)

    def test_create_worker(self):
        position = Position.objects.create(name="CEO")
        form_data = {
            "username": "worker_test",
            "password1": "test1234567",
            "password2": "test1234567",
            "first_name": "first_name3",
            "last_name": "last_name3",
            "position": position.id
        }

        url = reverse("tasks:worker-create")
        self.client.post(
            path=url,
            data=form_data,
        )
        new_user = get_user_model().objects.get(
            username=form_data["username"]
        )
        self.assertEqual(new_user.first_name, form_data["first_name"])
        self.assertEqual(new_user.position, position)


class PrivateTaskTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user', password='test_pass'
        )
        self.client.force_login(self.user)

        self.position = Position.objects.create(name="Manager")

        self.worker1 = Worker.objects.create(
            username='worker1',
            first_name='John',
            last_name='Doe',
            position=self.position
        )
        self.worker2 = Worker.objects.create(
            username='worker2',
            first_name='Jane',
            last_name='Smith',
            position=self.position
        )
        self.worker3 = Worker.objects.create(
            username='worker3',
            first_name='Bob',
            last_name='Johnson',
            position=self.position
        )

        self.task_type1 = TaskType.objects.create(name="Bug fix")

        self.task1 = Task.objects.create(
            name="Task 1",
            description="test_description 1",
            deadline="2023-06-20",
            is_completed=False,
            priority="critical",
            task_type=self.task_type1
        )
        self.task1.assignees.add(self.worker1)

        self.factory = RequestFactory()