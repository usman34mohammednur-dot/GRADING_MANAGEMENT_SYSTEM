from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Users, Teacher,Student


class AdminRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = Users
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_admin = True
        user.is_superuser = True  
        user.is_staff = True      
        if commit:
            user.save()
        return user




class TeacherRegistrationForm(UserCreationForm):
    # Additional fields for the Teacher model
    class_room = forms.CharField(max_length=100)
    phone_num = forms.CharField(max_length=22 )

    class Meta(UserCreationForm.Meta):
        model = Users
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        # First, create the Users instance from the form
        user = super().save(commit=False)
        user.is_teacher = True
        
        if commit:
            user.save()
            
            # Then, create the associated Teacher instance
            teacher = Teacher.objects.create(
                user=user,
                class_room=self.cleaned_data.get('class_room'),
                phone_num=self.cleaned_data.get('phone_num')
            )
            
        return user
    

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'second_name', 'code', 'grade', 'homeroom_teacher', 'director']


class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'