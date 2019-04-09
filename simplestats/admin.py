from django.contrib import admin
from . import models


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("widget", "owner")
    list_filter = (("owner", admin.RelatedOnlyFieldListFilter),)


@admin.register(models.Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ("name", "public", "owner")
    list_filter = ("public", ("owner", admin.RelatedOnlyFieldListFilter))


@admin.register(models.Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("name", "public", "owner")
    list_filter = ("public", ("owner", admin.RelatedOnlyFieldListFilter))
