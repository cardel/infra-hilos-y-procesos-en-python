# Hilos y procesos en Python

Infraestructuras Paralelas y Distribuidas
Escuela de Ingeniería de Sistemas y Computación, Universidad del Valle
Carlos Andrés Delgado Saavedra

La misma tarea repartida de tres maneras: una tras otra, entre hilos y entre
procesos. Con dos tareas de naturaleza distinta, para ver que la respuesta a
«qué conviene» depende de en qué se va el tiempo.

## Las dos tareas

En `src/tareas.py`, ya escritas:

- `cuenta_primos(limite)` gasta procesador de principio a fin.
- `consulta_lenta(segundos)` no gasta nada: espera.

## Qué hay que implementar

En `src/paralelo.py` están las tres formas de ejecutar una lista de tareas.
`en_secuencia` ya está; faltan las otras dos:

- `con_hilos`, con `threading.Thread` o con `ThreadPoolExecutor`.
- `con_procesos`, con `multiprocessing.Pool` o con `ProcessPoolExecutor`.

Las dos reciben la función y la lista de argumentos, y devuelven la lista de
resultados **en el mismo orden de los argumentos**. Ese detalle es parte de lo
que se prueba: si se recogen los resultados a medida que van terminando, el
orden se pierde.

## Ejecutar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m pytest tests/ -v     # correctitud
python -m scripts.medir        # tiempos
```

## Qué hay que entregar

Además del código, `INFORME.md` con la tabla de tiempos llena y la explicación.
Se espera que aparezcan dos observaciones y que estén sustentadas con los
números medidos:

1. En la tarea de cálculo, los hilos no mejoran a la ejecución secuencial, o
   mejoran muy poco. El bloqueo global del intérprete deja correr código de
   Python a un solo hilo a la vez.
2. En la tarea de espera, los hilos sí mejoran, porque el bloqueo se libera
   mientras el hilo espera. Ahí los procesos también sirven, pero cuestan más
   en memoria y en arranque.

## Qué revisa el flujo de Actions

Que las tres formas den el mismo resultado, que se respete el orden, que la
medición corra y que `INFORME.md` no quede en blanco. Los tiempos que aparecen
en el registro de la ejecución son de un servidor compartido; los que valen
para el informe son los de su máquina.
