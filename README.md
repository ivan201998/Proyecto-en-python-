# Simulador de asignación de espacio en disco

Simula cómo un sistema de archivos guarda archivos en un disco usando bloques e inodos, como hace ext4 en Linux.

> **Estado del proyecto:** la versión que se puede ejecutar hoy es `simulador_v3.py`. La versión final (`simulador.py`, con más funciones y pruebas automáticas) está en preparación.

## Qué hace
- El disco es una lista de bloques, libres u ocupados.
- Cada archivo tiene un inodo que guarda la lista de bloques que ocupa.
- La asignación es indexada: toma los primeros bloques libres, aunque no estén juntos.
- Calcula la ocupación del disco y la fragmentación externa.
- Muestra en cuántos **tramos** contiguos quedó cada archivo (el costo de la asignación indexada).
- Permite desfragmentar el disco y ver el antes y el después.

## Requisitos
Python 3.8 o superior. No necesita instalar librerías.

## Cómo ejecutarlo
```bash
python simulador_v3.py
```
Al iniciar pide la cantidad de bloques del disco (de 1 a 1024).

## Menú
| Opción | Qué hace |
|---|---|
| 1 | Crear un archivo (nombre y tamaño en bloques) |
| 2 | Eliminar un archivo |
| 3 | Mostrar el mapa del disco (una letra por archivo, `.` libre) |
| 4 | Listar archivos: tabla de inodos con bloques y tramos |
| 5 | Métricas: ocupación y archivos dispersos |
| 6 | Fragmentación externa |
| 7 | Desfragmentar el disco |
| 8 | Formatear (crear un disco nuevo) |
| 9 | Demo guiada del caso del taller, paso a paso |
| 0 | Salir |

## Fórmulas
- Ocupación (%) = (bloques ocupados / total de bloques) × 100
- Fragmentación externa (%) = (1 − mayor hueco libre / bloques libres) × 100

## Ejemplo (opción 9)
1. Crear `docA.txt`, `docB.txt` y `docC.txt` de 4 bloques cada uno.
2. Eliminar `docB.txt` → queda un hueco de 4 bloques (fragmentación 7,1 %).
3. Crear `docD.txt` de 6 bloques: entra en los bloques 4-7 y 12-13, en 2 tramos.
4. Eliminar `docA.txt` → la fragmentación sube a 7,4 %.
5. Desfragmentar → la fragmentación vuelve a 0 %.

## Errores que controla
- Nombre de archivo vacío o duplicado
- Archivo no encontrado
- Espacio en disco insuficiente (el disco no queda modificado)
- Tamaños inválidos (0, negativos o texto) y tamaño de disco fuera de rango (1 a 1024)
- Ctrl+C / Ctrl+D: sale sin mostrar errores

## Versiones
| Archivo | Descripción |
|---|---|
| `main.py` | Código base entregado por la cátedra |
| `simulador_v1.py` | + métricas de ocupación y fragmentación externa |
| `simulador_v2.py` | + menú por consola y listado de inodos |
| `simulador_v3.py` | **Versión actual**: mapa por archivo, tramos, desfragmentación, demo guiada, formateo y validaciones |

## En preparación
- `simulador.py`: versión final con la lógica separada de la interfaz.
- Pruebas automáticas en la carpeta `tests/`, que ejecuta GitHub Actions en cada cambio.
