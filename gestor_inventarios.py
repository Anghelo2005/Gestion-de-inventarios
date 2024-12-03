import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from PIL import ImageTk, Image  # Usamos Pillow para manejar imágenes de fondo

# Función para cargar los productos desde un archivo JSON
def load_data():
    if os.path.exists("productos.json"):
        with open("productos.json", "r") as file:
            data = json.load(file)  # Cargar los productos existentes
            # Eliminar productos predefinidos no deseados
            data["productos"] = [p for p in data.get("productos", []) if p["nombre"] not in ["Producto A", "Producto B"]]
            # Asegurarse de que 'transacciones' exista y que cada transacción tenga un 'id'
            if "transacciones" not in data:
                data["transacciones"] = []  # Inicializar transacciones si no existe
            # Asegurarse de que cada transacción tenga un 'id'
            for idx, transaction in enumerate(data["transacciones"]):
                if "id" not in transaction:
                    transaction["id"] = idx + 1  # Asignar un ID único si no existe
            return data
    else:
        # Si no existe el archivo, creamos uno vacío con productos predefinidos vacíos
        default_data = {
            "productos": [],
            "transacciones": []  # Lista para almacenar transacciones
        }
        with open("productos.json", "w") as file:
            json.dump(default_data, file, indent=4)
        return default_data  # Cargar los datos predeterminados

# Función para guardar los productos en el archivo JSON
def save_data(data):
    with open("productos.json", "w") as file:
        json.dump(data, file, indent=4)

# Función para generar un reporte de transacciones
def generate_report(data):
    transactions = []
    for transaction in data["transacciones"]:
        # Asegurarse de que todas las claves existen
        if "tipo" not in transaction:
            transaction["tipo"] = "desconocido"  # Si falta, asignamos un valor por defecto
        if "cantidad" not in transaction:
            transaction["cantidad"] = 0  # Si falta, asignamos una cantidad por defecto
        if "stock_final" not in transaction:
            transaction["stock_final"] = 0  # Si falta, asignamos un valor por defecto
        
        timestamp = transaction["hora"]
        producto = transaction["producto"]
        tipo = transaction["tipo"]
        cantidad = transaction["cantidad"]
        stock_final = transaction["stock_final"]
        transaction_id = transaction["id"]
        
        transactions.append(f"ID: {transaction_id} | Producto: {producto} | Tipo: {tipo} | Cantidad: {cantidad} | Stock Final: {stock_final} | Fecha: {timestamp}")
    
    return transactions

class GestorInventarios:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Inventarios")
        self.root.geometry("900x700")
        self.root.config(bg="#f4f4f9")
        self.data = load_data()  # Cargar los productos desde JSON
        self.create_widgets()

    def create_widgets(self):
        # Fondo de pantalla con canvas
        try:
            background_image = Image.open("fondo.jpg")  # Usamos la imagen para el fondo
            background_image = background_image.resize((900, 700), Image.Resampling.LANCZOS)  # Ajustamos el tamaño con LANCZOS
            background_photo = ImageTk.PhotoImage(background_image)

            # Usamos un canvas para poner la imagen
            canvas = tk.Canvas(self.root, width=900, height=700)
            canvas.place(relwidth=1, relheight=1)  # Cubre todo el fondo
            canvas.create_image(0, 0, anchor="nw", image=background_photo)
            canvas.image = background_photo  # Mantener una referencia para evitar que la imagen sea liberada
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encuentra el archivo 'fondo.jpg'. Asegúrate de que el archivo esté en la misma carpeta.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la imagen de fondo: {e}")

        # Título
        self.title_label = tk.Label(self.root, text="Gestor de Inventarios", font=("Poppins", 30, "bold"), fg="#ffffff", bg="#4a90e2")
        self.title_label.grid(row=0, column=0, columnspan=4, pady=40)

        # Botón de agregar producto con icono
        self.product_create_button = tk.Button(self.root, text="Agregar Nuevo Producto", command=self.open_add_product_window, font=("Poppins", 14), bg="#32cd32", fg="white", width=25, relief="flat", borderwidth=0, activebackground="#28a745", activeforeground="white")
        self.product_create_button.grid(row=1, column=0, columnspan=4, pady=20)

        # Lista de productos
        self.product_label = tk.Label(self.root, text="Seleccionar Producto:", font=("Poppins", 14), bg="#f4f4f9", fg="#333")
        self.product_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.product_list = ttk.Combobox(self.root, values=[prod["nombre"] for prod in self.data["productos"]], font=("Poppins", 14), width=20)
        self.product_list.grid(row=2, column=1, padx=10, pady=10)

        # Cantidad a agregar o quitar
        self.quantity_label = tk.Label(self.root, text="Cantidad:", font=("Poppins", 14), bg="#f4f4f9", fg="#333")
        self.quantity_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.quantity_entry = tk.Entry(self.root, font=("Poppins", 14), bg="#e1f5fe", relief="solid", borderwidth=1)
        self.quantity_entry.grid(row=3, column=1, padx=10, pady=10)

        # Botón para actualizar el inventario con un diseño atractivo
        self.update_button = tk.Button(self.root, text="Actualizar Inventario", command=self.update_inventory, font=("Poppins", 14), bg="#32cd32", fg="white", width=20, relief="flat", borderwidth=0, activebackground="#28a745", activeforeground="white")
        self.update_button.grid(row=4, column=0, columnspan=4, pady=20)

        # Botón para abrir el reporte de transacciones con un diseño atractivo
        self.report_button = tk.Button(self.root, text="Ver Reporte de Transacciones", command=self.open_report, font=("Poppins", 14), bg="#ff6347", fg="white", width=30, relief="flat", borderwidth=0, activebackground="#ff4500", activeforeground="white")
        self.report_button.grid(row=5, column=0, columnspan=4, pady=20)

        # Mostrar el stock en tiempo real con un diseño llamativo
        self.stock_label = tk.Label(self.root, text="Stock en Tiempo Real:", font=("Poppins", 18, "bold"), bg="#f4f4f9", fg="#333")
        self.stock_label.grid(row=6, column=0, columnspan=4, pady=20)

        # Mostrar el stock de cada producto con bordes redondeados y colores de alternancia
        self.stock_tree = ttk.Treeview(self.root, columns=("Nombre", "Cantidad", "Limite de Alerta", "Precio"), show="headings", height=5)
        self.stock_tree.grid(row=7, column=0, columnspan=4, padx=10, pady=10)

        self.stock_tree.heading("Nombre", text="Nombre")
        self.stock_tree.heading("Cantidad", text="Cantidad")
        self.stock_tree.heading("Limite de Alerta", text="Limite de Alerta")
        self.stock_tree.heading("Precio", text="Precio")
        
        # Aplicar estilos para bordes redondeados y colores de alternancia
        style = ttk.Style()
        style.configure("Treeview",
                        background="#f9f9f9",
                        fieldbackground="#f9f9f9",
                        font=("Poppins", 12),
                        rowheight=30)
        style.configure("Treeview.Heading", font=("Poppins", 14, "bold"), background="black", foreground="white")  # Fondo negro para los encabezados
        style.map("Treeview",
                  background=[('selected', '#c9daf8')])

        self.refresh_stock()

    def refresh_stock(self):
        # Limpiar la tabla de stock antes de agregar los productos actualizados
        for row in self.stock_tree.get_children():
            self.stock_tree.delete(row)

        # Insertar los productos en la tabla con bordes redondeados y colores de alternancia
        for product in self.data["productos"]:
            self.stock_tree.insert("", "end", values=(product["nombre"], product["cantidad"], product["limite_alerta"], product["precio"]))

        # Actualizar la lista de productos disponibles en el combobox
        self.product_list['values'] = [prod["nombre"] for prod in self.data["productos"]]

    def open_report(self):
        # Crear una ventana para el reporte de transacciones
        report_window = tk.Toplevel(self.root)
        report_window.title("Reporte de Transacciones")
        report_window.geometry("900x600")

        # Mostrar el historial de transacciones en un formato tabular
        report_tree = ttk.Treeview(report_window, columns=("ID", "Producto", "Tipo", "Cantidad", "Stock Final", "Fecha"), show="headings", height=20)
        report_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        report_tree.heading("ID", text="ID")
        report_tree.heading("Producto", text="Producto")
        report_tree.heading("Tipo", text="Tipo de Movimiento")
        report_tree.heading("Cantidad", text="Cantidad")
        report_tree.heading("Stock Final", text="Stock Final")
        report_tree.heading("Fecha", text="Fecha y Hora")

        # Insertar los datos de las transacciones
        for transaction in self.data["transacciones"]:
            report_tree.insert("", "end", values=(
                transaction["id"],
                transaction["producto"],
                transaction.get("tipo", "Desconocido"),
                transaction.get("cantidad", 0),
                transaction.get("stock_final", 0),
                transaction["hora"]
            ))

    def open_add_product_window(self):
        # Ventana nueva para agregar un producto
        add_product_window = tk.Toplevel(self.root)
        add_product_window.title("Agregar Nuevo Producto")
        add_product_window.geometry("400x400")

        # Campos para ingresar los datos del nuevo producto
        self.new_name_label = tk.Label(add_product_window, text="Nombre del Producto:", font=("Poppins", 14))
        self.new_name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.new_name_entry = tk.Entry(add_product_window, font=("Poppins", 14), bg="#e1f5fe", relief="solid", borderwidth=1)
        self.new_name_entry.grid(row=0, column=1, padx=10, pady=10)

        self.new_price_label = tk.Label(add_product_window, text="Precio del Producto:", font=("Poppins", 14))
        self.new_price_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.new_price_entry = tk.Entry(add_product_window, font=("Poppins", 14), bg="#e1f5fe", relief="solid", borderwidth=1)
        self.new_price_entry.grid(row=1, column=1, padx=10, pady=10)

        self.new_quantity_label = tk.Label(add_product_window, text="Cantidad del Producto:", font=("Poppins", 14))
        self.new_quantity_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.new_quantity_entry = tk.Entry(add_product_window, font=("Poppins", 14), bg="#e1f5fe", relief="solid", borderwidth=1)
        self.new_quantity_entry.grid(row=2, column=1, padx=10, pady=10)

        self.new_limit_label = tk.Label(add_product_window, text="Limite de Alerta:", font=("Poppins", 14))
        self.new_limit_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.new_limit_entry = tk.Entry(add_product_window, font=("Poppins", 14), bg="#e1f5fe", relief="solid", borderwidth=1)
        self.new_limit_entry.grid(row=3, column=1, padx=10, pady=10)

        self.add_product_button = tk.Button(add_product_window, text="Agregar Producto", command=lambda: self.add_product(add_product_window), font=("Poppins", 14), bg="#32cd32", fg="white", width=20, relief="flat", borderwidth=0)
        self.add_product_button.grid(row=4, column=0, columnspan=2, pady=20)

    def add_product(self, add_product_window):
        # Obtener los valores del formulario
        name = self.new_name_entry.get()
        price = self.new_price_entry.get()
        quantity = self.new_quantity_entry.get()
        limit = self.new_limit_entry.get()

        if not name or not price or not quantity or not limit:
            messagebox.showerror("Error", "Por favor complete todos los campos.")
            return

        try:
            price = float(price)
            quantity = int(quantity)
            limit = int(limit)
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores válidos para el precio, cantidad y límite.")
            return

        # Verificar si el producto ya existe
        for product in self.data["productos"]:
            if product["nombre"] == name:
                messagebox.showerror("Error", "El producto ya existe.")
                return

        # Agregar el nuevo producto al inventario
        new_product = {
            "id": str(len(self.data["productos"]) + 1),  # ID único
            "nombre": name,
            "precio": price,
            "cantidad": quantity,
            "limite_alerta": limit
        }
        self.data["productos"].append(new_product)

        # Registrar la transacción
        transaction = {
            "id": len(self.data["transacciones"]) + 1,  # ID único para la transacción
            "producto": name,
            "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": "adición",  # Tipo de movimiento: adición
            "cantidad": quantity,
            "stock_final": quantity  # El stock final es la cantidad inicial agregada
        }
        self.data["transacciones"].append(transaction)

        # Guardar los datos en el archivo JSON
        save_data(self.data)

        # Actualizar la interfaz y mostrar mensaje de éxito
        self.refresh_stock()
        add_product_window.destroy()  # Cerrar la ventana de agregar producto
        messagebox.showinfo("Éxito", f"Producto '{name}' agregado correctamente.")

    def update_inventory(self):
        # Obtener los valores del formulario
        product_name = self.product_list.get()
        quantity = self.quantity_entry.get()

        if not product_name or not quantity.isdigit():
            messagebox.showerror("Error", "Por favor seleccione un producto y ingrese una cantidad válida.")
            return

        quantity = int(quantity)

        # Buscar el producto en la lista de productos
        for product in self.data["productos"]:
            if product["nombre"] == product_name:
                product["cantidad"] += quantity
                break

        # Registrar la transacción de actualización
        transaction = {
            "id": len(self.data["transacciones"]) + 1,  # ID único para la transacción
            "producto": product_name,
            "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": "actualización",  # Tipo de movimiento: actualización
            "cantidad": quantity,
            "stock_final": product["cantidad"]  # El stock final es el valor actualizado
        }
        self.data["transacciones"].append(transaction)

        # Guardar los cambios en el archivo JSON
        save_data(self.data)

        # Actualizar la interfaz
        self.refresh_stock()
        messagebox.showinfo("Éxito", f"Se han actualizado {quantity} unidades de {product_name}.")

# Crear la ventana principal
root = tk.Tk()
app = GestorInventarios(root)
root.mainloop()
