"""Mide las tres formas de ejecución sobre una tarea de cálculo y una de espera."""
import time

from src.paralelo import con_hilos, con_procesos, en_secuencia
from src.tareas import consulta_lenta, cuenta_primos

CALCULO = [200000, 200000, 200000, 200000]
ESPERA = [1, 1, 1, 1]


def medir(nombre, ejecutor, funcion, argumentos):
    inicio = time.perf_counter()
    ejecutor(funcion, argumentos)
    print(f"{nombre:12s} {(time.perf_counter() - inicio) * 1000:8.1f} ms")


if __name__ == "__main__":
    print("Tarea de cálculo: contar primos")
    medir("secuencia", en_secuencia, cuenta_primos, CALCULO)
    medir("hilos", con_hilos, cuenta_primos, CALCULO)
    medir("procesos", con_procesos, cuenta_primos, CALCULO)

    print("\nTarea de espera: consultas lentas")
    medir("secuencia", en_secuencia, consulta_lenta, ESPERA)
    medir("hilos", con_hilos, consulta_lenta, ESPERA)
    medir("procesos", con_procesos, consulta_lenta, ESPERA)
