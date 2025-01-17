# Generated by Django 5.1.5 on 2025-01-16 16:57
from django.db import migrations
import csv
import os


def load_token_data(apps, schema_editor):
    Token = apps.get_model("greek_nt", "Token")
    data_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data",
        "macula-greek-sblgnt.tsv",
    )

    batch = []
    batch_size = 100  # Smaller batch size for memory efficiency

    with open(data_file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            # Handle the class field specially since it's a reserved word
            class_value = row.pop("class", "")

            # Create Token instance
            token = Token(
                id=row["xml:id"],
                class_field=class_value,
                ref=row["ref"],
                role=row["role"],
                type=row["type"],
                english=row["english"],
                mandarin=row["mandarin"],
                gloss=row["gloss"],
                text=row["text"],
                after=row["after"],
                lemma=row["lemma"],
                normalized=row["normalized"],
                strong=row["strong"],
                morph=row["morph"],
                person=row["person"],
                number=row["number"],
                gender=row["gender"],
                case=row["case"],
                tense=row["tense"],
                voice=row["voice"],
                mood=row["mood"],
                degree=row["degree"],
                domain=row["domain"],
                ln=row["ln"],
                frame=row["frame"],
                subjref=row["subjref"],
                referent=row["referent"],
            )
            batch.append(token)

            if len(batch) >= batch_size:
                Token.objects.bulk_create(batch)
                batch.clear()

        # Create any remaining tokens
        if batch:
            Token.objects.bulk_create(batch)


def reverse_migration(apps, schema_editor):
    Token = apps.get_model("greek_nt", "Token")
    Token.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("greek_nt", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_token_data, reverse_migration),
    ]
