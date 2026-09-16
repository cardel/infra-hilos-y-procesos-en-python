"""Un grupo de procesos que toman tareas de una cola a medida que se
desocupan. La cola reparte por demanda: el proceso que termina antes toma la
siguiente tarea, y ninguno se queda esperando a los demás."""
import multiprocessing


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
    raise NotImplementedError
