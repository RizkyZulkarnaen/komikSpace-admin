from django.db import models
from authentication.models import User
from manga.models import Manga, Chapter

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(manga__isnull=False) | 
                    models.Q(chapter__isnull=False)
                ),
                name='comment_manga_or_chapter'
            )
        ]
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.manga or self.chapter}"
