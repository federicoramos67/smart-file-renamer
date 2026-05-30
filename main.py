import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from renamer import RenameOptions, build_rename_plan, execute_rename_plan
from utils import format_file_size, list_files


class SmartFileRenamerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart File Renamer")
        self.geometry("1050x680")
        self.minsize(900, 560)

        self.folder_path = tk.StringVar(value="")
        self.remove_special = tk.BooleanVar(value=True)
        self.spaces_to_underscores = tk.BooleanVar(value=True)
        self.add_numbering = tk.BooleanVar(value=False)
        self.add_date_prefix = tk.BooleanVar(value=False)
        self.start_number = tk.IntVar(value=1)
        self.padding = tk.IntVar(value=3)
        self.date_value = tk.StringVar(value="")
        self.status_text = tk.StringVar(value="Select a folder to begin.")
        self.duplicate_text = tk.StringVar(value="Duplicates: 0")

        self.files = []
        self.rename_plan = []

        self._configure_theme()
        self._build_ui()

    def _configure_theme(self):
        self.colors = {
            "bg": "#111318",
            "panel": "#1a1d24",
            "panel_2": "#20242d",
            "text": "#f1f5f9",
            "muted": "#94a3b8",
            "accent": "#38bdf8",
            "danger": "#fb7185",
            "success": "#34d399",
            "border": "#2f3542",
        }

        self.configure(bg=self.colors["bg"])

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            ".",
            background=self.colors["bg"],
            foreground=self.colors["text"],
            fieldbackground=self.colors["panel_2"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["border"],
            darkcolor=self.colors["border"],
        )
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("Panel.TFrame", background=self.colors["panel"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"])
        style.configure(
            "Muted.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["muted"],
        )
        style.configure(
            "Panel.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["text"],
        )
        style.configure(
            "PanelMuted.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["muted"],
        )
        style.configure(
            "TButton",
            background=self.colors["panel_2"],
            foreground=self.colors["text"],
            borderwidth=1,
            focusthickness=0,
            padding=(12, 8),
        )
        style.map(
            "TButton",
            background=[("active", "#2b313d"), ("pressed", "#27303b")],
            foreground=[("disabled", "#64748b")],
        )
        style.configure(
            "Accent.TButton",
            background=self.colors["accent"],
            foreground="#06121a",
            padding=(14, 9),
        )
        style.map("Accent.TButton", background=[("active", "#7dd3fc"), ("pressed", "#0ea5e9")])
        style.configure(
            "Danger.TButton",
            background="#3a2028",
            foreground="#fecdd3",
            padding=(12, 8),
        )
        style.map("Danger.TButton", background=[("active", "#5a2835")])
        style.configure(
            "TCheckbutton",
            background=self.colors["panel"],
            foreground=self.colors["text"],
            padding=(0, 5),
        )
        style.map(
            "TCheckbutton",
            background=[("active", self.colors["panel"])],
            foreground=[("disabled", "#64748b")],
        )
        style.configure(
            "TEntry",
            fieldbackground=self.colors["panel_2"],
            foreground=self.colors["text"],
            insertcolor=self.colors["text"],
            borderwidth=1,
            padding=7,
        )
        style.configure(
            "Treeview",
            background=self.colors["panel"],
            fieldbackground=self.colors["panel"],
            foreground=self.colors["text"],
            rowheight=30,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=self.colors["panel_2"],
            foreground=self.colors["text"],
            relief="flat",
            padding=8,
        )
        style.map("Treeview", background=[("selected", "#075985")])

    def _build_ui(self):
        header = ttk.Frame(self, padding=(22, 18, 22, 12))
        header.pack(fill="x")

        title = ttk.Label(header, text="Smart File Renamer", font=("Segoe UI", 22, "bold"))
        title.pack(anchor="w")
        subtitle = ttk.Label(
            header,
            text="Preview, clean, and rename batches of files safely.",
            style="Muted.TLabel",
            font=("Segoe UI", 10),
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        main = ttk.Frame(self, padding=(22, 8, 22, 18))
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._build_controls(main)
        self._build_preview(main)
        self._build_footer()

    def _build_controls(self, parent):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        folder_label = ttk.Label(panel, text="Folder", style="Panel.TLabel", font=("Segoe UI", 11, "bold"))
        folder_label.pack(anchor="w")

        folder_row = ttk.Frame(panel, style="Panel.TFrame")
        folder_row.pack(fill="x", pady=(8, 16))

        self.folder_entry = ttk.Entry(folder_row, textvariable=self.folder_path, width=34)
        self.folder_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(folder_row, text="Browse", command=self.select_folder).pack(side="left", padx=(8, 0))

        options_title = ttk.Label(panel, text="Rename Options", style="Panel.TLabel", font=("Segoe UI", 11, "bold"))
        options_title.pack(anchor="w", pady=(4, 8))

        self._add_check(panel, "Remove special characters", self.remove_special)
        self._add_check(panel, "Replace spaces with underscores", self.spaces_to_underscores)
        self._add_check(panel, "Add numbering", self.add_numbering)
        self._add_check(panel, "Add date prefix", self.add_date_prefix)

        number_box = ttk.Frame(panel, style="Panel.TFrame")
        number_box.pack(fill="x", pady=(12, 4))
        ttk.Label(number_box, text="Start", style="PanelMuted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(number_box, textvariable=self.start_number, width=8).grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Label(number_box, text="Padding", style="PanelMuted.TLabel").grid(row=0, column=1, sticky="w", padx=(14, 0))
        ttk.Entry(number_box, textvariable=self.padding, width=8).grid(row=1, column=1, sticky="w", padx=(14, 0), pady=(4, 0))

        ttk.Label(panel, text="Date prefix", style="PanelMuted.TLabel").pack(anchor="w", pady=(12, 4))
        ttk.Entry(panel, textvariable=self.date_value).pack(fill="x")
        ttk.Label(
            panel,
            text="Leave empty to use today's date.",
            style="PanelMuted.TLabel",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(4, 0))

        actions = ttk.Frame(panel, style="Panel.TFrame")
        actions.pack(fill="x", pady=(20, 0))
        ttk.Button(actions, text="Refresh Preview", command=self.refresh_preview).pack(fill="x")
        ttk.Button(actions, text="Rename Files", command=self.rename_files, style="Accent.TButton").pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Clear", command=self.clear_selection, style="Danger.TButton").pack(fill="x", pady=(8, 0))

        info = ttk.Label(
            panel,
            textvariable=self.duplicate_text,
            style="PanelMuted.TLabel",
            font=("Segoe UI", 10, "bold"),
        )
        info.pack(anchor="w", pady=(18, 0))

    def _add_check(self, parent, text, variable):
        check = ttk.Checkbutton(parent, text=text, variable=variable, command=self.refresh_preview)
        check.pack(anchor="w", fill="x")

    def _build_preview(self, parent):
        preview_panel = ttk.Frame(parent, style="Panel.TFrame", padding=14)
        preview_panel.grid(row=0, column=1, sticky="nsew")
        preview_panel.rowconfigure(1, weight=1)
        preview_panel.columnconfigure(0, weight=1)

        top = ttk.Frame(preview_panel, style="Panel.TFrame")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(top, text="Preview", style="Panel.TLabel", font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Label(top, textvariable=self.status_text, style="PanelMuted.TLabel").pack(side="right")

        columns = ("current", "new", "size", "status")
        self.tree = ttk.Treeview(preview_panel, columns=columns, show="headings")
        self.tree.heading("current", text="Current Name")
        self.tree.heading("new", text="New Name")
        self.tree.heading("size", text="Size")
        self.tree.heading("status", text="Status")
        self.tree.column("current", minwidth=220, width=300)
        self.tree.column("new", minwidth=220, width=320)
        self.tree.column("size", minwidth=80, width=90, anchor="e")
        self.tree.column("status", minwidth=120, width=150)
        self.tree.grid(row=1, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(preview_panel, orient="vertical", command=self.tree.yview)
        scroll.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.tag_configure("warning", foreground="#fbbf24")
        self.tree.tag_configure("changed", foreground=self.colors["success"])
        self.tree.tag_configure("blocked", foreground=self.colors["danger"])

    def _build_footer(self):
        footer = ttk.Frame(self, padding=(22, 0, 22, 16))
        footer.pack(fill="x")
        ttk.Label(
            footer,
            text="Tip: rename is blocked when duplicates or filename conflicts are detected.",
            style="Muted.TLabel",
        ).pack(anchor="w")

    def select_folder(self):
        selected = filedialog.askdirectory(title="Select folder to rename")
        if selected:
            self.folder_path.set(selected)
            self.refresh_preview()

    def clear_selection(self):
        self.folder_path.set("")
        self.files = []
        self.rename_plan = []
        self._clear_tree()
        self.status_text.set("Select a folder to begin.")
        self.duplicate_text.set("Duplicates: 0")

    def current_options(self):
        return RenameOptions(
            remove_special=self.remove_special.get(),
            spaces_to_underscores=self.spaces_to_underscores.get(),
            add_numbering=self.add_numbering.get(),
            add_date_prefix=self.add_date_prefix.get(),
            start_number=max(0, self._safe_int(self.start_number.get(), 1)),
            padding=max(1, self._safe_int(self.padding.get(), 3)),
            date_prefix=self.date_value.get().strip() or None,
        )

    def refresh_preview(self):
        folder = self.folder_path.get().strip()
        if not folder:
            return

        path = Path(folder)
        if not path.exists() or not path.is_dir():
            self.status_text.set("Folder not found.")
            return

        self.files = list_files(path)
        self.rename_plan = build_rename_plan(self.files, self.current_options())
        self._render_plan()

    def _render_plan(self):
        self._clear_tree()
        duplicate_count = sum(1 for item in self.rename_plan if item.has_duplicate)
        blocked_count = sum(1 for item in self.rename_plan if item.is_blocked)
        changed_count = sum(1 for item in self.rename_plan if item.old_name != item.new_name)

        for item in self.rename_plan:
            status = item.status
            tag = "changed"
            if item.is_blocked:
                tag = "blocked"
            elif item.has_duplicate:
                tag = "warning"
            elif item.old_name == item.new_name:
                tag = "warning"

            self.tree.insert(
                "",
                "end",
                values=(item.old_name, item.new_name, format_file_size(item.path.stat().st_size), status),
                tags=(tag,),
            )

        self.duplicate_text.set(f"Duplicates: {duplicate_count}")
        self.status_text.set(
            f"{len(self.rename_plan)} files, {changed_count} changes, {blocked_count} blocked"
        )

    def _clear_tree(self):
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

    def rename_files(self):
        if not self.rename_plan:
            messagebox.showinfo("Nothing to rename", "Select a folder and refresh the preview first.")
            return

        blocked = [item for item in self.rename_plan if item.is_blocked]
        if blocked:
            messagebox.showerror(
                "Rename blocked",
                "Resolve duplicate or conflicting filenames before renaming.",
            )
            return

        changed = [item for item in self.rename_plan if item.old_name != item.new_name]
        if not changed:
            messagebox.showinfo("No changes", "The current options do not change any filenames.")
            return

        confirmed = messagebox.askyesno(
            "Confirm rename",
            f"Rename {len(changed)} files in this folder?",
        )
        if not confirmed:
            return

        try:
            renamed_count = execute_rename_plan(self.rename_plan)
        except OSError as exc:
            messagebox.showerror("Rename failed", str(exc))
            self.refresh_preview()
            return

        messagebox.showinfo("Done", f"Renamed {renamed_count} files.")
        self.refresh_preview()

    @staticmethod
    def _safe_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError, tk.TclError):
            return default


if __name__ == "__main__":
    app = SmartFileRenamerApp()
    app.mainloop()
