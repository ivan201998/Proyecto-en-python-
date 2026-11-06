# Simulador de asignación de espacio en disco (asignación indexada)
# Cada archivo tiene un Inodo que guarda la lista de bloques donde están sus datos.
#
# Mejoras respecto de la versión anterior:
#   - Mapa del disco que muestra qué archivo ocupa cada bloque
#   - Tramos: permite ver si un archivo quedó partido en el disco
#   - Desfragmentación, comparando el antes y el después
#   - Formateo del disco y demo guiada para presentar el caso del taller
#   - Correcciones: entradas raras o discos enormes ya no cierran el programa,
#     y crear_archivo rechaza nombres vacíos y tamaños de 0 o negativos
#   - Interfaz gráfica con tkinter
#
# Cómo ejecutarlo:
#   python simulador_disco.py             -> abre la interfaz gráfica
#   python simulador_disco.py --consola   -> usa el menú de consola de siempre

import contextlib
import io
import string
import sys

# En algunos Linux tkinter viene aparte. Si falta, el menú de consola sigue funcionando.
try:
    import tkinter as tk
    from tkinter import messagebox, ttk
    TKINTER_DISPONIBLE = True
except ImportError:
    TKINTER_DISPONIBLE = False

    class _SinTkinter:
        """Reemplazo mínimo para que el archivo cargue aunque falte tkinter."""
        Frame = object
        Toplevel = object

    tk = ttk = _SinTkinter

SIMBOLOS = string.ascii_uppercase + string.digits + string.ascii_lowercase
BLOQUES_POR_FILA = 16       # cuántos bloques se dibujan en cada fila del mapa
MAX_BLOQUES_DISCO = 1024    # tamaño máximo permitido para el disco


class Inodo:
    """Representa un archivo: guarda su nombre, su tamaño y en qué bloques está."""

    def __init__(self, nombre, tam_bloques, simbolo):
        self.nombre = nombre                # nombre del archivo
        self.tam_bloques = tam_bloques      # cuántos bloques ocupa
        self.simbolo = simbolo              # carácter que lo identifica en el mapa
        self.bloques_asignados = []         # Lista de índices de bloques en disco (los "punteros")

    def contar_tramos(self):
        """Cuenta los grupos de bloques consecutivos. 1 tramo = archivo contiguo."""
        if not self.bloques_asignados:
            return 0
        tramos = 1
        for i in range(1, len(self.bloques_asignados)):
            # Si el bloque no sigue al anterior, hay un salto: empieza otro tramo
            if self.bloques_asignados[i] != self.bloques_asignados[i - 1] + 1:
                tramos += 1
        return tramos


class SimuladorDisco:
    """Representa el disco: una lista de bloques y una tabla con los inodos."""

    def __init__(self, total_bloques=64):
        self.total_bloques = total_bloques      # capacidad del disco en bloques
        # None indica bloque libre, de lo contrario guarda el nombre del archivo
        self.bloques = [None] * total_bloques   # al inicio, todo el disco está libre
        self.tabla_inodos = {}                  # nombre del archivo -> su Inodo
        self.simbolos_entregados = 0            # evita repetir el símbolo de un archivo borrado

    def _siguiente_simbolo(self):
        """Devuelve un símbolo sin usar. Si todos están en uso, devuelve '#'."""
        usados = [inodo.simbolo for inodo in self.tabla_inodos.values()]
        for _ in SIMBOLOS:
            simbolo = SIMBOLOS[self.simbolos_entregados % len(SIMBOLOS)]
            self.simbolos_entregados += 1
            if simbolo not in usados:
                return simbolo
        return "#"

    def crear_archivo(self, nombre, tam_bloques):
        """Crea un archivo y le asigna bloques libres. Devuelve True si pudo, False si hubo error."""
        # 1. Validar los datos de entrada
        if nombre == "":
            print("Error: el nombre no puede estar vacío.")
            return False
        if nombre in self.tabla_inodos:
            print(f"Error: El archivo '{nombre}' ya existe.")
            return False
        if tam_bloques <= 0:
            print("Error: el tamaño debe ser de al menos 1 bloque.")
            return False

        # 2. Buscar bloques libres (los que valen None), estén donde estén
        bloques_libres = [i for i, b in enumerate(self.bloques) if b is None]
        # Si hay menos libres que los pedidos, no se puede crear
        if len(bloques_libres) < tam_bloques:
            print(f"Error: Espacio insuficiente. Pediste {tam_bloques} bloques "
                  f"y hay {len(bloques_libres)} libres.")
            return False

        # 3. Asignación indexada (toma los primeros libres disponibles)
        nuevo_inodo = Inodo(nombre, tam_bloques, self._siguiente_simbolo())
        for i in range(tam_bloques):
            idx = bloques_libres[i]                       # número de bloque elegido
            self.bloques[idx] = nombre                    # marcar el bloque como ocupado por este archivo
            nuevo_inodo.bloques_asignados.append(idx)     # el inodo recuerda ese bloque

        # Guardar el inodo en la tabla para poder encontrar el archivo después
        self.tabla_inodos[nombre] = nuevo_inodo
        print(f"Archivo '{nombre}' creado con éxito. Bloques asignados: {nuevo_inodo.bloques_asignados}")
        return True

    def eliminar_archivo(self, nombre):
        """Elimina un archivo y libera sus bloques. Devuelve True si pudo, False si hubo error."""
        # Si el archivo no existe, avisar
        if nombre not in self.tabla_inodos:
            print(f"Error: Archivo '{nombre}' no encontrado.")
            return False

        # El inodo ya sabe qué bloques usa: se liberan solo esos (no se recorre todo el disco)
        inodo = self.tabla_inodos[nombre]
        for idx in inodo.bloques_asignados:
            self.bloques[idx] = None        # None = bloque libre otra vez

        del self.tabla_inodos[nombre]       # borrar el inodo de la tabla
        print(f"Archivo '{nombre}' eliminado correctamente.")
        return True

    def mostrar_mapa(self):
        """Dibuja el disco: cada archivo con su símbolo y '.' para los bloques libres."""
        print("\nMapa del disco ('.' = libre):")
        for inicio in range(0, self.total_bloques, BLOQUES_POR_FILA):
            fila = self.bloques[inicio:inicio + BLOQUES_POR_FILA]
            celdas = ["." if b is None else self.tabla_inodos[b].simbolo for b in fila]
            print(f"  {inicio:>4} | {' '.join(celdas)}")

        if self.tabla_inodos:
            referencias = [f"{i.simbolo} = {i.nombre}" for i in self.tabla_inodos.values()]
            print("  Referencias:", ", ".join(referencias))

    def listar_archivos(self):
        """Muestra cada archivo con los bloques que tiene asignados (su inodo)."""
        if not self.tabla_inodos:
            print("No hay archivos en el disco.")
            return
        print("\n--- Archivos (tabla de inodos) ---")
        for nombre, inodo in self.tabla_inodos.items():
            print(f"[{inodo.simbolo}] {nombre}: {inodo.tam_bloques} bloques, "
                  f"{inodo.contar_tramos()} tramo(s) -> {inodo.bloques_asignados}")

    # ---------------- Desafío 1: métricas ----------------
    def calcular_metricas(self):
        """Muestra total, ocupados, libres, porcentaje de ocupación y archivos dispersos."""
        total = self.total_bloques
        libres = self.bloques.count(None)   # posiciones iguales a None
        ocupados = total - libres           # el resto de las posiciones están ocupadas
        ocupacion = ocupados / total * 100  # Ocupación (%) = ocupados / total x 100

        print("\n--- Métricas del disco ---")
        print(f"Total de bloques   : {total}")
        print(f"Bloques ocupados   : {ocupados}")
        print(f"Bloques libres     : {libres}")
        print(f"Ocupación del disco: {ocupacion:.1f}%")
        print(f"Archivos dispersos : {self.contar_dispersos()} de {len(self.tabla_inodos)}")

    def contar_dispersos(self):
        """Devuelve cuántos archivos están partidos en más de un tramo."""
        dispersos = 0
        for inodo in self.tabla_inodos.values():
            if inodo.contar_tramos() > 1:
                dispersos += 1
        return dispersos

    # ---------------- Desafío 2: fragmentación externa ----------------
    def mayor_hueco(self):
        """Devuelve la secuencia consecutiva más larga de bloques libres."""
        mayor_hueco = 0       # el hueco más grande encontrado hasta ahora
        hueco_actual = 0      # largo del hueco que se está recorriendo
        for b in self.bloques:
            if b is None:
                hueco_actual += 1                   # el hueco sigue creciendo
                if hueco_actual > mayor_hueco:
                    mayor_hueco = hueco_actual      # nuevo récord
            else:
                hueco_actual = 0                    # un bloque ocupado corta el hueco
        return mayor_hueco

    def calcular_fragmentacion(self):
        """Fragmentación Externa (%) = (1 - mayor hueco / bloques libres) x 100.

        0% = todo el espacio libre junto; cerca de 100% = libre muy disperso.
        """
        libres = self.bloques.count(None)
        if libres == 0:
            return 0.0  # sin bloques libres, la fragmentación es 0%
        return (1 - self.mayor_hueco() / libres) * 100

    def fragmentacion_externa(self):
        """Muestra el % de fragmentación externa y lo devuelve."""
        frag = self.calcular_fragmentacion()
        if self.bloques.count(None) == 0:
            print("No hay bloques libres: fragmentación externa 0.0%")
            return frag
        print(f"Mayor hueco contiguo libre: {self.mayor_hueco()}")
        print(f"Fragmentación externa     : {frag:.1f}%")
        return frag

    # ---------------- Mejora: desfragmentación ----------------
    def desfragmentar(self):
        """Junta todos los archivos al inicio del disco y compara el antes y el después."""
        frag_antes = self.calcular_fragmentacion()
        hueco_antes = self.mayor_hueco()
        dispersos_antes = self.contar_dispersos()

        self.bloques = [None] * self.total_bloques
        posicion = 0
        for inodo in self.tabla_inodos.values():
            nuevos = list(range(posicion, posicion + inodo.tam_bloques))
            for idx in nuevos:
                self.bloques[idx] = inodo.nombre
            inodo.bloques_asignados = nuevos    # se actualizan los punteros del inodo
            posicion += inodo.tam_bloques

        print("\nDisco desfragmentado.")
        print(f"Fragmentación externa: {frag_antes:.1f}% -> {self.calcular_fragmentacion():.1f}%")
        print(f"Mayor hueco contiguo : {hueco_antes} -> {self.mayor_hueco()}")
        print(f"Archivos dispersos   : {dispersos_antes} -> {self.contar_dispersos()}")


# =====================================================================
#                        INTERFAZ GRÁFICA (tkinter)
# =====================================================================
# La interfaz no repite la lógica: llama a los mismos métodos de SimuladorDisco.
# Esos métodos informan con print(), así que capturamos ese texto y lo mostramos
# en el registro de la ventana.

TAM_CELDA = 30      # lado de cada bloque en el mapa, en píxeles
MARGEN_MAPA = 44    # espacio a la izquierda para el número de cada fila

COLOR_LIBRE = "#eef0f3"
COLOR_BORDE = "#c5cad3"
COLOR_RESALTADO = "#111827"
COLORES_ARCHIVOS = ["#4e79a7", "#f28e2b", "#59a14f", "#e15759", "#76b7b2", "#b07aa1",
                    "#9c755f", "#d4a017", "#2f9e8f", "#c2528b", "#6a6fc9", "#7f8c3a"]


def color_de(inodo):
    """Devuelve el color de un archivo según su símbolo."""
    if inodo.simbolo not in SIMBOLOS:   # el símbolo '#' se usa cuando se agotaron todos
        return "#7a7a7a"
    return COLORES_ARCHIVOS[SIMBOLOS.index(inodo.simbolo) % len(COLORES_ARCHIVOS)]


def ejecutar(funcion, *args):
    """Ejecuta una función y devuelve lo que imprimió, en vez de mandarlo a la consola."""
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        funcion(*args)
    return salida.getvalue().strip()


class VistaMapa(ttk.Frame):
    """Dibuja los bloques del disco como una grilla de colores, con barra de desplazamiento."""

    def __init__(self, padre, al_hacer_clic=None):
        super().__init__(padre)
        self.al_hacer_clic = al_hacer_clic
        self.total_bloques = 0

        ancho = MARGEN_MAPA + BLOQUES_POR_FILA * TAM_CELDA + 8
        self.canvas = tk.Canvas(self, width=ancho, height=TAM_CELDA * 8 + 8,
                                background="white", highlightthickness=0)
        barra = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=barra.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        self.canvas.bind("<Button-1>", self._clic)
        self.canvas.bind("<MouseWheel>", self._rueda)                                # Windows y Mac
        self.canvas.bind("<Button-4>", lambda _: self.canvas.yview_scroll(-1, "units"))  # Linux
        self.canvas.bind("<Button-5>", lambda _: self.canvas.yview_scroll(1, "units"))   # Linux

    def dibujar(self, disco, resaltado=None):
        """Vuelve a dibujar todo el disco. 'resaltado' es el archivo a marcar con borde."""
        self.total_bloques = disco.total_bloques
        self.canvas.delete("all")

        for idx, nombre in enumerate(disco.bloques):
            fila, columna = divmod(idx, BLOQUES_POR_FILA)
            x = MARGEN_MAPA + columna * TAM_CELDA
            y = 4 + fila * TAM_CELDA

            if columna == 0:    # número del primer bloque de la fila, como en la consola
                self.canvas.create_text(MARGEN_MAPA - 8, y + TAM_CELDA / 2, text=str(idx),
                                        anchor="e", fill="#6b7280", font=("TkDefaultFont", 9))
            if nombre is None:
                self.canvas.create_rectangle(x, y, x + TAM_CELDA - 2, y + TAM_CELDA - 2,
                                             fill=COLOR_LIBRE, outline=COLOR_BORDE)
            else:
                inodo = disco.tabla_inodos[nombre]
                marcado = nombre == resaltado
                self.canvas.create_rectangle(x, y, x + TAM_CELDA - 2, y + TAM_CELDA - 2,
                                             fill=color_de(inodo),
                                             outline=COLOR_RESALTADO if marcado else color_de(inodo),
                                             width=3 if marcado else 1)
                self.canvas.create_text(x + TAM_CELDA / 2 - 1, y + TAM_CELDA / 2 - 1,
                                        text=inodo.simbolo, fill="white",
                                        font=("TkDefaultFont", 10, "bold"))

        filas = (disco.total_bloques + BLOQUES_POR_FILA - 1) // BLOQUES_POR_FILA
        self.canvas.configure(scrollregion=(0, 0, MARGEN_MAPA + BLOQUES_POR_FILA * TAM_CELDA + 8,
                                            filas * TAM_CELDA + 8))

    def _clic(self, evento):
        """Averigua qué bloque se tocó y avisa a la ventana."""
        if self.al_hacer_clic is None:
            return
        columna = int(self.canvas.canvasx(evento.x) - MARGEN_MAPA) // TAM_CELDA
        fila = int(self.canvas.canvasy(evento.y) - 4) // TAM_CELDA
        idx = fila * BLOQUES_POR_FILA + columna
        if 0 <= columna < BLOQUES_POR_FILA and 0 <= idx < self.total_bloques:
            self.al_hacer_clic(idx)

    def _rueda(self, evento):
        self.canvas.yview_scroll(-1 if evento.delta > 0 else 1, "units")


class Registro(ttk.Frame):
    """Cuadro de texto donde aparecen los mensajes del simulador."""

    def __init__(self, padre, alto=8):
        super().__init__(padre)
        self.texto = tk.Text(self, height=alto, wrap="word", state="disabled",
                             background="#1f2430", foreground="#e5e7eb",
                             font=("Courier New", 10), padx=8, pady=6)
        barra = ttk.Scrollbar(self, orient="vertical", command=self.texto.yview)
        self.texto.configure(yscrollcommand=barra.set)
        self.texto.tag_configure("error", foreground="#ff8a8a")
        self.texto.tag_configure("titulo", foreground="#8ec5ff")
        self.texto.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    def escribir(self, mensaje, etiqueta=None):
        """Agrega un mensaje al final. Los que empiezan con 'Error' salen en rojo."""
        if not mensaje:
            return
        if etiqueta is None and mensaje.startswith("Error"):
            etiqueta = "error"
        self.texto.configure(state="normal")
        self.texto.insert("end", mensaje + "\n", etiqueta or ())
        self.texto.configure(state="disabled")
        self.texto.see("end")


class VentanaDemo(tk.Toplevel):
    """Recorre el caso de la Parte 3 del taller paso a paso, en un disco aparte."""

    def __init__(self, padre):
        super().__init__(padre)
        self.title("Demo guiada del taller")
        self.disco = SimuladorDisco(64)
        d = self.disco
        # El mapa siempre está a la vista, por eso no hacen falta pasos para "ver el mapa"
        self.pasos = [
            ("Crear docA.txt (4 bloques)", lambda: d.crear_archivo("docA.txt", 4)),
            ("Crear docB.txt (4 bloques)", lambda: d.crear_archivo("docB.txt", 4)),
            ("Crear docC.txt (4 bloques)", lambda: d.crear_archivo("docC.txt", 4)),
            ("Eliminar docB.txt: deja un hueco en el medio", lambda: d.eliminar_archivo("docB.txt")),
            ("Ver la fragmentación externa", d.fragmentacion_externa),
            ("Crear docD.txt (6 bloques): no entra en el hueco y queda partido",
             lambda: d.crear_archivo("docD.txt", 6)),
            ("Ver los archivos y sus tramos", d.listar_archivos),
            ("Eliminar docA.txt: se abre otro hueco al inicio", lambda: d.eliminar_archivo("docA.txt")),
            ("Ver la fragmentación externa", d.fragmentacion_externa),
            ("Desfragmentar el disco", d.desfragmentar),
            ("Ver los archivos y sus tramos", d.listar_archivos),
        ]
        self.paso_actual = 0

        marco = ttk.Frame(self, padding=12)
        marco.pack(fill="both", expand=True)
        self.etiqueta_paso = ttk.Label(marco, wraplength=560, font=("TkDefaultFont", 11, "bold"))
        self.etiqueta_paso.pack(fill="x", pady=(0, 8))
        self.mapa = VistaMapa(marco)
        self.mapa.pack(fill="both", expand=True)
        self.registro = Registro(marco, alto=10)
        self.registro.pack(fill="both", expand=True, pady=8)
        self.boton = ttk.Button(marco, text="Ejecutar paso", command=self.ejecutar_paso)
        self.boton.pack(anchor="e")

        self.mapa.dibujar(self.disco)
        self.mostrar_siguiente()

    def mostrar_siguiente(self):
        total = len(self.pasos)
        if self.paso_actual < total:
            titulo = self.pasos[self.paso_actual][0]
            self.etiqueta_paso.configure(text=f"Paso {self.paso_actual + 1} de {total}: {titulo}")
        else:
            self.etiqueta_paso.configure(text="Fin de la demo. Tu disco no fue modificado.")
            self.boton.configure(text="Cerrar", command=self.destroy)

    def ejecutar_paso(self):
        titulo, accion = self.pasos[self.paso_actual]
        self.registro.escribir(f"> {titulo}", "titulo")
        self.registro.escribir(ejecutar(accion))
        self.mapa.dibujar(self.disco)
        self.paso_actual += 1
        self.mostrar_siguiente()


class AppDisco:
    """Ventana principal del simulador."""

    def __init__(self, raiz):
        self.raiz = raiz
        self.disco = SimuladorDisco(64)
        self.resaltado = None           # archivo marcado en el mapa
        self.fila_a_nombre = {}         # fila de la tabla -> nombre del archivo
        self.demo = None                # ventana de la demo, si está abierta

        raiz.title("Simulador de disco - Asignación indexada")
        self._armar_interfaz()
        self.actualizar()
        self.registro.escribir("Disco nuevo de 64 bloques. Creá un archivo para empezar.")

    # ---------------- Armado de la ventana ----------------
    def _armar_interfaz(self):
        principal = ttk.Frame(self.raiz, padding=12)
        principal.pack(fill="both", expand=True)
        principal.columnconfigure(1, weight=1)
        principal.rowconfigure(0, weight=1)
        principal.rowconfigure(1, weight=1)

        # Izquierda: el mapa del disco
        marco_mapa = ttk.LabelFrame(principal, text="Mapa del disco (clic en un bloque para ver su archivo)",
                                    padding=8)
        marco_mapa.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.mapa = VistaMapa(marco_mapa, al_hacer_clic=self.clic_en_bloque)
        self.mapa.pack(fill="both", expand=True)

        # Derecha: los controles y las métricas
        derecha = ttk.Frame(principal)
        derecha.grid(row=0, column=1, sticky="nsew")
        derecha.columnconfigure(0, weight=1)
        derecha.rowconfigure(1, weight=1)
        self._armar_crear(derecha)
        self._armar_tabla(derecha)
        self._armar_metricas(derecha)

        # Abajo: el registro de mensajes
        marco_registro = ttk.LabelFrame(principal, text="Registro", padding=8)
        marco_registro.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        self.registro = Registro(marco_registro)
        self.registro.pack(fill="both", expand=True)

    def _armar_crear(self, padre):
        marco = ttk.LabelFrame(padre, text="Crear archivo", padding=8)
        marco.grid(row=0, column=0, sticky="ew")
        marco.columnconfigure(1, weight=1)

        ttk.Label(marco, text="Nombre:").grid(row=0, column=0, padx=(0, 6))
        self.entrada_nombre = ttk.Entry(marco)
        self.entrada_nombre.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.entrada_nombre.bind("<Return>", lambda _: self.crear())

        ttk.Label(marco, text="Bloques:").grid(row=0, column=2, padx=(0, 6))
        self.entrada_tam = ttk.Spinbox(marco, from_=1, to=MAX_BLOQUES_DISCO, width=6)
        self.entrada_tam.set(4)
        self.entrada_tam.grid(row=0, column=3, padx=(0, 10))
        self.entrada_tam.bind("<Return>", lambda _: self.crear())

        ttk.Button(marco, text="Crear", command=self.crear).grid(row=0, column=4)

    def _armar_tabla(self, padre):
        marco = ttk.LabelFrame(padre, text="Archivos (tabla de inodos)", padding=8)
        marco.grid(row=1, column=0, sticky="nsew", pady=10)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        columnas = {"simbolo": ("Símbolo", 60), "nombre": ("Archivo", 130),
                    "bloques": ("Bloques", 60), "tramos": ("Tramos", 60),
                    "punteros": ("Punteros a bloques", 220)}
        self.tabla = ttk.Treeview(marco, columns=list(columnas), show="headings",
                                  height=7, selectmode="browse")
        for clave, (titulo, ancho) in columnas.items():
            centrada = clave in ("simbolo", "bloques", "tramos")
            self.tabla.heading(clave, text=titulo)
            self.tabla.column(clave, width=ancho, anchor="center" if centrada else "w",
                              stretch=clave == "punteros")
        self.tabla.bind("<<TreeviewSelect>>", self.seleccion_en_tabla)

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")

        botones = ttk.Frame(marco)
        botones.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(botones, text="Eliminar seleccionado", command=self.eliminar).pack(side="left")
        ttk.Button(botones, text="Desfragmentar", command=self.desfragmentar).pack(side="left", padx=6)
        ttk.Button(botones, text="Demo del taller", command=self.abrir_demo).pack(side="left")

    def _armar_metricas(self, padre):
        marco = ttk.LabelFrame(padre, text="Métricas", padding=8)
        marco.grid(row=2, column=0, sticky="ew")
        marco.columnconfigure((1, 3), weight=1)

        # Cada métrica es una etiqueta que se actualiza después de cada operación
        self.metricas = {}
        nombres = ["Total de bloques", "Ocupados", "Libres", "Ocupación",
                   "Mayor hueco contiguo", "Fragmentación externa", "Archivos dispersos"]
        for i, nombre in enumerate(nombres):
            fila, grupo = i // 2, i % 2
            ttk.Label(marco, text=nombre + ":").grid(row=fila, column=grupo * 2, sticky="w", padx=(0, 6))
            valor = ttk.Label(marco, font=("TkDefaultFont", 10, "bold"))
            valor.grid(row=fila, column=grupo * 2 + 1, sticky="w", padx=(0, 16))
            self.metricas[nombre] = valor

        fila_formato = len(nombres) // 2 + 1
        formato = ttk.Frame(marco)
        formato.grid(row=fila_formato, column=0, columnspan=4, sticky="w", pady=(10, 0))
        ttk.Label(formato, text="Formatear con").pack(side="left")
        self.entrada_disco = ttk.Spinbox(formato, from_=1, to=MAX_BLOQUES_DISCO, width=6)
        self.entrada_disco.set(64)
        self.entrada_disco.pack(side="left", padx=6)
        ttk.Label(formato, text=f"bloques (máx. {MAX_BLOQUES_DISCO})").pack(side="left")
        ttk.Button(formato, text="Formatear", command=self.formatear).pack(side="left", padx=(10, 0))

    # ---------------- Refrescar lo que se ve ----------------
    def actualizar(self):
        """Vuelve a dibujar el mapa, la tabla y las métricas según el estado del disco."""
        if self.resaltado not in self.disco.tabla_inodos:
            self.resaltado = None
        self.mapa.dibujar(self.disco, self.resaltado)
        self._actualizar_tabla()
        self._actualizar_metricas()

    def _actualizar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        self.fila_a_nombre = {}
        for nombre, inodo in self.disco.tabla_inodos.items():
            etiqueta = "color_" + inodo.simbolo
            self.tabla.tag_configure(etiqueta, foreground=color_de(inodo))
            fila = self.tabla.insert("", "end", tags=(etiqueta,), values=(
                inodo.simbolo, nombre, inodo.tam_bloques, inodo.contar_tramos(),
                ", ".join(str(b) for b in inodo.bloques_asignados)))
            self.fila_a_nombre[fila] = nombre
            if nombre == self.resaltado:
                self.tabla.selection_set(fila)

    def _actualizar_metricas(self):
        d = self.disco
        libres = d.bloques.count(None)
        ocupados = d.total_bloques - libres
        valores = {
            "Total de bloques": d.total_bloques,
            "Ocupados": ocupados,
            "Libres": libres,
            "Ocupación": f"{ocupados / d.total_bloques * 100:.1f}%",
            "Mayor hueco contiguo": d.mayor_hueco(),
            "Fragmentación externa": f"{d.calcular_fragmentacion():.1f}%",
            "Archivos dispersos": f"{d.contar_dispersos()} de {len(d.tabla_inodos)}",
        }
        for nombre, valor in valores.items():
            self.metricas[nombre].configure(text=str(valor))

    # ---------------- Acciones de los botones ----------------
    def crear(self):
        nombre = self.entrada_nombre.get().strip()
        try:
            tam = int(self.entrada_tam.get().strip())
        except ValueError:
            self.registro.escribir("Error: la cantidad de bloques debe ser un número entero.")
            return
        mensaje = ejecutar(self.disco.crear_archivo, nombre, tam)
        self.registro.escribir(mensaje)
        if not mensaje.startswith("Error"):
            self.entrada_nombre.delete(0, "end")
            self.resaltado = nombre
            self.actualizar()
        self.entrada_nombre.focus_set()

    def eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            self.registro.escribir("Error: elegí un archivo de la tabla para eliminarlo.")
            return
        self.registro.escribir(ejecutar(self.disco.eliminar_archivo, self.fila_a_nombre[seleccion[0]]))
        self.actualizar()

    def desfragmentar(self):
        self.registro.escribir(ejecutar(self.disco.desfragmentar))
        self.actualizar()

    def formatear(self):
        try:
            total = int(self.entrada_disco.get().strip())
        except ValueError:
            total = 0
        if not 1 <= total <= MAX_BLOQUES_DISCO:
            self.registro.escribir(f"Error: el disco debe tener entre 1 y {MAX_BLOQUES_DISCO} bloques.")
            return
        if self.disco.tabla_inodos and not messagebox.askyesno(
                "Formatear disco", "Se van a borrar todos los archivos. ¿Continuar?"):
            return
        self.disco = SimuladorDisco(total)
        self.registro.escribir(f"Disco formateado: {total} bloques libres.")
        self.actualizar()

    def abrir_demo(self):
        """Abre la demo, o la trae al frente si ya estaba abierta."""
        if self.demo is not None and self.demo.winfo_exists():
            self.demo.lift()
            return
        self.demo = VentanaDemo(self.raiz)

    # ---------------- Relación entre el mapa y la tabla ----------------
    def seleccion_en_tabla(self, _evento):
        seleccion = self.tabla.selection()
        if seleccion:
            self.resaltado = self.fila_a_nombre[seleccion[0]]
            self.mapa.dibujar(self.disco, self.resaltado)

    def clic_en_bloque(self, idx):
        """Al tocar un bloque, informa de quién es y marca su archivo."""
        nombre = self.disco.bloques[idx]
        if nombre is None:
            self.registro.escribir(f"Bloque {idx}: libre.")
            self.tabla.selection_remove(*self.tabla.selection())
            self.resaltado = None
            self.mapa.dibujar(self.disco)
            return
        self.registro.escribir(f"Bloque {idx}: pertenece a '{nombre}'.")
        self.resaltado = nombre
        self._actualizar_tabla()
        self.mapa.dibujar(self.disco, nombre)


# =====================================================================
#                           MENÚ DE CONSOLA
# =====================================================================

# ---------------- Lectura de datos ----------------
def pedir_entero(mensaje, maximo):
    """Pide un entero entre 1 y maximo, y vuelve a preguntar si se escribe mal."""
    while True:
        texto = input(mensaje).strip()
        try:
            valor = int(texto)
        except ValueError:
            print("Error: ingresá un número entero.")
            continue
        if 1 <= valor <= maximo:
            return valor
        print(f"Error: el número debe estar entre 1 y {maximo}.")


def pedir_disco():
    """Pregunta el tamaño y crea un disco vacío."""
    total = pedir_entero(f"¿Cuántos bloques tiene el disco? (1-{MAX_BLOQUES_DISCO}, ej: 64): ",
                         MAX_BLOQUES_DISCO)
    return SimuladorDisco(total)


# ---------------- Opciones del menú ----------------
def opcion_crear(disco):
    """Pide los datos del archivo. Avisa los errores antes de pedir el tamaño."""
    libres = disco.bloques.count(None)
    if libres == 0:
        print("Error: el disco está lleno.")
        return
    nombre = input("Nombre del archivo: ").strip()
    if nombre == "":
        print("Error: el nombre no puede estar vacío.")
        return
    if nombre in disco.tabla_inodos:
        print(f"Error: El archivo '{nombre}' ya existe.")
        return
    tam = pedir_entero(f"Cantidad de bloques (1-{libres} disponibles): ", libres)
    disco.crear_archivo(nombre, tam)


def opcion_eliminar(disco):
    """Muestra los archivos que hay y elimina el que se elija."""
    if not disco.tabla_inodos:
        print("No hay archivos para eliminar.")
        return
    print("Archivos:", ", ".join(disco.tabla_inodos))
    disco.eliminar_archivo(input("Nombre del archivo a eliminar: ").strip())


def demo():
    """Recorre el caso del taller paso a paso, en un disco aparte."""
    disco = SimuladorDisco(64)

    def paso(titulo, accion):
        input(f"\n[Enter] {titulo}")
        accion()

    print("\n===== DEMO: caso de la Parte 3 del taller =====")
    paso("Crear docA.txt (4 bloques)", lambda: disco.crear_archivo("docA.txt", 4))
    paso("Crear docB.txt (4 bloques)", lambda: disco.crear_archivo("docB.txt", 4))
    paso("Crear docC.txt (4 bloques)", lambda: disco.crear_archivo("docC.txt", 4))
    paso("Eliminar docB.txt: deja un hueco en el medio", lambda: disco.eliminar_archivo("docB.txt"))
    paso("Ver el mapa", disco.mostrar_mapa)
    paso("Ver la fragmentación externa", disco.fragmentacion_externa)
    paso("Crear docD.txt (6 bloques): no entra en el hueco y queda partido",
         lambda: disco.crear_archivo("docD.txt", 6))
    paso("Ver el mapa", disco.mostrar_mapa)
    paso("Ver los archivos y sus tramos", disco.listar_archivos)
    paso("Eliminar docA.txt: se abre otro hueco al inicio", lambda: disco.eliminar_archivo("docA.txt"))
    paso("Ver la fragmentación externa", disco.fragmentacion_externa)
    paso("Desfragmentar el disco", disco.desfragmentar)
    paso("Ver el mapa", disco.mostrar_mapa)
    paso("Ver los archivos y sus tramos", disco.listar_archivos)
    print("\n===== Fin de la demo. Tu disco no fue modificado. =====")


# ---------------- Menú interactivo ----------------
def menu():
    disco = pedir_disco()

    while True:
        ocupados = disco.total_bloques - disco.bloques.count(None)
        print(f"\n========= SIMULADOR DE DISCO ({ocupados}/{disco.total_bloques} ocupados) =========")
        print("1. Crear archivo")
        print("2. Eliminar archivo")
        print("3. Mostrar mapa del disco")
        print("4. Listar archivos (inodos)")
        print("5. Métricas del disco")
        print("6. Fragmentación externa")
        print("7. Desfragmentar")
        print("8. Formatear (disco nuevo)")
        print("9. Demo guiada del taller")
        print("0. Salir")
        opcion = input("Elegí una opción: ").strip()

        if opcion == "1":
            opcion_crear(disco)
        elif opcion == "2":
            opcion_eliminar(disco)
        elif opcion == "3":
            disco.mostrar_mapa()
        elif opcion == "4":
            disco.listar_archivos()
        elif opcion == "5":
            disco.calcular_metricas()
        elif opcion == "6":
            disco.fragmentacion_externa()
        elif opcion == "7":
            disco.desfragmentar()
            disco.mostrar_mapa()
        elif opcion == "8":
            disco = pedir_disco()
            print("Disco formateado.")
        elif opcion == "9":
            demo()
        elif opcion == "0":
            print("Saliendo del simulador...")
            break
        else:
            print("Opción inválida, probá de nuevo.")


def main():
    usar_consola = "--consola" in sys.argv
    if not usar_consola and not TKINTER_DISPONIBLE:
        print("No se encontró tkinter, así que se abre el menú de consola.")
        print("Para tener la interfaz gráfica en Linux: sudo apt install python3-tk")
        usar_consola = True

    if usar_consola:
        try:
            menu()
        except (KeyboardInterrupt, EOFError):  # Ctrl+C o fin de la entrada: salir sin error
            print("\nSaliendo del simulador...")
    else:
        raiz = tk.Tk()
        AppDisco(raiz)
        raiz.mainloop()


if __name__ == "__main__":
    main()