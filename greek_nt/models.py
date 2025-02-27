from django.db import models
from django.utils import timezone


class Token(models.Model):
    # Primary identifier (originally xml:id)
    id = models.CharField(max_length=25, primary_key=True)

    # Reference and role fields
    ref = models.CharField(max_length=100)  # e.g., "MAT 1:1!1"
    role = models.CharField(max_length=20, blank=True)  # e.g., "s", "v", "adv"

    # Classification fields
    class_field = models.CharField(
        max_length=100, blank=True, db_column="class"
    )  # Using db_column as class is reserved
    type = models.CharField(max_length=100, blank=True)

    # Translation fields
    english = models.CharField(max_length=100, blank=True)
    mandarin = models.CharField(max_length=100, blank=True)
    gloss = models.CharField(max_length=400, blank=True)

    # Greek text fields
    text = models.CharField(max_length=100)  # Original Greek text
    after = models.CharField(max_length=40, blank=True)  # Punctuation/space after token
    lemma = models.CharField(max_length=100)
    normalized = models.CharField(max_length=100)

    # Reference numbers
    strong = models.CharField(max_length=20)  # Strong's number
    morph = models.CharField(max_length=100)  # Morphological tag

    # Grammatical features
    person = models.CharField(max_length=20, blank=True)
    number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    case = models.CharField(max_length=100, blank=True)
    tense = models.CharField(max_length=100, blank=True)
    voice = models.CharField(max_length=100, blank=True)
    mood = models.CharField(max_length=100, blank=True)
    degree = models.CharField(max_length=100, blank=True)

    # Semantic fields
    domain = models.CharField(max_length=100, blank=True)
    ln = models.CharField(max_length=100, blank=True)  # Louw-Nida reference
    
    # SDBG definitional data
    sense_id = models.CharField(max_length=400, blank=True)
    semantic_domain = models.CharField(max_length=400, blank=True)
    contextual_glosses = models.CharField(max_length=1000, blank=True)
    definition = models.TextField(blank=True)

    # Reference fields
    frame = models.CharField(max_length=400, blank=True)
    subjref = models.CharField(max_length=400, blank=True)
    referent = models.CharField(max_length=400, blank=True)

    class Meta:
        db_table = "token"  # Explicitly set table name
        indexes = [
            # Standard indexes that work with all database backends
            models.Index(fields=["text"], name="token_text_idx"),
            models.Index(fields=["ref"], name="token_ref_idx"),
            models.Index(fields=["lemma"], name="token_lemma_idx"),
            models.Index(fields=["english"], name="token_english_idx"),
            models.Index(fields=["strong"], name="token_strong_idx"),
            models.Index(fields=["id"], name="token_id_prefix_idx"),
            
            # Composite index for search operations
            models.Index(
                fields=["text", "lemma", "english", "strong"], 
                name="token_search_idx"
            ),
        ]

    def __str__(self):
        return f"{self.ref} - {self.text} ({self.english})"


class SearchEvent(models.Model):
    """
    Records each individual search event with timestamp for detailed analytics.
    This approach allows for more flexible data analysis including trends over time.
    """
    query_text = models.CharField(max_length=255)
    result_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = "search_events"
        indexes = [
            models.Index(fields=["query_text"]),
            models.Index(fields=["timestamp"]),
        ]
    
    def __str__(self):
        return f"{self.query_text} ({self.result_count} results) - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def popular_queries(cls, days=30, limit=10):
        """
        Returns the most popular search queries within the specified time period.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries with query_text, count, and avg_results
        """
        from django.db.models import Count, Avg
        from django.utils import timezone
        
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        return cls.objects.filter(timestamp__gte=start_date) \
            .values('query_text') \
            .annotate(
                count=Count('id'),
                avg_results=Avg('result_count')
            ) \
            .order_by('-count')[:limit]
