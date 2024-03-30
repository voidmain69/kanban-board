from django.test import TestCase
from django.utils import timezone
from board.forms import (
    ProjectCreationForm,
    BoardCreationForm,
    TaskForm,
    TaskChangeBoardForm,
    TeamForm,
    TaskTypeForm,
    WorkerForm,
    RegisterForm,
    PositionForm,
)
from board.models import Project, Board, Task, Team, TaskType, Worker, Position
from datetime import date, timedelta
from django.contrib.auth import get_user_model


class FormTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        self.position = Position.objects.create(name="Developer")
        self.worker = Worker.objects.create_user(
            username="worker1",
            email="worker1@example.com",
            password="password",
            position=self.position,
        )
        self.team = Team.objects.create(name="Development Team")
        self.team.members.add(self.worker)
        self.project = Project.objects.create(
            name="Test Project",
            team=self.team,
            description="Test description",
            deadline=date.today() + timedelta(days=1),
            owner=self.user,
        )
        self.board = Board.objects.create(
            name="Test Board", project=self.project, color="#FFFFFF"
        )
        self.task_type = TaskType.objects.create(name="Bug")

    def test_project_creation_form(self):
        form_data = {
            "name": "New Project",
            "description": "New description",
            "deadline": timezone.now() + timedelta(days=1),
        }
        form = ProjectCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_project_creation_form_invalid_deadline(self):
        form_data = {
            "name": "New Project",
            "description": "New description",
            "deadline": timezone.now() - timedelta(days=2),
        }
        form = ProjectCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_board_creation_form(self):
        form_data = {"name": "New Board", "color": "#FFFFFF"}
        form = BoardCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_task_form(self):
        form_data = {
            "name": "New Task",
            "description": "New description",
            "deadline": timezone.now() + timedelta(days=1),
            "is_completed": False,
            "priority": "High",
            "task_type": self.task_type.id,
            "assignees": [self.worker.id],
            "board": self.board.id,
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_task_form_invalid_deadline(self):
        form_data = {
            "name": "New Task",
            "description": "New description",
            "deadline": timezone.now() - timedelta(days=1),
            "is_completed": False,
            "priority": "High",
            "task_type": self.task_type.id,
            "assignees": [self.worker.id],
            "board": self.board.id,
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_task_change_board_form(self):
        form_data = {"board": self.board.id}
        form = TaskChangeBoardForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_team_form(self):
        form_data = {"name": "New Team", "members": [self.worker.id]}
        form = TeamForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_task_type_form(self):
        form_data = {"name": "New Task Type"}
        form = TaskTypeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_worker_form(self):
        form_data = {
            "username": "newworker",
            "password1": "123QWEasd!",
            "password2": "123QWEasd!",
            "position": self.position.id,
            "avatar": None,
        }
        form = WorkerForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_register_form_invalid_pass(self):
        form_data = {
            "username": "newuser",
            "password1": "newpassword",
            "password2": "newpassword",
            "position": self.position.id,
            "email": "newuser@example.com",
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_position_form(self):
        form_data = {"name": "New Position"}
        form = PositionForm(data=form_data)
        self.assertTrue(form.is_valid())
