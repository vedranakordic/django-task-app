from django.contrib import messages
from tasks.models import Task
from .forms import TaskForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import UserRegisterForm  
from django.http import HttpRequest, HttpResponse
import csv
from .forms import UploadFileForm
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import time

executor = ThreadPoolExecutor()


def async_timing_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        elapsed = end - start
        print(
            f"Async function '{func.__name__}' "
            f"executed in {elapsed:.4f} seconds"
            )

        return result
    return wrapper


def save_task_sync(task_data):
    from .models import Task
    Task.objects.create(**task_data)


@async_timing_decorator
async def save_task_async(task_data):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, save_task_sync, task_data)


def user_register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UserRegisterForm(request.POST) 
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username} je uspješno registriran!')
            return redirect('login')  
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def task_list(request: HttpRequest) -> HttpResponse:

    if request.user.is_staff:
        tasks = list(Task.objects.all())
    else:
        tasks = list(Task.objects.filter(user=request.user))

    priority = request.GET.get('priority')

    def make_priority_filter(priority_value):
        def filter_task(task):
            return task.priority == priority_value
        return filter_task

    if priority in ['urgent', 'important', 'later']:
        filter_fn = make_priority_filter(priority)
        tasks = list(filter(filter_fn, tasks))

    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def add_task(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/add_task.html', {'form': form})


@login_required
def edit_task(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        return redirect('task_list')  
    return render(request, 'tasks/edit_task.html', {'form': form})


@login_required
def delete_task(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')  
    return render(request, 'tasks/delete_task.html', {'task': task})


@login_required
def toggle_task(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    task.completed = not task.completed
    task.save()
    return redirect('task_list')  


@login_required
def upload_tasks_csv(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            file = form.cleaned_data['file']
            decoded = file.read().decode('utf-8').splitlines()
            # Create a CSV DictReader to interpret each line as a dictionary 
            # (keys are column names).
            reader = csv.DictReader(decoded)

            tasks_to_save = []
            for row in reader:
                title = row.get('title', '').strip()
                if not title:
                    continue

                description = row.get('description', '').strip()
                completed = row.get(
                    'completed', 'False'
                ).strip().lower() in ('true', '1', 'yes')
                priority = row.get('priority', 'later').strip().lower()
                due_date_str = row.get('due_date', '').strip()

                try:
                    due_date = datetime.strptime(
                                                due_date_str,
                                                '%Y-%m-%d %H:%M'
                                                )
                except (ValueError, TypeError):
                    due_date = datetime.now()

                tasks_to_save.append({
                    'user': request.user,
                    'title': title,
                    'description': description,
                    'completed': completed,
                    'priority': priority if priority in [
                                                        'urgent', 
                                                        'important',
                                                        'later'
                                                        ] else 'later',
                    'due_date': due_date
                })

            async def save_all_tasks():
                await asyncio.gather(
                    *(save_task_async(data) for data in tasks_to_save)
                    )

            asyncio.run(save_all_tasks())  

            return redirect('task_list')
    else:
        form = UploadFileForm()
        
    return render(request, 'tasks/upload_tasks_csv.html', {'form': form})


@login_required
def upload_tasks_txt(request: HttpRequest) -> HttpResponse:
    priorities = {'urgent', 'important', 'later'}
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            uploaded_file = request.FILES['file']
            lines = uploaded_file.read().decode('utf-8').splitlines()

            tasks_to_save = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue  

                if ',' in line:
                    title, description = line.split(',', 1)
                    title = title.strip()
                    description = description.strip()
                else:
                    title = line
                    description = ''

                found_priority = 'later'
                description_words = description.split()
                for p in priorities:
                    if p in description_words:
                        found_priority = p
                        description_words.remove(p)
                        break
                description = ' '.join(description_words)

                tasks_to_save.append({
                    'user': request.user,
                    'title': title,
                    'description': description,
                    'completed': False,
                    'due_date': datetime.now(),
                    'priority': found_priority,
                })

            async def save_all_tasks():
                await asyncio.gather(
                    *(save_task_async(data) for data in tasks_to_save)
                    )

            asyncio.run(save_all_tasks())

            return redirect('task_list')
    else:
        form = UploadFileForm()
    return render(request, 'tasks/upload_tasks_txt.html', {'form': form})


@login_required
def export_tasks_pdf(request: HttpRequest) -> HttpResponse:
    if request.user.is_staff:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tasks.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 40
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y, "List of Tasks")
    y -= 30

    p.setFont("Helvetica", 12)
    for task in tasks:
        line = (
                f"{task.title} - {task.description} - "
                f"{'Dovršeno' if task.completed else 'Nedovršeno'} - "
                f"{task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Nema datuma'} - "
                f"{task.priority}"
                )
        p.drawString(40, y, line)
        y -= 20
        if y < 40:
            p.showPage()
            y = height - 40
            p.setFont("Helvetica", 12)

    p.showPage()
    p.save()
    return response


@login_required
def export_tasks_csv(request: HttpRequest) -> HttpResponse:
    if request.user.is_staff:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(user=request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tasks.csv"'

    writer = csv.writer(response)
    writer.writerow(
                    ['Title', 
                     'Description', 
                     'Completed',
                     'Due Date',
                     'Priority']
                    )

    for task in tasks:
        writer.writerow([
            task.title,
            task.description,
            'Yes' if task.completed else 'No',
            task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else '',
            task.priority,
        ])

    return response


