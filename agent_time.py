import tkinter as tk
from tkinter import ttk, messagebox
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

API_BASE_URL = "https://webdemo.cloud.invgate.net/api/v1"
USUARIO = "insight"
CONTRASENA = "bMfATCfh88dfpilLMRVKjYgI"
auth = HTTPBasicAuth(USUARIO, CONTRASENA)

def obtener_usuarios():
    url = f"{API_BASE_URL}/users"
    r = requests.get(url, auth=auth)
    r.raise_for_status()
    data = r.json()
    usuarios = {}
    for u in data:
        nombre = u.get("name") or u.get("username") or f"ID {u.get('id')}"
        usuarios[u["id"]] = nombre
    return usuarios

def obtener_timetracking(desde):
    url = f"{API_BASE_URL}/timetracking"
    desde_str = desde.strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {"from": desde_str}
    r = requests.get(url, auth=auth, params=params)
    r.raise_for_status()
    return r.json()

def segundos_a_horas(segundos):
    h = segundos // 3600
    m = (segundos % 3600) // 60
    return f"{h}h {m}m"

class TimeTrackerResumenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⏱️ Resumen de Time Tracking")
        self.geometry("750x450")
        self.resizable(False, False)

        columnas = ("Usuario", "Tiempo Trabajado", "Registros", "Tickets únicos", "Último registro")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings", height=18)
        for col in columnas:
            self.tree.heading(col, text=col)
            if col == "Usuario":
                self.tree.column(col, width=220, anchor=tk.W)
            elif col == "Último registro":
                self.tree.column(col, width=140, anchor=tk.CENTER)
            else:
                self.tree.column(col, width=110, anchor=tk.CENTER)
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        btn_refresh = ttk.Button(self, text="🔄 Refrescar", command=self.cargar_datos)
        btn_refresh.pack(pady=(0,10))

        self.lbl_info = ttk.Label(self, text="", font=("Arial", 10))
        self.lbl_info.pack()

        self.cargar_datos()

    def cargar_datos(self):
        try:
            self.lbl_info.config(text="Cargando datos, espere...")
            self.update_idletasks()

            desde = datetime.utcnow() - timedelta(days=15*365)
            timetracking = obtener_timetracking(desde)
            usuarios = obtener_usuarios()

            if not timetracking:
                messagebox.showinfo("Info", "No se encontraron registros de time tracking.")
                self.tree.delete(*self.tree.get_children())
                self.lbl_info.config(text="Sin datos para mostrar.")
                return

            resumen = {}
            for reg in timetracking:
                uid = reg.get("user_id")
                if uid is None:
                    continue
                if uid not in resumen:
                    resumen[uid] = {
                        "total_segundos": 0,
                        "count": 0,
                        "tickets": set(),
                        "ultimo": None
                    }
                resumen[uid]["total_segundos"] += reg.get("total", 0)
                resumen[uid]["count"] += 1
                if reg.get("incident"):
                    resumen[uid]["tickets"].add(reg["incident"])
                fecha_reg = datetime.strptime(reg["from"], "%Y-%m-%d %H:%M")
                if (resumen[uid]["ultimo"] is None) or (fecha_reg > resumen[uid]["ultimo"]):
                    resumen[uid]["ultimo"] = fecha_reg

            self.tree.delete(*self.tree.get_children())

            for uid, datos in sorted(resumen.items(), key=lambda x: x[1]["total_segundos"], reverse=True):
                nombre = usuarios.get(uid, f"👤 Usuario {uid}")
                tiempo_str = segundos_a_horas(datos["total_segundos"])
                cant_reg = datos["count"]
                cant_tickets = len(datos["tickets"])
                ultimo_str = datos["ultimo"].strftime("%Y-%m-%d %H:%M") if datos["ultimo"] else "N/A"
                icono = "🕒"
                self.tree.insert("", tk.END, values=(
                    f"{icono} {nombre}",
                    tiempo_str,
                    cant_reg,
                    cant_tickets,
                    ultimo_str,
                ))

            self.lbl_info.config(text=f"Se cargaron {len(timetracking)} registros para {len(resumen)} usuarios.")

        except requests.HTTPError as e:
            messagebox.showerror("Error HTTP", f"No se pudo conectar con la API:\n{e}")
            self.lbl_info.config(text="Error al cargar datos.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}")
            self.lbl_info.config(text="Error al cargar datos.")

if __name__ == "__main__":
    app = TimeTrackerResumenApp()
    app.mainloop()
