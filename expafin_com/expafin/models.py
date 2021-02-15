from django.db import models

# Create your models here.
class Portfolio(models.Model):
    # Images 
    image = models.ImageField(upload_to='images/')
    # Title 
    title = models.CharField(max_length=50, default="insert title")
    # Summary 
    summary = models.CharField(max_length=200)
    # Details
    details = models.CharField(max_length=500)

    def __str__(self):
        return self.title