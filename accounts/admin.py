# django imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from import_export.admin import ImportExportModelAdmin

# inner modules imports
from .forms import PersonnelCreationForm, PersonnelChangeForm
from .models import Personnel, Customer


@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ("phone_number",)
    search_fields = ("phone_number",)


class PersonnelAdmin(ImportExportModelAdmin, UserAdmin):
    add_form = PersonnelCreationForm
    form = PersonnelChangeForm

    list_display = ("full_name", "phone_number", "email", "is_admin")
    list_filter = ("is_admin", "is_active")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "full_name",
                    "email",
                    "phone_number",
                    "image",
                    "password",
                )
            },
        ),
        ("Permissions", {"fields": ("is_admin", "is_active", "is_superuser","last_login","groups", "user_permissions")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "full_name",
                    "email",
                    "phone_number",
                    "image",
                    "password1",
                    "password2",
                ),
            },
        ),
        ("Permissions", {"fields": ("is_admin", "is_active")}),
    )
    search_fields = (
        "email",
        "full_name",
        "phone_number",
    )
    ordering = ("full_name",)
    filter_horizontal = ("groups", "user_permissions")

    def get_form(self, request, obj, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields["is_superuser"].disabled = True
        return form

admin.site.register(Personnel, PersonnelAdmin)
