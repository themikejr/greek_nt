from django.views.generic import ListView, TemplateView, View
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q, Count, F, Value, Func, CharField, Avg
from django.db.models.functions import Substr
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings
from .models import Token, SearchEvent


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
        days = int(self.request.GET.get('days', 30))
        
        # Get top searches for the period
        context['days'] = days
        context['popular_searches'] = SearchEvent.objects.filter(
            timestamp__gte=timezone.now() - timezone.timedelta(days=days)
        ).values('query_text').annotate(
            count=Count('id'),
            avg_results=Avg('result_count')
        ).order_by('-count')[:50]
        
        return context


@method_decorator(
    cache_page(86400) if settings.ENVIRONMENT == "production" else lambda x: x,
    name="dispatch",
)
class SearchView(View):
    template_name = "greek_nt/search_results.html"
    paginate_by = 20

    def get(self, request):
        query = request.GET.get("q", "")
        if not query:
            return render(request, self.template_name)

        # Get matching verse IDs
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

        # Set up pagination
        paginator = Paginator(verse_ids, self.paginate_by)
        page_number = request.GET.get("page", 1)
        page = paginator.get_page(page_number)

        # Fetch tokens only for current page's verses
        verses = []
        for verse in page:
            verse_id = verse["verse_id"]
            tokens = Token.objects.filter(id__startswith=verse_id).order_by("id")

            if tokens:
                matching_tokens = [
                    token
                    for token in tokens
                    if (
                        query.lower() in token.text.lower()
                        or query.lower() in token.lemma.lower()
                        or query.lower() in token.english.lower()
                        or query.lower() in token.strong.lower()
                    )
                ]

                verses.append(
                    {
                        "ref": tokens[0].ref,
                        "tokens": tokens,
                        "matching_tokens": matching_tokens,
                    }
                )

        # Record the search event (only if there's a valid query)
        if query.strip():
            SearchEvent.objects.create(
                query_text=query[:255],  # Truncate to max length
                result_count=paginator.count
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
