import unittest

from src.cola import con_cola
from src.paralelo import en_secuencia
from src.tareas import consulta_lenta, cuenta_primos


class TestCola(unittest.TestCase):
    def test_da_lo_mismo_que_en_secuencia(self):
        args = [1000, 2000, 3000, 500, 4000]
        self.assertEqual(con_cola(cuenta_primos, args, 2), en_secuencia(cuenta_primos, args))

    def test_el_orden_se_respeta_con_pocos_trabajadores(self):
        self.assertEqual(con_cola(consulta_lenta, [0.3, 0.1, 0.2, 0.05], 2), [0.3, 0.1, 0.2, 0.05])

    def test_mas_trabajadores_que_tareas(self):
        self.assertEqual(con_cola(cuenta_primos, [100], 4), [25])

    def test_sin_tareas(self):
        self.assertEqual(con_cola(cuenta_primos, [], 3), [])


if __name__ == "__main__":
    unittest.main()
