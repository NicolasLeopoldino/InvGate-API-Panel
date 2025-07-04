import tkinter as tk
from tkinter import ttk, messagebox
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

# --- Configuración base ---
API_BASE_URL = "https://webdemo.cloud.invgate.net/api/v1"
usuario = "insight"
contrasena = "bMfATCfh88dfpilLMRVKjYgI"
auth = HTTPBasicAuth(usuario, contrasena)

# --- Colores por tipo de breaking news ---
COLOR_TIPO = {
    1: "#17a2b8",  # Info - azul claro
    2: "#ffc107",  # Warning - amarillo
    3: "#dc3545",  # Error/Critical - rojo
}

ICONOS_TIPO = {
    1: "ℹ️",
    2: "⚠️",
    3: "❌",
}

# --- Convertir timestamp ---
def epoch_a_fecha(epoch):
    if not epoch:
        return "N/A"
    return datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')


# --- Obtener diccionario de atributos (tipo o estado) ---
def obtener_atributos(endpoint):
    url = f"{API_BASE_URL}/{endpoint}"
    r = requests.get(url, auth=auth)
    r.raise_for_status()
    return {item["id"]: item["name"] for item in r.json()}


# --- Obtener todas las breaking news ---
def obtener_breaking_news():
    url = f"{API_BASE_URL}/breakingnews.all"
    r = requests.get(url, auth=auth)
    r.raise_for_status()
    return r.json()


# --- Interfaz principal ---
class BreakingNewsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Centro de Alertas - Breaking News")
        self.geometry("800x500")
        self.configure(bg="#1e1e1e")

        # Título principal
        titulo = tk.Label(self, text="📢 Centro de Alertas Globales", font=("Segoe UI", 20, "bold"),
                          fg="#ffffff", bg="#1e1e1e")
        titulo.pack(pady=15)

        # Contenedor de noticias
        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0)
        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas, bg="#1e1e1e")

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

        # Botón de refrescar
        btn = ttk.Button(self, text="🔄 Refrescar", command=self.cargar_alertas)
        btn.pack(pady=10)

        # Diccionarios
        self.tipo_dict = {}
        self.estado_dict = {}

        self.cargar_alertas()

    def cargar_alertas(self):
        # Limpiar alertas anteriores
        for widget in self.frame.winfo_children():
            widget.destroy()

        try:
            self.tipo_dict = obtener_atributos("breakingnews.attributes.type")
            self.estado_dict = obtener_atributos("breakingnews.attributes.status")
            alertas = obtener_breaking_news()

            if not alertas:
                lbl = tk.Label(self.frame, text="✅ No hay alertas activas",
                               fg="#28a745", bg="#1e1e1e", font=("Segoe UI", 14))
                lbl.pack(pady=20)
                return

            for alerta in alertas:
                self.mostrar_alerta(alerta)

        except requests.HTTPError as e:
            messagebox.showerror("Error HTTP", f"No se pudo conectar con la API:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

    def mostrar_alerta(self, alerta):
        tipo_id = alerta.get("type_id", 1)
        estado_id = alerta.get("status_id", 1)
        color = COLOR_TIPO.get(tipo_id, "#6c757d")
        icono = ICONOS_TIPO.get(tipo_id, "🔔")

        # Card visual
        card = tk.Frame(self.frame, bg="#2e2e2e", bd=2, relief="ridge")
        card.pack(fill="x", padx=20, pady=10)

        titulo = f"{icono} {alerta.get('title', 'Sin título')}"
        lbl_titulo = tk.Label(card, text=titulo, font=("Segoe UI", 14, "bold"),
                              fg=color, bg="#2e2e2e", anchor="w", justify="left")
        lbl_titulo.pack(fill="x", padx=10, pady=5)

        contenido = alerta.get("content", "").strip()
        if not contenido:
            contenido = "⚠️ Esta alerta no tiene contenido definido."

        lbl_contenido = tk.Label(card, text=contenido, wraplength=740, justify="left",
                                 fg="#dddddd", bg="#2e2e2e", font=("Segoe UI", 11))
        lbl_contenido.pack(fill="x", padx=10)

        info = f"📅 Desde: {epoch_a_fecha(alerta.get('start_date'))} | Estado: {self.estado_dict.get(estado_id, 'Desconocido')}"
        lbl_info = tk.Label(card, text=info, font=("Segoe UI", 10, "italic"),
                            fg="#aaaaaa", bg="#2e2e2e", anchor="w")
        lbl_info.pack(fill="x", padx=10, pady=(5, 10))


# --- Ejecutar la app ---
if __name__ == "__main__":
    app = BreakingNewsApp()
    app.mainloop()
