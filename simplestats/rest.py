import json
import logging

import pytz
from dateutil.parser import parse
from rest_framework import viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.decorators import detail_route
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.permissions import (DjangoModelPermissions,
                                        DjangoModelPermissionsOrAnonReadOnly)
from rest_framework.response import Response

from simplestats.models import Chart, Countdown, Location, Report, Stat
from simplestats.serializers import (ChartSerializer, CountdownSerializer,
                                     LocationSerializer, ReportSerializer,
                                     StatSerializer)

from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


class CountdownViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    filter_backends = (OrderingFilter,)
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Countdown.objects.all()
    serializer_class = CountdownSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return Countdown.objects.filter(owner=self.request.user)
        return Countdown.objects.filter(public=True)


class ChartViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    filter_backends = (OrderingFilter,)
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Chart.objects.all()
    serializer_class = ChartSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return Chart.objects.filter(owner=self.request.user)
        return Chart.objects.filter(public=True)


class StatViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('key',)
    permission_classes = (DjangoModelPermissions,)
    queryset = Stat.objects.all()
    serializer_class = StatSerializer


class ReportViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    filter_backends = (OrderingFilter,)
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Report.objects.filter(owner_id=self.request.user.id)


class LocationViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    filter_backends = (OrderingFilter,)
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @detail_route(methods=['post'], permission_classes=[])
    def ifttt(self, request, pk=None):
        location = get_object_or_404(Location, pk=pk)
        body = json.loads(request.body.decode("utf-8"))
        kwargs = {}
        kwargs['state'] = body['state']
        kwargs['map'] = body['location']
        kwargs['note'] = body.get('label')
        kwargs['created'] = parse(body['created'])
        if 'timezone' in body:
            kwargs['created'] = kwargs['created'].replace(tzinfo=pytz.timezone(body['timezone']))

        movement = location.record(**kwargs)

        logger.info('Logged movement from ifttt: %s', movement)
        return Response({'status': 'done'})

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Location.objects.filter(owner_id=self.request.user.id)
