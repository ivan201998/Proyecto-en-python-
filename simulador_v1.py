# Simulador de asignación de espacio en disco (asignación indexada, como ext4)
# Cada archivo tiene un Inodo que guarda la lista de bloques donde están sus datos.
# version con metrica de almacenamiento y fragmentacion externa


class Inodo:
    """Representa un archivo: guarda su nombre, su tamaño y en qué bloques está."""

    def __init__(self, nombre, tam_bloques):
        self.nombre = nombre                # nombre del archivo
        self.tam_bloques = tam_bloques      # cuántos bloques ocupa
        self.bloques_asignados = []         # Lista de índices de bloques en disco (los "punteros")


class SimuladorDisco:
    """Representa el disco: una lista de bloques y una tabla con los inodos."""

    def __init__(self, total_bloques=64):
        self.total_bloques = total_bloques      # capacidad del disco en bloques
        # None indica bloque libre, de lo contrario guarda el nombre del archivo
        self.bloques = [None] * total_bloques   # al inicio, todo el disco está libre
        self.tabla_inodos = {}                  # nombre del archivo -> su Inodo

    def crear_archivo(self, nombre, tam_bloques):
        """Crea un archivo y le asigna bloques libres. Devuelve True si pudo, False si hubo error."""
        # 1. Validar nombre duplicado
        if nombre in self.tabla_inodos:
            print(f"Error: El archivo '{nombre}' ya existe.")
            return False

        # 2. Buscar bloques libres (los que valen None), estén donde estén
        bloques_libres = [i for i, b in enumerate(self.bloques) if b is None]
        # Si hay menos libres que los pedidos, no se puede crear
        if len(bloques_libres) < tam_bloques:
            print("Error: Espacio en disco insuficiente / Bloques agotados.")
            return False

        # 3. Asignación indexada (toma los primeros libres disponibles)
        nuevo_inodo = Inodo(nombre, tam_bloques)
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
        """Dibuja el disco: [O] = bloque ocupado, [L] = bloque libre."""
        mapa = "".join(["[O]" if b else "[L]" for b in self.bloques])
        print("\nMapa del Disco:", mapa)

    # ---------------- Desafío 1: métricas ----------------
    def calcular_metricas(self):
        """Muestra total, ocupados, libres y porcentaje de ocupación."""
        total = self.total_bloques
        libres = self.bloques.count(None)   # posiciones iguales a None
        ocupados = total - libres           # el resto de las posiciones están ocupadas
        ocupacion = ocupados / total * 100  # Ocupación (%) = ocupados / total x 100

        print("\n--- Métricas del disco ---")
        print(f"Total de bloques   : {total}")
        print(f"Bloques ocupados   : {ocupados}")
        print(f"Bloques libres     : {libres}")
        print(f"Ocupación del disco: {ocupacion:.1f}%")

    # ---------------- Desafío 2: fragmentación externa ----------------
    def fragmentacion_externa(self):
        """Calcula el % de fragmentación externa: qué tan dispersos están los bloques libres."""
        libres = self.bloques.count(None)
        if libres == 0:
            return 0.0  # sin bloques libres, la fragmentación es 0%

        # Buscar la secuencia consecutiva más larga de None (el mayor hueco libre)
        mayor_hueco = 0       # el hueco más grande encontrado hasta ahora
        hueco_actual = 0      # largo del hueco que se está recorriendo
        for b in self.bloques:
            if b is None:
                hueco_actual += 1                   # el hueco sigue creciendo
                if hueco_actual > mayor_hueco:
                    mayor_hueco = hueco_actual      # nuevo récord
            else:
                hueco_actual = 0                    # un bloque ocupado corta el hueco

        # Fragmentación Externa (%) = (1 - mayor hueco / bloques libres) x 100
        # 0% = todo el espacio libre junto; cerca de 100% = libre muy disperso
        frag = (1 - mayor_hueco / libres) * 100
        print(f"Mayor hueco contiguo libre: {mayor_hueco}")
        print(f"Fragmentación externa     : {frag:.1f}%")
        return frag


# Prueba rápida (caso de la Parte 3 del taller)
if __name__ == "__main__":
    disco = SimuladorDisco(64)              # disco de 64 bloques
    disco.crear_archivo("docA.txt", 4)      # ocupa los bloques 0 a 3
    disco.crear_archivo("docB.txt", 4)      # ocupa los bloques 4 a 7
    disco.crear_archivo("docC.txt", 4)      # ocupa los bloques 8 a 11
    disco.eliminar_archivo("docB.txt")      # deja un hueco libre en el medio
    disco.mostrar_mapa()                    # ver el estado del disco
    disco.calcular_metricas()               # ocupación y bloques libres
    disco.fragmentacion_externa()           # fragmentación con el hueco del medio
