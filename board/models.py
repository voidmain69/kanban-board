from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TaskType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)


class Task(models.Model):
    URGENT = "Urgent"
    HIGH = "High"

    PRIORITY_CHOICES = [(URGENT, "Urgent"), (HIGH, "High")]

    name = models.CharField(max_length=255)
    board = models.ForeignKey(
        "Board", on_delete=models.CASCADE, related_name="tasks"
    )
    description = models.TextField()
    deadline = models.DateField()
    is_completed = models.BooleanField()
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=HIGH,
    )

    task_type = models.ForeignKey(
        TaskType, on_delete=models.CASCADE, related_name="tasks"
    )
    assignees = models.ManyToManyField(
        Worker, related_name="tasks", blank=True
    )

    attachments = models.ManyToManyField(
        "Attachment", related_name="tasks", blank=True
    )

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(Worker, related_name="teams")

    def __str__(self):
        return self.name


class Board(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="boards"
    )
    color = models.CharField(max_length=7, null=True, blank=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, default=None, null=True, blank=True
    )
    description = models.TextField()
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="projects",
        default=None,
        null=True,
    )

    def __str__(self):
        return self.name


class Attachment(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="attachments/")

    def __str__(self):
        return self.name
