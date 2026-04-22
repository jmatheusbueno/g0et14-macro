import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController

from macro_constants import MOUSE_BUTTONS
from macro_models import MacroItem
from macro_runner import MacroRunner
from macro_storage import SaveRepository
from macro_validator import MacroValidator


class MacroApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("G0et1a Macro")
        self.root.geometry("640x620")
        self.root.resizable(False, False)
        self.bg_color = "#322533"

        self._configure_theme()

        self.keyboard = KeyboardController()
        self.mouse = MouseController()

        self.validator = MacroValidator()
        base_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
        self.save_repo = SaveRepository(base_dir, self.validator)
        self.runner = MacroRunner(self._resolve_action)

        self.macros: list[MacroItem] = []
        self.next_id = 1

        self.action_var = tk.StringVar(value="key")
        self.key_var = tk.StringVar(value="space")
        self.interval_var = tk.StringVar(value="30")
        self.item_start_delay_var = tk.StringVar(value="0")
        self.start_delay_var = tk.StringVar(value="0")
        self.mouse_button_var = tk.StringVar(value="left")
        self.save_name_var = tk.StringVar(value="meu_save")
        self.selected_save_var = tk.StringVar(value="")

        self._build_ui()

    def _configure_theme(self) -> None:
        self.root.configure(bg=self.bg_color)
        style = ttk.Style(self.root)
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground="#FFFFFF")
        style.configure("TRadiobutton", background=self.bg_color, foreground="#FFFFFF")
        style.configure("TLabelframe", background=self.bg_color)
        style.configure("TLabelframe.Label", background=self.bg_color, foreground="#FFFFFF")
        style.configure("TButton", background="#E9E0EE", foreground="#322533")
        style.map(
            "TButton",
            background=[("active", "#E9E0EE"), ("disabled", "#CFC5D4")],
            foreground=[("disabled", "#6E5B73")],
        )
        style.configure("TEntry", fieldbackground="#755378", foreground="#FFFFFF")
        style.configure(
            "TCombobox",
            fieldbackground="#755378",
            background="#755378",
            foreground="#FFFFFF",
            arrowcolor="#FFFFFF",
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", "#755378")],
            selectbackground=[("readonly", "#755378")],
            selectforeground=[("readonly", "#FFFFFF")],
        )
        style.configure(
            "Treeview.Heading",
            background="#E9E0EE",
            foreground="#322533",
        )

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Cadastrar macro").pack(anchor="w")

        action_row = ttk.Frame(container)
        action_row.pack(fill="x", pady=(8, 6))
        ttk.Radiobutton(
            action_row,
            text="Tecla",
            value="key",
            variable=self.action_var,
            command=self._toggle_inputs,
        ).pack(side="left", padx=(0, 16))

        ttk.Radiobutton(
            action_row,
            text="Clique do mouse",
            value="mouse",
            variable=self.action_var,
            command=self._toggle_inputs,
        ).pack(side="left")

        form_grid = ttk.Frame(container)
        form_grid.pack(fill="x", pady=(4, 8))

        ttk.Label(form_grid, text="Tecla:").grid(row=0, column=0, sticky="w")
        self.key_entry = ttk.Entry(form_grid, textvariable=self.key_var, width=18)
        self.key_entry.grid(row=0, column=1, sticky="w", padx=(8, 16))
        self.key_entry.bind("<Tab>", self._on_key_entry_tab)
        self.key_entry.bind("<space>", self._on_key_entry_space)

        ttk.Label(form_grid, text="Botao:").grid(row=0, column=2, sticky="w")
        self.mouse_combo = ttk.Combobox(
            form_grid,
            textvariable=self.mouse_button_var,
            values=["left", "right", "middle"],
            state="readonly",
            width=12,
        )
        self.mouse_combo.grid(row=0, column=3, sticky="w", padx=(8, 16))

        ttk.Label(form_grid, text="Intervalo (s):").grid(row=0, column=4, sticky="w")
        self.interval_entry = ttk.Entry(form_grid, textvariable=self.interval_var, width=10)
        self.interval_entry.grid(row=0, column=5, sticky="w", padx=(8, 0))

        ttk.Label(form_grid, text="Delay do input (s):").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.item_delay_entry = ttk.Entry(form_grid, textvariable=self.item_start_delay_var, width=10)
        self.item_delay_entry.grid(row=1, column=1, sticky="w", padx=(8, 16), pady=(8, 0))

        crud_row = ttk.Frame(container)
        crud_row.pack(fill="x", pady=(4, 10))

        self.add_btn = ttk.Button(crud_row, text="Adicionar", command=self.add_macro)
        self.add_btn.pack(side="left", padx=(0, 8))

        self.update_btn = ttk.Button(crud_row, text="Atualizar", command=self.update_macro)
        self.update_btn.pack(side="left", padx=(0, 8))

        self.remove_btn = ttk.Button(crud_row, text="Remover", command=self.remove_macro)
        self.remove_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = ttk.Button(crud_row, text="Limpar campos", command=self.clear_form)
        self.clear_btn.pack(side="left")

        self.tree = ttk.Treeview(
            container,
            columns=("tipo", "valor", "intervalo", "delay_input"),
            show="headings",
            height=8,
        )
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("valor", text="Input")
        self.tree.heading("intervalo", text="Intervalo (s)")
        self.tree.heading("delay_input", text="Delay input (s)")

        self.tree.column("tipo", width=140, anchor="w")
        self.tree.column("valor", width=160, anchor="w")
        self.tree.column("intervalo", width=120, anchor="center")
        self.tree.column("delay_input", width=120, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_macro)

        controls = ttk.Frame(container)
        controls.pack(fill="x", pady=(12, 0))

        ttk.Label(controls, text="Delay inicial (s):").pack(side="left", padx=(0, 8))
        self.delay_entry = ttk.Entry(controls, textvariable=self.start_delay_var, width=8)
        self.delay_entry.pack(side="left", padx=(0, 12))

        self.start_btn = ttk.Button(controls, text="Iniciar", command=self.start_macro)
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = ttk.Button(controls, text="Parar", command=self.stop_macro, state="disabled")
        self.stop_btn.pack(side="left")

        self.status_label = ttk.Label(container, text="Status: parado (0 macros)")
        self.status_label.pack(anchor="w", pady=(10, 0))

        saves_frame = ttk.LabelFrame(container, text="Saves")
        saves_frame.pack(fill="x", pady=(12, 0))

        ttk.Label(saves_frame, text="Nome:").grid(row=0, column=0, sticky="w", padx=(8, 8), pady=(8, 6))
        self.save_name_entry = ttk.Entry(saves_frame, textvariable=self.save_name_var, width=24)
        self.save_name_entry.grid(row=0, column=1, sticky="w", pady=(8, 6))

        self.save_btn = ttk.Button(saves_frame, text="Salvar", command=self.save_macros)
        self.save_btn.grid(row=0, column=2, sticky="w", padx=(8, 0), pady=(8, 6))

        ttk.Label(saves_frame, text="Carregar:").grid(row=1, column=0, sticky="w", padx=(8, 8), pady=(0, 8))
        self.saves_combo = ttk.Combobox(
            saves_frame,
            textvariable=self.selected_save_var,
            state="readonly",
            width=21,
        )
        self.saves_combo.grid(row=1, column=1, sticky="w", pady=(0, 8))

        self.load_btn = ttk.Button(saves_frame, text="Carregar", command=self.load_selected_save)
        self.load_btn.grid(row=1, column=2, sticky="w", padx=(8, 0), pady=(0, 8))

        self.refresh_saves_btn = ttk.Button(
            saves_frame,
            text="Atualizar lista",
            command=self._refresh_saves_list,
        )
        self.refresh_saves_btn.grid(row=1, column=3, sticky="w", padx=(8, 0), pady=(0, 8))

        self._toggle_inputs()
        self._refresh_tree()
        self._refresh_saves_list()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _toggle_inputs(self) -> None:
        is_key = self.action_var.get() == "key"
        self.key_entry.configure(state="normal" if is_key else "disabled")
        self.mouse_combo.configure(state="disabled" if is_key else "readonly")

    def _selected_item_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            return None
        return int(selected[0])

    def _format_type_label(self, item: MacroItem) -> str:
        return "Tecla" if item.action_type == "key" else "Clique mouse"

    def _format_value_label(self, item: MacroItem) -> str:
        if item.action_type == "key":
            return item.value
        return f"click {item.value}"

    def _refresh_tree(self) -> None:
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)

        for item in self.macros:
            self.tree.insert(
                "",
                "end",
                iid=str(item.item_id),
                values=(
                    self._format_type_label(item),
                    self._format_value_label(item),
                    f"{item.interval:g}",
                    f"{item.start_delay:g}",
                ),
            )

        self.status_label.configure(text=f"Status: parado ({len(self.macros)} macros)")

    def _collect_form_data(self) -> tuple[str, str, float, float]:
        action_type = self.action_var.get()
        interval = self.validator.parse_positive_number(
            self.interval_var.get().strip(),
            "O intervalo deve ser um numero maior que zero.",
        )
        item_start_delay = self.validator.parse_non_negative_number(
            self.item_start_delay_var.get().strip(),
            "O delay do input deve ser um numero nao negativo.",
        )

        if action_type == "key":
            key_value = self.validator.normalize_key_input(self.key_var.get())
            self.validator.parse_key(key_value)
            return action_type, key_value, interval, item_start_delay

        mouse_button = self.validator.validate_mouse_button(self.mouse_button_var.get())
        return action_type, mouse_button, interval, item_start_delay

    def add_macro(self) -> None:
        try:
            action_type, value, interval, item_start_delay = self._collect_form_data()
        except ValueError as err:
            messagebox.showerror("Erro", str(err))
            return

        self.macros.append(
            MacroItem(
                item_id=self.next_id,
                action_type=action_type,
                value=value,
                interval=interval,
                start_delay=item_start_delay,
            )
        )
        self.next_id += 1
        self._refresh_tree()

    def update_macro(self) -> None:
        selected_id = self._selected_item_id()
        if selected_id is None:
            messagebox.showwarning("Aviso", "Selecione uma macro para atualizar.")
            return

        try:
            action_type, value, interval, item_start_delay = self._collect_form_data()
        except ValueError as err:
            messagebox.showerror("Erro", str(err))
            return

        for index, item in enumerate(self.macros):
            if item.item_id == selected_id:
                self.macros[index] = MacroItem(
                    item_id=selected_id,
                    action_type=action_type,
                    value=value,
                    interval=interval,
                    start_delay=item_start_delay,
                )
                self._refresh_tree()
                self.tree.selection_set(str(selected_id))
                break

    def remove_macro(self) -> None:
        selected_id = self._selected_item_id()
        if selected_id is None:
            messagebox.showwarning("Aviso", "Selecione uma macro para remover.")
            return

        self.macros = [item for item in self.macros if item.item_id != selected_id]
        self._refresh_tree()

    def clear_form(self) -> None:
        self.action_var.set("key")
        self.key_var.set("space")
        self.mouse_button_var.set("left")
        self.interval_var.set("30")
        self.item_start_delay_var.set("0")
        self._toggle_inputs()

    def on_select_macro(self, _event=None) -> None:
        selected_id = self._selected_item_id()
        if selected_id is None:
            return

        item = next((macro for macro in self.macros if macro.item_id == selected_id), None)
        if item is None:
            return

        self.action_var.set(item.action_type)
        if item.action_type == "key":
            self.key_var.set(item.value)
        else:
            self.mouse_button_var.set(item.value)
        self.interval_var.set(f"{item.interval:g}")
        self.item_start_delay_var.set(f"{item.start_delay:g}")
        self._toggle_inputs()

    def _on_key_entry_tab(self, _event) -> str:
        if self.action_var.get() == "key":
            self.key_var.set("tab")
            return "break"
        return ""

    def _on_key_entry_space(self, _event) -> str:
        if self.action_var.get() == "key":
            self.key_var.set("space")
            return "break"
        return ""

    def _refresh_saves_list(self) -> None:
        save_names = self.save_repo.list_save_names()
        previous_selection = self.selected_save_var.get().strip()
        self.saves_combo.configure(values=save_names)

        if previous_selection in save_names:
            self.selected_save_var.set(previous_selection)
        elif save_names:
            self.selected_save_var.set(save_names[0])
        else:
            self.selected_save_var.set("")

    def save_macros(self) -> None:
        try:
            save_name = self.validator.sanitize_save_name(self.save_name_var.get())
            start_delay = self.validator.parse_non_negative_number(
                self.start_delay_var.get().strip(),
                "O delay inicial deve ser um numero nao negativo.",
            )
            save_path = self.save_repo.save(save_name, start_delay, self.macros)
        except ValueError as err:
            messagebox.showerror("Erro", str(err))
            return

        self._refresh_saves_list()
        self.selected_save_var.set(save_name)
        messagebox.showinfo("Sucesso", f"Save '{save_name}' gravado em {save_path.name}.")

    def load_selected_save(self) -> None:
        if self.runner.is_running:
            messagebox.showwarning("Aviso", "Pare a execucao antes de carregar um save.")
            return

        selected_name = self.selected_save_var.get().strip()
        if not selected_name:
            messagebox.showwarning("Aviso", "Selecione um save para carregar.")
            return

        try:
            start_delay, loaded_macros = self.save_repo.load(selected_name)
        except ValueError as err:
            messagebox.showerror("Erro", str(err))
            self._refresh_saves_list()
            return

        self.macros = loaded_macros
        self.next_id = len(self.macros) + 1
        self.save_name_var.set(selected_name)
        self.start_delay_var.set(f"{start_delay:g}")
        self._refresh_tree()
        self.tree.selection_remove(self.tree.selection())
        self.clear_form()
        messagebox.showinfo("Sucesso", f"Save '{selected_name}' carregado.")

    def _resolve_action(self, item: MacroItem):
        if item.action_type == "key":
            parsed_key = self.validator.parse_key(item.value)
            return lambda parsed_key=parsed_key: self._press_key(parsed_key)

        mouse_button = MOUSE_BUTTONS[item.value]
        return lambda mouse_button=mouse_button: self.mouse.click(mouse_button)

    def start_macro(self) -> None:
        if self.runner.is_running:
            return

        if not self.macros:
            messagebox.showwarning("Aviso", "Adicione pelo menos uma macro antes de iniciar.")
            return

        try:
            start_delay = self.validator.parse_non_negative_number(
                self.start_delay_var.get().strip(),
                "O delay inicial deve ser um numero nao negativo.",
            )
        except ValueError as err:
            messagebox.showerror("Erro", str(err))
            return

        self.runner.start(self.macros, start_delay)

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self._set_crud_state("disabled")
        self.status_label.configure(
            text=f"Status: executando ({len(self.macros)} macros, delay {start_delay:g}s)"
        )

    def _press_key(self, key) -> None:
        self.keyboard.press(key)
        self.keyboard.release(key)

    def stop_macro(self) -> None:
        self.runner.stop()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self._set_crud_state("normal")
        self.status_label.configure(text=f"Status: parado ({len(self.macros)} macros)")

    def _set_crud_state(self, state: str) -> None:
        self.add_btn.configure(state=state)
        self.update_btn.configure(state=state)
        self.remove_btn.configure(state=state)
        self.clear_btn.configure(state=state)
        self.key_entry.configure(state=state if self.action_var.get() == "key" else "disabled")
        self.mouse_combo.configure(state="readonly" if state == "normal" and self.action_var.get() == "mouse" else "disabled")
        self.interval_entry.configure(state=state)
        self.item_delay_entry.configure(state=state)
        self.delay_entry.configure(state=state)
        self.save_name_entry.configure(state=state)
        self.save_btn.configure(state=state)
        self.load_btn.configure(state=state)
        self.refresh_saves_btn.configure(state=state)
        self.saves_combo.configure(state="readonly" if state == "normal" else "disabled")

    def on_close(self) -> None:
        self.stop_macro()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    MacroApp(root)
    root.mainloop()
