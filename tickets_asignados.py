import tkinter as tk
from tkinter import ttk, messagebox
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

API_BASE_URL = "https://webdemo.cloud.invgate.net/api/v1"
usuario = "insight"
contrasena = "bMfATCfh88dfpilLMRVKjYgI"
auth = HTTPBasicAuth(usuario, contrasena)

ESTADOS_A_LISTAR = [1, 2, 3, 4]

# Colores para los estados
COLOR_ESTADOS = {
    1: "#1E90FF",  # New - azul
    2: "#28A745",  # Open - verde
    3: "#FFC107",  # Pending - amarillo
    4: "#DC3545",  # Waiting - rojo
}

def epoch_a_fecha(epoch):
    if not epoch:
        return "N/A"
    return datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

def obtener_diccionario(endpoint, key_id="id", key_name="name"):
    url = f"{API_BASE_URL}/{endpoint}"
    r = requests.get(url, auth=auth)
    r.raise_for_status()
    datos = r.json()
    return {item[key_id]: item[key_name] for item in datos}

def obtener_ids_por_estado(status_id):
    url = f"{API_BASE_URL}/incidents.by.status"
    params = {"status_id": status_id}
    r = requests.get(url, auth=auth, params=params)
    r.raise_for_status()
    return r.json().get("requestIds", [])

def obtener_detalles(ids):
    if not ids:
        return {}
    url = f"{API_BASE_URL}/incidents"
    params = [("ids[]", i) for i in ids]
    r = requests.get(url, auth=auth, params=params)
    r.raise_for_status()
    return r.json()

class TicketsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tickets asignados por usuario")
        self.geometry("900x600")

        self.usuarios = {}
        self.prioridades = {}
        self.estados = {}

        # Treeview columnas
        cols = ("ID", "Título", "Estado", "Prioridad", "Creado")
        self.tree = ttk.Treeview(self, columns=cols, show="tree headings")
        self.tree.heading("#0", text="Usuario asignado")
        for c in cols:
            self.tree.heading(c, text=c)
            if c == "Título":
                self.tree.column(c, width=350)
            else:
                self.tree.column(c, width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configurar colores para tags
        for estado_id, color in COLOR_ESTADOS.items():
            nombre_estado = str(estado_id)  # vamos a usar id como tag
            self.tree.tag_configure(nombre_estado, foreground=color)

        btn_refresh = ttk.Button(self, text="Refrescar", command=self.cargar_tickets)
        btn_refresh.pack(pady=10)

        self.cargar_tickets()

    def cargar_tickets(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            # Obtener diccionarios
            self.usuarios = obtener_diccionario("users")
            self.prioridades = obtener_diccionario("incident.attributes.priority")
            self.estados = obtener_diccionario("incident.attributes.status")

            tickets_todos = {}

            for estado_id in ESTADOS_A_LISTAR:
                ids = obtener_ids_por_estado(estado_id)
                if not ids:
                    continue
                detalles = obtener_detalles(ids)
                tickets_todos.update(detalles)

            # Agrupar tickets por assigned_id
            tickets_por_usuario = {}
            for tid, ticket in tickets_todos.items():
                assigned_id = ticket.get("assigned_id")
                if assigned_id is None:
                    assigned_id = "Sin asignar"
                tickets_por_usuario.setdefault(assigned_id, []).append(ticket)

            for assigned_id, tickets in tickets_por_usuario.items():
                if assigned_id == "Sin asignar":
                    usuario_str = "🕶️ Sin asignar"
                else:
                    usuario_str = f"👤 {self.usuarios.get(assigned_id, f'Usuario ID {assigned_id}')}"
                parent_id = self.tree.insert("", tk.END, text=usuario_str, open=True)

                for t in tickets:
                    estado_nombre = self.estados.get(t.get("status_id"), "Estado desconocido")
                    prioridad = self.prioridades.get(t.get("priority_id"), "Prioridad desconocida")
                    creado = epoch_a_fecha(t.get("created_at"))
                    self.tree.insert(parent_id, tk.END, values=(t["id"], t["title"], estado_nombre, prioridad, creado),
                                     tags=(str(t.get("status_id")),))

            messagebox.showinfo("Listo", f"Se cargaron {len(tickets_todos)} tickets.")

        except requests.HTTPError as e:
            messagebox.showerror("Error HTTP", f"No se pudo conectar con la API:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

if __name__ == "__main__":
    app = TicketsApp()
    app.mainloop()
