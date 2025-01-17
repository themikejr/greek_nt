from django.views.generic import ListView, TemplateView
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import Token


class HomeView(TemplateView):
    template_name = "greek_nt/home.html"


@method_decorator(
    cache_page(86400) if settings.ENVIRONMENT == "production" else lambda x: x,
    name="dispatch",
)
class SearchView(ListView):
    model = Token
    template_name = "greek_nt/search_results.html"
    context_object_name = "verses"
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        if not query:
            return []

        # Find matching verse IDs with pagination
        matching_tokens = Token.objects.filter(
            Q(text__icontains=query)
            | Q(lemma__icontains=query)
            | Q(english__icontains=query)
            | Q(strong__icontains=query)
        ).values_list("id", flat=True)

        # Get unique verse IDs (first 9 chars of token ID)
        verse_ids = {token_id[:9] for token_id in matching_tokens}

        # Get all tokens for matching verses
        all_tokens = Token.objects.filter(
            id__in=[
                f"{verse_id}{i:03d}"
                for verse_id in verse_ids
                for i in range(1, 51)  # Max tokens per verse
            ]
        ).order_by("id")

        # Group into verses
        verses = []
        current_verse = []
        current_matches = []
        current_verse_id = None

        for token in all_tokens:
            verse_id = token.id[:9]

            if verse_id != current_verse_id:
                if current_verse:
                    verses.append(
                        {
                            "ref": current_verse[0].ref,
                            "tokens": current_verse,
                            "matching_tokens": current_matches,
                        }
                    )
                current_verse = []
                current_matches = []
                current_verse_id = verse_id

            current_verse.append(token)
            if (
                query.lower() in token.text.lower()
                or query.lower() in token.lemma.lower()
                or query.lower() in token.english.lower()
                or query.lower() in token.strong.lower()
            ):
                current_matches.append(token)

        if current_verse:
            verses.append(
                {
                    "ref": current_verse[0].ref,
                    "tokens": current_verse,
                    "matching_tokens": current_matches,
                }
            )

        return verses

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_results"] = len(self.get_queryset())
        return context
