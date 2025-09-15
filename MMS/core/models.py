from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class Users(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    USERNAME_FIELD = 'username'
   

    def __str__(self):
        return self.username
    

class Teacher(models.Model):
    
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    class_room = models.CharField(max_length=4, null=False, blank=False, default="9A")
    phone_num = models.CharField(max_length=22, null=False, blank=False, default="251912345678" )

    def __str__(self):
        return self.user.username

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    second_name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    grade = models.CharField(max_length=10)  # Should match teacher.class_room
    homeroom_teacher = models.CharField(max_length=100)
    director = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.second_name} ({self.code})"

    class Meta:
        ordering = ['grade', 'second_name', 'first_name']


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester1_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    semester2_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
   
    @property
    def semester1_total(self):
        """Total score for semester 1 (could be used if there are multiple components)"""
        return self.semester1_score  # Can be expanded if there are multiple components

    @property
    def semester2_total(self):
        """Total score for semester 2 (could be used if there are multiple components)"""
        return self.semester2_score  # Can be expanded if there are multiple components

    @property
    def semester1_average(self):
        """Average for semester 1 (useful when there are multiple grade components)"""
        return self.semester1_score  # Currently same as total, but structure is here for expansion

    @property
    def semester2_average(self):
        """Average for semester 2 (useful when there are multiple grade components)"""
        return self.semester2_score  # Currently same as total, but structure is here for expansion

    @property
    def year_total(self):
        """Total score for the entire year"""
        if self.semester1_score is not None and self.semester2_score is not None:
            return self.semester1_score + self.semester2_score
        elif self.semester1_score is not None:
            return self.semester1_score
        elif self.semester2_score is not None:
            return self.semester2_score
        return None

    @property
    def average_score(self):
        """Annual average score"""
        if self.semester1_score is not None and self.semester2_score is not None:
            return (self.semester1_score + self.semester2_score) / 2
        elif self.semester1_score is not None:
            return self.semester1_score
        elif self.semester2_score is not None:
            return self.semester2_score
        return None


    def __str__(self):
        return f"{self.student} - {self.subject} - Rank: {self.rank or 'N/A'}"

    class Meta:
        unique_together = ('student', 'subject')
        ordering = ['student', 'subject']

class SemesterRank(models.Model):
        student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ranks')
        semester = models.CharField(max_length=10, choices=[('1', 'Semester 1'), ('2', 'Semester 2'), ('A', 'Annual')])
        rank = models.PositiveIntegerField()
        calculation_date = models.DateTimeField(auto_now=True)

        class Meta:
            unique_together = ('student', 'semester')