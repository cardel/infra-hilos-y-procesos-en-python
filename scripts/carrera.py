"""Cinco corridas con cerrojo y cinco sin él, cuatro hilos y cien mil abonos
por hilo. El intervalo de conmutación del intérprete se baja para que los
hilos se alternen mucho más seguido de lo normal."""
import sys
import threading

from src.cuenta import abonar_entre_hilos

HILOS = 4
VECES = 100000

if __name__ == "__main__":
    sys.setswitchinterval(1e-6)
    esperado = HILOS * VECES
    print("Sin cerrojo")
    for _ in range(5):
        saldo = abonar_entre_hilos(HILOS, VECES)
        print(f"  esperado {esperado}  obtenido {saldo:7d}  perdidas {esperado - saldo:7d}")
    print("Con cerrojo")
    for _ in range(5):
        saldo = abonar_entre_hilos(HILOS, VECES, threading.Lock())
        print(f"  esperado {esperado}  obtenido {saldo:7d}  perdidas {esperado - saldo:7d}")
