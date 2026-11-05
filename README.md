# Simulador de asignación de espacio en disco

Simula cómo un sistema de archivos guarda archivos en un disco usando bloques e inodos, como hace ext4 en Linux.

## Qué hace
- El disco es una lista de bloques, libres u ocupados.
- Cada archivo tiene un inodo con la lista de bloques que ocupa.
- La asignación es indexada: toma los primeros bloques libres, aunque no estén juntos.
- Calcula la ocupación del disco y la fragmentación externa.

## Requisitos
Python 3.8 o superior. No necesita instalar librerías.

## Cómo ejecutarlo
```bash
python simulador.py
```
Al iniciar pide la cantidad de bloques del disco (por ejemplo, 64).

## Menú
| Opción | Qué hace |
|---|---|
| 1 | Crear un archivo (nombre y tamaño en bloques) |
| 2 | Eliminar un archivo |
| 3 | Mostrar el mapa del disco (`[O]` ocupado, `[L]` libre) |
| 4 | Listar archivos y sus bloques (inodos) |
| 5 | Métricas: total, ocupados, libres y % de ocupación |
| 6 | Fragmentación externa |
| 0 | Salir |

## Fórmulas
- Ocupación (%) = (bloques ocupados / total de bloques) × 100
- Fragmentación externa (%) = (1 − mayor hueco libre / bloques libres) × 100

## Ejemplo
1. Crear `docA.txt`, `docB.txt` y `docC.txt` de 4 bloques cada uno.
2. Eliminar `docB.txt`.
3. Crear `docD.txt` de 6 bloques.
4. Ver el mapa y las métricas.

El archivo `docD.txt` entra aunque el hueco libre no sea contiguo, porque el inodo guarda la lista de bloques.

## Errores que controla
- Nombre de archivo duplicado
- Archivo no encontrado
- Espacio en disco insuficiente
- Nombre vacío o tamaño inválido
