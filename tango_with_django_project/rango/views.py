from django.shortcuts import render
from django.http import HttpResponse

from .models import Category, Page


def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {
        'categories': category_list,
    }
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    
    context_dict = {
        'name': "Jay Welborn"
    }
    return render (request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):

    context_dict = {}

    try:
        """
        Look for a category with the given slug
        """

        # retrieve category with the given slug
        category = Category.objects.get(slug=category_name_slug)
        # retrieve pages matching the given category
        pages = Page.objects.filter(category=category)
        # load context dictionary
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context_dict)
