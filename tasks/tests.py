import unittest
from datetime import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from tasks.models import Task


# Unit testovi za Task model
class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        self.task = Task.objects.create(
            user=self.user,
            title="Test Task",
            description="Test Description",
            completed=False,
            due_date=datetime.now(),
            priority="later"
        )

    def test_task_creation(self):
        self.assertEqual(self.task.title, "Test Task")
        self.assertFalse(self.task.completed)


# Unit testovi za views 
class TaskViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        self.client.login(username='testuser', password='12345')

    def test_task_list_view(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)

    def test_task_create_view(self):
        response = self.client.post(reverse('task_create'), {
            'title': 'New Task',
            'description': 'Description',
            'completed': False,
            'priority': 'urgent',
            'due_date': '2025-06-10 12:00'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())


# Testovi za upload funkcionalnosti
class TaskUploadTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        self.client.login(username='testuser', password='12345')

    def test_upload_txt(self):
        content = b"Sample Title, Sample description urgent"
        response = self.client.post(reverse('upload_tasks_txt'), {
            'file': ('tasks.txt', content, 'text/plain')
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Task.objects.filter(title='Sample Title').exists()
        )

    def test_upload_csv(self):
        content = (
            b"title,description,completed,due_date,priority\n"
            b"Test CSV,Desc,False,2025-06-10 10:00,later"
        )
        response = self.client.post(reverse('upload_tasks_csv'), {
            'file': ('tasks.csv', content, 'text/csv')
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Task.objects.filter(title='Test CSV').exists()
        )


# Doctest funkcija
def parse_priority(text: str) -> str:
    """
    Extracts priority from a given text.

    >>> parse_priority("This is urgent")
    'urgent'
    >>> parse_priority("Something important")
    'important'
    >>> parse_priority("Normal task")
    'later'
    """
    for p in ['urgent', 'important']:
        if p in text.lower():
            return p
    return 'later'


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    unittest.main()
