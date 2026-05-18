from django.contrib import admin
from .models import Post,Category
from django.utils.html import format_html


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "created_at"]
    fields = ["title", "short_description", "icon", "icon_preview", "created_at"]
    search_fields = ["title", "short_desctiption"]
    list_filter = [
        "created_at",
    ]
    date_hierarchy = "created_at"
    ordering = [
        "-created_at",
    ]
    readonly_fields = [
        "created_at",
        "icon_preview"
    ]

    def icon_preview(self, obj):
        if obj.icon:
            return format_html(obj.icon)
        else:
            return "No category icon!"
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title","created_at"]
    search_fields = ["title", "short_description" ]
    fields=["title","short_description","content","image","category","author","created_at","icon_post_preview"]
    list_filter = [
        "category",
        "created_at",
    ]
    date_hierarchy = "created_at"
    ordering = [
        "-created_at",
    ]
    readonly_fields = [
        "created_at",
        "icon_post_preview"
    ]


    def icon_post_preview(self, obj):
        if obj.image:
            return format_html("<img src={}>", obj.image.url)
        else:
            return "No post icon!"

    # format_html("<img src={}>", obj.image.url)