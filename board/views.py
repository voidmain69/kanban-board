from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic

from board.forms import (
    ProjectSearchForm,
    ProjectCreationForm,
    TaskForm,
    TaskTypeForm,
    TaskChangeBoardForm,
    BoardCreationForm,
    WorkerSearchForm,
    WorkerForm,
    TeamForm,
    PositionForm,
    RegisterForm,
)
from board.models import Project, Board, Task, Team, TaskType, Position


def index(request):
    """View function for the home page of the site."""

    count_of_projects = Project.objects.count()
    count_of_tasks = Task.objects.count()
    count_of_users = get_user_model().objects.count()
    count_of_active_projects = Project.objects.filter(
        is_completed=False
    ).count()

    return render(
        request,
        "pages/index.html",
        context={
            "count_of_projects": count_of_projects,
            "count_of_tasks": count_of_tasks,
            "count_of_users": count_of_users,
            "count_of_active_projects": count_of_active_projects,
        },
    )


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = ProjectSearchForm(initial={"name": name})
        error = self.request.session.pop("error", None)
        if error:
            context["error"] = error
        return context

    def get_queryset(self):
        queryset = Project.objects.order_by("-pk")
        form = ProjectSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    form_class = ProjectCreationForm

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.team = Team.objects.create(name=project.name)
        project.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form, has_errors=True), status=202
        )

    def get_success_url(self):
        return reverse_lazy(
            "board:project-detail", kwargs={"pk": self.object.id}
        )


class ProjectUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView
):
    model = Project
    fields = "__all__"
    template_name = "board/project_update.html"
    success_url = reverse_lazy("board:project-list")

    error_message = (
        "You are not allowed to edit this project. "
        "Only the owner of the project can delete it."
    )

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, self.error_message)

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return super().handle_no_permission()

        return redirect(
            reverse(
                "board:project-detail", kwargs={"pk": self.kwargs.get("pk")}
            )
        )

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form, has_errors=True), status=202
        )


class ProjectDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView
):

    model = Project
    success_url = reverse_lazy("board:project-list")

    error_message = (
        "You are not allowed to delete this project. "
        "Only the owner of the project can delete it."
    )

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, self.error_message)

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return super().handle_no_permission()

        return redirect(reverse("board:project-list"))


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    fields = "__all__"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_form"] = TaskForm()
        return context


class TaskCreateView(
    LoginRequiredMixin, UserPassesTestMixin, generic.CreateView
):
    model = Task
    form_class = TaskForm

    error_message = (
        "You are not allowed to edit this project. "
        "Only the team members of the project can "
        "edit it."
    )

    def form_valid(self, form):
        board = get_object_or_404(Board, pk=self.kwargs["board_id"])
        form.instance.board = board
        return super().form_valid(form)

    def get_success_url(self):
        projects_id = self.object.board.project.id
        return reverse_lazy("board:project-detail", kwargs={"pk": projects_id})

    def get_initial(self):
        initial = super().get_initial()
        board_id = self.kwargs.get("board_id")
        if board_id:
            initial["board"] = board_id
        return initial

    def test_func(self):
        user = self.request.user
        self.board = get_object_or_404(Board, pk=self.kwargs["board_id"])
        return (
            user in self.board.project.team.members.all()
            or user == self.board.project.owner
        )

    def handle_no_permission(self):
        messages.add_message(self.request, messages.ERROR, self.error_message)

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {"error_message": self.error_message}, status=400
            )
        else:
            return redirect(
                reverse(
                    "board:project-detail",
                    kwargs={"pk": self.board.project.id},
                )
            )


class BoardCreateView(
    LoginRequiredMixin, UserPassesTestMixin, generic.CreateView
):
    model = Board
    form_class = BoardCreationForm

    error_message = (
        "You are not allowed to edit this project. "
        "Only the team members of the project can "
        "edit it."
    )

    def form_valid(self, form):
        form.instance.project_id = self.kwargs["project_id"]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "board:project-detail", kwargs={"pk": self.kwargs["project_id"]}
        )

    def test_func(self):
        user = self.request.user
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        return user in project.team.members.all() or user == project.owner

    def handle_no_permission(self):
        messages.add_message(self.request, messages.ERROR, self.error_message)
        return redirect(
            reverse(
                "board:project-detail",
                kwargs={"pk": self.get_object().board.project.id},
            )
        )


class BoardDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView
):
    model = Board

    error_message = (
        "You are not allowed to delete this board. "
        "Only the owner of the project can "
        "delete it."
    )

    def get_success_url(self):
        project = self.object.project_id
        return reverse_lazy("board:project-detail", kwargs={"pk": project})

    def test_func(self):
        user = self.request.user
        self.object = self.get_object()
        return user == self.object.project.owner

    def handle_no_permission(self):
        messages.error(self.request, self.error_message)

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return super().handle_no_permission()

        return redirect(
            reverse(
                "board:project-detail",
                kwargs={"pk": self.get_object().project.id},
            )
        )


class BoardUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView
):
    model = Board
    fields = "__all__"

    error_message = (
        "You are not allowed to edit this project. "
        "Only the owner of the project can delete it."
    )

    def test_func(self):
        project = self.get_object().project
        return project.owner == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, self.error_message)

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return super().handle_no_permission()

        return redirect(
            reverse(
                "board:project-detail",
                kwargs={"pk": self.get_object().project.id},
            )
        )

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form, has_errors=True), status=202
        )


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        first_name = self.request.GET.get("first_name", "")
        context["search_form"] = WorkerSearchForm(
            initial={"first_name": first_name}
        )
        return context

    def get_queryset(self):
        queryset = get_user_model().objects.all()
        form = WorkerSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                first_name__icontains=form.cleaned_data["first_name"]
            )
        return queryset


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    fields = "__all__"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker = self.object

        tasks = worker.tasks.select_related("board__project").prefetch_related(
            "assignees"
        )

        tasks_by_projects = {}
        for task in tasks:
            project_name = task.board.project.name
            tasks_by_projects.setdefault(project_name, []).append(task)

        context["tasks_by_projects"] = tasks_by_projects
        return context


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = get_user_model()
    form_class = WorkerForm
    success_url = reverse_lazy("board:worker-list")


@login_required
def toggle_assign_to_team(request, pk):
    project = Project.objects.get(id=pk)

    # Check if the project has a team
    if not project.team:
        # If the project doesn't have a team, create a new team
        team = Team.objects.create(
            name=f"team: {project.name[:200]}"
        )  # Assuming you have a Team model
        project.team = team
        project.save()

    # Now proceed to adding/removing the user from the team
    if request.user in project.team.members.all():
        project.team.members.remove(request.user)
    else:
        project.team.members.add(request.user)

    return HttpResponseRedirect(
        reverse_lazy("board:project-detail", args=[pk])
    )


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task


class TaskListView(LoginRequiredMixin, generic.DetailView):
    model = Task
    paginate_by = 10


class TaskDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView
):
    model = Task

    error_message = (
        "You are not allowed to delete this task. "
        "Only the team members of the project can delete it."
    )

    def test_func(self):
        user = self.request.user
        task = self.get_object()
        return (
            user in task.board.project.team.members.all()
            or user == task.board.project.owner
        )

    def get_success_url(self):
        project_id = self.object.board.project.id
        return reverse_lazy("board:project-detail", kwargs={"pk": project_id})

    def handle_no_permission(self):
        messages.error(self.request, self.error_message)
        return super().handle_no_permission()


class TaskUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView
):
    model = Task
    form_class = TaskForm

    error_message = (
        "You are not allowed to edit this task. "
        "Only the team members of the project can edit it."
    )

    def test_func(self):
        user = self.request.user
        task = self.get_object()
        return (
            user in task.board.project.team.members.all()
            or user == task.board.project.owner
        )

    def get_success_url(self):
        project_id = self.object.board.project.id
        return reverse_lazy("board:project-detail", kwargs={"pk": project_id})

    def handle_no_permission(self):
        messages.error(self.request, self.error_message)
        return redirect(
            reverse(
                "board:project-detail",
                kwargs={"pk": self.get_object().board.project.id},
            )
        )

    def get_initial(self):
        initial = super().get_initial()
        board_id = self.kwargs.get("board_id")
        if board_id:
            initial["board"] = board_id

        if self.object:
            initial["board"] = self.object.board.id

        return initial


class TaskChangeBoardView(
    LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView
):
    model = Task
    form_class = TaskChangeBoardForm

    error_message = (
        "You are not allowed to edit this task. "
        "Only the team members of the project can edit it."
    )

    def test_func(self):
        user = self.request.user
        task = self.get_object()
        return (
            user in task.board.project.team.members.all()
            or user == task.board.project.owner
        )

    def get_success_url(self):
        project_id = self.object.board.project.id
        return reverse_lazy("board:project-detail", kwargs={"pk": project_id})

    def handle_no_permission(self):
        messages.error(self.request, self.error_message)
        return redirect(
            reverse(
                "board:project-detail",
                kwargs={"pk": self.get_object().board.project.id},
            )
        )

    def get_initial(self):
        initial = super().get_initial()
        task_id = self.kwargs.get("pk")
        if task_id:
            initial["project"] = Task.objects.get(pk=task_id).board.project.id
        return initial


class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy("board:project-list")


class TeamUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Team
    form_class = TeamForm

    def get_success_url(self):
        projects_id = self.object.project_set.first().pk
        return reverse_lazy("board:project-detail", kwargs={"pk": projects_id})


class TaskTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = TaskType
    fields = ["name"]
    success_url = reverse_lazy("board:task-type-list")


class TaskTypeDetailView(LoginRequiredMixin, generic.DetailView):
    model = TaskType


class TaskTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TaskType
    form_class = TaskTypeForm

    def get_success_url(self):
        return reverse_lazy(
            "board:task-type-detail", kwargs={"pk": self.object}
        )


class TaskTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = TaskType
    success_url = reverse_lazy("board:task-type-list")


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType
    paginate_by = 10


class PositionCreateView(LoginRequiredMixin, generic.CreateView):
    model = Position
    fields = ["name"]
    success_url = reverse_lazy("board:position-list")


class PositionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Position


class PositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Position
    form_class = PositionForm
    success_url = reverse_lazy("board:position-list")


class PositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Position
    success_url = reverse_lazy("board:position-list")


class PositionListView(LoginRequiredMixin, generic.ListView):
    model = Position
    paginate_by = 10
