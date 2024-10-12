from django.db import models

class Book(models.Model):
    GENRE_CHOICES = [
        ('FAN', 'Fantasy'),
        ('ROM', 'Romance'),
        ('HOR', 'Horror'),
        ('SCI', 'Sci-Fi'),
        ('THR', 'Thriller'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    year = models.IntegerField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    
    class Meta:
        db_table = "TABLE2"

    def __str__(self):
        return f"{self.title} by {self.author}"