"""
Audit Logs Models

This module defines the Django models for the audit logging system.
Log entries are grouped into log groups that represent larger contexts.
"""

from django.db import models
from django.utils import timezone


class LogGroup(models.Model):
    """
    Log groups represent larger contexts within which log entries are recorded.
    """

    created = models.DateTimeField(
        auto_now_add=True, help_text="Datetime the log group was created"
    )

    type = models.CharField(
        max_length=50,
        help_text="The type of log group, which determines the expected properties",
    )

    reference_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="An identifier that should be unique across the log group type",
    )

    properties = models.JSONField(
        default=dict, blank=True, help_text="A dictionary of arbitrary key-values"
    )

    class Meta:
        unique_together = [["type", "reference_id"]]
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["type", "reference_id"]),
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return f"{self.type} - {self.reference_id}"


class LogEntry(models.Model):
    """
    A log entry is a single event that has been recorded.
    """

    log_group = models.ForeignKey(
        LogGroup,
        on_delete=models.CASCADE,
        related_name="log_entries",
        help_text="The log group this entry belongs to",
    )

    user = models.CharField(
        max_length=255,
        help_text="A string identifying the authenticated user that performed the action",  # noqa: E501
    )

    timestamp = models.DateTimeField(
        default=timezone.now, help_text="The time at which the logged action occurred"
    )

    description = models.TextField(
        blank=True,
        help_text="Textual description of the action for informative purposes",
    )

    type = models.CharField(
        max_length=50,
        help_text="The type of log entry, which determines the expected properties",
    )

    properties = models.JSONField(
        default=dict, blank=True, help_text="A dictionary of arbitrary key-values"
    )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["user"]),
            models.Index(fields=["log_group", "-timestamp"]),
        ]
        verbose_name_plural = "Log entries"

    def __str__(self):
        return f"{self.user} - {self.type} at {self.timestamp}"
