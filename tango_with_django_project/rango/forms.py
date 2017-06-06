from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper

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
