import unittest

from src.compartida import llenar_compartido, llenar_lista


class TestCompartida(unittest.TestCase):
    def test_la_lista_vuelve_vacia(self):
        self.assertEqual(llenar_lista(100, 4), [0] * 100)

    def test_el_array_compartido_si_se_llena(self):
        esperado = [i * i for i in range(100)]
        self.assertEqual(llenar_compartido(100, 4), esperado)
        self.assertEqual(llenar_compartido(1000, 3), [i * i for i in range(1000)])

    def test_devuelve_lista_de_python(self):
        self.assertIsInstance(llenar_compartido(10, 2), list)


if __name__ == "__main__":
    unittest.main()
