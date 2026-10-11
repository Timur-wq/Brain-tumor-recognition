import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from dotenv import load_dotenv
from PIL import Image, ImageTk

from NeuroModel import NeuroModel


class BrainTumorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NeuroScan | Анализ MRI")
        self.root.geometry("920x650")
        self.root.minsize(760, 560)
        self.root.configure(bg="#f2f5f4")
        self.image_path = None
        self.preview = None
        self.model = NeuroModel()
        self.model_ready = False

        self._configure_styles()
        self._build_interface()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f2f5f4")
        style.configure("TLabel", background="#f2f5f4", foreground="#18312d", font=("Segoe UI", 11))
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 25), foreground="#143d35")
        style.configure("Muted.TLabel", foreground="#64736f", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI Semibold", 10), padding=(16, 11))
        style.configure("Accent.TButton", background="#176b58", foreground="white")
        style.map("Accent.TButton", background=[("active", "#125545"), ("disabled", "#9aadaa")])

    def _build_interface(self):
        container = ttk.Frame(self.root, padding=(34, 26))
        container.pack(fill="both", expand=True)
        ttk.Label(container, text="NeuroScan", style="Title.TLabel").pack(anchor="w")
        ttk.Label(container, text="Анализ МРТ головного мозга", style="Muted.TLabel").pack(
            anchor="w", pady=(3, 22)
        )

        content = ttk.Frame(container)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        self.image_panel = tk.Frame(content, bg="#e4ebe8", highlightthickness=1, highlightbackground="#d4dfda")
        self.image_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.image_label = tk.Label(
            self.image_panel,
            text="Изображение не выбрано",
            bg="#e4ebe8",
            fg="#64736f",
            font=("Segoe UI", 12),
        )
        self.image_label.pack(fill="both", expand=True, padx=18, pady=18)

        result_panel = tk.Frame(content, bg="#ffffff", highlightthickness=1, highlightbackground="#dce5e1")
        result_panel.grid(row=0, column=1, sticky="nsew")
        tk.Label(result_panel, text="РЕЗУЛЬТАТ", bg="white", fg="#71817c", font=("Segoe UI Semibold", 9)).grid(
            row=0, column=0, sticky="w", padx=22, pady=(24, 12)
        )
        self.result_label = tk.Label(
            result_panel,
            text="Ожидает анализа",
            bg="white",
            fg="#18312d",
            font=("Segoe UI Semibold", 19),
            wraplength=250,
            justify="left",
        )
        self.result_label.grid(row=1, column=0, sticky="nw", padx=22)
        self.confidence_label = tk.Label(
            result_panel,
            text="Выберите снимок MRI",
            bg="white",
            fg="#64736f",
            font=("Segoe UI", 10),
            wraplength=250,
            justify="left",
        )
        self.confidence_label.grid(row=2, column=0, sticky="nw", padx=22, pady=(10, 16))
        self.status_label = ttk.Label(result_panel, text="Модель загружается...", style="Muted.TLabel", wraplength=250)
        self.status_label.grid(row=3, column=0, sticky="sw", padx=22, pady=(0, 22))

        actions = ttk.Frame(container)
        actions.pack(fill="x", pady=(18, 0))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        self.pick_button = ttk.Button(actions, text="Выбрать изображение", command=self._pick_image)
        self.pick_button.grid(row=0, column=0, sticky="w")
        self.analyze_button = ttk.Button(
            actions,
            text="Анализировать",
            style="Accent.TButton",
            command=self._analyze,
            state="disabled",
        )
        self.analyze_button.grid(row=0, column=1, sticky="e")
        ttk.Label(
            container,
            text="Результат модели не является медицинским диагнозом.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(14, 0))

        threading.Thread(target=self._load_model, daemon=True).start()

    def _load_model(self):
        self.root.after(0, lambda: self.status_label.configure(text="Подключение к Roboflow..."))
        try:
            self.model.getModel()
        except Exception as error:
            self.root.after(0, lambda error=error: self.status_label.configure(text=f"Модель недоступна: {error}"))
            return

        self.model_ready = True
        self.root.after(0, lambda: self.status_label.configure(text="Модель готова к анализу"))
        self.root.after(0, self._update_analyze_button)

    def _pick_image(self):
        path = filedialog.askopenfilename(
            title="Выберите изображение MRI",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"), ("Все файлы", "*.*")],
        )
        if not path:
            return

        try:
            self.root.update_idletasks()
            image = Image.open(path).convert("RGB")
            preview_width = max(1, self.image_panel.winfo_width() - 48)
            preview_height = max(1, self.image_panel.winfo_height() - 48)
            image.thumbnail((preview_width, preview_height))
            self.preview = ImageTk.PhotoImage(image)
        except OSError as error:
            messagebox.showerror("Не удалось открыть изображение", str(error))
            return

        self.image_path = path
        self.image_label.configure(image=self.preview, text="")
        self.confidence_label.configure(text=os.path.basename(path))
        self.result_label.configure(text="Ожидает анализа", fg="#18312d")
        self._update_analyze_button()

    def _update_analyze_button(self):
        enabled = self.image_path is not None and self.model_ready
        self.analyze_button.configure(state="normal" if enabled else "disabled")

    def _analyze(self):
        if not self.image_path or not self.model_ready:
            return

        self.analyze_button.configure(state="disabled")
        self.pick_button.configure(state="disabled")
        self.status_label.configure(text="Выполняется анализ...")
        threading.Thread(target=self._run_analysis, args=(self.image_path,), daemon=True).start()

    def _run_analysis(self, image_path):
        try:
            result = self.model.analyse(image_path)
        except Exception as error:
            self.root.after(0, lambda error=error: self._show_error(error))
            return
        self.root.after(0, lambda: self._show_result(image_path, result))

    def _show_result(self, image_path, result):
        has_tumor = result["has_tumor"]
        self.result_label.configure(
            text="Обнаружена опухоль" if has_tumor else "Опухоль не обнаружена",
            fg="#a33b36" if has_tumor else "#176b58",
        )
        confidence = result["confidence"]
        confidence_text = f"Уверенность: {confidence:.0%}" if confidence is not None else "Объекты не обнаружены"
        self.confidence_label.configure(text=f"{os.path.basename(image_path)}\n{confidence_text}")
        self.status_label.configure(text="Анализ завершен через Roboflow API")
        self.pick_button.configure(state="normal")
        self._update_analyze_button()

    def _show_error(self, error):
        message = str(error) if isinstance(error, RuntimeError) else "Не удалось выполнить запрос к Roboflow API."
        self.status_label.configure(text="Не удалось выполнить анализ")
        self.pick_button.configure(state="normal")
        self._update_analyze_button()
        messagebox.showerror("Ошибка анализа", message)


def launch():
    project_dir = Path(__file__).resolve().parent
    load_dotenv(project_dir / ".env")
    root = tk.Tk()
    BrainTumorApp(root)
    root.mainloop()