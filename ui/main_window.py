from __future__ import annotations

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from app_paths import get_app_dir
from core.configurator import Configurator
from core.executor import Executor
from core.planner import Planner
from core.verifier import Verifier


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Installer")
        self.root.geometry("980x700")
        self.root.minsize(900, 620)
        self.root.configure(bg="#f5f7fb")

        self.prompt_var = tk.StringVar(value="Install Git and Visual Studio Code. Configure Git with user name Matrix and email matrix@example.com.")
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.StringVar(value="0%")
        self.run_dir = get_app_dir() / "output" / "runs"
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=18)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="Auto Installer", font=("Segoe UI", 22, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        ttk.Label(frame, text="Installation prompt", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.prompt_box = tk.Text(frame, height=7, wrap="word", font=("Segoe UI", 11))
        self.prompt_box.insert("1.0", self.prompt_var.get())
        self.prompt_box.pack(fill="x", pady=(6, 12))
        ttk.Label(
            frame,
            text="Prompts are sent to your configured AI provider. Do not include passwords, API keys, or other secrets.",
            wraplength=900,
        ).pack(anchor="w", pady=(0, 10))

        button_row = ttk.Frame(frame)
        button_row.pack(fill="x", pady=(0, 12))
        self.run_button = ttk.Button(button_row, text="Run Auto Installer", command=self.run_workflow)
        self.run_button.pack(side="left")
        self.open_dir_button = ttk.Button(button_row, text="Open Output Folder", command=self.open_output_dir)
        self.open_dir_button.pack(side="left", padx=(10, 0))

        status_row = ttk.Frame(frame)
        status_row.pack(fill="x", pady=(0, 8))
        ttk.Label(status_row, text="Status:", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Label(status_row, textvariable=self.status_var, font=("Segoe UI", 10)).pack(side="left", padx=(8, 0))

        progress = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
        progress.pack(anchor="w", pady=(0, 8))
        self.progress = progress
        self.progress['value'] = 0

        ttk.Label(frame, textvariable=self.progress_var, font=("Segoe UI", 10)).pack(anchor="w")

        self.log_box = tk.Text(frame, height=14, wrap="word", state="disabled", bg="#ffffff")
        self.log_box.pack(fill="both", expand=True, pady=(8, 12))

        ttk.Label(frame, text="Generated batch script preview", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))
        self.script_box = tk.Text(frame, height=8, wrap="word", state="disabled", bg="#f8fafc")
        self.script_box.pack(fill="x", pady=(0, 10))

        self.summary_box = tk.Text(frame, height=6, wrap="word", state="disabled", bg="#f8fafc")
        self.summary_box.pack(fill="x", pady=(0, 8))

    def append_log(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def set_status(self, value: str) -> None:
        self.status_var.set(value)
        self.root.update_idletasks()

    def run_workflow(self) -> None:
        prompt = self.prompt_box.get("1.0", "end").strip()
        if not prompt:
            self.append_log("Please enter a prompt before running Auto Installer.")
            return
        self.run_button.config(state="disabled")
        threading.Thread(target=self._run_workflow_thread, args=(prompt,), daemon=True).start()

    def _run_workflow_thread(self, prompt: str) -> None:
        try:
            self.root.after(0, lambda: self.set_status("Planning..."))
            self.root.after(0, lambda: self.progress.configure(value=10))
            self.root.after(0, lambda: self.progress_var.set("10%"))
            self.root.after(0, lambda: self.append_log("Prompt received and sent to the configured AI provider."))

            planner = Planner()
            provider = planner.llm.provider
            model = (
                planner.llm.gemini_model
                if provider == "gemini"
                else planner.llm.model
            )
            self.root.after(0, lambda: self.append_log(f"Using {provider} model: {model}"))
            payload = planner.generate(prompt)
            run_id = "run_" + str(abs(hash(prompt)) % 100000)
            run_dir = self.run_dir / run_id
            planner.save_run(run_dir, payload["batch_script"], payload["manifest"])

            self.root.after(0, lambda: self.set_status("Writing batch file..."))
            self.root.after(0, lambda: self.progress.configure(value=35))
            self.root.after(0, lambda: self.progress_var.set("35%"))
            self.root.after(0, lambda: self.append_log(f"Batch script saved to {run_dir / 'install.bat'}"))

            self.root.after(0, lambda: self.script_box.configure(state="normal"))
            self.root.after(0, lambda: self.script_box.delete("1.0", "end"))
            self.root.after(0, lambda: self.script_box.insert("1.0", payload["batch_script"]))
            self.root.after(0, lambda: self.script_box.configure(state="disabled"))

            self.root.after(0, lambda: self.set_status("Executing installation..."))
            self.root.after(0, lambda: self.progress.configure(value=50))
            self.root.after(0, lambda: self.progress_var.set("50%"))
            executor = Executor(run_dir)
            script_path = run_dir / "install.bat"
            result_code = executor.run_batch_script(script_path)
            output = "\n".join(executor.activity)
            self.root.after(0, lambda: self.append_log(output or "No installer output captured."))

            self.root.after(0, lambda: self.set_status("Configuring..."))
            self.root.after(0, lambda: self.progress.configure(value=75))
            self.root.after(0, lambda: self.progress_var.set("75%"))
            configurator = Configurator()
            configured = configurator.configure(payload["manifest"])
            self.root.after(0, lambda: self.append_log(f"Configured: {', '.join(configured) if configured else 'nothing'}"))

            self.root.after(0, lambda: self.set_status("Verifying..."))
            self.root.after(0, lambda: self.progress.configure(value=90))
            self.root.after(0, lambda: self.progress_var.set("90%"))
            verifier = Verifier()
            verification = verifier.verify(payload["manifest"])

            summary = [
                "Auto Installer run summary",
                f"Run directory: {run_dir}",
                f"Installer exit code: {result_code}",
                f"Installed: {verification['installed']}",
                f"Configured: {verification['configured']}",
                f"Failed: {verification['failed']}",
            ]
            summary_text = "\n".join(summary)
            self.root.after(0, lambda: self.summary_box.configure(state="normal"))
            self.root.after(0, lambda: self.summary_box.delete("1.0", "end"))
            self.root.after(0, lambda: self.summary_box.insert("1.0", summary_text))
            self.root.after(0, lambda: self.summary_box.configure(state="disabled"))

            if result_code == 0:
                self.root.after(0, lambda: self.set_status("Completed successfully"))
                self.root.after(0, lambda: self.progress.configure(value=100))
                self.root.after(0, lambda: self.progress_var.set("100%"))
            else:
                self.root.after(0, lambda: self.set_status("Installation failed"))
                self.root.after(0, lambda: self.append_log("The installation failed. Review the output and manifest for details."))
        except Exception as exc:
            self._show_workflow_error(str(exc))
        finally:
            self.root.after(0, lambda: self.run_button.config(state="normal"))

    def _show_workflow_error(self, error_message: str) -> None:
        self.root.after(0, lambda: self.set_status("Error"))
        self.root.after(0, lambda message=error_message: self.append_log(f"ERROR: {message}"))
        self.root.after(0, lambda: self.summary_box.configure(state="normal"))
        self.root.after(0, lambda: self.summary_box.delete("1.0", "end"))
        self.root.after(
            0,
            lambda message=error_message: self.summary_box.insert("1.0", f"Error: {message}"),
        )
        self.root.after(0, lambda: self.summary_box.configure(state="disabled"))

    def open_output_dir(self):
        try:
            self.run_dir.mkdir(parents=True, exist_ok=True)
            os.startfile(str(self.run_dir))
        except Exception as exc:
            self.append_log(f"Unable to open output directory: {exc}")

    def run(self):
        self.root.mainloop()
