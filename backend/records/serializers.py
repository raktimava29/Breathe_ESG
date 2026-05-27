from rest_framework import serializers

from ingestion.serializers import RawRecordSerializer
from records.models import (
    AnomalyFlag,
    AuditLog,
    NormalizedEmissionRecord,
    ReviewDecision,
)


class AnomalyFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnomalyFlag
        fields = ("id", "rule_code", "message", "severity", "context", "created_at")


class NormalizedRecordListSerializer(serializers.ModelSerializer):
    flag_count = serializers.SerializerMethodField()

    class Meta:
        model = NormalizedEmissionRecord
        fields = (
            "id",
            "scope",
            "activity_category",
            "activity_date",
            "period_start",
            "period_end",
            "site_code",
            "description",
            "canonical_quantity",
            "canonical_unit",
            "distance_km",
            "status",
            "batch_id",
            "data_source_id",
            "created_at",
            "flag_count",
        )

    def get_flag_count(self, obj):
        return obj.flags.count()


class NormalizedRecordDetailSerializer(serializers.ModelSerializer):
    raw_record = RawRecordSerializer(read_only=True)
    flags = AnomalyFlagSerializer(many=True, read_only=True)
    decisions = serializers.SerializerMethodField()

    class Meta:
        model = NormalizedEmissionRecord
        fields = (
            "id",
            "scope",
            "activity_category",
            "activity_date",
            "period_start",
            "period_end",
            "site_code",
            "description",
            "quantity",
            "quantity_unit",
            "canonical_quantity",
            "canonical_unit",
            "distance_km",
            "currency_amount",
            "source_fields",
            "normalization_notes",
            "status",
            "reviewed_by",
            "reviewed_at",
            "review_comment",
            "batch_id",
            "data_source_id",
            "created_at",
            "updated_at",
            "raw_record",
            "flags",
            "decisions",
        )

    def get_decisions(self, obj):
        qs = obj.decisions.order_by("-created_at")[:20]
        return ReviewDecisionSerializer(qs, many=True).data


class ReviewDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewDecision
        fields = (
            "id",
            "previous_status",
            "new_status",
            "analyst",
            "comment",
            "created_at",
        )


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = (
            "id",
            "entity_type",
            "entity_id",
            "action",
            "actor",
            "before_state",
            "after_state",
            "metadata",
            "created_at",
        )


class ReviewActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject", "lock"])
    analyst = serializers.CharField(max_length=255)
    comment = serializers.CharField(required=False, allow_blank=True, default="")
