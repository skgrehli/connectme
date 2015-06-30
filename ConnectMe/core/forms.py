from django import forms
from django.contrib.auth.models import User
from ConnectMe.users.models import UserProfile
from django.core.exceptions import ValidationError
#from django_countries.countries import COUNTRIES
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField


class ProfileForm(forms.ModelForm):
    Gender=(('M','Male'),('F','Female'),)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), 
        max_length=30,
        required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), 
        max_length=30,
        required=False)
    email = forms.EmailField()
    address = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), 
        max_length=50,
        required=False)
    date_of_birth=forms.DateField(widget=forms.TextInput(attrs={'class':'datepicker'}))
    #country= forms.ChoiceField(COUNTRIES,required=False)

    #country=CountryField(widget=CountrySelectWidget(required=False))
    gender = forms.ChoiceField(Gender,required=False)
    phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$',required=False, 
                                error_message = ("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
             
    class Meta:
        model=UserProfile
        fields=['email','address','gender','phone_number','country']
        widgets = {'country': CountrySelectWidget()}

    def full_clean(self):
        'Strip whitespace automatically in all form fields'
        data = self.data.copy()
        for k, vs in self.data.lists():
            new_vs = []
            for v in vs:
                new_vs.append(v.strip())
            data.setlist(k, new_vs)
        self.data = data
        super(ProfileForm, self).full_clean()


class ChangePasswordForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput())
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), 
        label="Old password",
        required=True)

    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), 
        label="New password",
        required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), 
        label="Confirm new password",
        required=True)

    class Meta:
        model = User
        fields = ['id', 'old_password', 'new_password', 'confirm_password']

    def clean(self):
        super(ChangePasswordForm, self).clean()
        old_password = self.cleaned_data.get('old_password')
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        id = self.cleaned_data.get('id')
        user = User.objects.get(pk=id)
        if not user.check_password(old_password):
            self._errors['old_password'] = self.error_class(['Old password don\'t match'])
        if new_password and new_password != confirm_password:
            self._errors['new_password'] = self.error_class(['Passwords don\'t match'])
        return self.cleaned_data