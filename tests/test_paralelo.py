import unittest

from src.paralelo import con_hilos, con_procesos, en_secuencia
from src.tareas import consulta_lenta, cuenta_primos


class TestParalelo(unittest.TestCase):
    def test_secuencia_es_la_referencia(self):
        self.assertEqual(en_secuencia(cuenta_primos, [10, 100]), [4, 25])

    def test_hilos_dan_el_mismo_resultado(self):
        esperado = en_secuencia(cuenta_primos, [1000, 2000, 3000])
        self.assertEqual(con_hilos(cuenta_primos, [1000, 2000, 3000]), esperado)

    def test_procesos_dan_el_mismo_resultado(self):
        esperado = en_secuencia(cuenta_primos, [1000, 2000, 3000])
        self.assertEqual(con_procesos(cuenta_primos, [1000, 2000, 3000]), esperado)

    def test_el_orden_se_respeta(self):
        self.assertEqual(con_hilos(consulta_lenta, [0.3, 0.1, 0.2]), [0.3, 0.1, 0.2])
        self.assertEqual(con_procesos(consulta_lenta, [0.3, 0.1, 0.2]), [0.3, 0.1, 0.2])


if __name__ == "__main__":
    unittest.main()
