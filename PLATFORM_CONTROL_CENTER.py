import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import os
import time
import re
from datetime import datetime

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class AestheticControlCenter:
    def __init__(self, root):
        self.root = root
        self.root.title("PLATFORM OS - CORE CONTROL (VIBE EDITION)")
        self.root.geometry("1300x850")
        self.root.configure(bg="#050505")
        
        self.colors = {
            "bg": "#050505",
            "card": "#0d0d0d",
            "accent": "#00f2ff",
            "text": "#e0e0e0",
            "dim": "#555555",
            "success": "#00ff88",
            "danger": "#ff3366",
            "border": "#1a1a1a",
            "hinglish": "#ff00ff"
        }
        
        # Using the absolute python path from your startup.bat for reliability
        python_path = r"C:\Python314\python.exe"
        if not os.path.exists(python_path):
            python_path = "python" # Fallback to global python
            
        self.processes = {
            "MINIO CORE": {"cmd": r"E:\minio-data\minio.exe server E:\minio-data\data --console-address :9001", "cwd": None},
            "FASTAPI ENGINE": {"cmd": f"{python_path} main.py", "cwd": "minIO/server/backend"},
            "VITE FRONTEND": {"cmd": "npm run dev", "cwd": "."},
            "SYSTEM DASH": {"cmd": f"{python_path} -m http.server 3000", "cwd": "minIO"},
            "PUBLIC TUNNEL": {"cmd": "npx localtunnel --port 8000 --subdomain vibe-edtech", "cwd": "."}
        }
        
        self.translations = [
            (r"Starting.*MinIO", "Bhai, MinIO start ho raha hai, storage ready ho rahi hai..."),
            (r"Listening on", "Website yahan live hai, student login kar sakte hain! 🚀"),
            (r"POST.*upload", "Oye! Nayi file upload ho rahi hai backend mein..."),
            (r"GET.*stream/video", "Kisine video chalu kiya! Padhai shuru ho gayi hai. 🎥"),
            (r"ERROR|Fatal|bind", "Arre bhai! Port busy hai ya kuch gadbad hai, check kar! ⚠️"),
            (r"Compiled successfully", "Frontend ek dam ready hai, look mast aa raha hai! ✨"),
            (r"Port 5173 is in use", "5173 busy tha, tension mat le maine doosre port pe chalu kar diya."),
            (r"ngrok.*established", "Balle Balle! Ngrok tunnel chalu ho gaya, aab duniya bhar se access kar sakte ho! 🌍"),
        ]
        
        self.running_procs = {}
        self.log_boxes = {}
        self.setup_ui()
        self.start_monitors()

    def strip_ansi(self, text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def setup_ui(self):
        sidebar = tk.Frame(self.root, bg=self.colors["card"], width=80)
        sidebar.pack(side="left", fill="y")
        tk.Label(sidebar, text="●", font=("Arial", 20), fg=self.colors["accent"], bg=self.colors["card"]).pack(pady=20)
        
        main_content = tk.Frame(self.root, bg=self.colors["bg"])
        main_content.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        header = tk.Frame(main_content, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="PLATFORM COMMAND CENTER", font=("Courier New", 24, "bold"), fg="white", bg=self.colors["bg"]).pack(side="left")
        
        stats_bar = tk.Frame(header, bg=self.colors["bg"])
        stats_bar.pack(side="right")
        self.cpu_label = tk.Label(stats_bar, text="CPU: 0%", font=("Consolas", 10), fg=self.colors["accent"], bg=self.colors["bg"])
        self.cpu_label.pack(side="left", padx=10)
        self.network_label = tk.Label(stats_bar, text="NET: 0 KB/s", font=("Consolas", 10), fg=self.colors["success"], bg=self.colors["bg"])
        self.network_label.pack(side="left", padx=10)

        actions = tk.Frame(main_content, bg=self.colors["bg"])
        actions.pack(fill="x", pady=(0, 15))
        tk.Button(actions, text="[ INITIALIZE_SYSTEM ]", command=self.start_all, bg=self.colors["bg"], fg=self.colors["success"], font=("Consolas", 9, "bold"), bd=1, relief="flat", highlightthickness=1, highlightbackground=self.colors["success"], padx=15, pady=8).pack(side="left", padx=5)
        tk.Button(actions, text="[ TERMINATE_SYSTEM ]", command=self.stop_all, bg=self.colors["bg"], fg=self.colors["danger"], font=("Consolas", 9, "bold"), bd=1, relief="flat", highlightthickness=1, highlightbackground=self.colors["danger"], padx=15, pady=8).pack(side="left", padx=5)

        layout_frame = tk.Frame(main_content, bg=self.colors["bg"])
        layout_frame.pack(fill="both", expand=True)
        
        grid = tk.Frame(layout_frame, bg=self.colors["bg"])
        grid.pack(side="left", fill="both", expand=True)
        
        for i, (name, config) in enumerate(self.processes.items()):
            row, col = divmod(i, 2)
            card = tk.Frame(grid, bg=self.colors["card"], bd=0, highlightthickness=1, highlightbackground=self.colors["border"])
            card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            grid.grid_columnconfigure(col, weight=1)
            grid.grid_rowconfigure(row, weight=1)
            
            title_bar = tk.Frame(card, bg=self.colors["card"])
            title_bar.pack(fill="x", padx=10, pady=5)
            tk.Label(title_bar, text=f"// {name}", font=("Consolas", 9, "bold"), fg=self.colors["accent"], bg=self.colors["card"]).pack(side="left")
            
            status_dot = tk.Label(title_bar, text="●", font=("Arial", 10), fg=self.colors["dim"], bg=self.colors["card"])
            status_dot.pack(side="right", padx=5)
            
            log = scrolledtext.ScrolledText(card, bg="#000000", fg="#bbbbbb", font=("Consolas", 8), borderwidth=0, highlightthickness=0)
            log.pack(fill="both", expand=True, padx=5, pady=(0, 5))
            self.log_boxes[name] = log
            
            btn = tk.Button(title_bar, text="EXEC", command=lambda n=name: self.toggle_process(n), bg=self.colors["card"], fg=self.colors["dim"], font=("Consolas", 7), bd=1, relief="flat", highlightthickness=1, highlightbackground=self.colors["dim"])
            btn.pack(side="right")
            self.running_procs[name] = {"process": None, "button": btn, "dot": status_dot}

        hinglish_frame = tk.Frame(layout_frame, bg=self.colors["card"], width=300, bd=0, highlightthickness=1, highlightbackground=self.colors["hinglish"])
        hinglish_frame.pack(side="right", fill="y", padx=(15, 0))
        tk.Label(hinglish_frame, text="PLATFORM KI AWAAZ 🎤", font=("Outfit", 12, "bold"), fg=self.colors["hinglish"], bg=self.colors["card"]).pack(pady=10)
        self.hinglish_box = scrolledtext.ScrolledText(hinglish_frame, bg=self.colors["card"], fg=self.colors["text"], font=("Inter", 10), borderwidth=0, highlightthickness=0)
        self.hinglish_box.pack(fill="both", expand=True, padx=10, pady=10)

    def translate_log(self, message):
        for pattern, hinglish in self.translations:
            if re.search(pattern, message, re.IGNORECASE):
                timestamp = datetime.now().strftime("%H:%M")
                self.hinglish_box.insert(tk.END, f"[{timestamp}] {hinglish}\n")
                self.hinglish_box.insert(tk.END, "-"*20 + "\n")
                self.hinglish_box.see(tk.END)
                break

    def start_monitors(self):
        if not HAS_PSUTIL:
            self.cpu_label.config(text="CPU: N/A")
            self.network_label.config(text="NET: N/A")
            return

        def monitor():
            last_net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
            while True:
                cpu = psutil.cpu_percent()
                self.cpu_label.config(text=f"CPU: {cpu}%")
                curr_net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
                speed = (curr_net - last_net) / 1024
                self.network_label.config(text=f"NET: {speed:.1f} KB/s")
                last_net = curr_net
                time.sleep(1)
        threading.Thread(target=monitor, daemon=True).start()

    def log_message(self, name, message):
        clean_msg = self.strip_ansi(message)
        box = self.log_boxes[name]
        box.insert(tk.END, clean_msg)
        box.see(tk.END)
        self.translate_log(clean_msg)

    def read_output(self, name, process):
        for line in iter(process.stdout.readline, ''):
            if not line: break
            self.log_message(name, line)
        process.stdout.close()

    def toggle_process(self, name):
        if self.running_procs[name]["process"]:
            self.stop_process(name)
        else:
            self.start_process(name)

    def start_process(self, name):
        config = self.processes[name]
        try:
            cwd = config["cwd"] if config["cwd"] else os.getcwd()
            # Added creationflags to prevent new terminal windows from popping up
            proc = subprocess.Popen(
                config["cmd"], 
                cwd=cwd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                shell=True, 
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.running_procs[name]["process"] = proc
            self.running_procs[name]["button"].config(text="TERM", fg=self.colors["danger"], highlightbackground=self.colors["danger"])
            self.running_procs[name]["dot"].config(fg=self.colors["success"])
            threading.Thread(target=self.read_output, args=(name, proc), daemon=True).start()
        except Exception as e:
            self.log_message(name, f"FATAL_ERROR: {str(e)}\n")

    def stop_process(self, name):
        proc = self.running_procs[name]["process"]
        if proc:
            subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, capture_output=True)
            self.running_procs[name]["process"] = None
            self.running_procs[name]["button"].config(text="EXEC", fg=self.colors["dim"], highlightbackground=self.colors["dim"])
            self.running_procs[name]["dot"].config(fg=self.colors["dim"])

    def start_all(self):
        self.stop_all() # Clean start
        time.sleep(1)
        for name in self.processes:
            self.start_process(name)
            time.sleep(0.5)

    def stop_all(self):
        for name in self.processes:
            self.stop_process(name)

if __name__ == "__main__":
    root = tk.Tk()
    app = AestheticControlCenter(root)
    root.mainloop()
