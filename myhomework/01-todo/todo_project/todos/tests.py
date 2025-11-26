from django.test import TestCase
from django.urls import reverse
from .models import Todo
import datetime

class TodoModelTests(TestCase):
    def test_str_returns_title(self):
        t = Todo.objects.create(title='Test title')
        self.assertEqual(str(t), 'Test title')

    def test_default_resolved_is_false(self):
        t = Todo.objects.create(title='Other')
        self.assertFalse(t.resolved)

class TodoViewTests(TestCase):
    def setUp(self):
        self.todo = Todo.objects.create(title='Existing', description='Desc')

    def test_list_view(self):
        url = reverse('todos:list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Existing')

    def test_create_view_creates_todo(self):
        url = reverse('todos:create')
        data = {
            'title': 'Created',
            'description': 'Created desc',
            'due_date': datetime.date.today().isoformat(),
            # omit 'resolved' to leave as False
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Todo.objects.filter(title='Created').exists())

    def test_update_view_edits_todo(self):
        url = reverse('todos:edit', args=[self.todo.pk])
        data = {
            'title': 'Updated title',
            'description': 'New',
            'due_date': '',
            'resolved': 'on',
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated title')
        self.assertTrue(self.todo.resolved)

    def test_delete_view_deletes_todo(self):
        url = reverse('todos:delete', args=[self.todo.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Todo.objects.filter(pk=self.todo.pk).exists())

    def test_toggle_resolved(self):
        self.assertFalse(self.todo.resolved)
        url = reverse('todos:toggle_resolved', args=[self.todo.pk])
        resp = self.client.post(url, HTTP_REFERER=reverse('todos:list'))
        self.assertIn(resp.status_code, (302, 301))
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.resolved)

# Additional tests
class TodoFormTests(TestCase):
    def test_form_widget_and_save(self):
        # local import so we don't need to change top-of-file imports
        from .forms import TodoForm
        form = TodoForm()
        html = form.as_p()
        # due_date uses a date input widget
        self.assertIn('type="date"', html)

        data = {
            'title': 'FromForm',
            'description': 'created via form',
            'due_date': datetime.date.today().isoformat(),
        }
        form = TodoForm(data=data)
        self.assertTrue(form.is_valid())
        todo = form.save()
        self.assertEqual(todo.title, 'FromForm')

class TemplateTests(TestCase):
    def test_list_shows_due_date_and_resolved_class(self):
        due = datetime.date(2025, 1, 1)
        t1 = Todo.objects.create(title='Resolved', due_date=due, resolved=True)
        t2 = Todo.objects.create(title='Open', due_date=due, resolved=False)
        resp = self.client.get(reverse('todos:list'))
        self.assertEqual(resp.status_code, 200)
        # due date formatting appears on the page
        self.assertContains(resp, '2025-01-01')
        # resolved item renders with the resolved class
        self.assertContains(resp, 'class="resolved"')
        self.assertContains(resp, 'Resolved')
        self.assertContains(resp, 'Open')

class URLTests(TestCase):
    def test_named_urls_resolve_correctly(self):
        from django.urls import resolve
        r = resolve('/todos/')
        self.assertEqual(r.view_name, 'todos:list')
        r = resolve('/todos/create/')
        self.assertEqual(r.view_name, 'todos:create')
