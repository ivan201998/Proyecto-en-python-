#version original de partida de idea
class Inodo:
    def __init__(self, nombre, tam_bloques):
        self.nombre = nombre
        self.tam_bloques = tam_bloques
        self.bloques_asignados = []  # Lista de índices de bloques en disco

class SimuladorDisco:
    def __init__(self, total_bloques=64):
        self.total_bloques = total_bloques
        # None indica bloque libre, de lo contrario guarda el nombre del archivo
        self.bloques = [None] * total_bloques
        self.tabla_inodos = {}

    def crear_archivo(self, nombre, tam_bloques):
        # 1. Validar nombre duplicado
        if nombre in self.tabla_inodos:
            print(f"Error: El archivo '{nombre}' ya existe.")
            return False

        # 2. Buscar bloques libres
        bloques_libres = [i for i, b in enumerate(self.bloques) if b is None]
        if len(bloques_libres) < tam_bloques:
            print("Error: Espacio en disco insuficiente / Bloques agotados.")
            return False

        # 3. Asignación indexada (toma los primeros libres disponibles)
        nuevo_inodo = Inodo(nombre, tam_bloques)
        for i in range(tam_bloques):
            idx = bloques_libres[i]
            self.bloques[idx] = nombre
            nuevo_inodo.bloques_asignados.append(idx)

        self.tabla_inodos[nombre] = nuevo_inodo
        print(f"Archivo '{nombre}' creado con éxito. Bloques asignados: {nuevo_inodo.bloques_asignados}")
        return True

    def eliminar_archivo(self, nombre):
        if nombre not in self.tabla_inodos:
            print(f"Error: Archivo '{nombre}' no encontrado.")
            return False

        inodo = self.tabla_inodos[nombre]
        for idx in inodo.bloques_asignados:
            self.bloques[idx] = None

        del self.tabla_inodos[nombre]
        print(f"Archivo '{nombre}' eliminado correctamente.")
        return True

    def mostrar_mapa(self):
        mapa = "".join(["[O]" if b else "[L]" for b in self.bloques])
        print("\nMapa del Disco (Primeros bloques):", mapa)