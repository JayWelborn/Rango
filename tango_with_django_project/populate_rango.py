import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'tango_with_django_project.settings'

import django
django.setup()

from rango.models import Category, Page


def populate():
    """
    First, we will create lists of dictionaries contianing the pages
    we want to add into each category.
    Then we will create a dictionary of dictionaries for our categories.
    This will allow us to iterate through the data structures to
    add data to our models.
    """

    python_pages = [
        {
            "title": "Official Python Tutorial",
            "url": "http://docs.python.org/2/tutorial/",
            "views": 128
        },
        {
            "title": "How to Thing Like a Computer Scientist",
            "url": "http://www.greenteapress.com/thinkpython",
            "views": 64
        },
        {
            "title": "Learn Python in 10 Minutes",
            "url": "https://www.stavros.io/tutorials/python/",
            "views": 32
        },
    ]

    django_pages = [
        {
            "title": "Official Django Tutorial",
            "url": "https://docs.djangoproject.com/en/1.11/intro/tutorial01/",
            "views": 128
        },
        {
            "title": "Django Rocks",
            "url": "http://www.djangorocks.com/",
            "views": 64
        },
        {
            "title": "How to Tango with Django",
            "url": "http://www.tangowithdjango.com",
            "views": 32
        }
    ]

    php_pages = [
        {
            "title": "PHP Manual",
            "url": "http://php.net/manual/en/intro-whatis.php",
            "views": 0
        }
    ]

    perl_pages = [
        {
            "title": "Perl Foundation",
            "url": "https://www.perl.org/",
            "views": 12
        }
    ]

    programming_pages = [
        {
            "title": "Python Foundation",
            "url": "https://www.python.org",
            "views": 128
        }
    ]

    other_pages = [
        {
            "title": "Bottle",
            "url": "http://bottlepy.org/docs/dev",
            "views": 128
        },
        {
            "title": "Flask",
            "url": "https://flask.pocoo.org",
            "views": 64
        }
    ]

    cats = {
        "Python": {
            "pages": python_pages,
            "views": 128,
            "likes": 64
        },
        "Django": {
            "pages": django_pages,
            "views": 64,
            "likes": 32
        },
        "Other Frameworks": {
            "pages": other_pages,
            "views": 32,
            "likes": 16
        },
        "Perl": {
            "pages": perl_pages,
            "views": 8,
            "likes": 2
        },
        "PHP": {
            "pages": php_pages,
            "views": 12,
            "likes": 0
        },
        "Programming": {
            "pages": programming_pages,
            "views": 128,
            "likes": 128
        }
    }

    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data["views"], cat_data["likes"])
        for p in cat_data["pages"]:
            add_page(c, p["title"], p["url"], p["views"])

    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print("- {0} - {1}".format(str(c), str(p)))


def add_page(cat, title, url, views):

    p = Page.objects.get_or_create(category=cat, title=title)[0]

    p.url = url
    p.views = views
    p.save()
    return p


def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c


if __name__ == '__main__':

    print("Starting Rango population script...")
    populate()
