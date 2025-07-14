from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student
import json


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
    return render(request, 'students/login.html')

def register_view(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    return render(request, 'students/register.html', {'form': form})

@login_required
def home_view(request):
    return render(request, 'students/home.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def get_students(request):
    if request.user.is_authenticated:
        students = Student.objects.filter(user=request.user)
        data = list(students.values())
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@csrf_exempt
def save_student(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get("name")
        subject = data.get("subject")
        mark = int(data.get("mark"))
        user = request.user

        student_id = data.get("id")

        if student_id:
            # Editing existing student
            try:
                student = Student.objects.get(id=student_id, user=user)
                student.name = name
                student.subject = subject
                student.mark = mark
                student.save()
                return JsonResponse({"message": "Updated"})
            except Student.DoesNotExist:
                return JsonResponse({"error": "Student not found"}, status=404)
        else:
            # Check for duplicate name + subject for the same user
            existing = Student.objects.filter(name=name, subject=subject, user=user).first()
            if existing:
                # Add mark to the existing one
                existing.mark += mark
                existing.save()
                return JsonResponse({"message": "Mark added to existing record"})
            else:
                # Create new record
                Student.objects.create(name=name, subject=subject, mark=mark, user=user)
                return JsonResponse({"message": "Student created"})
@csrf_exempt
def delete_student(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        student_id = data.get("id")
        Student.objects.filter(id=student_id, user=request.user).delete()
        return JsonResponse({"status": "deleted"})
    
