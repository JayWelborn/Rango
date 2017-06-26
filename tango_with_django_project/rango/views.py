from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic

from .models import Category, Page, UserProfile
from .forms import CategoryForm, PageForm, RegistrationCrispyForm


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


def register(request):
    """
    Will allow users to register for a new account.
    'register' is a boolean value for whether or not
    a user is registered. Defaults to false so that 
    the page will render the normal form. When true
    the page will create the UserProfile object and
    log the user in.
    """

    registered = False

    # Process form data if HTTP method is POST
    if request.method == 'POST':
        # attempt to get data from raw info
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # only creates new user if both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # save info to database
            user=user_form.save()

            # hash password then update user object
            user.set_password(user.password)
            user.save()

            # add info for UserProfile portion.
            # waits to commit info to database until after user
            # instance is set to avoid null error
            profile = profile_form.save(commit=False)
            profile.user = user

            # if user provided a profile picture
            # get it from input form and
            # put it in UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # NOW save model to database
            profile.save()

            # Update registered variable to True
            # to indicate registration was successful
            registered = True

        else:
            # in case of invalid forms
            # print errors to console
            print(user_form.errors, profile_form.errors)

    # if NOT HTTP POST
    else:
        # set form variables to blank instances of Form classes
        user_form = UserForm()
        profile_form = UserProfileForm()

    # render request depending on context
    return render(
            request,
            'rango/register.html',
            {
                'user_form': user_form,
                'profile_form': profile_form,
                'registered': registered
            }
        )


def user_login(request):
    """
    Login page.
    Displays form on GET
    Validates credentials on POST
    """

    if request.method == 'POST':
        # Get info from POST data
        username = request.POST.get('username')
        password = request.POST.get('password')

        # django's built in auth returns a User object if data is valid
        user = authenticate(username=username, password=password)

        # if user exists, the credentials were valid
        if user:
            # ensure account hasn't been disabled
            if user.is_active:
                login(request, user=user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # stop inactive accounts from logging in
                return HttpResponse("Your Rango account is disabled")

        # bad login credentials presented
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            context_dict = {'error_message': 'Incorrect login credentials.'}
            return render(request, 'rango/login.html', context_dict)

    # method isn't POST, so display login form
    else:
        return render(request, 'rango/login.html', {})


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
        saves form, returns HttpResponse
        """
        form = form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return super(MyRegistrationView, self).form_valid(form)
