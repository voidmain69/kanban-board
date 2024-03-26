from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Task, Attachment, Project, Board, Team, Worker


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProjectSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by name", "class": "form-control"}
        ),
    )


class WorkerSearchForm(forms.Form):
    first_name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by name", "class": "form-control"}
        ),
    )


class ProjectCreationForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "deadline",
        ]

        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }


class BoardCreationForm(forms.ModelForm):

    class Meta:
        model = Board
        fields = [
            "name",
            "color",
        ]


class TaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_board = kwargs.get("initial", {}).get("board", None)

        if initial_board:
            self.fields["assignees"].queryset = Board.objects.get(
                id=kwargs["initial"]["board"]
            ).project.team.members.all()

    file_field = MultipleFileField()

    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "deadline",
            "is_completed",
            "priority",
            "task_type",
            "assignees",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter task name"}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    def save(self, commit=True):
        task = super().save(commit=False)
        if commit:
            try:
                task.save()
                for file in self.cleaned_data.get("file_field", []):
                    current_datetime = datetime.now().strftime(
                        "%Y-%m-%d-%H-%M-%S"
                    )
                    attachment = Attachment.objects.create(
                        name=f"{task.id}:{current_datetime}", file=file
                    )
                    task.attachments.add(attachment)
                self.save_m2m()
            except Exception as e:
                for attachment in task.attachments.all():
                    attachment.file.delete()
                raise e
        return task


class TaskChangeBoardForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_board = kwargs.get("initial", {}).get("project", None)

        if initial_board:
            self.fields["board"].queryset = Project.objects.get(
                id=kwargs["initial"]["project"]
            ).boards.all()

    class Meta:
        model = Task
        fields = [
            "board",
        ]


class TeamForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Team
        fields = "__all__"


class WorkerForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ("position", "avatar")
