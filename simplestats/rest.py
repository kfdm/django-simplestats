import datetime
import json
import logging
import time

import pytz
from dateutil.parser import parse
from rest_framework import status, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.decorators import detail_route, list_route
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import (DjangoModelPermissions,
                                        DjangoModelPermissionsOrAnonReadOnly)
from rest_framework.response import Response

from simplestats.models import (Annotation, Chart, Countdown, Location, Report,
                                Widget)
from simplestats.serializers import (ChartSerializer, CountdownSerializer,
                                     DataSerializer, LocationSerializer,
                                     ReportSerializer, StatSerializer,
                                     WidgetSerializer)

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware

logger = logging.getLogger(__name__)
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class WidgetViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    filter_backends = (OrderingFilter,)
    permission_classes = (DjangoModelPermissions,)
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return Widget.objects.filter(owner=self.request.user)
        return Widget.objects.filter(public=True)

    def search(self):
        Widget.objects.filter(label__name='name', label__value='foo')


class CountdownViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    filter_backends = (OrderingFilter,)
    permission_classes = (DjangoModelPermissions,)
    queryset = Countdown.objects.all()
    serializer_class = CountdownSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return Countdown.objects.filter(owner=self.request.user)
        return Countdown.objects.filter(public=True)


class ChartViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
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

    @detail_route(methods=['get', 'post'])
    def stats(self, request, pk=None):
        return getattr(self, 'stats_' + request.method)(request, pk)

    def stats_GET(self, request, pk):
        chart = self.get_object()
        queryset = chart.data_set.order_by('-timestamp')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DataSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = StatSerializer(queryset, many=True)
        return Response(serializer.data)

    def stats_POST(self, request, pk):
        chart = self.get_object()
        serializer = DataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(key=chart.keys)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['post'], authentication_classes=[BasicAuthentication])
    def search(self, request):
        '''Grafana Search'''
        return JsonResponse(list(
            Chart.objects.filter(
                Q(owner=request.user) | Q(public=True)
            ).values_list('keys', flat=True).distinct('label')
        ), safe=False)

    @list_route(methods=['post'], authentication_classes=[BasicAuthentication])
    def query(self, request):
        '''Grafana Query'''
        def ts(ts):
            return time.mktime(ts.timetuple()) * 1000
        body = json.loads(request.body.decode("utf-8"))
        start = make_aware(
            datetime.datetime.strptime(body['range']['from'], DATETIME_FORMAT),
            pytz.utc)
        end = make_aware(
            datetime.datetime.strptime(body['range']['to'], DATETIME_FORMAT),
            pytz.utc)
        results = []

        targets = [target['target'] for target in body['targets']]
        for chart in Chart.objects.filter(
                Q(owner=request.user) | Q(public=True)
                ).filter(keys__in=targets):
            response = {
                'target': chart.label,
                'datapoints': []
            }
            for dp in chart.data_set.filter(timestamp__gte=start, timestamp__lte=end).order_by('timestamp'):
                response['datapoints'].append([
                    dp.value,
                    ts(dp.timestamp)
                ])
            results.append(response)
        return JsonResponse(results, safe=False)

    @list_route(methods=['post'], authentication_classes=[BasicAuthentication])
    def annotations(self, request):
        '''Grafana annotation'''
        #TODO: Replace with something linked to user model
        body = json.loads(request.body.decode("utf-8"))
        start = make_aware(
            datetime.datetime.strptime(body['range']['from'], DATETIME_FORMAT),
            pytz.utc)
        end = make_aware(
            datetime.datetime.strptime(body['range']['to'], DATETIME_FORMAT),
            pytz.utc)

        results = []
        for annotation in Annotation.objects\
                .order_by('created')\
                .filter(created__gte=start)\
                .filter(created__lte=end):
            results.append({
                'annotation': body['annotation']['name'],
                'time': annotation.created_unix * 1000,
                'title': annotation.title,
                'tags': annotation.tags,
                'text': annotation.text,
                })

        return JsonResponse(results, safe=False)


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
