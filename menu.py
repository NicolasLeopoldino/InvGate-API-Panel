import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys

class MenuPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🛠️ Panel de Control InvGate")
        self.geometry("600x700")  # Ventana más grande para el diseño
        self.resizable(False, False)
        self.configure(bg="#121212")

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TButton",
                        font=("Segoe UI", 12, "bold"),
                        foreground="#EEE",
                        background="#1E88E5",
                        padding=12)
        style.map("TButton",
                  foreground=[('active', '#FFF')],
                  background=[('active', '#1565C0')])

        lbl_title = tk.Label(self, text="InvGate - Herramientas", 
                             font=("Segoe UI", 18, "bold"), fg="#FFF", bg="#121212")
        lbl_title.pack(pady=(30, 20))

        botones = [
            ("⏱️ Time Tracker General", self.abrir_agent_time),
            ("📰 Breaking News", self.abrir_news),
            ("🎫 Tickets Totales", self.abrir_ticket_todos),
            ("👤 Tickets Asignados", self.abrir_ticket_asignados),
            ("🔧 Administración Usuarios", self.abrir_user_admin),
        ]

        for (texto, comando) in botones:
            btn = ttk.Button(self, text=texto, command=comando)
            btn.pack(pady=12, padx=40, fill=tk.X)

        lbl_footer = tk.Label(self, text="© 2025 Nicolás Leopoldino", font=("Segoe UI", 9),
                              fg="#888", bg="#121212")
        lbl_footer.pack(side=tk.BOTTOM, pady=15)

    def ejecutar_script(self, nombre_script):
        try:
            subprocess.Popen([sys.executable, nombre_script], shell=False)
        except Exception as e:
            messagebox.showerror("Error", f"No pude arrancar {nombre_script}:\n{e}")

    def abrir_agent_time(self):
        self.ejecutar_script("agent_time.py")

    def abrir_news(self):
        self.ejecutar_script("news.py")

    def abrir_ticket_todos(self):
        self.ejecutar_script("ticket_todos.py")

    def abrir_ticket_asignados(self):
        self.ejecutar_script("ticket_asignados.py")

    def abrir_user_admin(self):
        self.ejecutar_script("user_admin.py")


if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()
