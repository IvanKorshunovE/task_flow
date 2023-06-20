from django.test import TestCase
from tasks.models import Position, Worker, TaskType, Task


class ModelTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Manager")

        self.worker = Worker.objects.create(
            username='worker1',
            first_name='John',
            last_name='Doe',
            position=self.position
        )

        self.task_type = TaskType.objects.create(name="Bug fix")

        self.task = Task.objects.create(
            name="Task 1",
            description="test_description",
            deadline="2023-06-20",
            is_completed=False,
            priority="critical",
            task_type=self.task_type
        )
        self.task.assignees.add(self.worker)

    def test_position_str(self):
        self.assertEqual(str(self.position), "Manager")

    def test_worker_str(self):
        self.assertEqual(str(self.worker), "worker1")

    def test_task_type_str(self):
        self.assertEqual(str(self.task_type), "Bug fix")

    def test_task_str(self):
        self.assertEqual(str(self.task), "Task 1")

    def test_task_absolute_url(self):
        expected_url = "/tasks/task-detail/{}/".format(self.task.pk)
        self.assertEqual(self.task.get_absolute_url(), expected_url)

    def test_task_ordering(self):
        task1 = Task.objects.create(
            name="Task 1",
            description="test_description",
            deadline="2023-06-20",
            is_completed=False,
            priority="normal",
            task_type=self.task_type
        )
        task2 = Task.objects.create(
            name="Task 2",
            description="test_description",
            deadline="2023-06-20",
            is_completed=False,
            priority="urgent",
            task_type=self.task_type
        )
        task3 = Task.objects.create(
            name="Task 3",
            description="test_description",
            deadline="2023-06-20",
            is_completed=False,
            priority="critical",
            task_type=self.task_type
        )
        tasks_ordered = [task3, task2, self.task, task1]
        self.assertQuerysetEqual(Task.objects.all(), tasks_ordered, transform=lambda x: x)

    def test_task_assignees(self):
        assignees = self.task.assignees.all()
        self.assertEqual(list(assignees), [self.worker])
        self.assertEqual(assignees[0].username, "worker1")
