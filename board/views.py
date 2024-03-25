from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views import generic

from board.forms import (
    ProjectSearchForm,
    TaskForm,
    ProjectCreationForm,
    BoardCreationForm,
    WorkerSearchForm,
    TeamForm,
    WorkerForm,
)
from board.models import Project, Board, Task, Team


@login_required
def index(request):
    """View function for the home page of the site."""

    num_workers = get_user_model().objects.count()
    num_projects = Project.objects.count()

    context = {
        "num_workers": num_workers,
        "num_projects": num_projects,
    }

    return render(request, "pages/index.html", context=context)


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = ProjectSearchForm(initial={"name": name})
        error = self.request.session.pop("error", None)
        if error:
            context["error"] = error
        return context

    def get_queryset(self):
        queryset = Project.objects.all()
        form = ProjectSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    form_class = ProjectCreationForm
    success_url = reverse_lazy("board:project-list")

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.team = Team.objects.create(name=project.name)
        project.save()
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    fields = "__all__"
    success_url = reverse_lazy("board:project-list")


class ProjectDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView
):

    model = Project
    success_url = reverse_lazy("board:project-list")

    def test_func(self):
        self.object = self.get_object()

        return self.object.owner == self.request.user

    def handle_no_permission(self):
        owner_name = self.get_object().owner
        error_message = (
            f"You are not allowed to delete this project. "
            f"Only the owner ({owner_name}) of the project can "
            f"delete it."
        )
        self.request.session["error"] = error_message
        return redirect("board:project-list")


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    fields = "__all__"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_form"] = TaskForm()
        return context


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("board:project-list")

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


class BoardCreateView(LoginRequiredMixin, generic.CreateView):
    model = Board
    form_class = BoardCreationForm

    def form_valid(self, form):
        form.instance.project_id = self.kwargs["project_id"]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "board:project-detail", kwargs={"pk": self.kwargs["project_id"]}
        )


class BoardDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Board

    def get_success_url(self):
        project = self.object.project_id
        return reverse_lazy("board:project-detail", kwargs={"pk": project})


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

        tasks = worker.tasks.select_related("board__project")

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

    def test_func(self):
        self.object = self.get_object()

        return (
            self.request.user in self.object.board.project.team.members.all()
        )

    def handle_no_permission(self):

        error_message = (
            f"You are not allowed to delete this task. "
            f"Only the team members of the project can "
            f"delete it."
        )
        self.request.session["error"] = error_message
        return redirect(
            reverse(
                "board:project-detail",
                kwargs={"pk": self.get_object().board.project.id},
            )
        )


class TaskUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView
):
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        projects_id = self.object.board.project.id
        return reverse_lazy("board:project-detail", kwargs={"pk": projects_id})

    def test_func(self):
        self.object = self.get_object()

        return (
            self.request.user in self.object.board.project.team.members.all()
        )

    def handle_no_permission(self):

        error_message = (
            f"You are not allowed to edit this task. "
            f"Only the team members of the project can "
            f"edit it."
        )
        self.request.session["error"] = error_message
        return redirect(
            reverse(
                "board:project-detail",
                kwargs={"pk": self.get_object().board.project.id},
            )
        )


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
