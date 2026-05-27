from django.contrib import admin

from records.models import (
    AnomalyFlag,
    AuditLog,
    NormalizedEmissionRecord,
    ReviewDecision,
    UnitConversionMap,
)


@admin.register(NormalizedEmissionRecord)
class NormalizedEmissionRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "activity_category",
        "status",
        "activity_date",
        "canonical_quantity",
    )
    list_filter = ("status", "scope", "activity_category")


admin.site.register(AnomalyFlag)
admin.site.register(ReviewDecision)
admin.site.register(AuditLog)
admin.site.register(UnitConversionMap)
