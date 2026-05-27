from rest_framework import generics

from tenants.models import Tenant
from tenants.serializers import TenantSerializer


class TenantListView(generics.ListAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
