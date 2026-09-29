"""Un grupo de procesos que toman tareas de una cola a medida que se
desocupan. La cola reparte por demanda: el proceso que termina antes toma la
siguiente tarea, y ninguno se queda esperando a los demás."""

import multiprocessing


def trabajador(funcion, cola_tareas, cola_resultados):
    while True:
        i, arg = cola_tareas.get()
        if i is None:
            break
        resultado = funcion(arg)
        cola_resultados.put((i, resultado))


def con_cola(funcion, argumentos, procesos):
    """TODO: ejecutar funcion(a) para cada a de argumentos con `procesos`
    procesos trabajadores, y devolver los resultados en el orden de los
    argumentos.

    Dos colas: una de tareas, donde el padre pone (indice, argumento), y una
    de resultados, donde cada trabajador pone (indice, resultado). Los
    trabajadores terminan cuando sacan un centinela (por ejemplo None) de la
    cola de tareas; el padre pone tantos centinelas como trabajadores. El
    índice es lo que permite devolver los resultados en orden aunque lleguen
    desordenados."""
    q1 = multiprocessing.Queue()
    q2 = multiprocessing.Queue()

    # Llenar la cola de tareas con (índice, argumento)
    for i, arg in enumerate(argumentos):
        q1.put((i, arg))

    # lanzar los procesos trabajadores
    procesos_trabajadores = []

    # colocar centinelas en la cola de tareas para que los trabajadores terminen
    for _ in range(procesos):
        q1.put((None, None))

    for p in range(procesos):
        p = multiprocessing.Process(target=trabajador, args=(funcion, q1, q2))
        p.start()
        procesos_trabajadores.append(p)

    for p in procesos_trabajadores:
        p.join()

    # Recoger los resultados de la cola de resultados
    resultados = [0] * len(argumentos)
    for _ in range(len(argumentos)):
        i, res = q2.get()
        resultados[i] = res
    return resultados
