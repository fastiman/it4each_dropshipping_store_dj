from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        # cleaned_data = super(LoginForm, self).clean()
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        try:
            self.user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(f'The user with username {username} does not exist!')

        if not self.user.check_password(password):
            raise forms.ValidationError(f'The password is incorrect!')


class RegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['username'].widget.attrs['placeholder'] = 'Enter your login'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email'
        self.fields['password'].widget.attrs['placeholder'] = 'Enter your password'
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Enter Your password'})
        }
