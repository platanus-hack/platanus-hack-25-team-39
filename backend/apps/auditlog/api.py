"""
Audit Logs API

This module implements the HTTP endpoints for the audit logging system.
"""

from ninja import Field, Query, Router, Schema

from .services import (
    LogEntryRequest,
    LogGroupRequest,
    create_log_entry,
    get_log_group_with_entry_counts_by_reference_id,
    get_or_create_log_group,
    list_log_entries,
    list_log_groups,
)


class LogGroupOut(Schema):
    """Output schema for log groups"""

    id: int
    created: str
    type: str
    reference_id: str
    properties: dict
    entry_counts: dict[str, int] = Field(default_factory=dict)


class LogEntryOut(Schema):
    """Output schema for log entries"""

    id: int
    user: str
    timestamp: str
    description: str
    type: str
    properties: dict
    log_group_id: int


class LogGroupsResponse(Schema):
    """Response schema for log groups endpoint"""

    log_groups: list[LogGroupOut]


class LogEntriesResponse(Schema):
    """Response schema for log entries endpoint"""

    log_entries: list[LogEntryOut]


class LogGroupFilters(Schema):
    """Query filters for log groups"""

    page_size: int = 100
    offset: int = 0
    type: str | None = None
    entry_types: list[str] | None = Field(default_factory=list)


class LogEntryFilters(Schema):
    """Query filters for log entries"""

    page_size: int = 100
    offset: int = 0
    log_group_reference_id: str | None = None
    user: str | None = None


class LogGroupIn(Schema):
    """Input schema for creating log groups"""

    type: str
    reference_id: str
    properties: dict = Field(default_factory=dict)


class LogEntryIn(Schema):
    """Input schema for creating log entries"""

    log_group_reference_id: str
    timestamp: str
    description: str = ""
    type: str
    properties: dict = Field(default_factory=dict)


router = Router()


@router.get("/log-groups", response=LogGroupsResponse)
async def get_log_groups(request, filters: LogGroupFilters = Query(...)):  # noqa: B008
    """
    Fetch audit logs, a list of available log groups.

    - Ordered in descending order of log group creation date
    - Page size = 100 by default
    - Optionally includes review statistics in batch
    """
    # Get log groups first
    groups = await list_log_groups(
        group_type=filters.type,
        entry_types=filters.entry_types,
        offset=filters.offset,
        limit=filters.page_size,
    )

    log_groups = []
    for lg in groups:
        # Build entry_counts dictionary from annotated fields
        entry_counts = {}
        for attr_name in dir(lg):
            if attr_name.startswith("count_"):
                entry_type = attr_name[6:]  # Remove "count_" prefix
                count_value = getattr(lg, attr_name)
                if count_value is not None:
                    entry_counts[entry_type] = count_value

        log_groups.append(
            LogGroupOut(
                id=lg.id,
                created=lg.created.isoformat(),
                type=lg.type,
                reference_id=lg.reference_id,
                properties=lg.properties,
                entry_counts=entry_counts,
            )
        )

    return LogGroupsResponse(log_groups=log_groups)


@router.get("/log-entries", response=LogEntriesResponse)
async def get_log_entries(request, filters: LogEntryFilters = Query(...)):  # noqa: B008
    """
    Fetches log entries.

    - Ordered in descending order of timestamp
    - Page size = 100 by default
    - Optional filters:
      - logGroupReferenceId
      - user
    """
    entries = await list_log_entries(
        log_group_reference_id=filters.log_group_reference_id,
        user=filters.user,
        offset=filters.offset,
        limit=filters.page_size,
    )

    log_entries = [
        LogEntryOut(
            id=le.id,
            user=le.user,
            timestamp=le.timestamp.isoformat(),
            description=le.description,
            type=le.type,
            properties=le.properties,
            log_group_id=le.log_group_id,
        )
        for le in entries
    ]

    return LogEntriesResponse(log_entries=log_entries)


@router.get("/log-group/{reference_id}", response=LogGroupOut)
async def get_log_group(
    request,
    reference_id: str,
    entry_types: list[str] | None = None,
):
    """
    Fetch a specific log group by reference ID.

    Returns the log group with all its properties.
    Optionally includes review statistics for calculation and reconciliation phases.
    """
    log_group = await get_log_group_with_entry_counts_by_reference_id(
        reference_id, entry_types=entry_types or []
    )

    if not log_group:
        from django.http import Http404

        raise Http404

    # Build entry_counts dictionary from annotated fields
    entry_counts = {}
    for attr_name in dir(log_group):
        if attr_name.startswith("count_"):
            entry_type = attr_name[6:]  # Remove "count_" prefix
            count_value = getattr(log_group, attr_name)
            if count_value is not None:
                entry_counts[entry_type] = count_value
    # Get users for this log group

    return LogGroupOut(
        id=log_group.id,
        created=log_group.created.isoformat(),
        type=log_group.type,
        reference_id=log_group.reference_id,
        properties=log_group.properties,
        entry_counts=entry_counts,
    )


@router.post("/log-groups", response=LogGroupOut)
async def create_log_group_endpoint(request, log_group_data: LogGroupIn):
    """
    Create a new log group.

    Creates a new log group with the specified type, reference_id, and properties.
    """

    # Create a concrete implementation of LogGroupRequest
    class ConcreteLogGroupRequest(LogGroupRequest):
        log_group_type = log_group_data.type

        def reference_id(self) -> str:
            return log_group_data.reference_id

        def properties(self) -> dict:
            return log_group_data.properties

    log_group_request = ConcreteLogGroupRequest()
    log_group = await get_or_create_log_group(log_group_request)

    return LogGroupOut(
        id=log_group.id,
        created=log_group.created.isoformat(),
        type=log_group.type,
        reference_id=log_group.reference_id,
        properties=log_group.properties,
        entry_counts={},  # New log groups have no entries yet
    )


@router.post("/log-entries", response=LogEntryOut)
async def create_log_entry_endpoint(request, log_entry_data: LogEntryIn):
    """
    Create a new log entry.

    Creates a new log entry for the specified log group.
    The user email is extracted from the JWT token automatically.
    """
    # Extract user email from JWT token
    user_email = request.auth or "anonymous"

    log_entry_request = LogEntryRequest(
        timestamp=log_entry_data.timestamp,
        log_group_reference_id=log_entry_data.log_group_reference_id,
        type=log_entry_data.type,
        properties=log_entry_data.properties,
        description=log_entry_data.description,
        user=user_email,
    )

    log_entry = await create_log_entry(log_entry_request)

    return LogEntryOut(
        id=log_entry.id,
        user=log_entry.user,
        timestamp=log_entry.timestamp.isoformat(),
        description=log_entry.description,
        type=log_entry.type,
        properties=log_entry.properties,
        log_group_id=log_entry.log_group_id,
    )
