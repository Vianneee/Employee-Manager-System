# tkinter → base GUI framework
# ttk → modern widgets (buttons, combobox)
# messagebox → popup dialogs (errors, warnings, confirmations)
import tkinter as tk
from tkinter import ttk, messagebox

from manager import (
    load_employees,
    add_employee,
    delete_employee,
    update_employee
)

# Creates a class for the whole application
# Inherits from tk.Tk (main window class)
# This is Object-Oriented Programming:
# The app is treated as an object
# State and behavior are grouped together
class EmployeeApp(tk.Tk):
    def __init__(self):
        super().__init__()


        self.title("Employee Management System")
        self.geometry("900x520")
        self.resizable(False, False)

        self.dept_values = ["HR", "IT", "Finance", "Sales", "Engineering"]
        self.selected_id = None

        self.create_widgets()
        self.refresh_list()

    #TEXT NORMALIZATION
    def smart_title(self, text):
        special = {"IT", "HR", "CEO", "CTO", "CFO", "UI", "UX"}
        words = text.strip().split()
        out = []

        for w in words:
            if w.upper() in special:
                out.append(w.upper())
            else:
                out.append(w.capitalize())

        return " ".join(out)

    #FIELD HELPERS
    def get_fields(self):
        name = self.smart_title(self.entry_name.get())
        dept = self.smart_title(self.entry_dept.get())
        role = self.smart_title(self.entry_role.get())

        if dept and dept not in self.dept_values:
            self.dept_values.append(dept)
            self.entry_dept["values"] = self.dept_values

        return {
            "id": self.entry_id.get().strip(),
            "name": name,
            "department": dept,
            "role": role
        }

    def clear_fields(self):
        self.entry_id.config(state="normal")
        self.entry_id.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.entry_dept.set("")
        self.entry_role.delete(0, tk.END)
        self.selected_id = None

    # ---------- LIST SELECTION ----------
    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return

        text = self.listbox.get(sel[0])
        # Format: ID - Name (Department) | Role
        emp_id, rest = text.split(" - ", 1)
        name, rest = rest.split(" (", 1)
        department, role = rest.split(") | ")

        self.entry_id.config(state="normal")
        self.entry_id.delete(0, tk.END)
        self.entry_id.insert(0, emp_id)
        self.entry_id.config(state="disabled")

        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, name)

        self.entry_dept.set(department)

        self.entry_role.delete(0, tk.END)
        self.entry_role.insert(0, role)

        self.selected_id = emp_id  # ✅ store selection safely

    # ---------- ACTIONS ----------
    def on_add(self):
        emp = self.get_fields()

        if not emp["id"] or not emp["name"] or not emp["department"] or not emp["role"]:
            messagebox.showwarning(
                "Validation Error",
                "All fields (ID, Name, Department, Role) are required."
            )
            return

        if not emp["id"].isdigit() or len(emp["id"]) != 6:
            messagebox.showerror(
                "Invalid ID",
                "Employee ID must be exactly 6 digits."
            )
            return

        ok, msg = add_employee(emp)

        if ok:
            messagebox.showinfo("Success", "Employee added successfully")
            self.refresh_list()
            self.clear_fields()
        else:
            messagebox.showerror("Error", msg)

    def on_update(self):
        if not self.selected_id:
            messagebox.showwarning("Update", "Select an employee to update.")
            return

        emp = self.get_fields()

        if not emp["id"] or not emp["name"] or not emp["department"] or not emp["role"]:
            messagebox.showwarning(
                "Validation Error",
                "All fields must be filled before updating."
            )
            return

        if not emp["id"].isdigit() or len(emp["id"]) != 6:
            messagebox.showerror(
                "Invalid ID",
                "Employee ID must be exactly 6 digits."
            )
            return

        if not messagebox.askyesno(
                "Confirm Update",
                "Are you sure you want to update this employee?"
        ):
            return

        ok, msg = update_employee(self.selected_id, emp)

        if ok:
            messagebox.showinfo("Updated", "Employee updated successfully")
            self.refresh_list()
            self.clear_fields()
        else:
            messagebox.showerror("Error", msg)

    def on_delete(self):
        if not self.selected_id:
            messagebox.showwarning("Delete", "Select an employee to delete.")
            return

        if not messagebox.askyesno(
                "Confirm Delete",
                "Are you sure you want to delete this employee?"
        ):
            return

        delete_employee(self.selected_id)
        self.refresh_list()
        self.clear_fields()

    def on_search(self):
        id_q = self.entry_id.get().strip()
        name_q = self.entry_name.get().strip().lower()
        dept_q = self.entry_dept.get().strip().lower()
        role_q = self.entry_role.get().strip().lower()

        employees = load_employees()
        results = []

        for e in employees:
            if id_q and id_q != e["id"]:
                continue
            if name_q and name_q not in e["name"].lower():
                continue
            if dept_q and dept_q not in e["department"].lower():
                continue
            if role_q and role_q not in e["role"].lower():
                continue
            results.append(e)

        self.listbox.delete(0, tk.END)
        for emp in results:
            self.listbox.insert(
                tk.END,
                f"{emp['id']} - {emp['name']} ({emp['department']}) | {emp['role']}"
            )

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for emp in load_employees():
            self.listbox.insert(
                tk.END,
                f"{emp['id']} - {emp['name']} ({emp['department']}) | {emp['role']}"
            )

    # ---------- GUI LAYOUT ----------
    def create_widgets(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            main,
            text="Employee Management System",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        form = ttk.Frame(main)
        form.pack(pady=10)

        ttk.Label(form, text="ID").grid(row=0, column=0, padx=10, sticky="w")
        ttk.Label(form, text="Name").grid(row=0, column=1, padx=10, sticky="w")
        ttk.Label(form, text="Department").grid(row=0, column=2, padx=10, sticky="w")
        ttk.Label(form, text="Role").grid(row=0, column=3, padx=10, sticky="w")

        self.entry_id = ttk.Entry(form, width=15)
        self.entry_id.grid(row=1, column=0, padx=10)

        self.entry_name = ttk.Entry(form, width=25)
        self.entry_name.grid(row=1, column=1, padx=10)

        self.entry_dept = ttk.Combobox(form, width=20, values=self.dept_values)
        self.entry_dept.grid(row=1, column=2, padx=10)

        self.entry_role = ttk.Entry(form, width=20)
        self.entry_role.grid(row=1, column=3, padx=10)

        btns = ttk.Frame(main)
        btns.pack(pady=10)

        ttk.Button(btns, text="Add", width=14, command=self.on_add).grid(row=0, column=0, padx=8)
        ttk.Button(btns, text="Search", width=14, command=self.on_search).grid(row=0, column=1, padx=8)
        ttk.Button(btns, text="Update", width=14, command=self.on_update).grid(row=0, column=2, padx=8)
        ttk.Button(btns, text="Delete", width=14, command=self.on_delete).grid(row=0, column=3, padx=8)
        ttk.Button(btns, text="Refresh", width=14, command=self.refresh_list).grid(row=0, column=4, padx=8)

        list_frame = ttk.Frame(main)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(list_frame, height=12)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)


if __name__ == "__main__":
    app = EmployeeApp()
    app.mainloop()
