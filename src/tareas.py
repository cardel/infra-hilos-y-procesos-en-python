"""Dos tareas con perfiles opuestos: una gasta procesador y la otra espera."""
import time


def cuenta_primos(limite):
    """Cuenta los primos menores que el límite. Gasta procesador, no espera."""
    total = 0
    for num in range(2, limite):
        primo = True
        for div in range(2, int(num**0.5) + 1):
            if num % div == 0:
                primo = False
                break
        if primo:
            total += 1
    return total


def consulta_lenta(segundos):
    """Simula una consulta a un servicio externo: el procesador queda libre."""
    time.sleep(segundos)
    return segundos
