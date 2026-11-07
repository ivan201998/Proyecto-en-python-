# =====================================================================
#  Simulador de Sistema de Archivos - Asignación Indexada (AE4)
#  Actividad de Clase 2 - Semana 13 (07/11/2026)
#
#  Cada archivo tiene un Inodo que guarda la lista de bloques del disco
#  donde están sus datos (los "punteros"). Así un archivo puede quedar
#  repartido en bloques NO contiguos y aprovechar los huecos libres.
#
#  Cómo ejecutarlo:   python3 main.py
# =====================================================================

import string

SIMBOLOS = string.ascii_uppercase + string.digits + string.ascii_lowercase
BLOQUES_POR_FILA = 16       # cuántos bloques se dibujan por fila en el mapa
TAMANIO_POR_DEFECTO = 64    # tamaño del disco si se presiona Enter al iniciar
MAX_BLOQUES_DISCO = 1024    # tamaño máximo permitido para el disco


class Inodo:
    """Representa un archivo: nombre, tamaño y lista de bloques asignados."""

    def __init__(self, nombre, tam_bloques, simbolo):
        self.nombre = nombre
        self.tam_bloques = tam_bloques
        self.simbolo = simbolo              # letra que lo identifica en el mapa
        self.bloques_asignados = []         # lista dinámica de índices de bloques (punteros)

    def contar_tramos(self):
        """Cuenta los grupos de bloques consecutivos. 1 tramo = archivo contiguo."""
        if not self.bloques_asignados:
            return 0
        tramos = 1
        for i in range(1, len(self.bloques_asignados)):
            if self.bloques_asignados[i] != self.bloques_asignados[i - 1] + 1:
                tramos += 1
        return tramos


class SimuladorDisco:
    """Representa el disco: un vector de bloques y una tabla de inodos."""

    def __init__(self, total_bloques=TAMANIO_POR_DEFECTO):
        self.total_bloques = total_bloques
        # None = bloque libre. Si está ocupado, guarda el nombre del archivo.
        self.bloques = [None] * total_bloques
        self.tabla_inodos = {}              # nombre del archivo -> su Inodo
        self.simbolos_entregados = 0

    def _siguiente_simbolo(self):
        """Devuelve una letra sin usar. Si se agotan todas, devuelve '#'."""
        usados = [inodo.simbolo for inodo in self.tabla_inodos.values()]
        for _ in SIMBOLOS:
            simbolo = SIMBOLOS[self.simbolos_entregados % len(SIMBOLOS)]
            self.simbolos_entregados += 1
            if simbolo not in usados:
                return simbolo
        return "#"

    # ---------------- Operaciones sobre archivos ----------------
    def crear_archivo(self, nombre, tam_bloques):
        """Crea un archivo y le asigna bloques libres. Devuelve True si pudo."""
        if nombre == "":
            print("Error: el nombre no puede estar vacío.")
            return False
        if nombre in self.tabla_inodos:
            print(f"Error: Nombre de archivo duplicado ('{nombre}' ya existe).")
            return False
        if tam_bloques <= 0:
            print("Error: el tamaño debe ser de al menos 1 bloque.")
            return False

        bloques_libres = [i for i, b in enumerate(self.bloques) if b is None]
        if len(bloques_libres) < tam_bloques:
            print("Error: Espacio en disco insuficiente / Bloques agotados. "
                  f"Pediste {tam_bloques} bloques y hay {len(bloques_libres)} libres.")
            return False

        # Asignación indexada: se toman los primeros bloques libres disponibles
        nuevo_inodo = Inodo(nombre, tam_bloques, self._siguiente_simbolo())
        for i in range(tam_bloques):
            idx = bloques_libres[i]
            self.bloques[idx] = nombre
            nuevo_inodo.bloques_asignados.append(idx)

        self.tabla_inodos[nombre] = nuevo_inodo
        print(f"Archivo '{nombre}' creado con éxito. "
              f"Bloques asignados: {nuevo_inodo.bloques_asignados}")
        return True

    def eliminar_archivo(self, nombre):
        """Elimina un archivo y libera sus bloques. Devuelve True si pudo."""
        if nombre not in self.tabla_inodos:
            print(f"Error: Archivo no encontrado ('{nombre}').")
            return False

        inodo = self.tabla_inodos[nombre]
        for idx in inodo.bloques_asignados:
            self.bloques[idx] = None

        del self.tabla_inodos[nombre]
        print(f"Archivo '{nombre}' eliminado correctamente. "
              f"Bloques liberados: {inodo.bloques_asignados}")
        return True

    # ---------------- Visualización ----------------
    def mostrar_mapa(self):
        """Dibuja el disco: cada archivo con su letra y '.' para los bloques libres."""
        print("\nMapa de bloques ('.' = libre):")
        for inicio in range(0, self.total_bloques, BLOQUES_POR_FILA):
            fila = self.bloques[inicio:inicio + BLOQUES_POR_FILA]
            celdas = ["." if b is None else self.tabla_inodos[b].simbolo for b in fila]
            print(f"  {inicio:>4} | {' '.join(celdas)}")

        if self.tabla_inodos:
            referencias = [f"{i.simbolo} = {i.nombre}" for i in self.tabla_inodos.values()]
            print("  Referencias:", ", ".join(referencias))

    def mostrar_tabla_inodos(self):
        """Muestra cada archivo con sus punteros a bloques."""
        print("\n--- Tabla de Inodos ---")
        if not self.tabla_inodos:
            print("No hay archivos en el disco.")
            return
        print(f"{'Sím.':<5}{'Archivo':<16}{'Bloques':>8}{'Tramos':>8}   Punteros")
        for nombre, inodo in self.tabla_inodos.items():
            print(f"{inodo.simbolo:<5}{nombre:<16}{inodo.tam_bloques:>8}"
                  f"{inodo.contar_tramos():>8}   {inodo.bloques_asignados}")

    # ---------------- Funciones matemáticas ----------------
    def calcular_metricas(self):
        """Totaliza bloques libres y ocupados. Se recalcula en cada llamada."""
        total = self.total_bloques
        libres = self.bloques.count(None)
        ocupados = total - libres
        ocupacion = ocupados / total * 100

        print("\n--- Métricas del disco ---")
        print(f"Total de bloques   : {total}")
        print(f"Bloques ocupados   : {ocupados}")
        print(f"Bloques libres     : {libres}")
        print(f"Ocupación del disco: {ocupacion:.2f}%")
        return {"total": total, "ocupados": ocupados, "libres": libres,
                "ocupacion": ocupacion}

    def mayor_hueco_contiguo(self):
        """Devuelve la secuencia consecutiva más larga de bloques libres."""
        mayor = 0
        actual = 0
        for b in self.bloques:
            if b is None:
                actual += 1
                mayor = max(mayor, actual)
            else:
                actual = 0
        return mayor

    def calcular_fragmentacion_externa(self):
        """Fragmentación Externa (%) = (1 - Mayor Hueco Contiguo / Total Libre) x 100."""
        total_libre = self.bloques.count(None)
        if total_libre == 0:
            print("Fragmentación externa: 0.00% (no hay bloques libres)")
            return 0.0
        mayor_hueco = self.mayor_hueco_contiguo()
        fragmentacion = (1 - mayor_hueco / total_libre) * 100
        print(f"Mayor hueco contiguo : {mayor_hueco}")
        print(f"Fragmentación externa: {fragmentacion:.2f}%")
        return fragmentacion


# =====================================================================
#                     INTERFAZ INTERACTIVA POR CONSOLA
# =====================================================================

def pedir_entero(mensaje):
    """Pide un número entero y vuelve a preguntar si no se escribe uno válido."""
    while True:
        texto = input(mensaje).strip()
        try:
            return int(texto)
        except ValueError:
            print("Error: ingresá un número entero.")


def pedir_tamanio_disco():
    """Pregunta el tamaño del disco. Con Enter usa el valor por defecto."""
    while True:
        texto = input(f"¿Cuántos bloques tiene el disco? "
                      f"(Enter = {TAMANIO_POR_DEFECTO}): ").strip()
        if texto == "":
            return TAMANIO_POR_DEFECTO
        try:
            total = int(texto)
        except ValueError:
            print("Error: ingresá un número entero.")
            continue
        if 1 <= total <= MAX_BLOQUES_DISCO:
            return total
        print(f"Error: el disco debe tener entre 1 y {MAX_BLOQUES_DISCO} bloques.")


def opcion_crear(disco):
    nombre = input("Nombre del archivo: ").strip()
    tam = pedir_entero("Cantidad de bloques: ")
    disco.crear_archivo(nombre, tam)


def opcion_eliminar(disco):
    if disco.tabla_inodos:
        print("Archivos en disco:", ", ".join(disco.tabla_inodos))
    nombre = input("Nombre del archivo a eliminar: ").strip()
    disco.eliminar_archivo(nombre)


def opcion_tabla_y_metricas(disco):
    disco.mostrar_tabla_inodos()
    disco.calcular_metricas()
    disco.calcular_fragmentacion_externa()


def menu():
    print("Simulador de Sistema de Archivos - Asignación Indexada")
    disco = SimuladorDisco(pedir_tamanio_disco())
    print(f"Disco creado con {disco.total_bloques} bloques libres.")

    while True:
        print("\n=======================================")
        print("1. Crear archivo")
        print("2. Eliminar archivo")
        print("3. Ver mapa de bloques")
        print("4. Ver tabla de Inodos y métricas")
        print("5. Salir")
        print("=======================================")
        opcion = input("Elegí una opción: ").strip()

        if opcion == "1":
            opcion_crear(disco)
        elif opcion == "2":
            opcion_eliminar(disco)
        elif opcion == "3":
            disco.mostrar_mapa()
        elif opcion == "4":
            opcion_tabla_y_metricas(disco)
        elif opcion == "5":
            print("Saliendo del simulador...")
            break
        else:
            print("Opción inválida, elegí un número del 1 al 5.")


if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo del simulador...")
