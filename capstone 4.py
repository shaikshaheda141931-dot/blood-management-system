
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ---------- COLORS & DATABASE ----------
DB_NAME = "lifeline_stylish.db"

BG = "#F4F6FB"
WHITE = "#FFFFFF"
NAVY = "#101A33"
NAVY2 = "#1B2948"
RED = "#E83D55"
RED_DARK = "#C92842"
PINK = "#FFF0F2"
TEAL = "#19A88A"
BLUE = "#4C7DF0"
GOLD = "#F3B746"
TEXT = "#202B45"
MUTED = "#7D879C"
BORDER = "#E7EAF2"

root = tk.Tk()
root.title("LifeLine | Blood Bank Management")
root.geometry("1320x820")
root.minsize(1080, 700)
root.configure(bg=BG)

db = sqlite3.connect(DB_NAME)
cur = db.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS doctors(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 specialization TEXT NOT NULL,
 experience INTEGER NOT NULL,
 fee REAL NOT NULL,
 availability TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS blood_stock(
 blood_group TEXT PRIMARY KEY,
 units INTEGER NOT NULL,
 service_cost REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS collections(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 donor TEXT NOT NULL,
 blood_group TEXT NOT NULL,
 volume_ml INTEGER NOT NULL,
 doctor TEXT NOT NULL,
 status TEXT NOT NULL,
 collected_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bills(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 patient TEXT NOT NULL,
 blood_group TEXT NOT NULL,
 units INTEGER NOT NULL,
 unit_cost REAL NOT NULL,
 total REAL NOT NULL,
 payment_method TEXT NOT NULL,
 payment_status TEXT NOT NULL,
 created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS nurses(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 details TEXT NOT NULL,
 experience INTEGER NOT NULL,
 availability TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hospital_daily_bills(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 bill_date TEXT NOT NULL UNIQUE,
 patient_bills INTEGER NOT NULL,
 total_units INTEGER NOT NULL,
 total_amount REAL NOT NULL,
 generated_at TEXT NOT NULL
);
""")

# Migrate older database versions safely. Existing SQLite tables are not
# changed by CREATE TABLE IF NOT EXISTS, so add new nurse columns if needed.
nurse_columns = {
    row[1] for row in cur.execute("PRAGMA table_info(nurses)").fetchall()
}
if "details" not in nurse_columns:
    cur.execute("ALTER TABLE nurses ADD COLUMN details TEXT NOT NULL DEFAULT ''")
    if "specialization" in nurse_columns:
        cur.execute("UPDATE nurses SET details = COALESCE(specialization, '')")
if "experience" not in nurse_columns:
    cur.execute("ALTER TABLE nurses ADD COLUMN experience INTEGER NOT NULL DEFAULT 0")

db.commit()

if cur.execute("SELECT COUNT(*) FROM doctors").fetchone()[0] == 0:
    cur.executemany("""
        INSERT INTO doctors
        (name, specialization, experience, fee, availability)
        VALUES (?, ?, ?, ?, ?)
    """, [
        ("Dr. Ravi Kumar", "Hematologist", 12, 500, "Available"),
        ("Dr. Priya Sharma", "General Physician", 8, 400, "Available"),
        ("Dr. Arjun Rao", "Pathologist", 10, 600, "Available"),
        ("Dr. Sneha Reddy", "Transfusion Medicine", 6, 350, "Available")
    ])

# Keep the pathologist available, including in databases created earlier.
cur.execute("UPDATE doctors SET availability='Available' WHERE LOWER(specialization) LIKE '%patholog%'")

if cur.execute("SELECT COUNT(*) FROM nurses").fetchone()[0] == 0:
    cur.executemany("""
        INSERT INTO nurses (name, details, experience, availability)
        VALUES (?, ?, ?, ?)
    """, [
        ("Nurse Anjali Patel", "Blood collection and donor care", 7, "Available"),
        ("Nurse Meera Shah", "Patient care and monitoring", 5, "Available"),
        ("Nurse Kavita Joshi", "Transfusion support", 6, "Available"),
        ("Nurse Riya Desai", "Ward and recipient support", 3, "Available")
    ])

if cur.execute("SELECT COUNT(*) FROM blood_stock").fetchone()[0] == 0:
    cur.executemany("""
        INSERT INTO blood_stock
        (blood_group, units, service_cost)
        VALUES (?, ?, ?)
    """, [
        ("A+", 20, 500),
        ("A-", 10, 600),
        ("B+", 25, 500),
        ("B-", 8, 600),
        ("AB+", 15, 700),
        ("AB-", 7, 800),
        ("O+", 30, 500),
        ("O-", 10, 700)
    ])

db.commit()

# ---------- GUI STYLING ----------
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    rowheight=31,
    font=("Segoe UI", 10),
    background=WHITE,
    fieldbackground=WHITE,
    foreground=TEXT,
    borderwidth=0
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 10, "bold"),
    background="#EEF1F8",
    foreground=NAVY,
    padding=9
)

style.map(
    "Treeview",
    background=[("selected", "#FFE2E7")],
    foreground=[("selected", NAVY)]
)

style.configure("TCombobox", padding=7)
style.configure("TNotebook", background=BG, borderwidth=0)

# ---------- MAIN LAYOUT ----------
sidebar = tk.Frame(root, bg=NAVY, width=238)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

main = tk.Frame(root, bg=BG)
main.pack(side="right", fill="both", expand=True)

brand = tk.Frame(sidebar, bg=NAVY)
brand.pack(fill="x", padx=22, pady=(24, 26))

logo = tk.Canvas(
    brand, width=48, height=48,
    bg=NAVY, highlightthickness=0
)
logo.pack(side="left")
logo.create_oval(3, 3, 45, 45, fill=RED, outline="")
logo.create_text(
    24, 24, text="+",
    fill=WHITE, font=("Segoe UI", 24, "bold")
)

brand_text = tk.Frame(brand, bg=NAVY)
brand_text.pack(side="left", padx=10)

tk.Label(
    brand_text, text="LifeLine",
    bg=NAVY, fg=WHITE,
    font=("Segoe UI", 19, "bold")
).pack(anchor="w")

tk.Label(
    brand_text, text="BLOOD BANK",
    bg=NAVY, fg="#AAB6D0",
    font=("Segoe UI", 8, "bold")
).pack(anchor="w")

tk.Label(
    sidebar, text="WORKSPACE",
    bg=NAVY, fg="#7F8BA8",
    font=("Segoe UI", 8, "bold")
).pack(anchor="w", padx=24, pady=(0, 10))

content = tk.Frame(main, bg=BG)
content.pack(fill="both", expand=True, padx=28, pady=(16, 22))

current_page = {"name": "Dashboard"}
nav_buttons = {}


def button(parent, text, command, bg=RED, fg=WHITE,
           padx=14, pady=9):
    return tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg,
        activebackground=bg,
        activeforeground=fg,
        relief="flat", bd=0,
        cursor="hand2",
        padx=padx, pady=pady,
        font=("Segoe UI", 10, "bold")
    )


def heading(parent, title, subtitle):
    tk.Label(
        parent, text=title,
        bg=BG, fg=NAVY,
        font=("Segoe UI", 23, "bold")
    ).pack(anchor="w")

    tk.Label(
        parent, text=subtitle,
        bg=BG, fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(3, 16))


def card(parent, title, value, subtitle, accent, symbol):
    outer = tk.Frame(
        parent, bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    tk.Frame(outer, bg=accent, height=4).pack(fill="x")

    body = tk.Frame(outer, bg=WHITE)
    body.pack(fill="both", expand=True, padx=16, pady=13)

    top = tk.Frame(body, bg=WHITE)
    top.pack(fill="x")

    tk.Label(
        top, text=title,
        bg=WHITE, fg=MUTED,
        font=("Segoe UI", 10, "bold")
    ).pack(side="left")

    tk.Label(
        top, text=symbol,
        bg=WHITE, fg=accent,
        font=("Segoe UI", 18, "bold")
    ).pack(side="right")

    tk.Label(
        body, text=value,
        bg=WHITE, fg=NAVY,
        font=("Segoe UI", 25, "bold")
    ).pack(anchor="w", pady=(8, 0))

    tk.Label(
        body, text=subtitle,
        bg=WHITE, fg=MUTED,
        font=("Segoe UI", 9)
    ).pack(anchor="w", pady=(2, 0))

    return outer


def clear_content():
    for child in content.winfo_children():
        child.destroy()


def make_table(parent, columns, widths=None, height=9):
    holder = tk.Frame(
        parent, bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    tree = ttk.Treeview(
        holder, columns=columns,
        show="headings", height=height
    )

    sy = ttk.Scrollbar(
        holder, orient="vertical",
        command=tree.yview
    )

    sx = ttk.Scrollbar(
        holder, orient="horizontal",
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=sy.set,
        xscrollcommand=sx.set
    )

    sy.pack(side="right", fill="y")
    sx.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True)

    for i, col in enumerate(columns):
        tree.heading(col, text=col.replace("_", " ").title())
        width = widths[i] if widths and i < len(widths) else 130
        tree.column(col, width=width, anchor="w")

    return holder, tree


def stock_rows():
    return cur.execute("""
        SELECT blood_group, units, service_cost
        FROM blood_stock ORDER BY blood_group
    """).fetchall()


# ---------- DASHBOARD ----------
def show_dashboard():
    current_page["name"] = "Dashboard"
    clear_content()

    heading(
        content,
        "Good day, Admin!",
        "Your blood bank overview at a glance. "
        "Every donation can help save a life."
    )

    hero = tk.Frame(content, bg=NAVY2, height=175)
    hero.pack(fill="x", pady=(0, 18))
    hero.pack_propagate(False)

    left = tk.Frame(hero, bg=NAVY2)
    left.pack(
        side="left", fill="both", expand=True,
        padx=25, pady=20
    )

    tk.Label(
        left, text="EVERY DROP COUNTS",
        bg=NAVY2, fg="#FFB9C3",
        font=("Segoe UI", 9, "bold")
    ).pack(anchor="w")

    tk.Label(
        left, text="Donate blood.\nShare life.",
        bg=NAVY2, fg=WHITE,
        font=("Segoe UI", 23, "bold"),
        justify="left"
    ).pack(anchor="w", pady=(6, 3))

    tk.Label(
        left,
        text="Manage inventory, doctors, collections and billing.",
        bg=NAVY2, fg="#C8D2E8",
        font=("Segoe UI", 10)
    ).pack(anchor="w")

    # Built-in blood drop illustration
    art = tk.Canvas(
        hero, width=230, height=175,
        bg=NAVY2, highlightthickness=0
    )
    art.pack(side="right", padx=20)

    art.create_oval(58, 16, 196, 154, fill="#293A60", outline="")
    art.create_oval(84, 36, 173, 130, fill="#3A4F79", outline="")

    art.create_polygon(
        130, 27, 93, 83, 91, 101, 100, 119,
        116, 128, 137, 128, 154, 117, 162, 100,
        157, 82, fill=RED, outline=""
    )

    art.create_oval(104, 86, 149, 125, fill=RED, outline="")
    art.create_oval(107, 89, 123, 105, fill="#FF9AA8", outline="")

    art.create_text(
        130, 103, text="+",
        fill=WHITE, font=("Segoe UI", 28, "bold")
    )

    art.create_text(
        37, 42, text="*",
        fill=GOLD, font=("Segoe UI", 16, "bold")
    )

    art.create_text(
        193, 118, text="+",
        fill="#91DCCB", font=("Segoe UI", 17, "bold")
    )

    total_units = cur.execute(
        "SELECT COALESCE(SUM(units), 0) FROM blood_stock"
    ).fetchone()[0]

    group_count = cur.execute(
        "SELECT COUNT(*) FROM blood_stock WHERE units > 0"
    ).fetchone()[0]

    doctors_count = cur.execute(
        "SELECT COUNT(*) FROM doctors WHERE availability='Available'"
    ).fetchone()[0]

    collection_count = cur.execute(
        "SELECT COUNT(*) FROM collections"
    ).fetchone()[0]

    stats = tk.Frame(content, bg=BG)
    stats.pack(fill="x", pady=(0, 17))

    items = [
        ("Available Units", str(total_units),
         "Across all blood groups", RED, "♥"),
        ("Blood Groups", f"{group_count}/8",
         "Groups currently in stock", BLUE, "◈"),
        ("Available Doctors", str(doctors_count),
         "Ready for consultation", TEAL, "+"),
        ("Collections", str(collection_count),
         "Collection records", GOLD, "↗")
    ]

    for i, item in enumerate(items):
        stats.grid_columnconfigure(i, weight=1, uniform="stat")
        card(stats, *item).grid(
            row=0, column=i, sticky="nsew",
            padx=(0 if i == 0 else 8, 0)
        )

    lower = tk.Frame(content, bg=BG)
    lower.pack(fill="both", expand=True)
    lower.grid_columnconfigure(0, weight=3)
    lower.grid_columnconfigure(1, weight=2)

    inv = tk.Frame(
        lower, bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    inv.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    tk.Label(
        inv, text="Blood inventory snapshot",
        bg=WHITE, fg=NAVY,
        font=("Segoe UI", 13, "bold")
    ).pack(anchor="w", padx=17, pady=(14, 2))

    tk.Label(
        inv, text="Units available by blood group",
        bg=WHITE, fg=MUTED,
        font=("Segoe UI", 9)
    ).pack(anchor="w", padx=17, pady=(0, 9))

    chart = tk.Canvas(
        inv, height=155, bg=WHITE,
        highlightthickness=0
    )
    chart.pack(fill="x", padx=14, pady=(0, 10))

    rows = stock_rows()
    max_units = max([r[1] for r in rows] + [1])

    for idx, (grp, units, cost) in enumerate(rows):
        x = 12 + idx * 63
        h = max(7, int((units / max_units) * 92))
        color = RED if units < 10 else (BLUE if idx % 2 else TEAL)

        chart.create_rectangle(
            x, 110-h, x+31, 110,
            fill=color, outline=""
        )
        chart.create_text(
            x+15, 99-h, text=str(units),
            fill=TEXT, font=("Segoe UI", 8, "bold")
        )
        chart.create_text(
            x+15, 126, text=grp,
            fill=MUTED, font=("Segoe UI", 9, "bold")
        )

    quick = tk.Frame(
        lower, bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    quick.grid(row=0, column=1, sticky="nsew")

    tk.Label(
        quick, text="Quick actions",
        bg=WHITE, fg=NAVY,
        font=("Segoe UI", 13, "bold")
    ).pack(anchor="w", padx=17, pady=(14, 10))

    actions = [
        ("View blood inventory", "Check stock and service costs",
         show_inventory, RED),
        ("Doctors directory", "Experience and consultation fees",
         show_doctors, BLUE),
        ("Register collection", "Record a donor collection",
         show_collections, TEAL),
        ("Payments & bills", "Create a sample bill/receipt",
         show_payments, GOLD)
    ]

    for label, desc, cmd, color in actions:
        row = tk.Frame(quick, bg=WHITE)
        row.pack(fill="x", padx=15, pady=4)

        tk.Frame(row, bg=color, width=4).pack(
            side="left", fill="y", padx=(0, 10)
        )

        txt = tk.Frame(row, bg=WHITE)
        txt.pack(side="left", fill="x", expand=True, pady=5)

        tk.Label(
            txt, text=label, bg=WHITE, fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        tk.Label(
            txt, text=desc, bg=WHITE, fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(anchor="w")

        button(
            row, "Open  >", cmd,
            bg="#F2F4FA", fg=NAVY,
            padx=10, pady=6
        ).pack(side="right")


# ---------- BLOOD INVENTORY ----------
def show_inventory():
    current_page["name"] = "Blood Inventory"
    clear_content()

    heading(
        content, "Blood Inventory",
        "View stock levels and update sample processing costs."
    )

    total = cur.execute(
        "SELECT COALESCE(SUM(units), 0) FROM blood_stock"
    ).fetchone()[0]

    tk.Label(
        content, text=f"TOTAL STOCK   {total} units",
        bg=PINK, fg=RED_DARK,
        font=("Segoe UI", 11, "bold"),
        padx=15, pady=10
    ).pack(anchor="w", pady=(0, 12))

    holder, tree = make_table(
        content,
        ("blood_group", "units", "service_cost", "stock_status"),
        [180, 180, 240, 220], 12
    )
    holder.pack(fill="both", expand=True, pady=(0, 12))

    for group, units, cost in stock_rows():
        tree.insert(
            "", "end",
            values=(
                group, units, f"₹{cost:,.2f}",
                "Low stock" if units < 10 else "Available"
            )
        )

    form = tk.Frame(
        content, bg=WHITE,
        highlightbackground=BORDER, highlightthickness=1
    )
    form.pack(fill="x", pady=(0, 5))

    tk.Label(
        form, text="Update inventory",
        bg=WHITE, fg=NAVY,
        font=("Segoe UI", 11, "bold")
    ).pack(anchor="w", padx=13, pady=(10, 4))

    fields = tk.Frame(form, bg=WHITE)
    fields.pack(fill="x", padx=10, pady=(0, 10))

    tk.Label(
        fields, text="Blood group",
        bg=WHITE, fg=MUTED
    ).pack(side="left", padx=(4, 5))

    group_var = tk.StringVar(value="A+")

    ttk.Combobox(
        fields, textvariable=group_var,
        values=[r[0] for r in stock_rows()],
        state="readonly", width=9
    ).pack(side="left", padx=5)

    tk.Label(
        fields, text="Units",
        bg=WHITE, fg=MUTED
    ).pack(side="left", padx=(12, 5))

    units_entry = tk.Entry(
        fields, width=10,
        font=("Segoe UI", 10), relief="solid", bd=1
    )
    units_entry.pack(side="left", ipady=5, padx=5)

    tk.Label(
        fields, text="Service cost ₹ / unit",
        bg=WHITE, fg=MUTED
    ).pack(side="left", padx=(12, 5))

    cost_entry = tk.Entry(
        fields, width=12,
        font=("Segoe UI", 10), relief="solid", bd=1
    )
    cost_entry.pack(side="left", ipady=5, padx=5)

    def update_stock():
        try:
            units = int(units_entry.get())
            cost = float(cost_entry.get())
            if units < 0 or cost < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid values",
                "Enter valid non-negative units and cost."
            )
            return

        cur.execute(
            "UPDATE blood_stock SET units=?, service_cost=? "
            "WHERE blood_group=?",
            (units, cost, group_var.get())
        )
        db.commit()
        show_inventory()

    button(
        fields, "Save changes",
        update_stock, bg=TEAL
    ).pack(side="right", padx=5)

    tk.Label(
        content,
        text="Sample processing/service costs only; not a selling price for blood.",
        bg=BG, fg=MUTED, font=("Segoe UI", 9)
    ).pack(anchor="w", pady=(8, 0))


# ---------- DOCTORS ----------
def show_doctors():
    current_page["name"] = "Doctors"
    clear_content()

    heading(
        content, "Doctors Directory",
        "Doctor profiles, experience and consultation fees."
    )

    holder, tree = make_table(
        content,
        ("id", "name", "specialization", "experience",
         "consultation_fee", "availability"),
        [60, 200, 220, 150, 170, 150], 12
    )
    holder.pack(fill="both", expand=True, pady=(0, 14))

    def refresh():
        tree.delete(*tree.get_children())

        rows = cur.execute("""
            SELECT id, name, specialization, experience,
                   fee, availability
            FROM doctors ORDER BY name
        """).fetchall()

        for row in rows:
            tree.insert(
                "", "end",
                values=(
                    row[0], row[1], row[2],
                    f"{row[3]} years",
                    f"₹{row[4]:,.2f}", row[5]
                )
            )

    refresh()

    form = tk.Frame(
        content, bg=WHITE,
        highlightbackground=BORDER, highlightthickness=1
    )
    form.pack(fill="x")

    tk.Label(
        form, text="Add a doctor",
        bg=WHITE, fg=NAVY,
        font=("Segoe UI", 11, "bold")
    ).pack(anchor="w", padx=13, pady=(10, 4))

    row = tk.Frame(form, bg=WHITE)
    row.pack(fill="x", padx=8, pady=(0, 10))

    entries = {}

    for key, width in [
        ("Name", 18),
        ("Specialization", 20),
        ("Experience years", 12),
        ("Consultation fee ₹", 13)
    ]:
        box = tk.Frame(row, bg=WHITE)
        box.pack(side="left", padx=5)

        tk.Label(
            box, text=key,
            bg=WHITE, fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        ent = tk.Entry(
            box, width=width,
            relief="solid", bd=1,
            font=("Segoe UI", 10)
        )
        ent.pack(ipady=5, pady=4)
        entries[key] = ent

    availability = tk.StringVar(value="Available")
    box = tk.Frame(row, bg=WHITE)
    box.pack(side="left", padx=5)

    tk.Label(
        box, text="Availability",
        bg=WHITE, fg=MUTED,
        font=("Segoe UI", 8, "bold")
    ).pack(anchor="w")

    ttk.Combobox(
        box, textvariable=availability,
        values=["Available", "On Leave"],
        state="readonly", width=13
    ).pack(pady=5)

    def add_doctor():
        name = entries["Name"].get().strip()
        spec = entries["Specialization"].get().strip()

        try:
            exp = int(entries["Experience years"].get())
            fee = float(entries["Consultation fee ₹"].get())

            if not name or not spec or exp < 0 or fee < 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Check details",
                "Enter valid name, specialization, experience and fee."
            )
            return

        cur.execute("""
            INSERT INTO doctors
            (name, specialization, experience, fee, availability)
            VALUES (?, ?, ?, ?, ?)
        """, (name, spec, exp, fee, availability.get()))

        db.commit()
        show_doctors()
        messagebox.showinfo("Saved", "Doctor added successfully.")

    button(
        row, "+ Add doctor",
        add_doctor, bg=TEAL
    ).pack(side="right", padx=5, pady=13)


# ---------- AVAILABLE NURSES ----------
def show_nurses():
    current_page["name"] = "Available Nurses"
    clear_content()

    heading(
        content, "Available Nurses",
        "Nurse details, experience and current availability."
    )

    holder, tree = make_table(
        content,
        ("id", "name", "details", "experience", "availability"),
        [70, 230, 330, 150, 170], 12
    )
    holder.pack(fill="both", expand=True, pady=(0, 14))

    rows = cur.execute("""
        SELECT id, name, details, experience, availability
        FROM nurses ORDER BY name
    """).fetchall()
    for record in rows:
        tree.insert("", "end", values=(
            record[0], record[1], record[2],
            f"{record[3]} years", record[4]
        ))

    form = tk.Frame(
        content, bg=WHITE,
        highlightbackground=BORDER, highlightthickness=1
    )
    form.pack(fill="x")

    tk.Label(
        form, text="Add a nurse",
        bg=WHITE, fg=NAVY,
        font=("Segoe UI", 11, "bold")
    ).pack(anchor="w", padx=13, pady=(10, 4))

    row = tk.Frame(form, bg=WHITE)
    row.pack(fill="x", padx=8, pady=(0, 10))
    entries = {}

    for key, width in [("Name", 21), ("Details", 28), ("Experience years", 13)]:
        box = tk.Frame(row, bg=WHITE)
        box.pack(side="left", padx=5)
        tk.Label(
            box, text=key, bg=WHITE, fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")
        ent = tk.Entry(
            box, width=width, relief="solid", bd=1,
            font=("Segoe UI", 10)
        )
        ent.pack(ipady=5, pady=4)
        entries[key] = ent

    availability = tk.StringVar(value="Available")
    box = tk.Frame(row, bg=WHITE)
    box.pack(side="left", padx=5)
    tk.Label(
        box, text="Availability", bg=WHITE, fg=MUTED,
        font=("Segoe UI", 8, "bold")
    ).pack(anchor="w")
    ttk.Combobox(
        box, textvariable=availability,
        values=["Available", "On Leave"],
        state="readonly", width=13
    ).pack(pady=5)

    def add_nurse():
        name = entries["Name"].get().strip()
        details = entries["Details"].get().strip()
        try:
            exp = int(entries["Experience years"].get())
            if not name or not details or exp < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Check details", "Enter name, details and valid experience."
            )
            return
        cur.execute("""
            INSERT INTO nurses (name, details, experience, availability)
            VALUES (?, ?, ?, ?)
        """, (name, details, exp, availability.get()))
        db.commit()
        show_nurses()
        messagebox.showinfo("Saved", "Nurse added successfully.")

    button(row, "+ Add nurse", add_nurse, bg=TEAL).pack(side="right", padx=5, pady=13)


# ---------- BLOOD COLLECTIONS ----------
def show_collections():
    current_page["name"] = "Collections"
    clear_content()

    heading(
        content, "Blood Collections",
        "Register donor collections and record collection status."
    )

    form = tk.Frame(
        content, bg=WHITE,
        highlightbackground=BORDER, highlightthickness=1
    )
    form.pack(fill="x", pady=(0, 13))

    fields = tk.Frame(form, bg=WHITE)
    fields.pack(fill="x", padx=10, pady=12)

    def field(label, choices=None, width=17):
        box = tk.Frame(fields, bg=WHITE)
        box.pack(side="left", padx=6)

        tk.Label(
            box, text=label,
            bg=WHITE, fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        if choices is not None:
            var = tk.StringVar(value=choices[0] if choices else "")
            widget = ttk.Combobox(
                box, textvariable=var,
                values=choices, state="readonly", width=width
            )
            widget.pack(pady=5)
            return widget

        widget = tk.Entry(
            box, width=width,
            relief="solid", bd=1,
            font=("Segoe UI", 10)
        )
        widget.pack(pady=5, ipady=4)
        return widget

    donor = field("Donor name", width=19)
    group = field("Blood group", [r[0] for r in stock_rows()], 9)
    volume = field("Volume (mL)", width=11)

    docs = [
        r[0] for r in cur.execute(
            "SELECT name FROM doctors WHERE availability='Available'"
        ).fetchall()
    ] or ["No Available Doctor"]

    doctor = field("Doctor", docs, 21)
    status = field(
        "Status", ["Not Collected", "Collected"], 15
    )

    holder, tree = make_table(
        content,
        ("id", "donor", "blood_group", "volume_ml",
         "doctor", "status", "collected_at"),
        [60, 190, 110, 110, 220, 150, 190], 10
    )
    holder.pack(fill="both", expand=True)

    def refresh():
        tree.delete(*tree.get_children())

        rows = cur.execute("""
            SELECT id, donor, blood_group, volume_ml,
                   doctor, status, collected_at
            FROM collections ORDER BY id DESC
        """).fetchall()

        for row in rows:
            tree.insert("", "end", values=row)

    def save_collection():
        name = donor.get().strip()
        grp = group.get()
        doc = doctor.get()

        try:
            # Accept both "100" and "100ml" in the volume field.
            volume_text = volume.get().strip().lower().replace("ml", "").strip()
            vol_number = float(volume_text)
            if not vol_number.is_integer():
                raise ValueError
            vol = int(vol_number)

            # Validate the selected doctor against the current database,
            # rather than relying only on the dropdown's displayed text.
            available_doctors = [
                row[0] for row in cur.execute(
                    "SELECT name FROM doctors WHERE availability='Available'"
                ).fetchall()
            ]
            if not name or vol <= 0 or doc not in available_doctors:
                raise ValueError
        except (ValueError, TypeError):
            messagebox.showerror(
                "Invalid details",
                "Enter donor name, a positive whole-number volume (e.g. 100 or 100ml), "
                "and select a doctor whose status is Available."
            )
            return

        st = status.get()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if st == "Collected":
            confirmed = messagebox.askyesno(
                "Confirm",
                "Confirm collection was completed by authorized medical staff?"
            )
            if not confirmed:
                return

        cur.execute("""
            INSERT INTO collections
            (donor, blood_group, volume_ml, doctor, status, collected_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, grp, vol, doc, st, now))

        if st == "Collected":
            cur.execute(
                "UPDATE blood_stock SET units=units+1 WHERE blood_group=?",
                (grp,)
            )

        db.commit()
        refresh()

        messagebox.showinfo(
            "Saved",
            "Collection saved." +
            (" Stock increased by one demo unit."
             if st == "Collected"
             else " Stock unchanged because it was not collected.")
        )

    button(
        form, "Save collection",
        save_collection, bg=TEAL
    ).pack(anchor="w", padx=16, pady=(0, 12))

    refresh()

    tk.Label(
        content,
        text="Educational demo only. Real collection must follow blood-bank procedures.",
        bg=BG, fg=MUTED, font=("Segoe UI", 9)
    ).pack(anchor="w", pady=(8, 0))


# ---------- PAYMENTS & BILLS ----------
def show_payments():
    current_page["name"] = "Payments & Bills"
    clear_content()

    heading(
        content, "Payments & Bills",
        "Create a demo bill and select a payment method."
    )

    form = tk.Frame(
        content, bg=WHITE,
        highlightbackground=BORDER, highlightthickness=1
    )
    form.pack(fill="x", pady=(0, 14))

    tk.Label(
        form, text="Create bill",
        bg=WHITE, fg=NAVY,
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w", padx=14, pady=(12, 6))

    row = tk.Frame(form, bg=WHITE)
    row.pack(fill="x", padx=10, pady=(0, 10))

    def add_input(parent, label, width=18):
        box = tk.Frame(parent, bg=WHITE)
        box.pack(side="left", padx=6)

        tk.Label(
            box, text=label,
            bg=WHITE, fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        ent = tk.Entry(
            box, width=width,
            relief="solid", bd=1,
            font=("Segoe UI", 10)
        )
        ent.pack(pady=5, ipady=5)
        return ent

    patient = add_input(row, "Patient name", 20)

    group_var = tk.StringVar(value="A+")

    box = tk.Frame(row, bg=WHITE)
    box.pack(side="left", padx=6)

    tk.Label(
        box, text="Blood group",
        bg=WHITE, fg=MUTED,
        font=("Segoe UI", 8, "bold")
    ).pack(anchor="w")

    ttk.Combobox(
        box, textvariable=group_var,
        values=[r[0] for r in stock_rows()],
        state="readonly", width=10
    ).pack(pady=5)

    units_entry = add_input(row, "Units / volume (e.g. 1 or 500ml)", 18)

    method_var = tk.StringVar(value="Cash at Hospital")
    box = tk.Frame(row, bg=WHITE)
    box.pack(side="left", padx=6)

    tk.Label(
        box, text="Payment method",
        bg=WHITE, fg=MUTED,
        font=("Segoe UI", 8, "bold")
    ).pack(anchor="w")

    ttk.Combobox(
        box, textvariable=method_var,
        values=["Online Payment (Demo)", "Cash at Hospital"],
        state="readonly", width=23
    ).pack(pady=5)

    total_label = tk.Label(
        form, text="Estimated total: ₹0.00",
        bg=WHITE, fg=RED,
        font=("Segoe UI", 14, "bold")
    )
    total_label.pack(anchor="w", padx=16, pady=(0, 8))

    def parse_requested_units(raw_value):
        """Accept a unit count (e.g. 1) or a blood-bag volume (e.g. 500ml).

        A volume entry represents one blood bag/unit; stock and billing are
        tracked in bags/units, not individual millilitres.
        """
        raw = raw_value.strip().lower().replace(" ", "")
        if not raw:
            return 0
        if raw.endswith("ml"):
            volume_text = raw[:-2]
            volume = int(volume_text)
            if volume <= 0:
                raise ValueError
            return 1
        count = int(raw)
        if count <= 0:
            raise ValueError
        return count

    def calc_total(*_):
        try:
            count = parse_requested_units(units_entry.get())
        except ValueError:
            count = 0

        result = cur.execute(
            "SELECT service_cost FROM blood_stock WHERE blood_group=?",
            (group_var.get(),)
        ).fetchone()

        cost = result[0] if result else 0

        total_label.config(
            text=f"Estimated total: ₹{cost * count:,.2f} "
                 f"({count} × ₹{cost:,.2f})"
        )

    group_var.trace_add("write", calc_total)
    units_entry.bind("<KeyRelease>", calc_total)

    holder, tree = make_table(
        content,
        ("id", "patient", "blood_group", "units",
         "unit_cost", "total", "payment_method",
         "payment_status", "created_at"),
        [55, 170, 100, 75, 110, 110, 200, 130, 180], 10
    )
    holder.pack(fill="both", expand=True)

    def generate_hospital_daily_bill():
        today = datetime.now().strftime("%Y-%m-%d")
        totals = cur.execute("""
            SELECT COUNT(*), COALESCE(SUM(units), 0), COALESCE(SUM(total), 0)
            FROM bills WHERE DATE(created_at)=?
        """, (today,)).fetchone()
        bill_count, total_units, total_amount = totals
        generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            INSERT INTO hospital_daily_bills
            (bill_date, patient_bills, total_units, total_amount, generated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(bill_date) DO UPDATE SET
                patient_bills=excluded.patient_bills,
                total_units=excluded.total_units,
                total_amount=excluded.total_amount,
                generated_at=excluded.generated_at
        """, (today, bill_count, total_units, total_amount, generated))
        hospital_id = cur.execute(
            "SELECT id FROM hospital_daily_bills WHERE bill_date=?", (today,)
        ).fetchone()[0]
        db.commit()

        messagebox.showinfo(
            "Hospital Daily Bill",
            f"HOSPITAL DAILY SUMMARY\n"
            f"Hospital Bill No: H-{hospital_id:05d}\n"
            f"Date: {today}\n\n"
            f"Individual patient bills: {bill_count}\n"
            f"Total blood units issued: {total_units}\n"
            f"Total amount: ₹{total_amount:,.2f}\n\n"
            "This is a separate daily summary bill for hospital records."
        )
        show_payments()

    button(
        form, "Generate separate hospital bill for today",
        generate_hospital_daily_bill, bg=BLUE
    ).pack(anchor="w", padx=16, pady=(0, 12))

    def refresh():
        tree.delete(*tree.get_children())

        rows = cur.execute("""
            SELECT id, patient, blood_group, units, unit_cost,
                   total, payment_method, payment_status, created_at
            FROM bills ORDER BY id DESC
        """).fetchall()

        for row_data in rows:
            vals = list(row_data)
            vals[4] = f"₹{vals[4]:,.2f}"
            vals[5] = f"₹{vals[5]:,.2f}"
            tree.insert("", "end", values=vals)

    def create_bill():
        name = patient.get().strip()

        try:
            count = parse_requested_units(units_entry.get())
            if not name or count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid details",
                "Enter patient name and a valid positive unit count (e.g. 1) "
                "or volume (e.g. 500ml). A volume entry counts as one blood bag."
            )
            return

        grp = group_var.get()

        stock = cur.execute("""
            SELECT units, service_cost
            FROM blood_stock WHERE blood_group=?
        """, (grp,)).fetchone()

        available, unit_cost = stock

        if count > available:
            messagebox.showerror(
                "Insufficient stock",
                f"Only {available} unit(s) of {grp} are listed in stock."
            )
            return

        method = method_var.get()

        if method == "Online Payment (Demo)":
            ok = messagebox.askyesno(
                "Demo online payment",
                "This is a simulation only. No real money will be transferred. "
                "Mark this demo payment as successful?"
            )
            if not ok:
                return
            pay_status = "Paid (Demo)"
        else:
            pay_status = "Cash Due"

        total = count * unit_cost
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            INSERT INTO bills
            (patient, blood_group, units, unit_cost, total,
             payment_method, payment_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, grp, count, unit_cost, total,
            method, pay_status, now
        ))

        receipt_id = cur.lastrowid

        cur.execute(
            "UPDATE blood_stock SET units=units-? WHERE blood_group=?",
            (count, grp)
        )

        db.commit()
        refresh()

        messagebox.showinfo(
            "Bill created",
            f"Receipt #{receipt_id:05d}\n"
            f"Patient: {name}\n"
            f"Total: ₹{total:,.2f}\n"
            f"Payment: {method}\n"
            f"Status: {pay_status}"
        )

        patient.delete(0, "end")
        units_entry.delete(0, "end")
        calc_total()

    button(
        form, "Generate bill & update stock",
        create_bill, bg=TEAL
    ).pack(anchor="w", padx=16, pady=(0, 13))

    refresh()
    calc_total()

    tk.Label(
        content,
        text="Online payment is demo-only. Charges are illustrative service fees.",
        bg=BG, fg=MUTED, font=("Segoe UI", 9)
    ).pack(anchor="w", pady=(8, 0))

    daily_rows = cur.execute("""
        SELECT id, bill_date, patient_bills, total_units, total_amount, generated_at
        FROM hospital_daily_bills ORDER BY bill_date DESC LIMIT 10
    """).fetchall()
    if daily_rows:
        popup_button = button(
            content, "View saved hospital daily bills",
            lambda: show_hospital_bill_history(), bg=NAVY2
        )
        popup_button.pack(anchor="w", pady=(8, 0))


def show_hospital_bill_history():
    win = tk.Toplevel(root)
    win.title("Hospital Daily Bill History")
    win.geometry("850x420")
    win.configure(bg=BG)
    heading(win, "Hospital Daily Bill History", "One separate summary per date.")
    holder, tree = make_table(
        win,
        ("bill_no", "date", "patient_bills", "total_units", "total_amount", "generated_at"),
        [100, 130, 130, 120, 140, 190], 10
    )
    holder.pack(fill="both", expand=True, padx=18, pady=(0, 18))
    for record in cur.execute("""
        SELECT id, bill_date, patient_bills, total_units, total_amount, generated_at
        FROM hospital_daily_bills ORDER BY bill_date DESC
    """).fetchall():
        tree.insert("", "end", values=(
            f"H-{record[0]:05d}", record[1], record[2], record[3],
            f"₹{record[4]:,.2f}", record[5]
        ))


# ---------- NAVIGATION ----------
def navigate(name, func):
    for key, btn in nav_buttons.items():
        btn.configure(
            bg=NAVY2 if key == name else NAVY,
            fg=WHITE if key == name else "#B9C4DB"
        )
    func()


pages = [
    ("Dashboard", show_dashboard, "▦"),
    ("Blood Inventory", show_inventory, "♥"),
    ("Doctors", show_doctors, "+"),
    ("Available Nurses", show_nurses, "✚"),
    ("Collections", show_collections, "↗"),
    ("Payments & Bills", show_payments, "▤")
]

for name, func, symbol in pages:
    btn = tk.Button(
        sidebar,
        text=f"  {symbol}    {name}",
        command=lambda n=name, f=func: navigate(n, f),
        bg=NAVY2 if name == "Dashboard" else NAVY,
        fg=WHITE if name == "Dashboard" else "#B9C4DB",
        activebackground=NAVY2,
        activeforeground=WHITE,
        relief="flat", bd=0,
        anchor="w", padx=18, pady=13,
        cursor="hand2",
        font=("Segoe UI", 10, "bold")
    )
    btn.pack(fill="x", padx=10, pady=3)
    nav_buttons[name] = btn

spacer = tk.Frame(sidebar, bg=NAVY)
spacer.pack(fill="both", expand=True)

bottom = tk.Frame(sidebar, bg="#202E4D")
bottom.pack(fill="x", padx=13, pady=15)

mini = tk.Canvas(
    bottom, height=62,
    bg="#202E4D", highlightthickness=0
)
mini.pack(fill="x", padx=8, pady=(8, 0))

mini.create_oval(12, 5, 53, 46, fill="#3A4D72", outline="")
mini.create_polygon(
    32, 11, 20, 29, 21, 37,
    28, 43, 36, 43, 43, 36, 42, 29,
    fill=RED, outline=""
)
mini.create_text(
    76, 25, text="Be a lifesaver",
    fill=WHITE, font=("Segoe UI", 10, "bold"), anchor="w"
)

tk.Label(
    bottom, text="A little care can save a life.",
    bg="#202E4D", fg="#B9C4DB",
    font=("Segoe UI", 8)
).pack(anchor="w", padx=13, pady=(0, 12))

# ---------- TOP STRIP ----------
strip = tk.Frame(
    main, bg=WHITE, height=54,
    highlightbackground=BORDER, highlightthickness=1
)
strip.pack(fill="x", before=content)
strip.pack_propagate(False)

tk.Label(
    strip, text="  HOSPITAL MANAGEMENT  /  BLOOD BANK",
    bg=WHITE, fg=MUTED,
    font=("Segoe UI", 9, "bold")
).pack(side="left", padx=18)

tk.Label(
    strip, text="● SYSTEM READY",
    bg=WHITE, fg=TEAL,
    font=("Segoe UI", 9, "bold")
).pack(side="right", padx=22)


def on_close():
    db.commit()
    db.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)
show_dashboard()
root.mainloop()
