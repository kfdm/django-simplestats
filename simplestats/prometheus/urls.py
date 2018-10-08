from . import views

from django.urls import path, re_path

urlpatterns = [
    path("jobs/<pk>", views.PushGateway.as_view()),
    path('metrics', views.Metrics.as_view()),
    re_path('metrics/job/(?P<api_key>[0-9a-fA-F]+)(/(?P<extra>.*))?', views.PushGateway.as_view(), ),
]
