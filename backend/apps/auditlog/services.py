"""
Core business logic for audit logs

This module contains transport-agnostic services for creating and querying
audit logs. HTTP and WebSocket entrypoints should call into these functions
and map their inputs/outputs to transport-specific schemas.
"""

from __future__ import annotations

from abc import ABC
from datetime import datetime  # noqa: TC003
from typing import Any, ClassVar

from django.db.models import BooleanField, Case, Count, When
from pydantic import BaseModel

from .models import LogEntry, LogGroup


###########################
# Service request models
###########################
class LogGroupRequest(ABC, BaseModel):
    """Base object that can be used to create a log group"""

    log_group_type: ClassVar[str] = "default"

    def reference_id(self) -> str:
        """Return the reference id of the log group"""
        msg = "Subclasses must implement this method"
        raise NotImplementedError(msg)

    def properties(self) -> dict[str, Any]:
        """Return the properties of the log group"""
        msg = "Subclasses must implement this method"
        raise NotImplementedError(msg)


class LogEntryRequest(BaseModel):
    """Request model for creating a log entry via WebSocket"""

    timestamp: datetime
    log_group_reference_id: str
    type: str
    properties: dict[str, Any]
    description: str = ""
    user: str = "sidekick"  # Default to sidekick


###########################
# Errors
###########################
class LogGroupNotFoundError(Exception):
    """Raised when a log group for the given reference id is not found."""

    def __init__(self, reference_id: str):
        self.reference_id = reference_id
        message = "Log group with reference ID '" + reference_id + "' not found"
        super().__init__(message)


###########################
# Async API
###########################
async def get_or_create_log_group(log_owner: LogGroupRequest) -> LogGroup:
    """
    Create or update a log group with the provided properties.
    """
    return (
        await LogGroup.objects.aget_or_create(
            reference_id=log_owner.reference_id(),
            defaults={
                "type": log_owner.log_group_type,
                "properties": log_owner.properties(),
            },
        )
    )[0]


async def get_log_group_by_reference_id(reference_id: str) -> LogGroup | None:
    """Return the log group for the given reference_id or None if not found."""
    try:
        return await LogGroup.objects.aget(reference_id=reference_id)
    except LogGroup.DoesNotExist:
        return None


async def get_log_group_with_entry_counts_by_reference_id(
    reference_id: str,
    entry_types: list[str] | None = None,
) -> LogGroup | None:
    """Return the log group with entry counts for the given reference_id or None."""
    # Build conditional counts for each type
    annotations = {}
    for entry_type in entry_types:
        annotations[f"count_{entry_type}"] = Count(
            "log_entries",
            filter=Case(
                When(log_entries__type=entry_type, then=True),
                default=False,
                output_field=BooleanField(),
            ),
        )

    try:
        return await LogGroup.objects.annotate(**annotations).aget(
            reference_id=reference_id
        )
    except LogGroup.DoesNotExist:
        return None


async def create_log_entry(request: LogEntryRequest) -> LogEntry:
    """
    Create a log entry for the specified log group by reference id.

    Raises LogGroupNotFoundError if the log group is not found.
    """
    try:
        log_group = await LogGroup.objects.aget(
            reference_id=request.log_group_reference_id
        )
    except LogGroup.DoesNotExist as err:
        raise LogGroupNotFoundError(request.log_group_reference_id) from err

    return await LogEntry.objects.acreate(
        log_group=log_group,
        **request.model_dump(exclude={"log_group_reference_id"}),
    )


async def list_log_groups(
    *,
    group_type: str | None = None,
    entry_types: list[str] | None = None,
    offset: int = 0,
    limit: int = 100,
    order_by: str = "-created",
) -> list[LogGroup]:
    """Return a list of log groups matching the provided filters."""
    # If no entry_types specified, get all distinct types
    if entry_types is None:
        entry_types = (
            await LogEntry.objects.values_list("type", flat=True).distinct().alist()
        )

    # Build conditional counts for each type
    annotations = {}
    for entry_type in entry_types:
        annotations[f"count_{entry_type}"] = Count(
            "log_entries",
            filter=Case(
                When(log_entries__type=entry_type, then=True),
                default=False,
                output_field=BooleanField(),
            ),
        )

    queryset = LogGroup.objects.all().annotate(**annotations)
    if group_type:
        queryset = queryset.filter(type=group_type)
    sliced = queryset.order_by(order_by)[offset : offset + limit]
    return [obj async for obj in sliced]


async def list_log_entries(
    *,
    log_group_reference_id: str,
    user: str | None = None,
    offset: int = 0,
    limit: int = 100,
    order_by: str = "-timestamp",
) -> list[LogEntry]:
    """Return a list of log entries matching the provided filters."""
    queryset = LogEntry.objects.select_related("log_group")
    if log_group_reference_id:
        queryset = queryset.filter(log_group__reference_id=log_group_reference_id)
    if user:
        queryset = queryset.filter(user=user)
    sliced = queryset.order_by(order_by)[offset : offset + limit]
    return [obj async for obj in sliced]


async def get_users_by_log_groups(
    log_group_ids: list[int],
) -> dict[int, list[str]]:
    """
    Get unique users for each log group.

    Args:
        log_group_ids: List of log group IDs

    Returns:
        Dictionary mapping log_group_id to list of unique users
    """
    # Get all log entries for the specified log groups
    log_entries = [
        entry
        async for entry in LogEntry.objects.filter(log_group_id__in=log_group_ids)
        .values("log_group_id", "user")
        .distinct()
    ]

    # Group users by log_group_id
    result: dict[int, list[str]] = {lg_id: [] for lg_id in log_group_ids}
    for entry in log_entries:
        if entry["user"]:
            result[entry["log_group_id"]].append(entry["user"])

    # Remove duplicates
    for lg_id in result:
        result[lg_id] = list(set(result[lg_id]))

    return result
