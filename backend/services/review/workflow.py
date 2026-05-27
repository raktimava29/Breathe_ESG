from django.core.exceptions import ValidationError
from django.utils import timezone

from records.models import NormalizedEmissionRecord, ReviewDecision, ReviewStatus
from services.audit import log_event


def transition_record(
    *,
    record: NormalizedEmissionRecord,
    new_status: str,
    analyst: str,
    comment: str = "",
) -> NormalizedEmissionRecord:
    allowed = {
        ReviewStatus.PENDING: {ReviewStatus.FLAGGED, ReviewStatus.APPROVED},
        ReviewStatus.FLAGGED: {ReviewStatus.APPROVED, ReviewStatus.PENDING},
        ReviewStatus.APPROVED: {ReviewStatus.LOCKED},
        ReviewStatus.LOCKED: set(),
    }

    if new_status not in ReviewStatus.values:
        raise ValidationError(f"Invalid status: {new_status}")

    current = record.status
    if new_status not in allowed.get(current, set()):
        raise ValidationError(f"Cannot transition {current} -> {new_status}")

    before = {"status": current}
    previous_status = current
    record.status = new_status
    record.reviewed_by = analyst
    record.reviewed_at = timezone.now()
    record.review_comment = comment
    record.save()

    ReviewDecision.objects.create(
        tenant=record.tenant,
        record=record,
        previous_status=previous_status,
        new_status=new_status,
        analyst=analyst,
        comment=comment,
    )

    log_event(
        tenant=record.tenant,
        entity_type="NormalizedEmissionRecord",
        entity_id=record.id,
        action=f"STATUS_{new_status}",
        actor=analyst,
        before_state=before,
        after_state={"status": new_status, "comment": comment},
    )
    return record
