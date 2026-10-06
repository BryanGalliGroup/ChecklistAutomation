import tkinter as tk
from tkinter import messagebox, ttk

from src.config import load_settings, save_settings


class SettingsDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None

        self.window = tk.Toplevel(parent)
        self.window.title("Configurações")
        self.window.geometry("920x820")
        self.window.minsize(920, 820)
        self.window.transient(parent)

        try:
            self.settings = load_settings()
        except (RuntimeError, ValueError) as error:
            messagebox.showerror(
                "Configurações",
                str(error),
                parent=self.window,
            )
            self.window.destroy()
            return

        self.create_variables()
        self.create_widgets()
        self.center_window()

        self.window.after(
            10,
            self._set_modal,
        )

    # ------------------------------------------------------------------
    # Inicialização
    # ------------------------------------------------------------------

    def _set_modal(self):
        self.window.grab_set()
        self.window.focus_force()

    def center_window(self):
        self.window.update_idletasks()

        width = self.window.winfo_width()
        height = self.window.winfo_height()

        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        self.window.geometry(
            f"{width}x{height}+{x}+{y}"
        )

    # ------------------------------------------------------------------
    # Variáveis
    # ------------------------------------------------------------------

    def create_variables(self):
        ai = self.settings.get("ai", {})
        email = self.settings.get("email", {})
        editor = self.settings.get("editor", {})

        self.ai_model_var = tk.StringVar(
            value=ai.get("model", "")
        )

        self.email_subject_var = tk.StringVar(
            value=email.get("subject", "")
        )

        self.email_from_name_var = tk.StringVar(
            value=email.get("from_name", "")
        )

        #self.email_from_address_var = tk.StringVar(
        #    value=email.get("from_address", "")
        #)

        recipients = email.get("to", [])

        if isinstance(recipients, list):
            recipients = ", ".join(recipients)

        self.email_recipients_var = tk.StringVar(
            value=recipients
        )

        self.email_image_url_var = tk.StringVar(
            value=email.get("image_url", "")
        )

        self.editor_command_var = tk.StringVar(
            value=editor.get("command", "")
        )

        self.ai_prompt = None
        self.email_signature = None

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------

    def create_widgets(self):
        main_frame = ttk.Frame(
            self.window,
            padding=20,
        )

        main_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        title = ttk.Label(
            main_frame,
            text="Configurações",
            font=("TkDefaultFont", 18, "bold"),
        )

        title.pack(
            anchor=tk.W,
            pady=(0, 5),
        )

        subtitle = ttk.Label(
            main_frame,
            text=(
                "Configure a IA, o envio de e-mail e o editor "
                "utilizado pela automação."
            ),
        )

        subtitle.pack(
            anchor=tk.W,
            pady=(0, 15),
        )

        notebook = ttk.Notebook(main_frame)

        notebook.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.create_ai_tab(notebook)
        self.create_email_tab(notebook)
        self.create_editor_tab(notebook)

        buttons = ttk.Frame(main_frame)

        buttons.pack(
            fill=tk.X,
            pady=(15, 0),
        )

        ttk.Button(
            buttons,
            text="Cancelar",
            command=self.cancel,
        ).pack(
            side=tk.RIGHT,
            padx=(8, 0),
        )

        ttk.Button(
            buttons,
            text="Salvar",
            command=self.save,
        ).pack(
            side=tk.RIGHT,
        )

    # ------------------------------------------------------------------
    # IA
    # ------------------------------------------------------------------

    def create_ai_tab(self, notebook):
        frame = ttk.Frame(
            notebook,
            padding=15,
        )

        notebook.add(
            frame,
            text="IA",
        )

        ttk.Label(
            frame,
            text="Modelo",
        ).pack(
            anchor=tk.W,
        )

        ttk.Entry(
            frame,
            textvariable=self.ai_model_var,
        ).pack(
            fill=tk.X,
            pady=(5, 15),
        )

        ttk.Label(
            frame,
            text="Prompt",
        ).pack(
            anchor=tk.W,
        )

        prompt_frame = ttk.Frame(frame)

        prompt_frame.pack(
            fill=tk.BOTH,
            expand=True,
            pady=(5, 0),
        )

        self.ai_prompt = tk.Text(
            prompt_frame,
            wrap=tk.WORD,
        )

        prompt_scrollbar = ttk.Scrollbar(
            prompt_frame,
            orient=tk.VERTICAL,
            command=self.ai_prompt.yview,
        )

        self.ai_prompt.configure(
            yscrollcommand=prompt_scrollbar.set,
        )

        self.ai_prompt.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )

        prompt_scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y,
        )

        self.ai_prompt.insert(
            "1.0",
            self.settings
            .get("ai", {})
            .get("prompt", ""),
        )

    # ------------------------------------------------------------------
    # E-mail
    # ------------------------------------------------------------------

    def create_email_tab(self, notebook):
        frame = ttk.Frame(
            notebook,
            padding=15,
        )

        notebook.add(
            frame,
            text="E-mail",
        )

        frame.columnconfigure(
            1,
            weight=1,
        )

        self.add_entry(
            frame,
            0,
            "Assunto",
            self.email_subject_var,
        )

        self.add_entry(
            frame,
            1,
            "Nome do remetente",
            self.email_from_name_var,
        )

        #self.add_entry(
        #    frame,
        #    2,
        #    "Endereço do remetente",
        #    self.email_from_address_var,
        #)

        self.add_entry(
            frame,
            3,
            "Destinatários",
            self.email_recipients_var,
        )

        self.add_entry(
            frame,
            4,
            "URL da imagem",
            self.email_image_url_var,
        )

        ttk.Label(
            frame,
            text="Assinatura",
        ).grid(
            row=5,
            column=0,
            sticky=tk.NW,
            pady=(15, 5),
        )

        signature_frame = ttk.Frame(frame)

        signature_frame.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky=tk.NSEW,
        )

        self.email_signature = tk.Text(
            signature_frame,
            height=8,
            wrap=tk.WORD,
        )

        signature_scrollbar = ttk.Scrollbar(
            signature_frame,
            orient=tk.VERTICAL,
            command=self.email_signature.yview,
        )

        self.email_signature.configure(
            yscrollcommand=signature_scrollbar.set,
        )

        self.email_signature.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )

        signature_scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y,
        )

        self.email_signature.insert(
            "1.0",
            self.settings
            .get("email", {})
            .get("signature", ""),
        )

        frame.rowconfigure(
            6,
            weight=1,
        )

    # ------------------------------------------------------------------
    # Editor
    # ------------------------------------------------------------------

    def create_editor_tab(self, notebook):
        frame = ttk.Frame(
            notebook,
            padding=15,
        )

        notebook.add(
            frame,
            text="Editor",
        )

        ttk.Label(
            frame,
            text="Comando do editor",
        ).pack(
            anchor=tk.W,
        )

        ttk.Entry(
            frame,
            textvariable=self.editor_command_var,
        ).pack(
            fill=tk.X,
            pady=(5, 10),
        )

        ttk.Label(
            frame,
            text=(
                "Exemplo: code. O parâmetro de espera "
                "é adicionado automaticamente quando necessário."
            ),
            wraplength=600,
        ).pack(
            anchor=tk.W,
        )

    # ------------------------------------------------------------------
    # Componentes
    # ------------------------------------------------------------------

    @staticmethod
    def add_entry(
        parent,
        row,
        label,
        variable,
    ):
        ttk.Label(
            parent,
            text=label,
        ).grid(
            row=row,
            column=0,
            sticky=tk.W,
            padx=(0, 12),
            pady=6,
        )

        ttk.Entry(
            parent,
            textvariable=variable,
        ).grid(
            row=row,
            column=1,
            sticky=tk.EW,
            pady=6,
        )

    # ------------------------------------------------------------------
    # Salvar
    # ------------------------------------------------------------------

    def save(self):
        recipients = [
            email.strip()
            for email in self.email_recipients_var
            .get()
            .split(",")
            if email.strip()
        ]

        settings = {
            "ai": {
                "model": self.ai_model_var.get().strip(),
                "prompt": self.ai_prompt
                .get("1.0", tk.END)
                .strip(),
            },
            "email": {
                "subject": self.email_subject_var.get().strip(),
                "from_name": self.email_from_name_var.get().strip(),
                "to": recipients,
                "signature": self.email_signature
                .get("1.0", tk.END)
                .strip(),
                "image_url": self.email_image_url_var.get().strip(),
            },
            "editor": {
                "command": self.editor_command_var.get().strip(),
            },
        }

        try:
            save_settings(settings)

        except (RuntimeError, ValueError) as error:
            messagebox.showerror(
                "Configurações",
                str(error),
                parent=self.window,
            )
            return

        self.result = settings
        self.window.destroy()

    def cancel(self):
        self.result = None
        self.window.destroy()