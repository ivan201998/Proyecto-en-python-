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
 
import string
 
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
 
 
if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):  # Ctrl+C o fin de la entrada: salir sin error
        print("\nSaliendo del simulador...")
 