import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from PIL import Image, ImageTk

import database

# ---------------- COLORS ----------------

BG = "#FFF5F8"
PINK = "#E9A6BD"
DARK_PINK = "#C66F91"
LAVENDER = "#E8DDF5"
WHITE = "#FFFFFF"
TEXT = "#554455"
LIGHT_TEXT = "#917D91"
CATEGORIES = [
    "Books", "Electronics", "Fashion",
    "Beauty", "Accessories", "Other"
]

# ---------------- MAIN APPLICATION ----------------

class WishlistApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("My Wishlist Manager")
        self.geometry("1150x720")
        self.minsize(950, 650)
        self.configure(bg=BG)

        self.selected_image = ""
        self.current_photo = None

        self.setup_styles()
        self.create_widgets()
        self.refresh_items()

    # ---------------- STYLES ----------------

    def setup_styles(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=WHITE,
            foreground=TEXT,
            rowheight=35,
            fieldbackground=WHITE,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=LAVENDER,
            foreground=TEXT,
            font=("Arial", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", PINK)],
            foreground=[("selected", TEXT)]
        )

        style.configure(
            "TCombobox",
            fieldbackground=WHITE,
            background=WHITE
        )

        style.configure(
            "Pink.Horizontal.TProgressbar",
            troughcolor=LAVENDER,
            background=DARK_PINK
        )

    # ---------------- MAIN SCREEN ----------------

    def create_widgets(self):

        # Header
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=30, pady=(22, 10))

        tk.Label(
            header,
            text="my wishlist",
            font=("Georgia", 28, "bold"),
            bg=BG,
            fg=DARK_PINK
        ).pack(anchor="w")

        tk.Label(
            header,
            text="A little place for everything you dream of buying.",
            font=("Arial", 11),
            bg=BG,
            fg=LIGHT_TEXT
        ).pack(anchor="w")

        # Statistics
        stats_frame = tk.Frame(self, bg=BG)
        stats_frame.pack(fill="x", padx=30, pady=12)

        self.stat_labels = {}

        stats = [
            ("Total Items", "total", PINK),
            ("Purchased", "purchased", LAVENDER),
            ("Pending", "pending", "#F5E3E9"),
            ("Total Spent", "spent", "#E8E5FA")
        ]

        for title, key, color in stats:

            card = tk.Frame(
                stats_frame,
                bg=color,
                padx=20,
                pady=13
            )

            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=6
            )

            tk.Label(
                card,
                text=title,
                bg=color,
                fg=TEXT,
                font=("Arial", 10)
            ).pack(anchor="w")

            value = tk.Label(
                card,
                text="0",
                bg=color,
                fg=TEXT,
                font=("Arial", 20, "bold")
            )

            value.pack(anchor="w")

            self.stat_labels[key] = value

        # Budget section
        budget_frame = tk.Frame(
            self,
            bg=WHITE,
            padx=18,
            pady=12
        )

        budget_frame.pack(fill="x", padx=36, pady=10)

        budget_top = tk.Frame(budget_frame, bg=WHITE)
        budget_top.pack(fill="x")

        tk.Label(
            budget_top,
            text="My Shopping Budget",
            font=("Arial", 11, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(side="left")

        tk.Button(
            budget_top,
            text="Set Budget",
            bg=LAVENDER,
            fg=TEXT,
            relief="flat",
            command=self.change_budget,
            padx=12
        ).pack(side="right")

        self.budget_label = tk.Label(
            budget_frame,
            text="Spent: ₹0 / ₹0",
            bg=WHITE,
            fg=LIGHT_TEXT,
            font=("Arial", 10)
        )

        self.budget_label.pack(anchor="w", pady=7)

        self.progress = ttk.Progressbar(
            budget_frame,
            style="Pink.Horizontal.TProgressbar",
            maximum=100,
            mode="determinate"
        )

        self.progress.pack(fill="x")

        # Search and filter section
        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill="x", padx=36, pady=12)

        self.search_var = tk.StringVar()

        search_entry = tk.Entry(
            toolbar,
            textvariable=self.search_var,
            font=("Arial", 11),
            bg=WHITE,
            fg=TEXT,
            relief="flat",
            width=30
        )

        search_entry.pack(side="left", ipady=8)
        search_entry.bind(
            "<KeyRelease>",
            lambda event: self.refresh_items()
        )

        self.category_var = tk.StringVar(value="All")

        category_box = ttk.Combobox(
            toolbar,
            textvariable=self.category_var,
            values=["All"] + CATEGORIES,
            state="readonly",
            width=16
        )

        category_box.pack(side="left", padx=12, ipady=5)

        category_box.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_items()
        )

        tk.Button(
            toolbar,
            text="+ Add Item",
            bg=DARK_PINK,
            fg=WHITE,
            relief="flat",
            font=("Arial", 10, "bold"),
            command=self.add_new_item,
            padx=18,
            pady=5
        ).pack(side="right")

        # Main content
        content = tk.Frame(self, bg=BG)
        content.pack(
            fill="both",
            expand=True,
            padx=36,
            pady=(0, 20)
        )

        # Product table
        table_frame = tk.Frame(content, bg=WHITE)
        table_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        columns = (
            "ID", "Name", "Category",
            "Price", "Status"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "ID": "ID",
            "Name": "Product Name",
            "Category": "Category",
            "Price": "Price (₹)",
            "Status": "Status"
        }

        widths = {
            "ID": 40,
            "Name": 170,
            "Category": 100,
            "Price": 90,
            "Status": 100
        }

        for column in columns:

            self.tree.heading(
                column,
                text=headings[column]
            )

            self.tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        scrollbar.pack(side="right", fill="y")

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.show_selected_item
        )

        # Product preview
        preview = tk.Frame(
            content,
            bg=WHITE,
            width=255,
            padx=15,
            pady=15
        )

        preview.pack(
            side="right",
            fill="y",
            padx=(15, 0)
        )

        preview.pack_propagate(False)

        tk.Label(
            preview,
            text="Item Details",
            bg=WHITE,
            fg=DARK_PINK,
            font=("Georgia", 16, "bold")
        ).pack(pady=(0, 12))

        self.image_label = tk.Label(
            preview,
            text="No image selected",
            bg=BG,
            fg=LIGHT_TEXT,
            width=25,
            height=5
        )

        self.image_label.pack(fill="x", pady=5)

        # Buttons at the bottom of the preview
        button_frame = tk.Frame(preview, bg=WHITE)
        button_frame.pack(side="bottom", fill="x")

        buttons = [
            ("Edit Item", self.edit_item),
            ("Delete Item", self.remove_item),
            ("Mark Purchased / Pending", self.toggle_status)
        ]

        for text, command in buttons:
            tk.Button(
                button_frame,
                text=text,
                command=command,
                bg=LAVENDER,
                fg=TEXT,
                relief="flat",
                font=("Arial", 9, "bold"),
                pady=5
            ).pack(fill="x", pady=3)

        # Item Details heading
        tk.Label(
            preview,
            text="Item Details",
            bg=WHITE,
            fg=DARK_PINK,
            font=("Georgia", 16, "bold")
        ).pack(pady=(0, 8))

        # Product image
        self.image_label = tk.Label(
            preview,
            text="No image selected",
            bg=BG,
            fg=LIGHT_TEXT,
            width=25,
            height=4
        )

        self.image_label.pack(fill="x", pady=4)

        # Item information
        self.detail_label = tk.Label(
            preview,
            text="Select a product to see details.",
            bg=WHITE,
            fg=TEXT,
            font=("Arial", 9),
            justify="left",
            wraplength=215
        )

        self.detail_label.pack(
            anchor="w",
            fill="x",
            pady=5
        )


        for text, command in buttons:

            tk.Button(
                preview,
                text=text,
                command=command,
                bg=LAVENDER,
                fg=TEXT,
                relief="flat",
                font=("Arial", 9, "bold"),
                pady=8
            ).pack(fill="x", pady=5)

    # ---------------- REFRESH DATA ----------------

    def refresh_items(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        items = database.get_items(
            self.search_var.get(),
            self.category_var.get()
        )

        for item in items:

            self.tree.insert(
                "",
                "end",
                iid=str(item[0]),
                values=(
                    item[0],
                    item[1],
                    item[2],
                    f"{item[3]:.2f}",
                    item[6]
                )
            )

        self.update_dashboard()

    # ---------------- DASHBOARD ----------------

    def update_dashboard(self):

        total, purchased, pending, spent, budget = (
            database.get_stats()
        )

        self.stat_labels["total"].config(text=str(total))

        self.stat_labels["purchased"].config(
            text=str(purchased)
        )

        self.stat_labels["pending"].config(
            text=str(pending)
        )

        self.stat_labels["spent"].config(
            text=f"₹{spent:.2f}"
        )

        self.budget_label.config(
            text=f"Spent: ₹{spent:.2f} / ₹{budget:.2f}"
        )

        percentage = 0

        if budget > 0:
            percentage = min((spent / budget) * 100, 100)

        self.progress["value"] = percentage

    # ---------------- SELECT ITEM ----------------

    def get_selected_id(self):

        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a product first."
            )
            return None

        return int(selected[0])

    
    def show_selected_item(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        item_id = int(selected[0])

        items = database.get_items()
        item = next(
            (x for x in items if x[0] == item_id),
            None
        )

        if item is None:
            return

        self.detail_label.config(
            text=(
                f"Name: {item[1]}\n"
                f"Category: {item[2]}\n"
                f"Price: ₹{item[3]:.2f}\n"
                f"Status: {item[6]}\n\n"
                f"Description:\n{item[4] or 'No description'}"
            )
        )

        self.current_photo = None

        if item[5]:
            try:
                image = Image.open(item[5])
                image.thumbnail((215, 120))

                self.current_photo = ImageTk.PhotoImage(image)

                self.image_label.config(
                    image=self.current_photo,
                    text=""
                )

            except Exception:
                self.image_label.config(
                    image="",
                    text="Image unavailable"
                )

        else:
            self.image_label.config(
                image="",
                text="No image selected"
            )


    # ---------------- ADD ITEM ----------------

    def add_new_item(self):
        self.item_form()

    # ---------------- EDIT ITEM ----------------

    def edit_item(self):

        item_id = self.get_selected_id()

        if item_id is None:
            return

        items = database.get_items()
        item = next(
            (x for x in items if x[0] == item_id),
            None
        )

        if item:
            self.item_form(item)

    # ---------------- ITEM FORM ----------------

    def item_form(self, item=None):

        editing = item is not None

        window = tk.Toplevel(self)
        window.title("Edit Wishlist Item" if editing else "Add Wishlist Item")
        window.geometry("420x550")
        window.configure(bg=BG)
        window.resizable(False, False)
        window.transient(self)
        window.grab_set()

        image_path = tk.StringVar(
            value=item[5] if editing else ""
        )

        tk.Label(
            window,
            text="Edit Item" if editing else "Add New Item",
            font=("Georgia", 21, "bold"),
            bg=BG,
            fg=DARK_PINK
        ).pack(pady=18)

        form = tk.Frame(window, bg=BG, padx=30)
        form.pack(fill="both", expand=True)

        def add_label(text):
            tk.Label(
                form,
                text=text,
                bg=BG,
                fg=TEXT,
                font=("Arial", 10, "bold")
            ).pack(anchor="w", pady=(7, 3))

        add_label("Product Name")

        name_entry = tk.Entry(form, font=("Arial", 11))
        name_entry.pack(fill="x", ipady=5)

        add_label("Category")

        category_var = tk.StringVar(
            value=item[2] if editing else CATEGORIES[0]
        )

        category_box = ttk.Combobox(
            form,
            textvariable=category_var,
            values=CATEGORIES,
            state="readonly"
        )

        category_box.pack(fill="x", ipady=4)

        add_label("Price (₹)")

        price_entry = tk.Entry(form, font=("Arial", 11))
        price_entry.pack(fill="x", ipady=5)

        add_label("Description")

        description_entry = tk.Text(
            form,
            height=4,
            font=("Arial", 10)
        )

        description_entry.pack(fill="x")

        add_label("Product Image")

        image_frame = tk.Frame(form, bg=BG)
        image_frame.pack(fill="x")

        tk.Entry(
            image_frame,
            textvariable=image_path,
            state="readonly"
        ).pack(side="left", fill="x", expand=True)

        def browse_image():

            path = filedialog.askopenfilename(
                parent=window,
                title="Select Product Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")
                ]
            )

            if path:
                image_path.set(path)

        tk.Button(
            image_frame,
            text="Browse",
            command=browse_image,
            bg=LAVENDER,
            relief="flat"
        ).pack(side="right", padx=5)

        if editing:

            name_entry.insert(0, item[1])
            price_entry.insert(0, str(item[3]))
            description_entry.insert("1.0", item[4] or "")

        def save_item():

            name = name_entry.get().strip()
            category = category_var.get()
            price_text = price_entry.get().strip()
            description = description_entry.get("1.0", "end").strip()
            image = image_path.get()

            if not name or not price_text:
                messagebox.showerror(
                    "Missing Information",
                    "Please enter product name and price.",
                    parent=window
                )
                return

            try:
                price = float(price_text)

                if price < 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Invalid Price",
                    "Please enter a valid non-negative price.",
                    parent=window
                )
                return

            if editing:

                database.update_item(
                    item[0],
                    name,
                    category,
                    price,
                    description,
                    image
                )

            else:

                database.add_item(
                    name,
                    category,
                    price,
                    description,
                    image
                )

            window.destroy()
            self.refresh_items()

            messagebox.showinfo(
                "Success",
                "Wishlist item saved successfully!"
            )

        tk.Button(
            form,
            text="Save Item",
            command=save_item,
            bg=DARK_PINK,
            fg=WHITE,
            font=("Arial", 11, "bold"),
            relief="flat",
            pady=9
        ).pack(fill="x", pady=15)

    # ---------------- DELETE ITEM ----------------

    def remove_item(self):

        item_id = self.get_selected_id()

        if item_id is None:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this item?"
        )

        if confirm:

            database.delete_item(item_id)

            self.detail_label.config(
                text="Select a product to see details."
            )

            self.image_label.config(
                image="",
                text="No image selected"
            )

            self.current_photo = None

            self.refresh_items()

    # ---------------- PURCHASE STATUS ----------------

    def toggle_status(self):

        item_id = self.get_selected_id()

        if item_id is None:
            return

        items = database.get_items()

        item = next(
            (x for x in items if x[0] == item_id),
            None
        )

        if item is None:
            return

        if item[6] == "Pending":
            new_status = "Purchased"
        else:
            new_status = "Pending"

        database.update_status(item_id, new_status)

        self.refresh_items()

        self.show_selected_item()

    
    # ---------------- BUDGET ----------------

    def change_budget(self):

        current_budget = database.get_stats()[4]

        amount = simpledialog.askfloat(
            "Shopping Budget",
            "Enter your total shopping budget (₹):",
            initialvalue=current_budget,
            minvalue=0,
            parent=self
        )

        if amount is not None:

            database.set_budget(amount)
            self.update_dashboard()


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    app = WishlistApp()
    app.mainloop()
