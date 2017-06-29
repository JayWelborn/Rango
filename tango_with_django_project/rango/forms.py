from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FieldWithButtons, StrictButton

from registration.forms import RegistrationForm

from .models import Category, Page, UserProfile


class CrispyForm (forms.ModelForm):
    """
    SubClass for adding FormHelper from crispy_forms
    http://django-crispy-forms.readthedocs.io/en/latest/crispy_tag_forms.html
    """
    def __init__(self, *args, **kwargs):
        super(CrispyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()


class CategoryForm (CrispyForm):
    """
    Form for letting users create a new category
    name - name of category
    views - hidden field setting views to 0
    likes - hidden field setting likes to 0
    slug - hidden field. slug will be created when the view performs Category.save()
    """
    name = forms.CharField(help_text='Please enter the Category Name')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.helper.form_id = 'category_form'
        self.helper.form_method = 'post'
        self.helper.form_action = '/rango/add_category/'
        self.helper.add_input(Submit('submit', 'Add Category'))


class PageForm(CrispyForm):
    """
    Form for letting users create a new page
    title - title of page
    url - web address of page
    views - hidden field setting views to 0
    """
    title = forms.CharField(help_text='Please enter the Page Title')
    url = forms.CharField(help_text='Please enter the URL of the page')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page
        exclude = ('category',)

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # add http:// to urls without it
        if url and not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://' + url
            cleaned_data['url'] = url

            return cleaned_data

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.helper.form_id = 'page_form'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Add Page'))


class UserForm(CrispyForm):
    """
    Form for creating a new user
    password - password (duh)
    username - username
    email - email
    """

    # specify widget for password
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper.form_id = 'user_form'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'


class UserProfileForm(CrispyForm):
    """
    Form for creating UserProfile (see rango.models)
    adds fields for:
    website - user's website url
    picture - profile picture for user
    """

    class Meta:
        model = UserProfile
        fields = ('website', 'picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.helper.form_id = 'user_profile_form'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Register'))


class RegistrationCrispyForm(CrispyForm):
    """
    Allows user to register for a new account.
    Saves 'username', 'email', 'password', to User model
    Saves 'website', 'picture' to UserProfile model
    Assigns User model to UserProfile via OnetoOne field
    """

    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    website = forms.URLField(required=False)
    picture = forms.ImageField(required=False)
    

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super(RegistrationCrispyForm, self).__init__(*args, **kwargs)
        self.helper.form_id = 'registration_form'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        self.helper.add_input(Submit('submit', 'Register'))

    def save(self):
        """
        Creates and saves new User object with username, password, and email.
        Creates and saves new UserProfile object with website and picture
        """
        user = User.objects.create(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
            )

        password = self.cleaned_data['password']
        password_confirmation = self.cleaned_data['confirm_password']

        if password and password_confirmation and password==password_confirmation:
            user.set_password(self.cleaned_data['password'])
            user.save()

        website = self.cleaned_data['website']
        picture = self.cleaned_data['picture']
        profile = UserProfile.objects.create(user=user)

        if website:
            profile.website = website

        if picture:
            profile.picture = picture

        profile.save()
        return self

class SearchForm(forms.Form):

    query = forms.CharField(
        help_text='Find Pages to add to Rango',
        label='',
        required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'search'
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        self.helper.layout = Layout (
            FieldWithButtons(
                'query', 
                StrictButton('Search', type='submit')))
