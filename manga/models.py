from django.db import models
from authentication.models import User

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    country = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name

class Publisher(models.Model):
    name = models.CharField(max_length=100)
    website_url = models.URLField(blank=True)
    
    def __str__(self):
        return self.name

class Manga(models.Model):
    MANGA = 'MG'
    MANHWA = 'MW'
    MANHUA = 'MH'
    TYPE_CHOICES = [
        (MANGA, 'Manga'),
        (MANHWA, 'Manhwa'),
        (MANHUA, 'Manhua'),
    ]
    
    ONGOING = 'OG'
    COMPLETED = 'CP'
    HIATUS = 'HT'
    STATUS_CHOICES = [
        (ONGOING, 'Ongoing'),
        (COMPLETED, 'Completed'),
        (HIATUS, 'Hiatus'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover = models.ImageField(upload_to='manga_covers/')
    manga_type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=MANGA)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=ONGOING)
    authors = models.ManyToManyField(Author, related_name='mangas')
    publishers = models.ManyToManyField(Publisher, related_name='mangas', blank=True)
    genres = models.ManyToManyField(Genre, related_name='mangas')
    total_views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def average_rating(self):
        from django.db.models import Avg
        return self.ratings.aggregate(Avg('score'))['score__avg'] or 0.0
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['manga_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.title

class Chapter(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.DecimalField(max_digits=10, decimal_places=2)
    title = models.CharField(max_length=255, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['chapter_number']
        unique_together = ['manga', 'chapter_number']
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'
    
    def __str__(self):
        return f"{self.manga.title} - Chapter {self.chapter_number}"

class Page(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='pages')
    page_number = models.PositiveIntegerField()
    image = models.ImageField(upload_to='chapter_pages/')
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ['page_number']
        unique_together = ['chapter', 'page_number']
    
    def __str__(self):
        return f"Page {self.page_number} of {self.chapter}"

class Rating(models.Model):
    SCORE_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'manga']
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
    
    def __str__(self):
        return f"{self.user.username} rated {self.manga.title} {self.score}/5"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='bookmarks')
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, related_name='bookmarks', null=True, blank=True)
    page = models.ForeignKey(Page, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'manga']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s bookmark for {self.manga.title}"