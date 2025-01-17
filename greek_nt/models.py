from django.db import models


class Token(models.Model):
    # Primary identifier (originally xml:id)
    id = models.CharField(max_length=12, primary_key=True)

    # Reference and role fields
    ref = models.CharField(max_length=20)  # e.g., "MAT 1:1!1"
    role = models.CharField(max_length=10, blank=True)  # Changed from max_length=1

    # Classification fields
    class_field = models.CharField(
        max_length=20, blank=True, db_column="class"
    )  # Using db_column as class is reserved
    type = models.CharField(max_length=20, blank=True)

    # Translation fields
    english = models.CharField(max_length=50, blank=True)
    mandarin = models.CharField(max_length=50, blank=True)
    gloss = models.CharField(max_length=100, blank=True)

    # Greek text fields
    text = models.CharField(max_length=50)  # Original Greek text
    after = models.CharField(max_length=5, blank=True)  # Punctuation/space after token
    lemma = models.CharField(max_length=50)
    normalized = models.CharField(max_length=50)

    # Reference numbers
    strong = models.CharField(max_length=10)  # Strong's number
    morph = models.CharField(max_length=20)  # Morphological tag

    # Grammatical features
    person = models.CharField(max_length=10, blank=True)
    number = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    case = models.CharField(max_length=20, blank=True)
    tense = models.CharField(max_length=20, blank=True)
    voice = models.CharField(max_length=20, blank=True)
    mood = models.CharField(max_length=20, blank=True)
    degree = models.CharField(max_length=20, blank=True)

    # Semantic fields
    domain = models.CharField(max_length=20, blank=True)
    ln = models.CharField(max_length=20, blank=True)  # Louw-Nida reference

    # Reference fields
    frame = models.CharField(max_length=100, blank=True)
    subjref = models.CharField(max_length=100, blank=True)
    referent = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "token"  # Explicitly set table name
        indexes = [
            models.Index(fields=["text"]),
            models.Index(fields=["ref"]),  # Common lookup by reference
            models.Index(fields=["lemma"]),  # Common lookup by lemma
            models.Index(fields=["strong"]),  # Common lookup by Strong's number
            models.Index(fields=["id"], name="token_id_prefix_idx"),
            models.Index(
                fields=["text", "lemma", "english", "strong"], name="token_search_idx"
            ),
        ]

    def __str__(self):
        return f"{self.ref} - {self.text} ({self.english})"
