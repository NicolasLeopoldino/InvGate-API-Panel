import tkinter as tk
from tkinter import ttk, messagebox
from requests.auth import HTTPBasicAuth
import requests

API_BASE_URL = "https://webdemo.cloud.invgate.net/api/v1"  # Cambiar por tu URL
USUARIO = "insight"
CONTRASENA = "bMfATCfh88dfpilLMRVKjYgI"

auth = HTTPBasicAuth(USUARIO, CONTRASENA)

def obtener_usuarios():
    url = f"{API_BASE_URL}/users"
    r = requests.get(url, auth=auth)
    r.raise_for_status()
    return r.json()

def obtener_info_usuario_por_email(email):
    url = f"{API_BASE_URL}/user.by"
    params = {"email": email}
    r = requests.get(url, auth=auth, params=params)
    r.raise_for_status()
    return r.json()

class UserAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Administración de Usuarios - InvGate")
        self.root.geometry("900x500")

        self.usuarios = []

        # Lista usuarios en un Treeview
        columnas = ("id", "name", "email")
        self.tree = ttk.Treeview(root, columns=columnas, show="headings")
        for col in columnas:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=250)
        self.tree.pack(side=tk.LEFT, fill=tk.Y)

        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # Panel derecho para detalle
        self.detail_text = tk.Text(root, width=60, bg="#f9f9f9", font=("Consolas", 11))
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Definimos tags con colores para etiquetas
        self.detail_text.tag_configure("label", foreground="#004080", font=("Consolas", 11, "bold"))
        self.detail_text.tag_configure("value", foreground="#202020")
        self.detail_text.tag_configure("email", foreground="#007700", font=("Consolas", 11, "italic"))
        self.detail_text.tag_configure("id", foreground="#aa0000")
        self.detail_text.tag_configure("bool_true", foreground="#008000")
        self.detail_text.tag_configure("bool_false", foreground="#800000")

        self.tree.bind("<<TreeviewSelect>>", self.mostrar_detalle_usuario)

        self.cargar_usuarios()

    def cargar_usuarios(self):
        try:
            self.usuarios = obtener_usuarios()
            for u in self.usuarios:
                self.tree.insert("", tk.END, values=(u.get("id"), u.get("name"), u.get("email")))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar usuarios:\n{e}")

    def mostrar_detalle_usuario(self, event):
        seleccionado = self.tree.selection()
        if not seleccionado:
            return
        item = self.tree.item(seleccionado[0])
        user_id, name, email = item["values"]

        try:
            detalle = obtener_info_usuario_por_email(email)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener detalle del usuario:\n{e}")
            return

        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)

        # Map de emojis para campos clave
        emojis = {
            "id": "🆔 ",
            "name": "👤 ",
            "lastname": "👥 ",
            "username": "🔑 ",
            "email": "📧 ",
            "other_email": "✉️ ",
            "mobile": "📱 ",
            "phone": "📞 ",
            "office": "🏢 ",
            "department": "🏷️ ",
            "position": "💼 ",
            "country": "🌎 ",
            "city": "🏙️ ",
            "is_external": "🚪 ",
            "role_name": "🎭 ",
            "is_disabled": "🚫 ",
            "is_deleted": "❌ ",
            "birthday": "🎂 ",
            "employee_number": "🆔 ",
        }

        for key, value in detalle.items():
            emoji = emojis.get(key, "• ")
            label_text = f"{emoji}{key}: "
            self.detail_text.insert(tk.END, label_text, "label")

            # Colorear booleanos de forma especial
            if isinstance(value, bool):
                tag = "bool_true" if value else "bool_false"
                val_str = "Sí" if value else "No"
                self.detail_text.insert(tk.END, val_str + "\n", tag)
            else:
                # Emails en cursiva verde
                if "email" in key and value:
                    self.detail_text.insert(tk.END, f"{value}\n", "email")
                # ID en rojo
                elif key == "id":
                    self.detail_text.insert(tk.END, f"{value}\n", "id")
                else:
                    self.detail_text.insert(tk.END, f"{value}\n", "value")

        self.detail_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = UserAdminApp(root)
    root.mainloop()
