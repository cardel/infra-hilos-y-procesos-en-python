import sys
import threading
import unittest

from src.cuenta import abonar_entre_hilos

HILOS = 4
VECES = 50000
INTENTOS = 10


class TestCuenta(unittest.TestCase):
    def setUp(self):
        self.intervalo = sys.getswitchinterval()
        sys.setswitchinterval(1e-6)

    def tearDown(self):
        sys.setswitchinterval(self.intervalo)

    def test_sin_cerrojo_se_pierden_abonos(self):
        saldos = [abonar_entre_hilos(HILOS, VECES) for _ in range(INTENTOS)]
        malos = [s for s in saldos if s != HILOS * VECES]
        self.assertTrue(malos, "ningún intento perdió abonos")

    def test_con_cerrojo_no_se_pierde_ninguno(self):
        for _ in range(INTENTOS):
            self.assertEqual(abonar_entre_hilos(HILOS, VECES, threading.Lock()), HILOS * VECES)


if __name__ == "__main__":
    unittest.main()
