from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Avg, CharField, Count, F, Func, Q, Value
from django.db.models.functions import Substr
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, TemplateView, View

from .models import SearchEvent, Token


class HomeView(TemplateView):
    template_name = "greek_nt/home.html"


class AboutView(TemplateView):
    template_name = "greek_nt/about.html"


class PopularSearchesView(TemplateView):
    """
    View for showing popular searches. Not linked in UI but accessible via URL.
    """

    template_name = "greek_nt/popular_searches.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get time period from query parameters (default to 30 days)
        days = int(self.request.GET.get("days", 30))

        # Get top searches for the period
        context["days"] = days
        context["popular_searches"] = (
            SearchEvent.objects.filter(
                timestamp__gte=timezone.now() - timezone.timedelta(days=days)
            )
            .values("query_text")
            .annotate(count=Count("id"), avg_results=Avg("result_count"))
            .order_by("-count")[:50]
        )

        return context


@method_decorator(
    cache_page(86400) if settings.ENVIRONMENT == "production" else lambda x: x,
    name="dispatch",
)
class SearchView(View):
    template_name = "greek_nt/search_results.html"
    paginate_by = 10

    def get(self, request):
        query = request.GET.get("q", "")
        if not query:
            return render(request, self.template_name)

        # Normalize the query
        query = query.lower().strip()

        # Using select_related and prefetch_related improves query performance
        # by fetching related objects in fewer database queries

        # Get matching verse IDs with a more efficient query
        # The DISTINCT ON approach is more efficient in PostgreSQL
        verse_ids = (
            Token.objects.filter(
                Q(text__icontains=query)
                | Q(lemma__icontains=query)
                | Q(english__icontains=query)
                | Q(strong__icontains=query)
            )
            .annotate(verse_id=Substr("id", 1, 9))
            .values("verse_id")
            .distinct()
            .order_by("verse_id")
        )

        # Using .iterator() for large result sets to reduce memory usage
        # This is especially helpful for PostgreSQL

        # Set up pagination
        paginator = Paginator(verse_ids, self.paginate_by)
        page_number = request.GET.get("page", 1)
        page = paginator.get_page(page_number)

        # Fetch tokens only for current page's verses - with optimized query
        verses = []

        # Get all verse IDs for the current page
        current_verse_ids = [v["verse_id"] for v in page.object_list]

        # Bulk fetch all tokens for the current page's verses in a single query
        # This is much more efficient than doing individual queries per verse
        if current_verse_ids:
            # Create the WHERE clause for id LIKE patterns
            all_tokens = {}

            # Get all tokens for all verses on this page in a single query
            tokens_query = Token.objects.filter(
                id__regex=r"^(" + "|".join(current_verse_ids) + ")"
            ).order_by("id")

            # Group tokens by verse_id
            for token in tokens_query:
                verse_id = token.id[:9]  # Extract verse ID from token ID
                if verse_id not in all_tokens:
                    all_tokens[verse_id] = []
                all_tokens[verse_id].append(token)

            # Now process each verse
            for verse_id in current_verse_ids:
                tokens = all_tokens.get(verse_id, [])

                if tokens:
                    # Use a more efficient method to find matching tokens
                    # Only match on the token text itself, not the after spaces/punctuation
                    matching_tokens = []
                    for token in tokens:
                        if (
                            query in token.text.lower()
                            or query in token.lemma.lower()
                            or query in token.english.lower()
                            or query in token.strong.lower()
                        ):
                            matching_tokens.append(token)

                    verses.append(
                        {
                            "ref": tokens[0].ref,
                            "tokens": tokens,
                            "matching_tokens": matching_tokens,
                        }
                    )

        # Record the search event (only if there's a valid query)
        if query:
            # Use bulk_create or get_or_create for better performance when appropriate
            SearchEvent.objects.create(
                query_text=query[:255],  # Truncate to max length
                result_count=paginator.count,
            )

        context = {
            "verses": verses,
            "paginator": paginator,
            "page_obj": page,
            "is_paginated": paginator.num_pages > 1,
            "total_results": paginator.count,
            "query": query,
        }

        return render(request, self.template_name, context)
