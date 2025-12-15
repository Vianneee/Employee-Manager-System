
# storage.py
# Handles all file operations for employees (read, write, search).
import os
import csv
import tempfile
import shutil

DATA_FILE = "employees.txt"
FIELDNAMES = ["id", "name", "department", "role"]


def ensure_data_file(path=DATA_FILE):
    if not os.path.exists(path):
        # create containing directory if needed
        d = os.path.dirname(path)
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        with open(path, "w", newline='', encoding='utf-8') as f:
            pass


def load_employees(path=DATA_FILE):
    """Return list of dicts: [{id,name,department,role}, ...]"""
    ensure_data_file(path)
    employees = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            parts = [p.strip() for p in row]
            while len(parts) < 4:
                parts.append("")
            emp = dict(zip(FIELDNAMES, parts[:4]))
            employees.append(emp)
    return employees


def atomic_save_employees(employees, path=DATA_FILE):
    """Save employees list to file atomically (write to temp then replace)."""
    dirpath = os.path.dirname(os.path.abspath(path)) or '.'
    fd, tmpname = tempfile.mkstemp(prefix="emp_", dir=dirpath, text=True)
    os.close(fd)
    try:
        with open(tmpname, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for e in employees:
                writer.writerow([e.get('id',''), e.get('name',''), e.get('department',''), e.get('role','')])
        shutil.move(tmpname, path)
    finally:
        if os.path.exists(tmpname):
            os.remove(tmpname)


def find_employee_by_id(emp_id, employees):
    for e in employees:
        if e.get('id') == emp_id:
            return e
    return None


def add_employee(emp_dict, path=DATA_FILE):
    employees = load_employees(path)
    if find_employee_by_id(emp_dict.get('id','').strip(), employees):
        return False, "ID already exists"
    employees.append(emp_dict)
    atomic_save_employees(employees, path)
    return True, "Added"


def delete_employee(emp_id, path=DATA_FILE):
    employees = load_employees(path)
    before = len(employees)
    employees = [e for e in employees if e.get('id') != emp_id]
    if len(employees) == before:
        return False, "ID not found"
    atomic_save_employees(employees, path)
    return True, "Deleted"


def update_employee(emp_id, updated_dict, path=DATA_FILE):
    employees = load_employees(path)
    found = False
    for i, e in enumerate(employees):
        if e.get('id') == emp_id:
            new_id = updated_dict.get('id', emp_id).strip()
            if new_id != emp_id and find_employee_by_id(new_id, employees):
                return False, "Target ID already exists"
            employees[i] = updated_dict
            found = True
            break
    if not found:
        return False, "ID not found"
    atomic_save_employees(employees, path)
    return True, "Updated"
