"""Varios hilos abonan sobre el mismo saldo. Aumentar un saldo son tres
pasos: leerlo, sumarle uno y escribirlo. Entre el primero y el tercero el
número leído vive dentro del hilo, y si otro hilo escribe en ese intervalo su
escritura queda tapada: es una actualización perdida."""

import threading


class Cuenta:
    def __init__(self):
        self.saldo = 0

    def consultar(self):
        return self.saldo

    def guardar(self, valor):
        self.saldo = valor


def abonar_sin_cerrojo(cuenta, veces, arranque):
    """Lo que hace cada hilo cuando nadie protege el saldo. Está escrito así
    a propósito: es la versión que pierde abonos."""
    arranque.wait()  # todos los hilos salen juntos
    for _ in range(veces):
        cuenta.guardar(cuenta.consultar() + 1)


def abonar_con_cerrojo(cuenta, veces, arranque, cerrojo):
    """TODO: los mismos abonos, sin perder ninguno. Los tres pasos de cada
    abono tienen que ocurrir sin que otro hilo se meta en la mitad."""
    arranque.wait()  # todos los hilos salen juntos
    with cerrojo:
        for _ in range(veces):
            cuenta.guardar(cuenta.consultar() + 1)


def abonar_entre_hilos(hilos, veces, cerrojo=None):
    """Lanza `hilos` hilos que abonan `veces` cada uno y devuelve el saldo
    final. Con cerrojo usa abonar_con_cerrojo; sin él, abonar_sin_cerrojo."""
    cuenta = Cuenta()
    arranque = threading.Barrier(hilos)
    if cerrojo is None:
        objetivo, args = abonar_sin_cerrojo, (cuenta, veces, arranque)
    else:
        objetivo, args = abonar_con_cerrojo, (cuenta, veces, arranque, cerrojo)
    trabajadores = [threading.Thread(target=objetivo, args=args) for _ in range(hilos)]
    for t in trabajadores:
        t.start()
    for t in trabajadores:
        t.join()
    return cuenta.saldo
