from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify

# Create your models here.
class Category(models.Model):
    """
    Category is a class for displaying websites with similar content.
    name = name of the category
    slug = name slugified for URL purposes
    pub_date = date the category was published
    pages = reverse lookup for pages related to a category
    """

    class Meta:
        verbose_name_plural='Categories'

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Page(models.Model):
    """
    Page will store info for displaying pages within a category
    category = reference to category to which the page belongs
    title = page title
    url = page url
    views = number of times users have viewed the page
    """
    
    category = models.ForeignKey(Category, related_name='pages')
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title
        
