from django.urls import path

from .views import (
    index,
    ProjectListView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    ProjectDetailView,
    TaskCreateView,
    TaskListView,
    TaskDetailView,
    TaskUpdateView,
    TaskDeleteView,
    TaskChangeBoardView,
    TaskTypeListView,
    TaskTypeCreateView,
    TaskTypeUpdateView,
    TaskTypeDetailView,
    TaskTypeDeleteView,
    BoardCreateView,
    BoardDeleteView,
    WorkerCreateView,
    WorkerListView,
    WorkerDetailView,
    TeamCreateView,
    TeamUpdateView,
    toggle_assign_to_team,
    PositionCreateView,
    PositionListView,
    PositionDetailView,
    PositionDeleteView,
    PositionUpdateView,
)

urlpatterns = [
    path("", index, name="index"),
    path(
        "projects/",
        ProjectListView.as_view(),
        name="project-list",
    ),
    path(
        "projects/create/",
        ProjectCreateView.as_view(),
        name="project-create",
    ),
    path(
        "projects/<int:pk>/update/",
        ProjectUpdateView.as_view(),
        name="project-update",
    ),
    path(
        "projects/<int:pk>/delete/",
        ProjectDeleteView.as_view(),
        name="project-delete",
    ),
    path(
        "projects/<int:pk>/",
        ProjectDetailView.as_view(),
        name="project-detail",
    ),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path(
        "tasks/<int:pk>/update", TaskUpdateView.as_view(), name="task-update"
    ),
    path(
        "tasks/create/<int:board_id>/",
        TaskCreateView.as_view(),
        name="task-create",
    ),
    path(
        "tasks/change-board/<int:pk>/",
        TaskChangeBoardView.as_view(),
        name="task-change-board",
    ),
    path(
        "boards/create/<int:project_id>/",
        BoardCreateView.as_view(),
        name="board-create",
    ),
    path(
        "boards/<int:pk>/delete/",
        BoardDeleteView.as_view(),
        name="board-delete",
    ),
    path(
        "tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"
    ),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path(
        "workers/<int:pk>/", WorkerDetailView.as_view(), name="worker-detail"
    ),
    path("workers/create/", WorkerCreateView.as_view(), name="worker-create"),
    path("teams/create/", TeamCreateView.as_view(), name="team-create"),
    path(
        "teams/<int:pk>/update/", TeamUpdateView.as_view(), name="team-update"
    ),
    path(
        "teams/<int:pk>/toggle-assign/",
        toggle_assign_to_team,
        name="toggle-assign-to-team",
    ),
    path(
        "taskstypes/create/",
        TaskTypeCreateView.as_view(),
        name="task-type-create",
    ),
    path("taskstypes/", TaskTypeListView.as_view(), name="task-type-list"),
    path(
        "taskstypes/<int:pk>/",
        TaskTypeDetailView.as_view(),
        name="task-type-detail",
    ),
    path(
        "taskstypes/<int:pk>/delete/",
        TaskTypeDeleteView.as_view(),
        name="task-type-delete",
    ),
    path(
        "taskstypes/<int:pk>/update/",
        TaskTypeUpdateView.as_view(),
        name="task-type-update",
    ),
    path(
        "positions/create/",
        PositionCreateView.as_view(),
        name="position-create",
    ),
    path("positions/", PositionListView.as_view(), name="position-list"),
    path(
        "positions/<int:pk>/",
        PositionDetailView.as_view(),
        name="position-detail",
    ),
    path(
        "positions/<int:pk>/delete/",
        PositionDeleteView.as_view(),
        name="position-delete",
    ),
    path(
        "positions/<int:pk>/update/",
        PositionUpdateView.as_view(),
        name="position-update",
    ),
]

app_name = "board"
