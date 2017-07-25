from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views import generic

from .models import Category, Page, UserProfile
from .forms import CategoryForm, PageForm, RegistrationCrispyForm, SearchForm
from .webhose_search import run_query


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    """
    Get the number of visits to the site.
    We use Cookies.get() to obtain the visits cookie.
    If the cookie exists, the value returned is cast to an integer.
    If the cookie doesn't exit, then the value is set to 1.
    """
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 
                                               'last_visit', 
                                               str(datetime.now()))

    last_visit_time = datetime.strptime(last_visit_cookie[:-7], 
                                        '%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit
    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        # Update last visit cookie
        request.session['last_visit'] = str(datetime.now())
    else:
        visits = 1
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # Update/set visits cookie after creating or incrementing
    request.session['visits'] = visits


def index(request):
    """
    View for index page.
    Passes template a list of the top five rated categories, and
    the top five most viewed pages.
    """

    request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]

    # Handle cookies and session data
    visitor_cookie_handler(request)

    context_dict = {
        'categories': category_list,
        'pages': pages_list,
        'visits': request.session['visits'],
    }

    # Obtain response
    response = render(request, 'rango/index.html', context=context_dict)

    # Send response to user
    return response


def about(request):
    """
    View for about page.
    Renders template with 'name' for demonstration purposes
    """

    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

    # Handle cookies and session data
    visitor_cookie_handler(request)

    context_dict = {
        'name': "Jay Welborn",
        'visits': request.session['visits'],
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
    result_list = []

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
        context_dict['form'] = SearchForm

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    # get search results if method is POST
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
    
    # add search results to context
    context_dict['results_list'] = result_list

    return render(request, 'rango/category.html', context_dict)


@login_required
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


@login_required
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


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


@login_required
def user_logout(request):
    logout(request)
    # take user back to home page after logging out
    return HttpResponseRedirect(reverse('index'))


class MyRegistrationView(generic.FormView):
    """
    Redirect users to index page upon successful login
    """
    template_name = 'registration/registration_form.html'
    form_class = RegistrationCrispyForm
    success_url = '/rango'

    def form_valid(self, form):
        """
        saves form, logs new user in, and returns HttpResponse
        """
        form = form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return super(MyRegistrationView, self).form_valid(form)


def search(request):
    result_list = []
    form = SearchForm
    context = {}

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)

    context['results_list'] = result_list
    context['form'] = form

    return render(request, 'rango/search.html', context)


def track_url(request):
    page_id = None
    if request.method == 'GET':
        if request.GET['page_id']:

            # increments page's views
            page = Page.objects.get(id=request.GET['page_id'])
            page.views += 1
            page.save()
            # direct user to page clicked
            return redirect(str(page.url))
        else:
            return reverse(index)

@method_decorator(login_required, name='dispatch')
class ProfileView(generic.DetailView):
    """docstring for ProfileView"""
    model = UserProfile
    template_name = 'rango/profile.html'
    