from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from front_end.forms import AccountCreationForm, ReportForm, TaskForm, UpdateTaskForm, NewsForm
from api.controllers import *
from api.models import Report, Task, News
import requests
from functools import wraps

# Create your views here.

def require_authority_level(required_levels):
    """
    Decorator to require specific authority levels for views.
    required_levels can be a string or list of strings.
    Admins (A) always have access to everything.
    """
    if isinstance(required_levels, str):
        required_levels = [required_levels]
    
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Admins have access to everything
            if request.user.authority_level == 'A':
                return view_func(request, *args, **kwargs)
            # Check if user has required authority level
            if request.user.authority_level not in required_levels:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def geocode_address(address):
    url = f"https://nominatim.openstreetmap.org/search"
    # Add Bosnia and Herzegovina to the address for better accuracy
    full_address = f"{address}, Bosnia and Herzegovina"
    params = {
        "q": full_address, 
        "format": "json",
        "countrycodes": "ba",  # Restrict search to Bosnia and Herzegovina
        "limit": 1
    }
    headers = {
        "User-Agent": "bndms/1.0 (ognjen.zaric@stu.ibu.edu.ba)"
    }
    response = requests.get(url, params=params, headers=headers)
    print(response)
    if response.status_code == 200:
        results = response.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    return None, None

def home(request):
    reports = Report.objects.all()[::-1][:5]
    news = News.objects.all()[::-1][:5]
    return render(request, "Home.html", {"reports": reports, "news": news})


def register(request):
    form = AccountCreationForm(request.POST)
    if form.is_valid():
        account = form.save(commit=False)
        account.authority_level = "L"  # Automatically set to "Logged In"
        account.is_superuser = False
        account.is_staff = False
        account.is_active = True
        account.is_deleted = False
        account.save()
        return redirect("/login")
    else:
        print(form.errors)
        # form = AccountCreationForm()
    return render(request, "Register.html", {"form": form})


login = LoginView.as_view(template_name="Login.html")


def map(request):
    reports = Report.objects.all()
    return render(request, "map.html", {"reports": reports})


def reports(request):
    context = {"reports": ReportController.all()[::-1]}
    return render(request, "reports_main.html", context=context)


@login_required
def create_report(request):
    form = ReportForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False)
        report.account = request.user
        lat, lng = geocode_address(report.address)
        if lat and lng:
            report.latitude = lat
            report.longitude = lng
        report.save()
        return redirect("/")
    else:
        form = ReportForm()
    return render(request, "Create_Report.html", {"form": form})


@require_authority_level('O')
def create_task(request, pk):
    request.method = "POST"
    report = get_object_or_404(Report, pk=pk)
    form = TaskForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.report = report
        task.save()
        return redirect("/reports")
    else:
        form = TaskForm()
    return render(request, "Create_Task.html", {"form": form})


def tasks(request, pk):
    report = get_object_or_404(Report, pk=pk)
    tasks = Task.objects.filter(report=report)
    return render(request, 'Tasks_main.html', {"tasks": tasks})

@require_authority_level(['E', 'A'])
def assigned_tasks(request, pk):
    # Emergency workers can only see their own tasks, admins can see any user's tasks
    if request.user.authority_level != 'A' and request.user.username != pk:
        messages.error(request, "You can only view your own assigned tasks.")
        return redirect('home')
    tasks = Task.objects.filter(username=pk)
    return render(request, 'Tasks_main.html', {"tasks": tasks})

def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Emergency workers can only update tasks assigned to them, admins can update any task
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.authority_level != 'A' and task.username != request.user:
        messages.error(request, "You can only update tasks assigned to you.")
        return redirect('home')
    
    request.method = 'POST'
    form = UpdateTaskForm(request.POST, instance=task)
    if form.is_valid():
        task.save()
        return redirect('/')
    else:
        form = UpdateTaskForm(instance=task)
    return render(request, 'Create_Task.html', {'form': form})


@require_authority_level('O')
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    request.method = 'POST'
    form = TaskForm(request.POST, instance=task)
    if form.is_valid():
        task.save()
        return redirect('/')
    else:
        form = TaskForm(instance=task)
    return render(request, 'Create_Task.html', {'form': form})


@require_authority_level('O')
def update_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    request.method = 'POST'
    form = ReportForm(request.POST, instance=report)
    if form.is_valid():
        report.save()
        return redirect('/')
    else:
        form = ReportForm(instance=report)
    return render(request, 'Create_Report.html', {'form': form})


@require_authority_level('O')
def delete_task(request, pk):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=pk)
        task.is_deleted = True
        task.save()
        return redirect('/reports')


@require_authority_level('O')
def delete_report(request, pk):
    if request.method == 'GET':
        report = get_object_or_404(Report, pk=pk)
        report.is_deleted = True
        report.save()
        return redirect('/reports')

@require_authority_level(['O', 'A'])
def create_news(request):
    form = NewsForm(request.POST)
    if form.is_valid():
        news = form.save(commit=False)
        news.account = request.user
        news.save()
        return redirect("/")
    else:
        form = NewsForm()
    return render(request, 'Create_News.html', {'form': form})

@require_authority_level(['O', 'A'])
def update_news(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news_item)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = NewsForm(instance=news_item)
    return render(request, 'Create_News.html', {'form': form})

@require_authority_level(['O', 'A'])
def delete_news(request, pk):
    if request.method == 'GET':
        news_item = get_object_or_404(News, pk=pk)
        news_item.is_deleted = True
        news_item.save()
        return redirect('/')

def news_list(request):
    news = News.objects.filter(is_deleted=False).order_by('-date')
    return render(request, 'news_main.html', {'news': news})


