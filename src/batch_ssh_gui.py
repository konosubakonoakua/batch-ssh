import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import paramiko
import threading
import concurrent.futures
from datetime import datetime
from queue import Queue
import json


class BatchSSHGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch SSH Executor")
        self.root.geometry("800x700")

        # Create menu bar
        self.create_menu()

        # Create logs directory if missing
        os.makedirs("logs", exist_ok=True)

        # Variables
        self.ip_list = []
        self.scripts = []
        self.files = []
        self.logs = []
        self.log_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.log_queue = Queue()

        # Create GUI elements
        self.create_widgets()

        # Start log processor
        self.process_logs()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Use", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)

    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)

        # IP List
        ttk.Label(main_frame, text="IP List File:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.ip_file_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.ip_file_var, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), pady=2
        )
        ttk.Button(main_frame, text="Browse", command=self.browse_ip_file).grid(
            row=0, column=2, padx=5, pady=2
        )

        # Scripts
        ttk.Label(main_frame, text="Scripts:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.scripts_frame = ttk.Frame(main_frame)
        self.scripts_frame.grid(
            row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2
        )
        self.scripts_listbox = tk.Listbox(
            self.scripts_frame, height=5, selectmode=tk.MULTIPLE
        )
        self.scripts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scripts_scrollbar = ttk.Scrollbar(
            self.scripts_frame, orient=tk.VERTICAL, command=self.scripts_listbox.yview
        )
        scripts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scripts_listbox.config(yscrollcommand=scripts_scrollbar.set)
        scripts_buttons_frame = ttk.Frame(main_frame)
        scripts_buttons_frame.grid(row=1, column=3, padx=5, pady=2)
        ttk.Button(
            scripts_buttons_frame, text="Add Scripts", command=self.add_scripts
        ).pack(pady=2)
        ttk.Button(
            scripts_buttons_frame, text="New Script", command=self.create_new_script
        ).pack(pady=2)
        ttk.Button(
            scripts_buttons_frame, text="Remove", command=self.remove_selected_script
        ).pack(pady=2)

        # Files
        ttk.Label(main_frame, text="Files:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.files_frame = ttk.Frame(main_frame)
        self.files_frame.grid(
            row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2
        )
        self.files_listbox = tk.Listbox(
            self.files_frame, height=5, selectmode=tk.MULTIPLE
        )
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar = ttk.Scrollbar(
            self.files_frame, orient=tk.VERTICAL, command=self.files_listbox.yview
        )
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.config(yscrollcommand=files_scrollbar.set)
        files_buttons_frame = ttk.Frame(main_frame)
        files_buttons_frame.grid(row=2, column=3, padx=5, pady=2)
        ttk.Button(files_buttons_frame, text="Add Files", command=self.add_files).pack(
            pady=2
        )
        ttk.Button(
            files_buttons_frame, text="Remove", command=self.remove_selected_file
        ).pack(pady=2)

        # Remote Directory
        ttk.Label(main_frame, text="Remote Directory:").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        self.remote_dir_var = tk.StringVar(value=f"/tmp/batch-{timestamp}")
        ttk.Entry(main_frame, textvariable=self.remote_dir_var, width=50).grid(
            row=3, column=1, sticky=(tk.W, tk.E), pady=2
        )

        # SSH Settings
        ttk.Label(main_frame, text="SSH User:").grid(
            row=4, column=0, sticky=tk.W, pady=2
        )
        self.ssh_user_var = tk.StringVar(value="root")
        ttk.Entry(main_frame, textvariable=self.ssh_user_var, width=20).grid(
            row=4, column=1, sticky=tk.W, pady=2
        )

        ttk.Label(main_frame, text="SSH Password:").grid(
            row=4, column=2, sticky=tk.W, pady=2, padx=(20, 0)
        )
        self.ssh_pass_var = tk.StringVar(value="imp")
        ttk.Entry(main_frame, textvariable=self.ssh_pass_var, show="*", width=20).grid(
            row=4, column=3, sticky=tk.W, pady=2
        )

        ttk.Label(main_frame, text="SSH Key File:").grid(
            row=5, column=0, sticky=tk.W, pady=2
        )
        self.ssh_key_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.ssh_key_var, width=50).grid(
            row=5, column=1, sticky=(tk.W, tk.E), pady=2
        )
        ttk.Button(main_frame, text="Browse", command=self.browse_ssh_key).grid(
            row=5, column=2, padx=5, pady=2
        )

        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=6, column=0, columnspan=4, sticky=tk.W, pady=5)

        self.cleanup_var = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="Cleanup remote directory after execution",
            variable=self.cleanup_var,
        ).pack(side=tk.LEFT)

        ttk.Label(options_frame, text="Max Workers:").pack(side=tk.LEFT, padx=(20, 5))
        self.workers_var = tk.StringVar(value="20")
        ttk.Spinbox(
            options_frame, from_=1, to=100, textvariable=self.workers_var, width=10
        ).pack(side=tk.LEFT)

        # Control Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=7, column=0, columnspan=4, pady=10)

        self.execute_button = ttk.Button(
            buttons_frame, text="Execute", command=self.execute_batch
        )
        self.execute_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            buttons_frame, text="Stop", command=self.stop_execution, state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(buttons_frame, text="Clear Logs", command=self.clear_logs).pack(
            side=tk.LEFT, padx=5
        )

        # Log Display
        ttk.Label(main_frame, text="Execution Logs:").grid(
            row=8, column=0, sticky=tk.W, pady=2
        )
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(
            row=9, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5
        )

        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN
        )
        status_bar.grid(row=10, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=2)

    def browse_ip_file(self):
        filename = filedialog.askopenfilename(
            title="Select IP List File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if filename:
            self.ip_file_var.set(filename)
            self.load_ip_list()

    def load_ip_list(self):
        try:
            with open(self.ip_file_var.get(), "r") as f:
                self.ip_list = [line.strip() for line in f if line.strip()]
            self.status_var.set(f"Loaded {len(self.ip_list)} IP addresses")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load IP list: {str(e)}")

    def add_scripts(self):
        filenames = filedialog.askopenfilenames(
            title="Select Script Files",
            filetypes=[("Shell scripts", "*.sh"), ("All files", "*.*")],
        )
        for filename in filenames:
            if filename not in self.scripts:
                self.scripts.append(filename)
                self.scripts_listbox.insert(tk.END, os.path.basename(filename))

    def add_files(self):
        filenames = filedialog.askopenfilenames(
            title="Select Files to Upload", filetypes=[("All files", "*.*")]
        )
        for filename in filenames:
            if filename not in self.files:
                self.files.append(filename)
                self.files_listbox.insert(tk.END, os.path.basename(filename))

    def create_new_script(self):
        # Create a simple script editor window
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Create New Bash Script")
        editor_window.geometry("600x400")

        # Script name
        name_frame = ttk.Frame(editor_window, padding="10")
        name_frame.pack(fill=tk.X)
        ttk.Label(name_frame, text="Script Name:").pack(side=tk.LEFT)
        script_name_var = tk.StringVar(value="new_script.sh")
        ttk.Entry(name_frame, textvariable=script_name_var, width=30).pack(
            side=tk.LEFT, padx=10
        )

        # Script content
        content_frame = ttk.Frame(editor_window, padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(content_frame, text="Script Content:").pack(anchor=tk.W)

        script_text = scrolledtext.ScrolledText(content_frame, height=15, wrap=tk.WORD)
        script_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Default script content
        default_script = """#!/bin/bash
# Your bash script here
echo "Hello from batch SSH script"
# Add your commands below
"""
        script_text.insert(tk.END, default_script)

        # Buttons
        button_frame = ttk.Frame(editor_window, padding="10")
        button_frame.pack(fill=tk.X)

        def save_script():
            script_name = script_name_var.get()
            if not script_name.endswith(".sh"):
                script_name += ".sh"

            script_content = script_text.get(1.0, tk.END).strip()

            # Ask for save location
            filename = filedialog.asksaveasfilename(
                title="Save Script",
                defaultextension=".sh",
                filetypes=[("Shell scripts", "*.sh"), ("All files", "*.*")],
            )

            if filename:
                try:
                    with open(filename, "w") as f:
                        f.write(script_content)

                    # Add to scripts list
                    if filename not in self.scripts:
                        self.scripts.append(filename)
                        self.scripts_listbox.insert(tk.END, os.path.basename(filename))

                    self.status_var.set(f"Script saved: {filename}")
                    editor_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save script: {str(e)}")

        def cancel():
            editor_window.destroy()

        ttk.Button(button_frame, text="Save", command=save_script).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(
            side=tk.LEFT, padx=5
        )

    def remove_selected_script(self):
        selection = self.scripts_listbox.curselection()
        if selection:
            # Sort indices in reverse order to avoid index shifting issues
            indices_to_remove = sorted(selection, reverse=True)
            removed_count = 0

            for index in indices_to_remove:
                # Remove from listbox
                self.scripts_listbox.delete(index)
                # Remove from scripts list
                if index < len(self.scripts):
                    del self.scripts[index]
                removed_count += 1

            self.status_var.set(f"Removed {removed_count} script(s)")
        else:
            messagebox.showwarning("No Selection", "Please select script(s) to remove")

    def remove_selected_file(self):
        selection = self.files_listbox.curselection()
        if selection:
            # Sort indices in reverse order to avoid index shifting issues
            indices_to_remove = sorted(selection, reverse=True)
            removed_count = 0

            for index in indices_to_remove:
                # Remove from listbox
                self.files_listbox.delete(index)
                # Remove from files list
                if index < len(self.files):
                    del self.files[index]
                removed_count += 1

            self.status_var.set(f"Removed {removed_count} file(s)")
        else:
            messagebox.showwarning("No Selection", "Please select file(s) to remove")

    def browse_ssh_key(self):
        filename = filedialog.askopenfilename(
            title="Select SSH Private Key",
            filetypes=[("Private keys", "*.pem *.key"), ("All files", "*.*")],
        )
        if filename:
            self.ssh_key_var.set(filename)

    def log_message(self, message):
        self.log_queue.put(message)

    def process_logs(self):
        try:
            while not self.log_queue.empty():
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
        except:
            pass
        self.root.after(100, self.process_logs)

    def clear_logs(self):
        self.log_text.delete(1.0, tk.END)

    def log_step(self, host: str, message: str, ok: bool = True):
        """Thread-safe logging with [ip] prefix."""
        symbol = "✓" if ok else "✗"
        line = f"[{host}] {symbol} {message}"
        self.log_message(line)

        with self.log_lock:
            self.logs.append(line)

    def run_on_host(
        self, host, scripts, files, remote_dir, cleanup, ssh_user, ssh_pass, ssh_key
    ):
        results = []
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if self.stop_event.is_set():
                return results

            self.log_step(host, f"Connecting to {host}...")
            if ssh_key:
                key = paramiko.RSAKey.from_private_key_file(ssh_key)
                ssh.connect(host, username=ssh_user, pkey=key, timeout=10)
            else:
                ssh.connect(host, username=ssh_user, password=ssh_pass, timeout=10)
            sftp = ssh.open_sftp()

            ssh.exec_command(f"mkdir -p {remote_dir}")
            self.log_step(host, f"Created batch dir {remote_dir}")

            # Upload files
            for f in files:
                if self.stop_event.is_set():
                    break
                if not os.path.exists(f):
                    results.append((host, f, False, "Local file not found"))
                    self.log_step(host, f"Local file {f} not found", ok=False)
                    continue
                remote_path = f"{remote_dir}/{os.path.basename(f)}"
                sftp.put(f, remote_path)
                results.append((host, f, True, f"Uploaded to {remote_path}"))
                self.log_step(host, f"Uploaded {f} -> {remote_path}")

            # Upload and execute scripts
            for script in scripts:
                if self.stop_event.is_set():
                    break
                if not os.path.exists(script):
                    results.append((host, script, False, "Local script not found"))
                    self.log_step(host, f"Local script {script} not found", ok=False)
                    break
                remote_path = f"{remote_dir}/{os.path.basename(script)}"
                sftp.put(script, remote_path)
                sftp.chmod(remote_path, 0o755)
                self.log_step(host, f"Uploaded script {script}")

                stdin, stdout, stderr = ssh.exec_command(
                    f"cd {remote_dir} && bash {remote_path}"
                )
                exit_code = stdout.channel.recv_exit_status()
                out = stdout.read().decode()
                err = stderr.read().decode()

                if exit_code != 0:
                    results.append(
                        (
                            host,
                            script,
                            False,
                            f"Exit {exit_code}, stderr: {err.strip()}",
                        )
                    )
                    self.log_step(
                        host, f"Script {script} failed (exit {exit_code})", ok=False
                    )
                    break
                else:
                    results.append((host, script, True, out.strip()))
                    self.log_step(host, f"Script {script} executed successfully")

            if cleanup and not self.stop_event.is_set():
                ssh.exec_command(f"rm -rf {remote_dir}")
                results.append(
                    (host, remote_dir, True, "Remote batch directory removed")
                )
                self.log_step(host, f"Cleaned up {remote_dir}")

            sftp.close()
            ssh.close()
        except Exception as e:
            results.append((host, None, False, f"Connection error: {str(e)}"))
            self.log_step(host, f"Connection error: {str(e)}", ok=False)

        return results

    def execute_batch(self):
        # Validate inputs
        if not self.ip_file_var.get():
            messagebox.showerror("Error", "Please select an IP list file")
            return

        if not self.ip_list:
            messagebox.showerror("Error", "No IP addresses loaded")
            return

        if not self.scripts and not self.files:
            messagebox.showerror("Error", "Please add at least one script or file")
            return

        # Reset stop event
        self.stop_event.clear()

        # Update UI
        self.execute_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Executing...")

        # Start execution in separate thread
        threading.Thread(target=self._execute_thread, daemon=True).start()

    def _execute_thread(self):
        try:
            max_workers = int(self.workers_var.get())
            summary = {}

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                futures = {
                    executor.submit(
                        self.run_on_host,
                        ip,
                        self.scripts,
                        self.files,
                        self.remote_dir_var.get(),
                        self.cleanup_var.get(),
                        self.ssh_user_var.get(),
                        self.ssh_pass_var.get(),
                        self.ssh_key_var.get(),
                    ): ip
                    for ip in self.ip_list
                }

                for future in concurrent.futures.as_completed(futures):
                    if self.stop_event.is_set():
                        break

                    host = futures[future]
                    try:
                        results = future.result()
                        summary[host] = results
                        self.log_step(host, "Completed successfully")
                    except Exception as e:
                        summary[host] = [
                            (host, None, False, f"Unhandled error: {str(e)}")
                        ]
                        self.log_step(host, f"Error: {e}", ok=False)

            # Save log to file
            self.save_log_to_file(summary)

            if not self.stop_event.is_set():
                self.log_message("\nExecution completed successfully!")
                self.status_var.set("Completed")
            else:
                self.log_message("\nExecution stopped by user")
                self.status_var.set("Stopped")

        except Exception as e:
            self.log_message(f"Execution error: {str(e)}")
            self.status_var.set("Error")
        finally:
            # Update UI
            self.root.after(0, lambda: self.execute_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))

    def stop_execution(self):
        self.stop_event.set()
        self.log_message("Stopping execution...")

    def save_log_to_file(self, summary):
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        log_file_path = os.path.join("logs", f"batch-{timestamp}.log")

        try:
            with open(log_file_path, "w", encoding="utf-8") as f:
                for log in self.logs:
                    f.write(log + "\n")

                f.write("\nExecution Summary:\n")
                for host, results in summary.items():
                    for _, target, ok, msg in results:
                        status = "SUCCESS" if ok else "FAIL"
                        f.write(f"{host}\t{target}\t{status}\t{msg}\n")

            self.log_message(f"\nLog saved to: {log_file_path}")
        except Exception as e:
            self.log_message(f"Failed to save log: {str(e)}")

    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("How to Use Batch SSH Executor")
        help_window.geometry("700x600")

        help_text = scrolledtext.ScrolledText(
            help_window, wrap=tk.WORD, width=80, height=35
        )
        help_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        help_content = """BATCH SSH EXECUTOR - USER GUIDE

=== OVERVIEW ===
Batch SSH Executor allows you to execute shell scripts and transfer files to multiple remote servers simultaneously via SSH.

=== SETUP ===

1. IP LIST FILE
   • Create a text file with one IP address per line
   • Example:
     192.168.1.10
     192.168.1.11
     192.168.1.12
   • Click "Browse" to select your IP list file

2. SSH CREDENTIALS
   • SSH User: Username for remote login (default: root)
   • SSH Password: Password for authentication
   • SSH Key File: Optional - Use private key instead of password

3. SCRIPTS
   • Add Scripts: Select existing shell scripts (.sh files)
   • New Script: Create new bash scripts with the built-in editor
   • Multiple Selection: Hold Ctrl/Cmd to select multiple items
   • Remove: Select one or more items and click Remove

4. FILES
   • Add Files: Select any files to upload to remote servers
   • Multiple Selection: Hold Ctrl/Cmd to select multiple items
   • Remove: Select one or more items and click Remove

=== EXECUTION ===

1. REMOTE DIRECTORY
   • Directory where files and scripts will be uploaded
   • Default: /tmp/batch-{timestamp}
   • Must be writable by SSH user

2. OPTIONS
   • Cleanup remote directory: Removes uploaded files after execution
   • Max Workers: Number of concurrent SSH connections (1-100)

3. RUN EXECUTION
   • Click "Execute" to start
   • Monitor progress in the Execution Logs
   • Click "Stop" to abort execution
   • Logs are automatically saved to logs/ directory

=== FEATURES ===

• Multi-threaded execution for faster processing
• Real-time logging with [IP] prefixes
• Automatic log file generation with timestamps
• Support for both password and key-based authentication
• Multiple selection and batch removal
• Built-in script editor
• Progress tracking and error reporting

=== TROUBLESHOOTING ===

• Connection timeouts: Check network connectivity and firewall settings
• Authentication failures: Verify credentials and SSH key permissions
• Permission denied: Ensure remote user has write permissions to target directory
• Script execution failures: Check script syntax and file permissions

=== KEYBOARD SHORTCUTS ===

• Ctrl+Click: Select multiple non-adjacent items
• Shift+Click: Select range of items
• Delete: Remove selected items (after clicking Remove button)

=== LOG FILES ===

Execution logs are saved as: logs/batch-{timestamp}.log
Format: [HOST] STATUS MESSAGE
Status: ✓ (Success) or ✗ (Failed)
"""

        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)

        # Close button
        ttk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=5)

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About Batch SSH Executor")
        about_window.geometry("400x300")
        about_window.resizable(False, False)

        # Center the window
        about_window.transient(self.root)
        about_window.grab_set()

        frame = ttk.Frame(about_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            frame, text="Batch SSH Executor", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Version
        version_label = ttk.Label(frame, text="Version 1.0", font=("Arial", 12))
        version_label.pack(pady=(0, 20))

        # Description
        desc_text = """A powerful GUI application for executing 
shell scripts and transferring files to 
multiple remote servers simultaneously.

Features:
• Multi-threaded SSH execution
• Built-in script editor
• Real-time logging
• Batch file management
• Support for key authentication"""

        desc_label = ttk.Label(frame, text=desc_text, justify=tk.CENTER)
        desc_label.pack(pady=(0, 20))

        # Close button
        ttk.Button(frame, text="Close", command=about_window.destroy, width=15).pack(
            pady=10
        )


def main():
    root = tk.Tk()
    app = BatchSSHGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
