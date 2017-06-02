from django.shortcuts import render
from django.http import HttpResponse

from .models import Category, Page
from .forms import CategoryForm, PageForm


def index(request):
    """
    View for index page.
    Passes template a list of the top five rated categories, and
    the top five most viewed pages.
    """

    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]
    context_dict = {
        'categories': category_list,
        'pages': pages_list
    }
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    """
    View for about page.
    Renders template with 'name' for demonstration purposes
    """

    context_dict = {
        'name': "Jay Welborn"
    }
    return render (request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    """
    Detail view for category.
    Loads category data and related page data into
    context dictionary.
    If specified category doesn't exist, returns
    empty list.
    """

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


def add_category(request):
    """
    View for allowing users to add categories.
    CategoryForm defined in rango.forms.py
    """

    form = CategoryForm()

    # Is HTTP method POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Validates form
        if form.is_valid():
            form.save(commit=True)
            # Take user back to index page where they will see their new 
            # category listed
            return index(request)

        else:
            # Print errors to terminal
            print(form.errors)

    return render(request, 'rango/add_category.html/', {'form': form})


def add_page(request, category_name_slug):
    """
    View for allong users to add pages.
    PageForm defined in rango.forms.py
    """

    try:
        category = Category.objects.get(slug=category_name_slug)

    except Category.DoesNotExist:
        category = None

    form = PageForm()

    # handles incoming data when form is posted
    if request.method == 'POST':
        form = PageForm(request.POST)

        # saves model if form is valid
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)

        # print errors to terminal if form isn't valid
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)
