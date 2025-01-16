from django.views.generic import ListView, TemplateView
from django.db.models import Q
from .models import Token


class HomeView(TemplateView):
    template_name = "greek_nt/home.html"


class SearchView(ListView):
    model = Token
    template_name = "greek_nt/search_results.html"
    context_object_name = "verses"
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        if not query:
            return []

        # First find matching tokens
        matching_tokens = Token.objects.filter(
            Q(text__icontains=query)
            | Q(lemma__icontains=query)
            | Q(english__icontains=query)
            | Q(strong__icontains=query)
        )

        # Get unique verse identifiers from matching tokens
        verse_ids = set()
        for token in matching_tokens:
            # Extract book, chapter, verse from token ID
            verse_id = token.id[:9]  # First 9 digits identify the verse
            verse_ids.add(verse_id)

        # For each verse that has a match, get all its tokens
        verses = []
        for verse_id in verse_ids:
            # Get all tokens for this verse using ID pattern
            verse_tokens = Token.objects.filter(id__startswith=verse_id).order_by("id")

            # Get the matching tokens for this verse
            verse_matches = matching_tokens.filter(id__startswith=verse_id)

            verses.append(
                {
                    "ref": verse_tokens.first().ref,  # Reference from first token
                    "tokens": verse_tokens,
                    "matching_tokens": verse_matches,
                }
            )

        # Sort verses by reference
        verses.sort(key=lambda x: x["tokens"].first().id)
        return verses
