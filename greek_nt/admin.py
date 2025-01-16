from django.contrib import admin
from .models import Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ["id", "ref", "text", "english", "lemma"]
    list_display_links = ["id", "text"]
    search_fields = ["id", "text", "english", "lemma", "ref"]
    list_filter = ["gender", "case", "number", "tense", "voice", "mood"]
    readonly_fields = [
        field.name for field in Token._meta.fields
    ]  # All fields readonly since this is reference data

    # Make the list view more efficient
    list_select_related = True
    list_per_page = 50

    # Customize the changelist view to show more useful information
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

    # Add some helpful text at the top of the change list
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "Greek New Testament Tokens"
        return super().changelist_view(request, extra_context=extra_context)
