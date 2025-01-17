from django.db import models


class Token(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    ref = models.CharField(max_length=100)
    role = models.CharField(max_length=50, blank=True)
    class_field = models.CharField(max_length=100, blank=True, db_column="class")
    type = models.CharField(max_length=100, blank=True)
    english = models.CharField(max_length=500, blank=True)
    mandarin = models.CharField(max_length=500, blank=True)
    gloss = models.CharField(max_length=500, blank=True)
    text = models.CharField(max_length=200)
    after = models.CharField(max_length=50, blank=True)
    lemma = models.CharField(max_length=200)
    normalized = models.CharField(max_length=200)
    strong = models.CharField(max_length=50)
    morph = models.CharField(max_length=100)
    person = models.CharField(max_length=50, blank=True)
    number = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    case = models.CharField(max_length=100, blank=True)
    tense = models.CharField(max_length=100, blank=True)
    voice = models.CharField(max_length=100, blank=True)
    mood = models.CharField(max_length=100, blank=True)
    degree = models.CharField(max_length=100, blank=True)
    domain = models.CharField(max_length=100, blank=True)
    ln = models.CharField(max_length=100, blank=True)
    frame = models.CharField(max_length=500, blank=True)
    subjref = models.CharField(max_length=500, blank=True)
    referent = models.CharField(max_length=500, blank=True)

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
