import tkinter as tk
from tkinter import ttk, messagebox
from requests.auth import HTTPBasicAuth
import requests
from datetime import datetime
import textwrap
import re

API_BASE_URL = "https://webdemo.cloud.invgate.net/api/v1"
usuario = "insight"
contrasena = "bMfATCfh88dfpilLMRVKjYgI"

ESTADOS_A_LISTAR = {
    1: ("New", "#375A7F"),     # Azul petróleo
    2: ("Open", "#3D9970"),    # Verde oscuro
    3: ("Pending", "#B8860B"), # Dorado oscuro
    4: ("Waiting", "#8B0000")  # Rojo oscuro
}

def epoch_a_fecha(epoch):
    if not epoch:
        return "N/A"
    return datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

def limpiar_html(texto):
    cleanr = re.compile('<.*?>')
    limpio = re.sub(cleanr, '', texto)
    limpio = ' '.join(limpio.split())
    return limpio

def obtener_diccionario(api_endpoint, auth, key_id="id", key_name="name"):
    url = f"{API_BASE_URL}/{api_endpoint}"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    datos = response.json()
    return {item[key_id]: item[key_name] for item in datos}

def obtener_ids_por_estado(auth, status_id):
    url = f"{API_BASE_URL}/incidents.by.status"
    params = {"status_id": status_id}
    response = requests.get(url, auth=auth, params=params)
    response.raise_for_status()
    return response.json().get("requestIds", [])

def obtener_detalles(auth, ids):
    if not ids:
        return {}
    url = f"{API_BASE_URL}/incidents"
    params = [("ids[]", i) for i in ids]
    response = requests.get(url, auth=auth, params=params)
    response.raise_for_status()
    return response.json()

class TicketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tickets Abiertos - InvGate")
        self.root.geometry("1200x650")

        self.auth = HTTPBasicAuth(usuario, contrasena)

        columnas = ("ID", "Estado", "Prioridad", "Creado", "Título", "Descripción corta")
        self.tree = ttk.Treeview(root, columns=columnas, show="headings", height=25)

        for col in columnas:
            self.tree.heading(col, text=col)
            if col == "Título":
                self.tree.column(col, width=350, anchor=tk.W)
            elif col == "Descripción corta":
                self.tree.column(col, width=350, anchor=tk.W)
            else:
                self.tree.column(col, width=100, anchor=tk.W)

        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        btn_refresh = ttk.Button(root, text="Refrescar Tickets", command=self.cargar_tickets)
        btn_refresh.pack(side=tk.BOTTOM, pady=10)

        self.tree.bind("<Double-1>", self.ver_detalle_ticket)

        self.tickets_cache = {}
        self.cargar_tickets()

    def cargar_tickets(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            prioridades = obtener_diccionario("incident.attributes.priority", self.auth)
            orden_prioridad = {pid: int(pid) if str(pid).isdigit() else 999 for pid in prioridades}
            tickets_todos = {}

            for status_id, (nombre_estado, color) in ESTADOS_A_LISTAR.items():
                ids = obtener_ids_por_estado(self.auth, status_id)
                if not ids:
                    continue
                detalles = obtener_detalles(self.auth, ids)
                for tid, ticket in detalles.items():
                    ticket["estado_nombre"] = nombre_estado
                    ticket["color_estado"] = color
                    tickets_todos[tid] = ticket

            if not tickets_todos:
                messagebox.showinfo("Información", "No hay tickets en estados New, Open, Pending o Waiting.")
                return

            ordenados = sorted(
                tickets_todos.items(),
                key=lambda x: orden_prioridad.get(str(x[1].get("priority_id", "")), 999)
            )

            self.tickets_cache = {}

            for tid, ticket in ordenados:
                estado = ticket["estado_nombre"]
                color = ticket["color_estado"]
                prioridad = prioridades.get(ticket.get("priority_id"), "Desconocida")
                creado = epoch_a_fecha(ticket.get("created_at"))
                titulo = ticket.get("title", "Sin título")
                descripcion = limpiar_html(ticket.get("description", ""))
                descripcion_corta = textwrap.shorten(descripcion, width=80, placeholder="...")

                self.tickets_cache[tid] = {
                    "titulo": titulo,
                    "descripcion": descripcion,
                    "estado": estado,
                    "prioridad": prioridad,
                    "creado": creado,
                    "color": color
                }

                iid = self.tree.insert("", tk.END,
                    values=(tid, estado, prioridad, creado, titulo, descripcion_corta))

                self.tree.tag_configure(estado, foreground=color)
                self.tree.item(iid, tags=(estado,))

        except requests.HTTPError as e:
            messagebox.showerror("Error HTTP", f"Error al comunicarse con la API:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

    def ver_detalle_ticket(self, event):
        item = self.tree.selection()
        if not item:
            return
        tid = self.tree.item(item)["values"][0]
        ticket = self.tickets_cache.get(tid)
        if not ticket:
            return

        ventana = tk.Toplevel(self.root)
        ventana.title(f"Detalle del Ticket #{tid}")
        ventana.geometry("700x500")

        tk.Label(ventana, text="Título:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=4)
        tk.Message(ventana, text=ticket["titulo"], width=680, font=("Arial", 10)).pack(anchor="w", padx=10)

        tk.Label(ventana, text=f"Estado: {ticket['estado']}     Prioridad: {ticket['prioridad']}     Creado: {ticket['creado']}", font=("Arial", 9, "italic")).pack(anchor="w", padx=10, pady=6)

        tk.Label(ventana, text="Descripción completa:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)

        frame_text = tk.Frame(ventana)
        frame_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        text_widget = tk.Text(frame_text, wrap=tk.WORD)
        text_widget.insert(tk.END, ticket["descripcion"])
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_text, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

if __name__ == "__main__":
    root = tk.Tk()
    app = TicketApp(root)
    root.mainloop()
