# Simulador de asignación de espacio en disco

Simula cómo un sistema de archivos guarda archivos en un disco usando bloques e inodos, como hace ext4 en Linux.

## Qué hace
- El disco es una lista de bloques, libres u ocupados.
- Cada archivo tiene un inodo (con número) que guarda la lista de bloques que ocupa.
- La asignación es indexada: toma los primeros bloques libres, aunque no estén juntos.
- Calcula la ocupación del disco y la fragmentación externa.
- Compara con la asignación contigua: al crear un archivo avisa si también habría entrado en un solo hueco.
- Muestra en cuántos **tramos** contiguos quedó cada archivo (el costo de la asignación indexada).

## Requisitos
Python 3.8 o superior. No necesita instalar librerías (solo `pytest` para correr las pruebas).

## Cómo ejecutarlo
```bash
python simulador.py
```
Al iniciar pide la cantidad de bloques del disco (Enter = 64).

## Menú
| Opción | Qué hace |
|---|---|
| 1 | Crear un archivo (nombre y tamaño en bloques) |
| 2 | Eliminar un archivo (por nombre o número de inodo, con confirmación) |
| 3 | Ampliar un archivo (agregarle bloques) |
| 4 | Mostrar el mapa del disco (una letra y un color por archivo, `.` libre) |
| 5 | Listar archivos: tabla de inodos con bloques, tramos y ubicación |
| 6 | Ver el detalle de un inodo y resaltar sus bloques en el mapa |
| 7 | Métricas: ocupación, huecos, mayor hueco y fragmentación externa (con barras) |
| 8 | Desfragmentar (compactar) el disco y ver cuántos bloques se movieron |
| 9 | Escenario guiado del taller (Parte 3), paso a paso |
| 10 | Simulación aleatoria de N operaciones (con semilla opcional) |
| 11 | Bitácora de operaciones realizadas |
| 12 / 13 | Guardar / cargar el estado del disco en JSON |
| 14 | Crear un disco nuevo |
| 0 | Salir |

Arriba del menú se ve siempre un resumen: bloques, archivos, ocupación y fragmentación.

## Fórmulas
- Ocupación (%) = (bloques ocupados / total de bloques) × 100
- Fragmentación externa (%) = (1 − mayor hueco libre / bloques libres) × 100

## Ejemplo (opción 9)
1. Crear `docA.txt`, `docB.txt` y `docC.txt` de 4 bloques cada uno.
2. Eliminar `docB.txt` → queda un hueco de 4 bloques (fragmentación 7,1 %).
3. Crear `docD.txt` de 6 bloques.

`docD.txt` entra aunque no haya 6 bloques libres juntos en ese lugar: el inodo guarda los bloques 4-7 y 12-13, en 2 tramos.

## Errores que controla
- Nombre de archivo duplicado, vacío o con `/`
- Archivo no encontrado
- Espacio en disco insuficiente (el disco no queda modificado)
- Tamaños inválidos (0, negativos, texto) y tamaño de disco fuera de rango (1 a 1024)
- Archivo de estado JSON inexistente o corrupto
- Ctrl+C / Ctrl+D: sale sin mostrar errores

## Pruebas automáticas
```bash
pip install pytest
pytest
```
Las pruebas (`tests/test_simulador.py`) verifican creación, eliminación, métricas del caso del taller,
fragmentación, comparación con la asignación contigua, ampliación, desfragmentación y guardado/carga.
GitHub Actions las ejecuta en cada push.

## Versiones
| Archivo | Descripción |
|---|---|
| `main.py` | Código base entregado por la cátedra |
| `simulador_v1.py` | + métricas de ocupación y fragmentación externa |
| `simulador_v2.py` | + menú por consola y listado de inodos |
| `simulador.py` | **Versión final**: lógica separada de la interfaz, pruebas, mapa por colores, tramos, comparación con asignación contigua, ampliar, desfragmentar, escenario guiado, simulación aleatoria, bitácora y JSON |
