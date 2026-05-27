from records.models import AuditLog


def log_event(
    *,
    tenant,
    entity_type: str,
    entity_id: int,
    action: str,
    actor: str = "",
    before_state=None,
    after_state=None,
    metadata=None,
):
    return AuditLog.objects.create(
        tenant=tenant,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        before_state=before_state,
        after_state=after_state,
        metadata=metadata or {},
    )
