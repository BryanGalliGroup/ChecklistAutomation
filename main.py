import re
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from settings_dialog import SettingsDialog
from src.automation import (
    prepare_summary,
    send_summary_email,
)
from src.config import (
    load_projects,
    load_settings,
    save_projects,
)
from src.logger import Logger


BASE_DIR = Path(__file__).resolve().parent


class ProjectManager:
    def __init__(self, root):
        self.root = root

        self.root.title(
            "Automação de Resumo de Commits"
        )

        self.root.geometry(
            "1000x700"
        )

        self.root.minsize(
            850,
            600,
        )

        self.projects = []
        self.settings = {}
        self.is_running = False

        self.project_buttons = []

        self.load_configuration()
        self.create_widgets()
        self.refresh_list()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application,
        )

    # ==================================================================
    # CONFIGURAÇÃO
    # ==================================================================

    def load_configuration(self):
        try:
            self.projects = load_projects()
            self.settings = load_settings()

        except (RuntimeError, ValueError) as error:
            messagebox.showerror(
                "Erro de configuração",
                str(error),
                parent=self.root,
            )

            self.projects = []
            self.settings = {}

    # ==================================================================
    # INTERFACE
    # ==================================================================

    def create_widgets(self):
        main_frame = ttk.Frame(
            self.root,
            padding=20,
        )

        main_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        # --------------------------------------------------------------
        # Título
        # --------------------------------------------------------------

        title = ttk.Label(
            main_frame,
            text="Gerenciador de Projetos",
            font=("TkDefaultFont", 18, "bold"),
        )

        title.pack(
            anchor=tk.W,
            pady=(0, 5),
        )

        subtitle = ttk.Label(
            main_frame,
            text=(
                "Gerencie os projetos utilizados "
                "pela automação de commits."
            ),
        )

        subtitle.pack(
            anchor=tk.W,
            pady=(0, 20),
        )

        # --------------------------------------------------------------
        # Lista de projetos
        # --------------------------------------------------------------

        list_frame = ttk.Frame(
            main_frame
        )

        list_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        columns = (
            "key",
            "name",
            "path",
        )

        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="extended",
        )

        self.tree.heading(
            "key",
            text="Chave",
        )

        self.tree.heading(
            "name",
            text="Nome",
        )

        self.tree.heading(
            "path",
            text="Caminho",
        )

        self.tree.column(
            "key",
            width=120,
            anchor=tk.W,
        )

        self.tree.column(
            "name",
            width=220,
            anchor=tk.W,
        )

        self.tree.column(
            "path",
            width=420,
            anchor=tk.W,
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview,
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y,
        )

        self.tree.bind(
            "<Double-1>",
            self.edit_project,
        )

        # --------------------------------------------------------------
        # Botões de projeto
        # --------------------------------------------------------------

        buttons_frame = ttk.Frame(
            main_frame
        )

        buttons_frame.pack(
            fill=tk.X,
            pady=(15, 0),
        )

        add_button = ttk.Button(
            buttons_frame,
            text="+ Adicionar",
            command=self.add_project,
        )

        add_button.pack(
            side=tk.LEFT
        )

        edit_button = ttk.Button(
            buttons_frame,
            text="Editar",
            command=self.edit_project,
        )

        edit_button.pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        remove_button = ttk.Button(
            buttons_frame,
            text="Remover",
            command=self.remove_project,
        )

        remove_button.pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        refresh_button = ttk.Button(
            buttons_frame,
            text="Atualizar",
            command=self.refresh,
        )

        refresh_button.pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        settings_button = ttk.Button(
            buttons_frame,
            text="Configurações",
            command=self.open_settings,
        )

        settings_button.pack(
            side=tk.LEFT,
            padx=(20, 0),
        )

        self.run_button = ttk.Button(
            buttons_frame,
            text="Executar automação",
            command=self.run_automation,
        )

        self.run_button.pack(
            side=tk.RIGHT
        )

        self.project_buttons = [
            add_button,
            edit_button,
            remove_button,
            refresh_button,
            settings_button,
        ]

        # --------------------------------------------------------------
        # Separador
        # --------------------------------------------------------------

        ttk.Separator(
            main_frame,
            orient=tk.HORIZONTAL,
        ).pack(
            fill=tk.X,
            pady=15,
        )

        # --------------------------------------------------------------
        # Logs
        # --------------------------------------------------------------

        ttk.Label(
            main_frame,
            text="Logs",
            font=("TkDefaultFont", 11, "bold"),
        ).pack(
            anchor=tk.W
        )

        log_frame = ttk.Frame(
            main_frame
        )

        log_frame.pack(
            fill=tk.BOTH,
            expand=True,
            pady=(8, 0),
        )

        self.log_text = tk.Text(
            log_frame,
            height=10,
            state=tk.DISABLED,
            wrap=tk.WORD,
        )

        log_scrollbar = ttk.Scrollbar(
            log_frame,
            orient=tk.VERTICAL,
            command=self.log_text.yview,
        )

        self.log_text.configure(
            yscrollcommand=log_scrollbar.set
        )

        self.log_text.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )

        log_scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y,
        )

        # --------------------------------------------------------------
        # Status
        # --------------------------------------------------------------

        status_frame = ttk.Frame(
            main_frame
        )

        status_frame.pack(
            fill=tk.X,
            pady=(10, 0),
        )

        self.status_label = ttk.Label(
            status_frame,
            text="Pronto.",
        )

        self.status_label.pack(
            side=tk.LEFT
        )

        self.close_button = ttk.Button(
            status_frame,
            text="Fechar",
            command=self.close_application,
        )

        self.close_button.pack(
            side=tk.RIGHT
        )

    # ==================================================================
    # LISTA DE PROJETOS
    # ==================================================================

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, project in enumerate(self.projects):
            self.tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    project.get("key", ""),
                    project.get("name", ""),
                    project.get("path", ""),
                ),
            )

        count = len(self.projects)

        if count == 1:
            message = "1 projeto cadastrado."
        else:
            message = f"{count} projetos cadastrados."

        self.status_label.config(
            text=message
        )

    def refresh(self):
        if self.is_running:
            return

        try:
            projects = load_projects()

        except (RuntimeError, ValueError) as error:
            messagebox.showerror(
                "Projetos",
                str(error),
                parent=self.root,
            )
            return

        self.projects = projects

        self.refresh_list()

        self.add_log(
            "Lista de projetos atualizada."
        )

    # ==================================================================
    # ADICIONAR PROJETO
    # ==================================================================

    def add_project(self):
        if self.is_running:
            return

        dialog = ProjectDialog(
            self.root,
            title="Adicionar projeto",
        )

        self.root.wait_window(
            dialog.window
        )

        if dialog.result is None:
            return

        project = dialog.result

        if not self.validate_project(
            project
        ):
            return

        new_projects = [
            *self.projects,
            project,
        ]

        try:
            save_projects(
                new_projects
            )

        except (RuntimeError, ValueError) as error:
            messagebox.showerror(
                "Adicionar projeto",
                str(error),
                parent=self.root,
            )
            return

        self.projects = new_projects

        self.refresh_list()

        self.add_log(
            f"Projeto '{project['name']}' adicionado."
        )

    # ==================================================================
    # EDITAR PROJETO
    # ==================================================================

    def edit_project(self, event=None):
        if self.is_running:
            return

        selected = self.tree.selection()

        if not selected:
            if event is None:
                messagebox.showwarning(
                    "Projeto",
                    "Selecione um projeto para editar.",
                    parent=self.root,
                )

            return

        if len(selected) > 1:
            messagebox.showwarning(
                "Editar projeto",
                "Selecione apenas um projeto para editar.",
                parent=self.root,
            )

            return

        try:
            index = int(
                selected[0]
            )

        except (TypeError, ValueError):
            messagebox.showerror(
                "Projeto",
                "Não foi possível identificar o projeto selecionado.",
                parent=self.root,
            )

            return

        if index < 0 or index >= len(self.projects):
            messagebox.showerror(
                "Projeto",
                "O projeto selecionado não está mais disponível.",
                parent=self.root,
            )

            self.refresh_list()
            return

        project = self.projects[index]

        dialog = ProjectDialog(
            self.root,
            title="Editar projeto",
            project=project,
        )

        self.root.wait_window(
            dialog.window
        )

        if dialog.result is None:
            return

        updated_project = dialog.result

        if not self.validate_project(
            updated_project,
            current_index=index,
        ):
            return

        new_projects = list(
            self.projects
        )

        new_projects[index] = updated_project

        try:
            save_projects(
                new_projects
            )

        except (RuntimeError, ValueError) as error:
            messagebox.showerror(
                "Editar projeto",
                str(error),
                parent=self.root,
            )
            return

        self.projects = new_projects

        self.refresh_list()

        self.add_log(
            f"Projeto '{updated_project['name']}' atualizado."
        )

    # ==================================================================
    # REMOVER PROJETO
    # ==================================================================

    def remove_project(self):
        if self.is_running:
            return

        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Projeto",
                "Selecione pelo menos um projeto para remover.",
                parent=self.root,
            )

            return

        indexes = []

        for item in selected:
            try:
                index = int(item)

            except (TypeError, ValueError):
                continue

            if (
                0 <= index < len(self.projects)
                and index not in indexes
            ):
                indexes.append(index)

        if not indexes:
            messagebox.showerror(
                "Projeto",
                "Não foi possível identificar os projetos selecionados.",
                parent=self.root,
            )

            self.refresh_list()
            return

        indexes.sort()

        projects_to_remove = [
            self.projects[index]
            for index in indexes
        ]

        if len(projects_to_remove) == 1:
            project = projects_to_remove[0]

            message = (
                "Tem certeza que deseja remover o projeto?\n\n"
                f"{project.get('name', '')}\n"
                f"{project.get('path', '')}"
            )

        else:
            names = "\n".join(
                f"• {project.get('name', '')}"
                for project in projects_to_remove
            )

            message = (
                "Tem certeza que deseja remover "
                f"{len(projects_to_remove)} projetos?\n\n"
                f"{names}"
            )

        confirmed = messagebox.askyesno(
            "Remover projeto",
            message,
            parent=self.root,
        )

        if not confirmed:
            return

        indexes_to_remove = set(
            indexes
        )

        new_projects = [
            project
            for index, project in enumerate(
                self.projects
            )
            if index not in indexes_to_remove
        ]

        try:
            save_projects(
                new_projects
            )

        except (RuntimeError, ValueError) as error:
            messagebox.showerror(
                "Remover projeto",
                str(error),
                parent=self.root,
            )
            return

        self.projects = new_projects

        self.refresh_list()

        self.add_log(
            f"{len(projects_to_remove)} projeto(s) removido(s)."
        )

    # ==================================================================
    # VALIDAÇÃO
    # ==================================================================

    def validate_project(
        self,
        project,
        current_index=None,
    ):
        if not isinstance(
            project,
            dict,
        ):
            messagebox.showwarning(
                "Validação",
                "Dados inválidos para o projeto.",
                parent=self.root,
            )

            return False

        key = project.get(
            "key",
            "",
        ).strip()

        name = project.get(
            "name",
            "",
        ).strip()

        path = project.get(
            "path",
            "",
        ).strip()

        if not key:
            messagebox.showwarning(
                "Validação",
                "Informe a chave do projeto.",
                parent=self.root,
            )

            return False

        if not name:
            messagebox.showwarning(
                "Validação",
                "Informe o nome do projeto.",
                parent=self.root,
            )

            return False

        if not path:
            messagebox.showwarning(
                "Validação",
                "Informe o caminho do projeto.",
                parent=self.root,
            )

            return False

        if not re.fullmatch(
            r"[A-Za-z0-9_-]+",
            key,
        ):
            messagebox.showwarning(
                "Validação",
                (
                    "A chave pode conter apenas letras, "
                    "números, underscore (_) e hífen (-)."
                ),
                parent=self.root,
            )

            return False

        normalized_key = key.upper()

        for index, existing in enumerate(
            self.projects
        ):
            if (
                current_index is not None
                and index == current_index
            ):
                continue

            existing_key = str(
                existing.get(
                    "key",
                    "",
                )
            ).strip().upper()

            if existing_key == normalized_key:
                messagebox.showwarning(
                    "Validação",
                    (
                        f"A chave '{key}' "
                        "já está sendo utilizada."
                    ),
                    parent=self.root,
                )

                return False

        project_path = Path(
            path
        ).expanduser()

        try:
            project_path = project_path.resolve()

        except OSError:
            messagebox.showwarning(
                "Validação",
                (
                    "Não foi possível resolver o caminho informado:\n\n"
                    f"{path}"
                ),
                parent=self.root,
            )

            return False

        if not project_path.exists():
            messagebox.showwarning(
                "Validação",
                (
                    "O caminho informado não existe:\n\n"
                    f"{project_path}"
                ),
                parent=self.root,
            )

            return False

        if not project_path.is_dir():
            messagebox.showwarning(
                "Validação",
                (
                    "O caminho informado não é uma pasta:\n\n"
                    f"{project_path}"
                ),
                parent=self.root,
            )

            return False

        if not self.is_git_repository(
            project_path
        ):
            confirmed = messagebox.askyesno(
                "Repositório Git",
                (
                    "A pasta selecionada não parece "
                    "ser um repositório Git:\n\n"
                    f"{project_path}\n\n"
                    "Deseja cadastrar mesmo assim?"
                ),
                parent=self.root,
            )

            if not confirmed:
                return False

        project["key"] = normalized_key
        project["name"] = name
        project["path"] = str(
            project_path
        )

        return True

    # ==================================================================
    # GIT
    # ==================================================================

    @staticmethod
    def is_git_repository(path):
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(path),
                    "rev-parse",
                    "--is-inside-work-tree",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5,
                check=False,
            )

            return (
                result.returncode == 0
                and result.stdout.strip() == "true"
            )

        except (
            FileNotFoundError,
            subprocess.SubprocessError,
            OSError,
        ):
            return False

    # ==================================================================
    # LOGS
    # ==================================================================

    def add_log(self, message):
        if not self.root.winfo_exists():
            return

        self.root.after(
            0,
            self._append_log,
            str(message),
        )

    def _append_log(self, message):
        try:
            if not self.root.winfo_exists():
                return

            self.log_text.config(
                state=tk.NORMAL
            )

            self.log_text.insert(
                tk.END,
                message + "\n",
            )

            self.log_text.see(
                tk.END
            )

            self.log_text.config(
                state=tk.DISABLED
            )

        except tk.TclError:
            pass

    def clear_logs(self):
        self.log_text.config(
            state=tk.NORMAL
        )

        self.log_text.delete(
            "1.0",
            tk.END,
        )

        self.log_text.config(
            state=tk.DISABLED
        )

    # ==================================================================
    # CONTROLE DA INTERFACE DURANTE EXECUÇÃO
    # ==================================================================

    def set_running_state(self, running):
        self.is_running = running

        state = (
            tk.DISABLED
            if running
            else tk.NORMAL
        )

        for button in self.project_buttons:
            button.config(
                state=state
            )

        self.run_button.config(
            state=state
        )

        if running:
            self.close_button.config(
                state=tk.DISABLED
            )
        else:
            self.close_button.config(
                state=tk.NORMAL
            )

    # ==================================================================
    # AUTOMAÇÃO
    # ==================================================================

    def run_automation(self):
        if self.is_running:
            return

        selected_items = self.tree.selection()

        if not selected_items:
            messagebox.showwarning(
                "Automação",
                "Selecione pelo menos um projeto.",
                parent=self.root,
            )

            return

        selected_projects = []

        for item in selected_items:
            try:
                index = int(item)

            except (TypeError, ValueError):
                continue

            if (
                0 <= index < len(self.projects)
            ):
                selected_projects.append(
                    self.projects[index]
                )

        if not selected_projects:
            messagebox.showerror(
                "Automação",
                (
                    "Não foi possível identificar "
                    "os projetos selecionados."
                ),
                parent=self.root,
            )

            self.refresh_list()
            return

        # Cria uma cópia para evitar que alterações posteriores
        # na interface afetem a execução em andamento.
        selected_projects = [
            dict(project)
            for project in selected_projects
        ]

        # Copia também as configurações usadas nessa execução.
        settings_snapshot = dict(
            self.settings
        )

        if isinstance(
            self.settings.get("ai"),
            dict,
        ):
            settings_snapshot["ai"] = dict(
                self.settings["ai"]
            )

        if isinstance(
            self.settings.get("email"),
            dict,
        ):
            settings_snapshot["email"] = dict(
                self.settings["email"]
            )

        if isinstance(
            self.settings.get("editor"),
            dict,
        ):
            settings_snapshot["editor"] = dict(
                self.settings["editor"]
            )

        self.set_running_state(
            True
        )

        self.clear_logs()

        self.status_label.config(
            text="Executando automação..."
        )

        self.add_log(
            (
                f"Iniciando automação com "
                f"{len(selected_projects)} projeto(s)."
            )
        )

        logger = Logger(
            callback=self.add_log
        )

        thread = threading.Thread(
            target=self._automation_worker,
            args=(
                selected_projects,
                settings_snapshot,
                logger,
            ),
            daemon=True,
        )

        thread.start()

    def _automation_worker(
        self,
        selected_projects,
        settings,
        logger,
    ):
        try:
            summary = prepare_summary(
                selected_projects,
                settings,
                logger,
            )

            self.root.after(
                0,
                self._automation_finished,
                summary,
            )

        except Exception as error:
            self.root.after(
                0,
                self._automation_failed,
                error,
            )

    def _automation_finished(
        self,
        summary,
    ):
        if not summary:
            self.set_running_state(
                False
            )

            self.status_label.config(
                text=(
                    "Concluído — "
                    "nenhum resumo disponível."
                )
            )

            return

        self.status_label.config(
            text=(
                "Resumo preparado — "
                "aguardando confirmação."
            )
        )

        confirmed = messagebox.askyesno(
            "Enviar resumo",
            (
                "O resumo foi preparado e revisado.\n\n"
                "Deseja enviá-lo por e-mail?"
            ),
            parent=self.root,
        )

        if not confirmed:
            self.add_log(
                "Envio cancelado pelo usuário."
            )

            self.set_running_state(
                False
            )

            self.status_label.config(
                text=(
                    "Concluído — "
                    "envio cancelado."
                )
            )

            return

        self._send_email_async(
            summary
        )

    def _automation_failed(
        self,
        error,
    ):
        self.set_running_state(
            False
        )

        self.status_label.config(
            text="Erro na automação."
        )

        self.add_log(
            f"✗ Erro: {error}"
        )

        messagebox.showerror(
            "Erro na automação",
            str(error),
            parent=self.root,
        )

    # ==================================================================
    # E-MAIL
    # ==================================================================

    def _send_email_async(
        self,
        summary,
    ):
        if not self.is_running:
            self.set_running_state(
                True
            )

        self.status_label.config(
            text="Enviando e-mail..."
        )

        self.add_log(
            "Iniciando envio do resumo por e-mail..."
        )

        settings_snapshot = dict(
            self.settings
        )

        if isinstance(
            self.settings.get("email"),
            dict,
        ):
            settings_snapshot["email"] = dict(
                self.settings["email"]
            )

        logger = Logger(
            callback=self.add_log
        )

        thread = threading.Thread(
            target=self._email_worker,
            args=(
                summary,
                settings_snapshot,
                logger,
            ),
            daemon=True,
        )

        thread.start()

    def _email_worker(
        self,
        summary,
        settings,
        logger,
    ):
        try:
            send_summary_email(
                summary,
                settings,
                logger,
            )

            self.root.after(
                0,
                self._email_finished,
            )

        except Exception as error:
            self.root.after(
                0,
                self._email_failed,
                error,
            )

    def _email_finished(self):
        self.set_running_state(
            False
        )

        self.status_label.config(
            text="Concluído — e-mail enviado."
        )

        messagebox.showinfo(
            "Automação",
            (
                "Resumo enviado por e-mail "
                "com sucesso."
            ),
            parent=self.root,
        )

    def _email_failed(
        self,
        error,
    ):
        self.set_running_state(
            False
        )

        self.status_label.config(
            text="Erro ao enviar e-mail."
        )

        self.add_log(
            f"✗ Erro ao enviar e-mail: {error}"
        )

        messagebox.showerror(
            "E-mail",
            str(error),
            parent=self.root,
        )

    # ==================================================================
    # CONFIGURAÇÕES
    # ==================================================================

    def open_settings(self):
        if self.is_running:
            return

        dialog = SettingsDialog(
            self.root
        )

        self.root.wait_window(
            dialog.window
        )

        if dialog.result is None:
            return

        self.settings = dialog.result

        self.add_log(
            "Configurações atualizadas."
        )

        self.status_label.config(
            text="Configurações salvas."
        )

    # ==================================================================
    # FECHAMENTO
    # ==================================================================

    def close_application(self):
        if self.is_running:
            messagebox.showwarning(
                "Automação em andamento",
                (
                    "A automação está em andamento.\n\n"
                    "Aguarde a conclusão antes de fechar "
                    "o aplicativo."
                ),
                parent=self.root,
            )

            return

        self.root.destroy()


class ProjectDialog:
    def __init__(
        self,
        parent,
        title,
        project=None,
    ):
        self.result = None

        self.window = tk.Toplevel(
            parent
        )

        self.window.title(
            title
        )

        self.window.geometry(
            "620x300"
        )

        self.window.minsize(
            620,
            300
        )

        self.window.resizable(
            False,
            False
        )

        self.window.transient(
            parent
        )

        self.key_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.path_var = tk.StringVar()

        if project:
            self.key_var.set(
                project.get(
                    "key",
                    "",
                )
            )

            self.name_var.set(
                project.get(
                    "name",
                    "",
                )
            )

            self.path_var.set(
                project.get(
                    "path",
                    "",
                )
            )

        self.create_widgets()

        self.center_window(
            parent
        )

        self.window.after(
            10,
            self._set_modal,
        )

    def _set_modal(self):
        try:
            self.window.grab_set()
            self.window.focus_force()

        except tk.TclError:
            pass

    def center_window(
        self,
        parent,
    ):
        self.window.update_idletasks()

        width = self.window.winfo_width()
        height = self.window.winfo_height()

        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        x = (
            parent_x
            + (parent_width - width) // 2
        )

        y = (
            parent_y
            + (parent_height - height) // 2
        )

        self.window.geometry(
            f"{width}x{height}+{x}+{y}"
        )

    def create_widgets(self):
        frame = ttk.Frame(
            self.window,
            padding=20,
        )

        frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        # --------------------------------------------------------------
        # Chave
        # --------------------------------------------------------------

        ttk.Label(
            frame,
            text="Chave",
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
            pady=(0, 5),
        )

        self.key_entry = ttk.Entry(
            frame,
            textvariable=self.key_var,
        )

        self.key_entry.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky=tk.EW,
        )

        # --------------------------------------------------------------
        # Nome
        # --------------------------------------------------------------

        ttk.Label(
            frame,
            text="Nome",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            pady=(15, 5),
        )

        ttk.Entry(
            frame,
            textvariable=self.name_var,
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky=tk.EW,
        )

        # --------------------------------------------------------------
        # Caminho
        # --------------------------------------------------------------

        ttk.Label(
            frame,
            text="Caminho do repositório",
        ).grid(
            row=4,
            column=0,
            sticky=tk.W,
            pady=(15, 5),
        )

        path_frame = ttk.Frame(
            frame
        )

        path_frame.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky=tk.EW,
        )

        ttk.Entry(
            path_frame,
            textvariable=self.path_var,
        ).pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
        )

        ttk.Button(
            path_frame,
            text="...",
            width=4,
            command=self.select_directory,
        ).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        # --------------------------------------------------------------
        # Botões
        # --------------------------------------------------------------

        buttons = ttk.Frame(
            frame
        )

        buttons.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky=tk.E,
            pady=(25, 0),
        )

        ttk.Button(
            buttons,
            text="Cancelar",
            command=self.cancel,
        ).pack(
            side=tk.LEFT,
            padx=(0, 8),
        )

        ttk.Button(
            buttons,
            text="Salvar",
            command=self.save,
        ).pack(
            side=tk.LEFT
        )

        frame.columnconfigure(
            0,
            weight=1,
        )

        frame.columnconfigure(
            1,
            weight=0,
        )

        self.key_entry.focus_set()

    def select_directory(self):
        directory = filedialog.askdirectory(
            parent=self.window,
            title="Selecionar repositório Git",
        )

        if directory:
            self.path_var.set(
                directory
            )

    def save(self):
        self.result = {
            "key": self.key_var.get().strip(),
            "name": self.name_var.get().strip(),
            "path": self.path_var.get().strip(),
        }

        try:
            self.window.grab_release()

        except tk.TclError:
            pass

        self.window.destroy()

    def cancel(self):
        self.result = None

        try:
            self.window.grab_release()

        except tk.TclError:
            pass

        self.window.destroy()


def main():
    root = tk.Tk()

    try:
        style = ttk.Style(
            root
        )

        if "clam" in style.theme_names():
            style.theme_use(
                "clam"
            )

    except tk.TclError:
        pass

    ProjectManager(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()