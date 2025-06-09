# Task Management Web Application (Django)

A simple web application for managing personal tasks, built with Django.  
Users can register, log in, create, edit, delete, and mark tasks as complete.  
The app supports importing tasks from CSV and TXT files, and exporting tasks to PDF and CSV.

---

## Features

- User registration and authentication
- Add, edit, delete, and toggle (complete/incomplete) tasks
- Filter tasks by priority (urgent, important, later)
- Import tasks from CSV and TXT files
- Export tasks to PDF and CSV
- Separate views for regular users and admin (admin sees all tasks)
- Basic form validation

---

## Prerequisites

- Python 3.9+
- Django 4.x
- pip (Python package manager)
- (Optional) virtualenv for isolated environment

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone 
   cd 
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the app:**
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Usage

- **Register a new user** or log in with an existing account.
- **Add tasks** using the "Add Task" button.
- **Edit, delete, or mark tasks as complete/incomplete** from the task list.
- **Filter tasks** by priority using the filter options.
- **Import tasks**:
  - Upload a CSV or TXT file with task data (CSV: columns `title`, `description`, `completed`, `priority`, `due_date`; TXT: one task per line, optional description and priority).
- **Export tasks**:
  - Download your tasks as PDF or CSV using the export buttons.

---

## File Import/Export Formats

### CSV Import

- **Required:** `title`
- **Optional:** `description`, `completed` (`True`/`False`), `priority` (`urgent`, `important`, `later`), `due_date` (`YYYY-MM-DD HH:MM`)
- Example:
  ```
  title,description,completed,priority,due_date
  Buy groceries,Milk and eggs,False,urgent,2025-06-10 18:00
  ```

### TXT Import

- Each line is a task.  
- Format: `title, description` (priority can be included as a word in the description: urgent, important, later).
- Example:
  ```
  Finish project, urgent Finish the Django project ASAP
  Read book, important Read for exam
  ```

---

## Export

- **PDF:** Download a printable list of your tasks.
- **CSV:** Download all your tasks in a CSV file for further editing or backup.

---

## Project Structure

- `tasks/` – Django app with models, views, forms, and templates
- `templates/` – HTML templates for the app
- `static/` – (optional) static files (CSS, JS)
- `manage.py` – Django management script

---

## Notes

- Only logged-in users can manage tasks.
- Admin users see all tasks; regular users see only their own.
- Asynchronous import is used for faster processing of large files.

---

