from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required,user_passes_test
from .forms import TeacherRegistrationForm, StudentRegistrationForm
from .models import Student,Teacher,Subject,Users,SemesterRank
from .forms import TeacherRegistrationForm,StudentRegistrationForm,StudentForm,AdminRegistrationForm


def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required(login_url='core:login')
@user_passes_test(is_admin)
def register_admin(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return messages.success(request, 'Admin account created successfully!')
           
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'base/register_admin.html', {'form': form})





@login_required(login_url='core:login')
@user_passes_test(is_admin)
def admin_dashboard(request):
    teacher_form = TeacherRegistrationForm()
    student_form = StudentRegistrationForm()

    if request.method == 'POST':
        if 'submit_teacher' in request.POST:
            teacher_form = TeacherRegistrationForm(request.POST)
            if teacher_form.is_valid():
                teacher_form.save()
                return redirect('core:admin_dashboard')

        elif 'submit_student' in request.POST:
            student_form = StudentRegistrationForm(request.POST)
            if student_form.is_valid():
                student_form.save()
                return redirect('core:admin_dashboard')

    context = {
        'teacher_form': teacher_form,
        'student_form': student_form,
        'teachers': Teacher.objects.select_related('user'),
        'students': Student.objects.all(),
    }
    return render(request, 'base/admin_dashboard.html', context)






@login_required(login_url='core:login')
@user_passes_test(is_admin)
def edit_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    user = teacher.user

    if request.method == 'POST':
        teacher_form = TeacherRegistrationForm(request.POST, instance=user)
        if teacher_form.is_valid():
            user = teacher_form.save(commit=False)
            user.is_teacher = True  # Ensure this is still True
            user.save()

            
            teacher.class_room = request.POST.get('class_room', teacher.class_room)
            teacher.phone_num = request.POST.get('phone_num', teacher.phone_num)
            teacher.save()

            return redirect('core:admin_dashboard')
    else:
        
        initial = {
            'class_room': teacher.class_room,
            'phone_num': teacher.phone_num,
        }
        teacher_form = TeacherRegistrationForm(instance=user, initial=initial)

    context = {
        'teacher_form': teacher_form,
        'teacher': teacher,
    }
    return render(request, 'base/edit_teacher.html', context)



@login_required(login_url='core:login')
@user_passes_test(is_admin)
def delete_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    user = teacher.user

    if request.method == 'POST':
        
        user.delete()
        return redirect('core:admin_dashboard')

    context = {
        'teacher': teacher,
    }
    return render(request, 'base/delete_teacher.html', context)







@login_required(login_url='core:login')
@user_passes_test(is_admin)
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentRegistrationForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        return redirect('core:admin_dashboard')
    return render(request, 'base/edit_student.html', {'form': form})

@login_required(login_url='core:login')
@user_passes_test(is_admin)
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect('core:admin_dashboard')





def home(request):
    return render(request, 'base/home_page.html')
def about(request):
    return render(request, 'base/about.html')


def logout_view(request):
    logout(request)
    return redirect('core:login')

def logout_student(request):
    request.session.flush()
    return redirect('core:home')


def custom_login_view(request):
    if request.user.is_authenticated:
        # Redirect already logged-in users
        if request.user.is_superuser:
            return redirect('core:admin_dashboard')
        elif getattr(request.user, 'is_teacher', False):
            return redirect('core:teacher_dashboard')
        else:
            return redirect('core:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Redirect based on role
            if user.is_superuser:
                return redirect('core:admin_dashboard')
            elif getattr(user, 'is_teacher', False):
                return redirect('core:teacher_dashboard')
            else:
                return redirect('core:home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'base/login.html')

    





@login_required(login_url='core:login')
def teacher_dashboard(request):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed here.")

    teacher = get_object_or_404(Teacher, user=request.user)
    students = Student.objects.filter(grade=teacher.class_room)
    graded_ids = Grade.objects.filter(student__in=students).values_list('student_id', flat=True).distinct()
    student_status = []
    for student in students:
        student_status.append({
            'student': student,
            'has_grades': student.id in graded_ids
        })

    return render(request, 'base/teacher_dashboard.html', {
        'teacher': teacher,
        'student_status': student_status
    })


@login_required(login_url='core:login')
def add_or_edit_grades(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    teacher = get_object_or_404(Teacher, user=request.user)

    # Verify teacher has permission for this student
    if student.grade != teacher.class_room:
        return HttpResponseForbidden("Not your student")

    subjects = Subject.objects.all()
    student_form = StudentForm(instance=student)
    is_editing = Grade.objects.filter(student=student).exists()

    if request.method == 'POST':
        student_form = StudentForm(request.POST, instance=student)
        if student_form.is_valid():
            student_form.save()
            
            # Process subject grades
            for subject in subjects:
                sem1 = request.POST.get(f'sem1_{subject.id}')
                sem2 = request.POST.get(f'sem2_{subject.id}')
                
                if sem1 or sem2:
                    grade, _ = Grade.objects.get_or_create(
                        student=student, 
                        subject=subject
                    )
                    grade.semester1_score = float(sem1) if sem1 else None
                    grade.semester2_score = float(sem2) if sem2 else None
                    grade.save()
            
            # Process semester ranks (if provided)
            sem1_rank = request.POST.get('sem1_rank')
            sem2_rank = request.POST.get('sem2_rank')
            annual_rank = request.POST.get('annual_rank')
            
            if sem1_rank:
                SemesterRank.objects.update_or_create(
                    student=student,
                    semester='1',
                    defaults={'rank': int(sem1_rank)}
                )
            
            if sem2_rank:
                SemesterRank.objects.update_or_create(
                    student=student,
                    semester='2',
                    defaults={'rank': int(sem2_rank)}
                )
            
            if annual_rank:
                SemesterRank.objects.update_or_create(
                    student=student,
                    semester='A',
                    defaults={'rank': int(annual_rank)}
                )
            
            return redirect('core:teacher_dashboard')

    # Get existing grades and ranks
    grades_dict = {g.subject.id: g for g in Grade.objects.filter(student=student)}
    ranks = {
        '1': SemesterRank.objects.filter(student=student, semester='1').first(),
        '2': SemesterRank.objects.filter(student=student, semester='2').first(),
        'A': SemesterRank.objects.filter(student=student, semester='A').first(),
    }

    return render(request, 'base/submit_grade.html', {
        'student': student,
        'student_form': student_form,
        'subjects': subjects,
        'grades': grades_dict,
        'ranks': ranks,
        'is_editing': is_editing,
    })


def student_access(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip().lower()
        code = request.POST.get('code', '').strip()
        grade = request.POST.get('grade', '').strip()

        # Try to find the student
        student = Student.objects.filter(
            first_name__iexact=name,
            code__iexact=code,
            grade=grade
        ).first()

        if student:
            # Save student ID in session
            request.session['student_authenticated'] = student.id
            return redirect('core:view_student_grades', student_id=student.id)
        else:
            return render(request, 'base/student_access.html', {
                'error': 'No matching student found. Please check your inputs.'
            })

    return render(request, 'base/student_access.html')






from django.http import HttpResponseForbidden, Http404
from .models import Student, Grade


def view_student_grades(request, student_id):
    auth_id = request.session.get('student_authenticated')
    student = get_object_or_404(Student, pk=student_id)

    if not auth_id or int(auth_id) != student_id:
        return HttpResponseForbidden("Access Denied: You are not allowed to view this student's grades.")
    
    
    grades = Grade.objects.filter(student=student).select_related('subject')
    ranks = SemesterRank.objects.filter(student=student)
    
    # Calculate totals and averages
    total_sem1 = sum(g.semester1_score for g in grades if g.semester1_score is not None)
    total_sem2 = sum(g.semester2_score for g in grades if g.semester2_score is not None)
    
    sem1_scores = [g.semester1_score for g in grades if g.semester1_score is not None]
    sem2_scores = [g.semester2_score for g in grades if g.semester2_score is not None]
    avg_scores = [g.average_score for g in grades if g.average_score is not None]
    
    avg_sem1 = sum(sem1_scores) / len(sem1_scores) if sem1_scores else None
    avg_sem2 = sum(sem2_scores) / len(sem2_scores) if sem2_scores else None
    avg_avg = sum(avg_scores) / len(avg_scores) if avg_scores else None
    
    # Get ranks
    rank_sem1 = ranks.filter(semester='1').first()
    rank_sem2 = ranks.filter(semester='2').first()
    rank_annual = ranks.filter(semester='A').first()
    
    context = {
        'student': student,
        'grades': grades,
        'total_sem1': total_sem1,
        'total_sem2': total_sem2,
        'total_avg': (total_sem1 + total_sem2) / 2 if total_sem1 is not None and total_sem2 is not None else None,
        'avg_sem1': avg_sem1,
        'avg_sem2': avg_sem2,
        'avg_avg': avg_avg,
        'rank_sem1': rank_sem1.rank if rank_sem1 else None,
        'rank_sem2': rank_sem2.rank if rank_sem2 else None,
        'rank_annual': rank_annual.rank if rank_annual else None,
    }
    
    
    
    return render(request, 'base/student_grade.html', context)




@login_required(login_url='core:login')
@user_passes_test(is_admin)
def delete_admin(request, pk):
    user_delete = get_object_or_404(Users, pk=pk)

    if request.method == 'POST':
        user_delete.delete()
    return redirect('core:home')