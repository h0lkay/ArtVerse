# Generated by Django 4.2.20 on 2025-03-13 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_artworkforsale'),
    ]

    operations = [
        migrations.AddField(
            model_name='artworkforsale',
            name='category',
            field=models.CharField(choices=[('featured', 'Featured'), ('furry', 'Furry'), ('pony', 'Pony'), ('human', 'Human'), ('adoptables', 'Adoptables'), ('crafts', 'Crafts')], default='featured', max_length=20),
        ),
    ]
