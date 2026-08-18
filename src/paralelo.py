"""Tres formas de ejecutar la misma lista de tareas.

Cada función recibe la función a ejecutar y la lista de argumentos, y devuelve
la lista de resultados en el mismo orden de los argumentos.
"""


def en_secuencia(funcion, argumentos):
    """Ejecuta las tareas una tras otra. Es el punto de comparación."""
    return [funcion(a) for a in argumentos]


def con_hilos(funcion, argumentos):
    """TODO: ejecutar con varios hilos, uno por argumento.

    Sirven threading.Thread o concurrent.futures.ThreadPoolExecutor. El orden
    de los resultados tiene que corresponder al de los argumentos.
    """
    raise NotImplementedError


def con_procesos(funcion, argumentos):
    """TODO: ejecutar con varios procesos, uno por argumento.

    Sirven multiprocessing.Pool o concurrent.futures.ProcessPoolExecutor.
    """
    raise NotImplementedError
