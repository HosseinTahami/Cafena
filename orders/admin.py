# django imports
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# inner modules imports
from .models import Order, OrderItem, Table

# Register your models here.


@admin.register(Table)
class TableAdmin(ImportExportModelAdmin , admin.ModelAdmin):
    list_display = ("table_number",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ("product",)


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin , admin.ModelAdmin):
    list_display = ("id", "create_time", "paid")
    list_filter = ("paid",)
    inlines = (OrderItemInline,)
