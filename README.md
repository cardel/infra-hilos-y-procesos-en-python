# Hilos y procesos en Python

Infraestructuras Paralelas y Distribuidas
Escuela de Ingeniería de Sistemas y Computación, Universidad del Valle
Carlos Andrés Delgado Saavedra

[![Pruebas](../../actions/workflows/pruebas.yml/badge.svg)](../../actions/workflows/pruebas.yml)

Lo que cada parte necesita de las bibliotecas y herramientas está en
[DOCUMENTACION.md](DOCUMENTACION.md), con ejemplos que corren y los enlaces
a la documentación oficial.

La misma tarea repartida de tres maneras: una tras otra, entre hilos y entre
procesos, con dos tareas de naturaleza distinta, para ver que la respuesta a
«qué conviene» depende de en qué se va el tiempo. Después, lo que pasa cuando
los hilos comparten una variable, lo que pasa cuando los procesos no comparten
nada, y una cola para repartir trabajo entre procesos.

| Parte | Archivo | Qué se resuelve |
|---|---|---|
| 1 | `src/paralelo.py` | La misma lista de tareas en secuencia, con hilos y con procesos |
| 2 | `src/cuenta.py` | Cuatro hilos sobre el mismo saldo: la actualización perdida y el cerrojo |
| 3 | `src/compartida.py` | Procesos que llenan un arreglo: la copia y la memoria compartida |
| 4 | `src/cola.py` | Un grupo de procesos que toma tareas de una cola |

## Requisitos

| Qué | Linux (Debian/Ubuntu) | macOS | Windows |
|---|---|---|---|
| Python 3.10 o más reciente, con `venv` y `pip` | `sudo apt install python3 python3-venv python3-pip` | `brew install python` o el instalador de python.org | instalador de python.org, marcando *Add python.exe to PATH* |
| `pytest` y `pytest-timeout` | `pip install -r requirements.txt` dentro del entorno virtual | igual | igual |

El entorno virtual se activa distinto según el sistema: `source
.venv/bin/activate` en Linux y macOS, `.venv\Scripts\activate` en Windows.
En Windows y en macOS los procesos nuevos arrancan con `spawn` y no con
`fork`: el código que lanza procesos va debajo de `if __name__ ==
"__main__":`, y las funciones que reciben los trabajadores tienen que
estar en un módulo importable, no definidas dentro de otra función. Los
tiempos de hilos y procesos cambian entre sistemas; los que van en el
informe son los de su máquina.

Cómo dejar cada sistema listo, paso a paso, está en
[DOCUMENTACION.md](DOCUMENTACION.md), al final.

## Parte 1: hilos y procesos

### Las dos tareas

En `src/tareas.py`, ya escritas:

- `cuenta_primos(limite)` gasta procesador de principio a fin.
- `consulta_lenta(segundos)` no gasta nada: espera.

### Qué hay que implementar

En `src/paralelo.py` están las tres formas de ejecutar una lista de tareas.
`en_secuencia` ya está; faltan las otras dos:

- `con_hilos`, con `threading.Thread` o con `ThreadPoolExecutor`.
- `con_procesos`, con `multiprocessing.Pool` o con `ProcessPoolExecutor`.

Las dos reciben la función y la lista de argumentos, y devuelven la lista de
resultados **en el mismo orden de los argumentos**. Ese detalle es parte de lo
que se prueba: si se recogen los resultados a medida que van terminando, el
orden se pierde.

### Ejecutar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m pytest tests/test_paralelo.py -v     # correctitud
python -m scripts.medir                        # tiempos
```

En `INFORME.md` va la tabla de tiempos llena y la explicación. Se espera que
aparezcan dos observaciones, sustentadas con los números medidos:

1. En la tarea de cálculo, los hilos no mejoran a la ejecución secuencial, o
   mejoran muy poco. El bloqueo global del intérprete deja correr código de
   Python a un solo hilo a la vez.
2. En la tarea de espera, los hilos sí mejoran, porque el bloqueo se libera
   mientras el hilo espera. Ahí los procesos también sirven, pero cuestan más
   en memoria y en arranque.

## Parte 2: la actualización perdida

Cuatro hilos abonan cien mil veces cada uno sobre el mismo saldo, que arranca
en cero. Aumentar un saldo son tres pasos: leerlo, sumarle uno y escribirlo.
Entre el primero y el tercero el número leído vive dentro del hilo, y si otro
hilo escribe en ese intervalo su escritura queda tapada.

En `src/cuenta.py`, `abonar_sin_cerrojo` ya está y es la versión que pierde
abonos. Falta `abonar_con_cerrojo`: los mismos abonos, con un
`threading.Lock` que deje los tres pasos juntos.

```bash
python -m pytest tests/test_cuenta.py -v
python -m scripts.carrera
```

El script baja el intervalo de conmutación del intérprete con
`sys.setswitchinterval` para que los hilos se alternen mucho más seguido, y
corre cinco veces cada versión. Sin cerrojo se pierde una fracción grande de
los abonos y cada corrida pierde una cantidad distinta; con cerrojo, ninguna.
Las pruebas comprueban las dos cosas.

## Parte 3: los procesos no comparten memoria

`llenar_lista` en `src/compartida.py` reparte el llenado de una lista entre
varios procesos y devuelve la lista sin tocar: cada proceso hijo recibió una
copia, la llenó, y la copia murió con él. Falta `llenar_compartido`, que hace
el mismo reparto sobre un `multiprocessing.Array` de enteros de 64 bits y
devuelve su contenido como lista. Cada proceso escribe posiciones distintas,
así que no hace falta cerrojo.

```bash
python -m pytest tests/test_compartida.py -v
```

## Parte 4: un grupo de procesos con una cola

`con_cola` en `src/cola.py` recibe una función, una lista de argumentos y un
número de procesos trabajadores. El padre pone las tareas en una
`multiprocessing.Queue` como pares `(índice, argumento)`; cada trabajador saca
una, la resuelve y pone `(índice, resultado)` en otra cola; cuando saca el
centinela, termina. Con el índice, el padre devuelve los resultados en el
orden de los argumentos aunque lleguen desordenados.

```bash
python -m pytest tests/test_cola.py -v
python -m scripts.medir
```

La última sección de `medir.py` corre ocho tareas de costo desigual, dos
largas y seis cortas, con uno, dos y cuatro trabajadores. De dos a cuatro casi
no se gana, y la razón va en el informe.

## Qué revisa el flujo de Actions

- Parte 1: que las tres formas den el mismo resultado y respeten el orden;
  que con procesos la tarea de cálculo baje del 70 % del tiempo secuencial y
  que con hilos la de espera baje a la mitad.
- Parte 2: que sin cerrojo se pierdan abonos en al menos uno de diez
  intentos, y que con cerrojo no se pierda ninguno en diez.
- Parte 3: que la lista vuelva sin tocar y que el arreglo compartido vuelva
  lleno.
- Parte 4: que la cola devuelva lo mismo que la ejecución en secuencia, en
  orden, con menos trabajadores que tareas, con más, y sin tareas; y que con
  cuatro trabajadores las tareas desiguales bajen del 70 % del tiempo
  secuencial.
- Que `INFORME.md` tenga las tablas y las explicaciones.

Cada parte es un job aparte: la lista de verificaciones del commit dice cuál
quedó en verde y cuál no, y la pestaña del run trae un resumen con la salida
de cada programa y el conteo de partes en verde. Cuando una verificación de
tiempos falla, el flujo repite la corrida una vez antes de marcar rojo, y el
error queda anotado sobre el archivo de esa parte. Un push nuevo cancela el
run anterior.

Los tiempos que aparecen en el registro de la ejecución son de un servidor
compartido; los que valen para el informe son los de su máquina. Las pruebas
de `pytest` se cortan a los dos minutos: una cola sin centinelas se queda
esperando para siempre, y así el flujo no se queda con ella.
