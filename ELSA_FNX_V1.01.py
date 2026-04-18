# Librerías
import sys
import os
import sqlite3
from datetime import datetime, timedelta
import customtkinter
from tkinter import messagebox
import tkinter as tk 
from PIL import Image, ImageTk  


if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Rutas
ruta_tema = os.path.join(base_path, "naranja.json")
db_path = os.path.join(base_path, "fenix.db")
icono_path = os.path.join(base_path, "logo.ico")
logo_img_path = os.path.join(base_path, "LogoFenixR.png")   # logo para la esquina
fondo_img_path = os.path.join(base_path, "LogoFenixSR.jpg") # imagen de fondo

# -------------------------------------------------------
# Funciones de base de datos
# -------------------------------------------------------
def inicializar_base_datos():
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()
    # Tabla con nuevas columnas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alumnos (
        matricula INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        nombre TEXT NOT NULL,
        telefono TEXT,
        inscripcion TEXT NOT NULL,
        ultimopago TEXT NOT NULL,
        proximopago TEXT,
        fechanacimiento TEXT,
        telefono_emergencia TEXT,
        esquema_pago TEXT
    );
    """)

    # Por si ya existía una tabla vieja sin columnas nuevas, intentamos agregarlas
    nuevas_columnas = [
        ("fechanacimiento", "TEXT"),
        ("telefono_emergencia", "TEXT"),
        ("esquema_pago", "TEXT"),
    ]
    for nombre_col, tipo_col in nuevas_columnas:
        try:
            cursor.execute(f"ALTER TABLE alumnos ADD COLUMN {nombre_col} {tipo_col}")
        except sqlite3.OperationalError:
            # La columna ya existe, no pasa nada
            pass

    conexion.commit()
    conexion.close()
    print("Base de datos lista (tabla 'alumnos').")


def consultar_alumnos():
    conexion = sqlite3.connect(db_path)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM alumnos")
    filas = cursor.fetchall()
    lista = []
    for fila in filas:
        s = {
            'matricula': fila['matricula'],
            'nombre': fila['nombre'],
            'telefono': fila['telefono'],
            'inscripcion': fila['inscripcion'],
            'ultimopago': fila['ultimopago'],
            'proximopago': fila['proximopago'],
            'fechanacimiento': fila['fechanacimiento'] if 'fechanacimiento' in fila.keys() else None,
            'telefono_emergencia': fila['telefono_emergencia'] if 'telefono_emergencia' in fila.keys() else None,
            'esquema_pago': fila['esquema_pago'] if 'esquema_pago' in fila.keys() else None,
        }
        lista.append(s)
    cursor.close()
    conexion.close()
    return lista


def obtener_alumno(matricula):
    conexion = sqlite3.connect(db_path)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM alumnos WHERE matricula=?", (matricula,))
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()
    if fila:
        return {
            'matricula': fila['matricula'],
            'nombre': fila['nombre'],
            'telefono': fila['telefono'],
            'inscripcion': fila['inscripcion'],
            'ultimopago': fila['ultimopago'],
            'proximopago': fila['proximopago'],
            'fechanacimiento': fila['fechanacimiento'] if 'fechanacimiento' in fila.keys() else None,
            'telefono_emergencia': fila['telefono_emergencia'] if 'telefono_emergencia' in fila.keys() else None,
            'esquema_pago': fila['esquema_pago'] if 'esquema_pago' in fila.keys() else None,
        }
    else:
        return None

# -------------------------------------------------------
# Clase principal
# -------------------------------------------------------
class MainWindow:
    def __init__(self, parent):
        # Frame principal gris con esquinas redondeadas
        self.main_frame = customtkinter.CTkFrame(parent, fg_color="#2b2b2b", corner_radius=20)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Logo global reutilizable
        if os.path.exists(logo_img_path):
            self.logo_image = customtkinter.CTkImage(
                Image.open(logo_img_path),
                size=(200, 50)
            )
        else:
            self.logo_image = None

        self.some_kind_of_controler = 0
        self.pagina_actual = 0
        self.registros_por_pagina = 5

        self.main_gui()

    # ---------------------------------------------
    # Ventana principal de bienvenida
    # ---------------------------------------------
    def main_gui(self):
        root.title('ELectronic Storage Administrator - FNX Edition')
        self.gui_elements_remove(getattr(self, "gui_elements", []))

        # Top frame
        self.top_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_frame.pack(side="top", fill="both", expand=True)

        # Logo con imagen si existe, si no, texto
        if self.logo_image:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                image=self.logo_image,
                text=""
            )
        else:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                text="FENIX",
                font=("Arial", 20, "bold")
            )
        self.logo.pack(side="left", fill="both", expand=True)

        self.main_BotonAdmin = customtkinter.CTkButton(
            self.top_frame,
            text='Administración',
            font=("Roboto", 20)
        )
        self.main_BotonAdmin.pack(ipady=10, ipadx=10, pady=10, expand=True, side="right")
        self.main_BotonAdmin.bind('<Button-1>', self.setings_gui)

        # Label bienvenida
        self.main_label_2 = customtkinter.CTkLabel(
            self.main_frame,
            text='Bienvenido\nIngrese su matricula',
            font=("Roboto", 40)
        )
        self.main_label_2.pack(fill="both", expand=True)

        # Entry matricula
        self.main_ingresamatricula = customtkinter.CTkEntry(
            self.main_frame,
            placeholder_text='Ingrese matricula',
            font=("Arial", 30, "bold"),
            justify="center"
        )
        self.main_ingresamatricula.pack(pady=20, fill="both", expand=True)
        self.main_ingresamatricula.bind('<Return>', self.mostrar_alumno)

        # Bottom frame
        self.bottom_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)
        self.main_botonenter = customtkinter.CTkButton(
            self.bottom_frame,
            text='Entrar',
            font=("Arial", 30, "bold"),
            command=self.mostrar_alumno
        )
        self.main_botonenter.pack(ipady=30, ipadx=40, pady=10, padx=10, expand=True, side="right")
        self.main_botoncerrar = customtkinter.CTkButton(
            self.bottom_frame,
            text='Cerrar',
            font=("Arial", 30, "bold"),
            command=root.destroy
        )
        self.main_botoncerrar.pack(ipady=30, ipadx=40, pady=10, padx=10, expand=True, side="left")

        self.some_kind_of_controler = 0
        self.gui_elements = [
            self.logo,
            self.main_label_2,
            self.main_ingresamatricula,
            self.main_botonenter,
            self.main_botoncerrar,
            self.top_frame,
            self.bottom_frame,
            self.main_BotonAdmin
        ]

    # ---------------------------------------------
    # Ventana de administración
    # ---------------------------------------------
    def setings_gui(self, event=None):
        self.gui_elements_remove(getattr(self, "gui_elements", []))
        root.title('Administración')

        # Top frame
        self.top_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_frame.pack(side="top", fill="both", expand=True)

        if self.logo_image:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                image=self.logo_image,
                text=""
            )
        else:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                text="FENIX",
                font=("Arial", 20, "bold")
            )
        self.logo.pack(side="left", fill="both", expand=True)

        self.main_label_1 = customtkinter.CTkLabel(
            self.top_frame,
            text='Opciones de Administración',
            font=("Roboto", 40)
        )
        self.main_label_1.pack(side="left", padx=12, fill="both", expand=True)

        self.main_menu_button = customtkinter.CTkButton(
            self.top_frame,
            text='Inicio',
            font=("Roboto", 20)
        )
        self.main_menu_button.pack(ipady=10, ipadx=10, pady=10, expand=True, side="right")
        self.main_menu_button.bind('<Button-1>', self.back_to_main)

        # Botones de administración
        self.main_botonconsulta = customtkinter.CTkButton(
            self.main_frame, text='Consultar', text_color="black", font=("Roboto", 40),
            fg_color="cyan", hover_color="dark cyan",
            command=self.ventana_consulta_tabla
        )
        self.main_botonconsulta.pack(fill="both", expand=True, padx=100, pady=10)

        self.main_botonagregar = customtkinter.CTkButton(
            self.main_frame,
            text='Agregar',
            text_color="black",
            font=("Roboto", 40),
            fg_color="light green",
            hover_color="dark green"
        )
        self.main_botonagregar.pack(fill="both", expand=True, padx=100, pady=10)
        self.main_botonagregar.bind('<Button-1>', self.ventana_agregar)

        self.main_botonmodificar = customtkinter.CTkButton(
            self.main_frame,
            text='Modificar/Actualizar',
            text_color="black",
            font=("Roboto", 40),
            fg_color="gold",
            hover_color="#CE9846"
        )
        self.main_botonmodificar.pack(fill="both", expand=True, padx=100, pady=10)
        self.main_botonmodificar.bind('<Button-1>', self.ventana_modificar)

        self.main_botoneliminar = customtkinter.CTkButton(
            self.main_frame,
            text='Eliminar',
            text_color="black",
            font=("Roboto", 40),
            fg_color="red",
            hover_color="dark red"
        )
        self.main_botoneliminar.pack(fill="both", expand=True, padx=100, pady=10)
        self.main_botoneliminar.bind('<Button-1>', self.ventana_eliminar)

        # Bottom frame
        self.bottom_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)
        self.main_botoncerrar = customtkinter.CTkButton(
            self.bottom_frame,
            text='Cerrar',
            font=("Arial", 30, "bold"),
            command=root.destroy
        )
        self.main_botoncerrar.pack(ipady=30, ipadx=40, pady=10, expand=True)

        self.some_kind_of_controler = 1
        self.gui_elements = [
            self.main_menu_button,
            self.top_frame,
            self.bottom_frame,
            self.main_botoncerrar,
            self.logo,
            self.main_botonconsulta,
            self.main_botonagregar,
            self.main_botonmodificar,
            self.main_botoneliminar,
            self.main_label_1
        ]

    # ---------------------------------------------
    # Ventana Agregar Cliente
    # ---------------------------------------------
    def ventana_agregar(self, event=None):
        self.gui_elements_remove(getattr(self, "gui_elements", []))
        root.title('Función Agregar')

        # Top frame
        self.top_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_frame.pack(side="top", fill="both", expand=True)

        if self.logo_image:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                image=self.logo_image,
                text=""
            )
        else:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                text="FENIX",
                font=("Arial", 20, "bold")
            )
        self.logo.pack(side="left", fill="both", expand=True)

        self.main_label_1 = customtkinter.CTkLabel(
            self.top_frame,
            text='Función AGREGAR',
            font=("Roboto", 40)
        )
        self.main_label_1.pack(side="left", fill="both", expand=True)

        self.main_menu_button = customtkinter.CTkButton(
            self.top_frame,
            text='Inicio',
            font=("Roboto", 20)
        )
        self.main_menu_button.pack(ipady=10, ipadx=10, pady=10, expand=True, side="right")
        self.main_menu_button.bind('<Button-1>', self.back_to_main)

        # Labels y Entrys
        self.main_label_2 = customtkinter.CTkLabel(
            self.main_frame,
            text='Ingrese todos los datos correspondientes',
            font=("Roboto", 40)
        )
        self.main_label_2.pack(fill="both", expand=True)

        self.main_nombrellenar = customtkinter.CTkEntry(
            self.main_frame,
            placeholder_text='Nombre',
            font=("Roboto", 40)
        )
        self.main_nombrellenar.pack(fill="both", expand=True)

        self.main_telefono = customtkinter.CTkEntry(
            self.main_frame,
            placeholder_text='Teléfono',
            font=("Roboto", 40)
        )
        self.main_telefono.pack(fill="both", expand=True)

        self.main_fechanac = customtkinter.CTkEntry(
            self.main_frame,
            placeholder_text='Fecha de nacimiento AAAA/MM/DD',
            font=("Roboto", 40)
        )
        self.main_fechanac.pack(fill="both", expand=True)

        self.main_tel_emerg = customtkinter.CTkEntry(
            self.main_frame,
            placeholder_text='Teléfono de emergencia',
            font=("Roboto", 40)
        )
        self.main_tel_emerg.pack(fill="both", expand=True)

        self.main_esquema_label = customtkinter.CTkLabel(
            self.main_frame,
            text='Esquema de pago',
            font=("Roboto", 30)
        )
        self.main_esquema_label.pack(pady=(10,0))

        self.main_esquema = customtkinter.CTkOptionMenu(
            self.main_frame,
            values=["Semanal", "Quincenal", "Mensual"],
            dropdown_fg_color="dark orange",
            dropdown_text_color="black",
            fg_color="dark orange",
            button_color="dark orange",
            text_color="black"
        )
        self.main_esquema.set("Mensual")
        self.main_esquema.pack(fill="both", expand=True, pady=(0,10))

        self.main_inscripcionllenar = customtkinter.CTkEntry(
            self.main_frame,
            placeholder_text='Fecha de inscripción AAAA/MM/DD',
            font=("Roboto", 40)
        )
        self.main_inscripcionllenar.pack(fill="both", expand=True)

        # Bottom frame
        self.bottom_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)

        self.main_botonenter = customtkinter.CTkButton(
            self.bottom_frame,
            text='Agregar',
            font=("Arial", 30, "bold"),
            command=self.agregar_alumno_interfaz
        )
        self.main_botonenter.pack(ipady=30, ipadx=40, pady=10, expand=True, side="right")

        self.main_botoncerrar = customtkinter.CTkButton(
            self.bottom_frame,
            text='Volver a opciones',
            font=("Arial", 30, "bold")
        )
        self.main_botoncerrar.pack(ipady=30, ipadx=40, pady=10, side="left", expand=True)
        self.main_botoncerrar.bind('<Button-1>', self.setings_gui)

        self.some_kind_of_controler = 2
        self.gui_elements = [
            self.main_menu_button,
            self.top_frame,
            self.bottom_frame,
            self.logo,
            self.main_nombrellenar,
            self.main_telefono,
            self.main_fechanac,
            self.main_tel_emerg,
            self.main_esquema_label,
            self.main_esquema,
            self.main_inscripcionllenar,
            self.main_label_2,
            self.main_label_1
        ]

    # ---------------------------------------------
    # Registrar Cliente desde interfaz
    # ---------------------------------------------
    def agregar_alumno_interfaz(self):
        nombre = self.main_nombrellenar.get().strip()
        telefono = self.main_telefono.get().strip()
        fechanac = self.main_fechanac.get().strip()
        tel_emerg = self.main_tel_emerg.get().strip()
        esquema = self.main_esquema.get()
        inscripcion = self.main_inscripcionllenar.get().strip()

        if not nombre or not inscripcion:
            messagebox.showerror("Error", "Nombre e inscripción son obligatorios")
            return

        # Validar fecha de inscripción
        try:
            fecha_ins = datetime.strptime(inscripcion, "%Y/%m/%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha de inscripción incorrecto. Use AAAA/MM/DD")
            return

        # Validar fecha de nacimiento si se ingresó
        if fechanac:
            try:
                datetime.strptime(fechanac, "%Y/%m/%d")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha de nacimiento incorrecto. Use AAAA/MM/DD")
                return

        # Calcular próximo pago según esquema
        if esquema == "Semanal":
            dias = 7
        elif esquema == "Quincenal":
            dias = 15
        else:
            dias = 30
        ultimopago = inscripcion
        proximopago = (fecha_ins + timedelta(days=dias)).strftime("%Y/%m/%d")
        
        # Obtenemos matrícula libre
        matricula_libre = self.obtener_matricula_libre()

        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO alumnos (
                matricula,
                nombre,
                telefono,
                inscripcion,
                ultimopago,
                proximopago,
                fechanacimiento,
                telefono_emergencia,
                esquema_pago
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (matricula_libre, nombre, telefono, inscripcion, ultimopago, proximopago,
              fechanac if fechanac else None,
              tel_emerg if tel_emerg else None,
              esquema))
        conexion.commit()
        conexion.close()

        messagebox.showinfo("Cliente registrado", f"Cliente registrado con matrícula {matricula_libre:04d}")

        self.main_nombrellenar.delete(0, "end")
        self.main_telefono.delete(0, "end")
        self.main_fechanac.delete(0, "end")
        self.main_tel_emerg.delete(0, "end")
        self.main_inscripcionllenar.delete(0, "end")
        self.main_esquema.set("Mensual")

    # ---------------------------------------------
    # Mostrar tabla paginada
    # ---------------------------------------------
    def ventana_consulta_tabla(self):
        self.gui_elements_remove(getattr(self, "gui_elements", []))
        root.title('Función Consulta')

        # Top frame
        self.top_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_frame.pack(side="top", fill="both", expand=True)

        if self.logo_image:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                image=self.logo_image,
                text="",
            )
        else:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                text="FENIX",
                font=("Arial", 20, "bold")
            )
        self.logo.pack(side="left", fill="both", expand=True)

        self.main_label_1 = customtkinter.CTkLabel(
            self.top_frame,
            text='Consulta de Clientes',
            font=("Roboto", 40)
        )
        self.main_label_1.pack(side="left", fill="both", expand=True)

        # Bottom frame
        self.bottom_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)

        self.main_boton_volver = customtkinter.CTkButton(
            self.bottom_frame,
            text='Volver a Administración',
            font=("Arial", 30, "bold")
        )
        self.main_boton_volver.pack(ipady=30, ipadx=40, pady=10)
        self.main_boton_volver.bind('<Button-1>', self.setings_gui)

        # Frame de tabla
        self.frame_tabla = customtkinter.CTkFrame(self.main_frame)
        self.frame_tabla.pack(fill="both", expand=True, padx=50, pady=20)

        self.pagina_actual = 0
        self.mostrar_tabla_paginada_consulta()

    # ---------------------------------------------
    # Función paginación en interfaz de consulta
    # ---------------------------------------------
    def mostrar_tabla_paginada_consulta(self):
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()

        alumnos = consultar_alumnos()
        total = len(alumnos)
        inicio = self.pagina_actual * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        pagina = alumnos[inicio:fin]

        encabezados = [
            "Matrícula", "Nombre", "Teléfono", "Inscripción",
            "Último Pago", "Próximo Pago", "Nacimiento",
            "Tel. Emergencia", "Esquema Pago"
        ]
        for col, texto in enumerate(encabezados):
            lbl = customtkinter.CTkLabel(self.frame_tabla, text=texto, font=("Roboto", 20, "bold"))
            lbl.grid(row=0, column=col, padx=5, pady=5)

        for fila_idx, alumno in enumerate(pagina, start=1):
            valores = [
                f"{alumno['matricula']:04d}",
                alumno['nombre'],
                alumno['telefono'] or "",
                alumno['inscripcion'],
                alumno['ultimopago'],
                alumno['proximopago'],
                alumno['fechanacimiento'] or "",
                alumno['telefono_emergencia'] or "",
                alumno['esquema_pago'] or "",
            ]
            for col_idx, val in enumerate(valores):
                lbl = customtkinter.CTkLabel(self.frame_tabla, text=val, font=("Roboto", 18))
                lbl.grid(row=fila_idx, column=col_idx, padx=5, pady=5)

        self.btn_anterior = customtkinter.CTkButton(self.frame_tabla, text="Anterior", command=self.pagina_anterior_consulta)
        self.btn_anterior.grid(row=self.registros_por_pagina+1, column=0, pady=10)
        self.btn_siguiente = customtkinter.CTkButton(self.frame_tabla, text="Siguiente", command=self.pagina_siguiente_consulta)
        self.btn_siguiente.grid(row=self.registros_por_pagina+1, column=len(encabezados)-1, pady=10)

        self.btn_anterior.configure(state="normal" if self.pagina_actual > 0 else "disabled")
        self.btn_siguiente.configure(state="normal" if fin < total else "disabled")

        self.gui_elements = [
            self.top_frame,
            self.bottom_frame,
            self.frame_tabla,
            self.logo,
            self.main_label_1,
            self.main_boton_volver
        ]

    def pagina_siguiente_consulta(self):
        self.pagina_actual += 1
        self.mostrar_tabla_paginada_consulta()

    def pagina_anterior_consulta(self):
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
            self.mostrar_tabla_paginada_consulta()

    # ---------------------------------------------
    # Mostrar datos de un Cliente por matrícula (con confirmación)
    # ---------------------------------------------
    def mostrar_alumno(self, event=None):
        matricula_str = self.main_ingresamatricula.get()
        if not matricula_str.isdigit():
            messagebox.showerror("Error", "Matrícula inválida")
            return

        matricula = int(matricula_str)
        alumno = obtener_alumno(matricula)
        if not alumno:
            messagebox.showerror("Error", "No se encontró Cliente con esa matrícula")
            return

        # 🔹 Pestaña de confirmación
        confirma = messagebox.askyesno(
            "Confirmar cliente",
            f"¿Eres el cliente:\n\n{alumno['nombre']}\n\n(Matrícula {matricula:04d})?"
        )
        if not confirma:
            # Si no es, limpiamos el campo y no mostramos nada
            self.main_ingresamatricula.delete(0, "end")
            return

        # Limpiar pantalla
        self.gui_elements_remove(getattr(self, "gui_elements", []))
        root.title(f"Cliente {matricula:04d}")

        # Top frame
        self.top_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_frame.pack(side="top", fill="both", expand=True)

        if self.logo_image:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                image=self.logo_image,
                text=""
            )
        else:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                text="FENIX",
                font=("Arial", 20, "bold")
            )
        self.logo.pack(side="left", fill="both", expand=True)

        self.main_label_1 = customtkinter.CTkLabel(
            self.top_frame,
            text=f"Datos Cliente {matricula:04d}",
            font=("Roboto", 40),
            padx=10
        )
        self.main_label_1.pack(side="left", fill="both", expand=True)

        self.main_menu_button = customtkinter.CTkButton(
            self.top_frame,
            text='Volver',
            font=("Roboto", 20)
        )
        self.main_menu_button.pack(ipady=10, ipadx=10, pady=10, expand=True, side="right")
        self.main_menu_button.bind('<Button-1>', self.back_to_main)

        # Frame con datos
        self.data_frame = customtkinter.CTkFrame(self.main_frame)
        self.data_frame.pack(fill="both", expand=True, padx=50, pady=50)

        etiquetas = [
            "Matrícula", "Nombre", "Teléfono", "Nacimiento",
            "Tel. Emergencia", "Inscripción", "Esquema Pago",
            "Último Pago", "Próximo Pago",
        ]
        valores = [
            f"{alumno['matricula']:04d}",
            alumno['nombre'],
            alumno['telefono'] or "",
            alumno['fechanacimiento'] or "",
            alumno['telefono_emergencia'] or "",
            alumno['inscripcion'],
            alumno['esquema_pago'] or "",
            alumno['ultimopago'],
            alumno['proximopago'],
        ]

        for idx, (etq, val) in enumerate(zip(etiquetas, valores)):
            lbl_etq = customtkinter.CTkLabel(self.data_frame, text=f"{etq}:", font=("Roboto", 30, "bold"))
            lbl_val = customtkinter.CTkLabel(self.data_frame, text=val, font=("Roboto", 30))
            lbl_etq.grid(row=idx, column=0, sticky="e", padx=10, pady=10)
            lbl_val.grid(row=idx, column=1, sticky="w", padx=10, pady=10)

        self.some_kind_of_controler = 3
        self.gui_elements = [
            self.logo,
            self.main_label_1,
            self.main_menu_button,
            self.data_frame,
            self.top_frame
        ]

    # ---------------------------------------------
    # Modificar Cliente
    # ---------------------------------------------
    def ventana_modificar(self, event=None):
        self.gui_elements_remove(getattr(self, "gui_elements", []))
        root.title('Funcion Modificar')

        # Top frame
        self.top_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_frame.pack(side="top", fill="both", expand=True)

        if self.logo_image:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                image=self.logo_image,
                text=""
            )
        else:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                text="FENIX",
                font=("Arial", 20, "bold")
            )
        self.logo.pack(side="left", fill="both", expand=True)

        self.main_label_1 = customtkinter.CTkLabel(
            self.top_frame,
            text='Modificar Cliente',
            font=("Roboto", 40),
            padx=10
        )
        self.main_label_1.pack(side="left", fill="both", expand=True)

        self.main_menu_button = customtkinter.CTkButton(
            self.top_frame,
            text='Inicio',
            font=("Roboto", 20)
        )
        self.main_menu_button.pack(ipady=10, ipadx=10, pady=10, expand=True, side="right")
        self.main_menu_button.bind('<Button-1>', self.setings_gui)

        self.main_label_2 = customtkinter.CTkLabel(
            self.main_frame,
            text='Ingrese la matrícula del Cliente a modificar',
            font=("Roboto", 30)
        )
        self.main_label_2.pack(fill="both", expand=True)

        self.main_matricula_mod = customtkinter.CTkEntry(
            self.main_frame,
            placeholder_text='Matrícula',
            font=("Roboto", 30)
        )
        self.main_matricula_mod.pack(fill="both", expand=True)
        self.main_matricula_mod.bind('<Return>', self.cargar_datos_modificar)

        self.btn_cargar = customtkinter.CTkButton(
            self.main_frame,
            text='Cargar datos',
            font=("Roboto", 25),
            command=self.cargar_datos_modificar
        )
        self.btn_cargar.pack(pady=10)

        # Frame que contendrá los campos en 2 columnas (usaremos grid aquí)
        self.frame_datos = customtkinter.CTkFrame(self.main_frame)
        self.frame_datos.pack(fill="both", expand=True, padx=50, pady=20)

        # Muy importante: que las 2 columnas se expandan
        self.frame_datos.grid_columnconfigure(0, weight=1)
        self.frame_datos.grid_columnconfigure(1, weight=1)

        self.bottom_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)
        self.main_botoncerrar = customtkinter.CTkButton(
            self.bottom_frame,
            text='Volver a opciones',
            font=("Arial", 30, "bold")
        )
        self.main_botoncerrar.pack(ipady=30, ipadx=40, pady=10)
        self.main_botoncerrar.bind('<Button-1>', self.setings_gui)

        self.gui_elements = [
            self.main_menu_button,
            self.top_frame,
            self.main_label_1,
            self.main_label_2,
            self.main_matricula_mod,
            self.btn_cargar,
            self.frame_datos,
            self.bottom_frame,
            self.main_botoncerrar
        ]


    def cargar_datos_modificar(self, event=None):
        matricula = self.main_matricula_mod.get()
        if not matricula.isdigit():
            messagebox.showerror("Error", "Matrícula inválida")
            return

        conexion = sqlite3.connect(db_path)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM alumnos WHERE matricula=?", (matricula,))
        alumno = cursor.fetchone()
        conexion.close()

        if not alumno:
            messagebox.showerror("Error", "Cliente no encontrado")
            return

        # Limpiar frame_datos
        for widget in self.frame_datos.winfo_children():
            widget.destroy()

        # Asegurar pesos de columnas
        self.frame_datos.grid_columnconfigure(0, weight=1)
        self.frame_datos.grid_columnconfigure(1, weight=1)

        # ---------- Columna izquierda / derecha en filas ----------

        # Fila 0-1: Nombre / Teléfono
        self.main_label_nombre = customtkinter.CTkLabel(self.frame_datos, text="Nombre", font=("Roboto", 25))
        self.main_label_nombre.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))

        self.entry_nombre = customtkinter.CTkEntry(self.frame_datos, font=("Roboto", 25))
        self.entry_nombre.insert(0, alumno['nombre'])
        self.entry_nombre.grid(row=1, column=0, sticky="we", padx=10, pady=(0, 10))

        self.main_label_telefono = customtkinter.CTkLabel(self.frame_datos, text="Teléfono", font=("Roboto", 25))
        self.main_label_telefono.grid(row=0, column=1, sticky="w", padx=10, pady=(10, 0))

        self.entry_telefono = customtkinter.CTkEntry(self.frame_datos, font=("Roboto", 25))
        self.entry_telefono.insert(0, alumno['telefono'] or "")
        self.entry_telefono.grid(row=1, column=1, sticky="we", padx=10, pady=(0, 10))

        # Fila 2-3: Fecha nacimiento / Tel. emergencia
        self.main_label_fechanac = customtkinter.CTkLabel(
            self.frame_datos,
            text="Fecha de nacimiento (AAAA/MM/DD)",
            font=("Roboto", 25)
        )
        self.main_label_fechanac.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))

        self.entry_fechanac = customtkinter.CTkEntry(self.frame_datos, font=("Roboto", 25))
        self.entry_fechanac.insert(0, alumno['fechanacimiento'] or "")
        self.entry_fechanac.grid(row=3, column=0, sticky="we", padx=10, pady=(0, 10))

        self.main_label_tel_emerg = customtkinter.CTkLabel(
            self.frame_datos,
            text="Teléfono de emergencia",
            font=("Roboto", 25)
        )
        self.main_label_tel_emerg.grid(row=2, column=1, sticky="w", padx=10, pady=(10, 0))

        self.entry_tel_emerg = customtkinter.CTkEntry(self.frame_datos, font=("Roboto", 25))
        self.entry_tel_emerg.insert(0, alumno['telefono_emergencia'] or "")
        self.entry_tel_emerg.grid(row=3, column=1, sticky="we", padx=10, pady=(0, 10))

        # Fila 4-5: Inscripción / Esquema de pago
        self.main_label_inscripcion = customtkinter.CTkLabel(
            self.frame_datos,
            text="Fecha de Inscripción",
            font=("Roboto", 25)
        )
        self.main_label_inscripcion.grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))

        self.entry_inscripcion = customtkinter.CTkEntry(self.frame_datos, font=("Roboto", 25))
        self.entry_inscripcion.insert(0, alumno['inscripcion'])
        self.entry_inscripcion.grid(row=5, column=0, sticky="we", padx=10, pady=(0, 10))

        self.main_label_esquema = customtkinter.CTkLabel(
            self.frame_datos,
            text="Esquema de pago",
            font=("Roboto", 25)
        )
        self.main_label_esquema.grid(row=4, column=1, sticky="w", padx=10, pady=(10, 0))

        self.menu_esquema = customtkinter.CTkOptionMenu(
            self.frame_datos,
            values=["Semanal", "Quincenal", "Mensual"],
            dropdown_fg_color="dark orange",
            dropdown_text_color="black",
            fg_color="dark orange",
            button_color="dark orange",
            text_color="black"
        )
        esquema_actual = alumno['esquema_pago'] if alumno['esquema_pago'] else "Mensual"
        self.menu_esquema.set(esquema_actual)
        self.menu_esquema.grid(row=5, column=1, sticky="we", padx=10, pady=(0, 10))

        # Fila 6-7: Último pago / Próximo pago
        self.main_label_ultimopago = customtkinter.CTkLabel(
            self.frame_datos,
            text="Fecha de Último pago realizado",
            font=("Roboto", 25)
        )
        self.main_label_ultimopago.grid(row=6, column=0, sticky="w", padx=10, pady=(10, 0))

        self.entry_ultimopago = customtkinter.CTkEntry(self.frame_datos, font=("Roboto", 25))
        self.entry_ultimopago.insert(0, alumno['ultimopago'])
        self.entry_ultimopago.grid(row=7, column=0, sticky="we", padx=10, pady=(0, 10))

        self.main_label_proximopago = customtkinter.CTkLabel(
            self.frame_datos,
            text="Fecha de Próximo pago",
            font=("Roboto", 25)
        )
        self.main_label_proximopago.grid(row=6, column=1, sticky="w", padx=10, pady=(10, 0))

        self.entry_proximopago = customtkinter.CTkEntry(self.frame_datos, font=("Roboto", 25))
        self.entry_proximopago.insert(0, alumno['proximopago'])
        self.entry_proximopago.grid(row=7, column=1, sticky="we", padx=10, pady=(0, 10))

        # Fila 8: Botón guardar (ocupa ambas columnas)
        self.btn_guardar = customtkinter.CTkButton(
            self.frame_datos,
            text="Guardar cambios",
            font=("Roboto", 25),
            command=lambda: self.guardar_cambios(matricula)
        )
        self.btn_guardar.grid(row=8, column=0, columnspan=2, pady=20, padx=10, sticky="e")


    def guardar_cambios(self, matricula):
        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        fechanac = self.entry_fechanac.get().strip()
        tel_emerg = self.entry_tel_emerg.get().strip()
        ultimopago = self.entry_ultimopago.get().strip()
        proximopago = self.entry_proximopago.get().strip()
        esquema = self.menu_esquema.get()

        # Validar formato de fechas si vienen
        if fechanac:
            try:
                datetime.strptime(fechanac, "%Y/%m/%d")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha de nacimiento incorrecto. Use AAAA/MM/DD")
                return
        if ultimopago:
            try:
                datetime.strptime(ultimopago, "%Y/%m/%d")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha de último pago incorrecto. Use AAAA/MM/DD")
                return
        if proximopago:
            try:
                datetime.strptime(proximopago, "%Y/%m/%d")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha de próximo pago incorrecto. Use AAAA/MM/DD")
                return

        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE alumnos
            SET nombre=?,
                telefono=?,
                ultimopago=?,
                proximopago=?,
                fechanacimiento=?,
                telefono_emergencia=?,
                esquema_pago=?
            WHERE matricula=?
        """, (nombre,
              telefono,
              ultimopago,
              proximopago,
              fechanac if fechanac else None,
              tel_emerg if tel_emerg else None,
              esquema,
              matricula))
        conexion.commit()
        conexion.close()
        messagebox.showinfo("Actualizado", f"Cliente {matricula} actualizado correctamente")

    # ---------------------------------------------
    # Ventana Eliminar Cliente
    # ---------------------------------------------
    def ventana_eliminar(self, event=None):
        self.gui_elements_remove(getattr(self, "gui_elements", []))
        root.title('Función Eliminar')

        # Top frame
        self.top_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_frame.pack(side="top", fill="both", expand=True)

        if self.logo_image:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                image=self.logo_image,
                text=""
            )
        else:
            self.logo = customtkinter.CTkLabel(
                self.top_frame,
                text="FENIX",
                font=("Arial", 20, "bold")
            )
        self.logo.pack(side="left", fill="both", expand=True)

        self.main_label_1 = customtkinter.CTkLabel(
            self.top_frame,
            text='Eliminar Cliente',
            font=("Roboto", 40),
            padx=10
        )
        self.main_label_1.pack(side="left", fill="both", expand=True)

        self.main_menu_button = customtkinter.CTkButton(
            self.top_frame,
            text='Inicio',
            font=("Roboto", 20)
        )
        self.main_menu_button.pack(ipady=10, ipadx=10, pady=10, expand=True, side="right")
        self.main_menu_button.bind('<Button-1>', self.setings_gui)

        # Ingreso de matrícula
        self.main_label_2 = customtkinter.CTkLabel(
            self.main_frame,
            text='Ingrese la matrícula del Cliente a eliminar',
            font=("Roboto", 30)
        )
        self.main_label_2.pack(fill="both", expand=True)

        self.main_matricula_del = customtkinter.CTkEntry(
            self.main_frame,
            placeholder_text='Matrícula',
            font=("Roboto", 30)
        )
        self.main_matricula_del.pack(fill="both", expand=True)
        self.main_matricula_del.bind('<Return>', self.eliminar_alumno)
        
        self.btn_eliminar = customtkinter.CTkButton(
            self.main_frame,
            text='Eliminar Cliente',
            font=("Roboto", 25),
            fg_color="red",
            hover_color="dark red",
            command=self.eliminar_alumno
        )
        self.btn_eliminar.pack(pady=20)

        # Bottom frame
        self.bottom_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)

        self.main_botoncerrar = customtkinter.CTkButton(
            self.bottom_frame,
            text='Volver a Administración',
            font=("Arial", 30, "bold")
        )
        self.main_botoncerrar.pack(ipady=30, ipadx=40, pady=10)
        self.main_botoncerrar.bind('<Button-1>', self.setings_gui)

        self.gui_elements = [
            self.top_frame, self.logo, self.main_label_1, self.main_menu_button,
            self.main_label_2, self.main_matricula_del, self.btn_eliminar,
            self.bottom_frame, self.main_botoncerrar
        ]

    def eliminar_alumno(self, event=None):
        matricula_str = self.main_matricula_del.get()
        if not matricula_str.isdigit():
            messagebox.showerror("Error", "Matrícula inválida")
            return
        matricula = int(matricula_str)

        alumno = obtener_alumno(matricula)
        if not alumno:
            messagebox.showerror("Error", "Cliente no encontrado")
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que desea eliminar al alumno {alumno['nombre']} (Matrícula {matricula:04d})?"
        )
        if not confirm:
            return

        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM alumnos WHERE matricula=?", (matricula,))
        conexion.commit()
        conexion.close()

        messagebox.showinfo("Eliminado", f"Cliente {alumno['nombre']} eliminado correctamente")
        self.setings_gui()

    # ---------------------------------------------
    # Funciones auxiliares
    # ---------------------------------------------
    def back_to_main(self, event=None):
        self.gui_elements_remove(getattr(self, "gui_elements", []))
        self.main_gui()

    def gui_elements_remove(self, elements):
        for element in elements:
            try:
                element.destroy()
            except:
                pass

    def obtener_matricula_libre(self):
        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()
        cursor.execute("SELECT matricula FROM alumnos ORDER BY matricula ASC")
        filas = cursor.fetchall()
        conexion.close()

        matricula = 1
        for fila in filas:
            if fila[0] != matricula:
                return matricula  # hueco encontrado
            matricula += 1
        return matricula  # si no hay huecos, retorna el siguiente disponible

# -------------------------------------------------------
# Loop principal con CANVAS como fondo
# -------------------------------------------------------
def main():
    global root
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme(ruta_tema)

    root = customtkinter.CTk()
    root.geometry('1920x1080')

    if os.path.exists(icono_path):
        try:
            root.iconbitmap(icono_path)
        except Exception:
            pass

    # Canvas que cubre toda la ventana
    canvas = tk.Canvas(
        root,
        highlightthickness=0,
        borderwidth=0,
        bg="#212121"   # color oscuro en vez de blanco
    )
    canvas.pack(fill="both", expand=True)

    # Cargar imagen de fondo con PIL + ImageTk
    if os.path.exists(fondo_img_path):
        img_fondo = Image.open(fondo_img_path).resize((1920, 1080))
        root.bg_image = ImageTk.PhotoImage(img_fondo)  # guardamos en root para que no se libere
        canvas.create_image(0, 0, anchor="nw", image=root.bg_image)

    # Contenedor sobre el canvas
    contenedor = customtkinter.CTkFrame(canvas, fg_color="transparent")
    canvas.create_window(960, 540, window=contenedor, anchor="center")
    window = MainWindow(contenedor)

    root.mainloop()

if __name__ == '__main__':
    inicializar_base_datos()
    main()
