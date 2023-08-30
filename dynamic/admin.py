# django imports
from django.contrib import admin

# inner modules imports
from .models import PageData, Footer, Dashboard


# Register your models here.
@admin.register(PageData)
class PageDataAdmin(admin.ModelAdmin):
    readonly_fields = [
        "banner_preview",
    ]
    list_display = ("name", "title", "target_name", "banner_preview")
    search_fields = ("name", "title", "targer_name")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "target_name",
                    "title",
                    ("banner", "banner_preview"),
                    "route",
                    "footer",
                )
            },
        ),
    )


@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    readonly_fields = ["logo_preview"]
    list_display = ("footer_name", "footer_phone", "logo_preview")
    search_fields = ("footer_name", "footer_phone", "footer_text")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "footer_name",
                    "footer_phone",
                    ("footer_logo", "logo_preview"),
                    "footer_address",
                    "footer_text",
                )
            },
        ),
        (
            "Social Links",
            {
                "classes": ("collapse", "close"),
                "fields": (
                    "footer_youtube",
                    "footer_telegram",
                    "footer_instagram",
                    "footer_googleplus",
                    "footer_twitter",
                ),
            },
        ),
    )

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "target_name",)
    search_fields = ("name", "title", "targer_name", "menu_bg_color")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "target_name",
                    "title",
                    "menu_bg_color",
                )
            },
        ),
    )
