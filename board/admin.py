from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Position,
    TaskType,
    Worker,
    Task,
    Team,
    Board,
    Project,
    Attachment,
)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["name", "deadline", "is_completed", "priority"]
    list_filter = ["deadline", "is_completed", "priority", "task_type"]
    search_fields = ["name", "description"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_filter = ["deadline", "is_completed", "name"]


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ["name", "file"]
    search_fields = ["name"]


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (
        "position",
        "avatar_thumbnail",
    )
    fieldsets = UserAdmin.fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "position",
                        "avatar",
                    )
                },
            ),
        )
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "position",
                    )
                },
            ),
        )
    )

    def avatar_thumbnail(self, obj):
        if obj.avatar:
            return (
                f'<img src="{obj.avatar.url}" '
                f'style="max-width:100px;max-height:100px;" />'
            )
        else:
            return "(No img)"

    avatar_thumbnail.allow_tags = True


admin.site.register(Position)
admin.site.register(TaskType)
admin.site.register(Team)
admin.site.register(Board)
