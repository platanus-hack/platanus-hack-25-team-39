"""
Django admin configuration for audit logs models
"""

from django.contrib import admin

from .models import LogEntry, LogGroup


@admin.register(LogGroup)
class LogGroupAdmin(admin.ModelAdmin):
    """Admin interface for LogGroup model"""

    list_display = ["reference_id", "type", "created"]
    list_filter = ["type", "created"]
    search_fields = ["reference_id"]
    readonly_fields = ["created"]
    ordering = ["-created"]

    fieldsets = (
        (None, {"fields": ("type", "reference_id", "properties")}),
        ("Timestamps", {"fields": ("created",), "classes": ("collapse",)}),
    )


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Admin interface for LogEntry model"""

    list_display = ["user", "type", "timestamp", "log_group", "description"]
    list_filter = ["type", "timestamp", "log_group__type"]
    search_fields = ["user", "description", "log_group__reference_id"]
    readonly_fields = ["timestamp"]
    ordering = ["-timestamp"]

    fieldsets = (
        (None, {"fields": ("log_group", "user", "type", "description")}),
        ("Data", {"fields": ("properties",), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("timestamp",), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("log_group")
