from django.test import TestCase
from django.contrib.auth import get_user_model
from board.models import (
    Position,
    TaskType,
    Worker,
    Task,
    Team,
    Board,
    Project,
    Attachment,
)
from datetime import date


class ModelTestCase(TestCase):
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
        self.task_type = TaskType.objects.create(name="Bug")
        self.team = Team.objects.create(name="Development Team")
        self.team.members.add(self.worker)
        self.project = Project.objects.create(
            name="Test Project",
            team=self.team,
            description="Test description",
            deadline=date.today(),
            owner=self.user,
        )
        self.board = Board.objects.create(
            name="Test Board", project=self.project, color="#FFFFFF"
        )
        self.attachment = Attachment.objects.create(
            name="Test Attachment", file="attachments/test.txt"
        )

    def test_position(self):
        self.assertEqual(str(self.position), "Developer")

    def test_task_type(self):
        self.assertEqual(str(self.task_type), "Bug")

    def test_worker(self):
        self.assertEqual(str(self.worker), "worker1")

    def test_team(self):
        self.assertEqual(str(self.team), "Development Team")
        self.assertEqual(self.team.members.count(), 1)
        self.assertIn(self.worker, self.team.members.all())

    def test_board(self):
        self.assertEqual(str(self.board), "Test Board")
        self.assertEqual(self.board.project, self.project)

    def test_project(self):
        self.assertEqual(str(self.project), "Test Project")
        self.assertEqual(self.project.team, self.team)
        self.assertEqual(self.project.owner, self.user)

    def test_attachment(self):
        self.assertEqual(str(self.attachment), "Test Attachment")

    def test_task(self):
        task = Task.objects.create(
            name="Test Task",
            board=self.board,
            description="Test description",
            deadline=date.today(),
            is_completed=False,
            priority=Task.HIGH,
            task_type=self.task_type,
        )
        task.assignees.add(self.worker)
        task.attachments.add(self.attachment)
        self.assertEqual(str(task), "Test Task")
        self.assertEqual(task.board, self.board)
        self.assertTrue(self.worker in task.assignees.all())
        self.assertTrue(self.attachment in task.attachments.all())
