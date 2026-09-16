# Documentación de apoyo: hilos y procesos en Python

Aquí está lo que cada parte del README necesita de la biblioteca estándar:
hilos, ejecutores, procesos, cerrojos, memoria compartida y colas, con un
ejemplo corrido por parte. Las secciones siguen el orden y el nombre de las
partes del README. Cada ejemplo corre tal cual y trae su salida; los
enlaces van al final de cada sección.

## Parte 1: hilos y procesos

### Lo que se usa

- `threading.Thread(target=funcion, args=(a, b))` crea un hilo que ejecutará
  `funcion(a, b)`. `args` es una tupla: con un solo argumento se escribe
  `(a,)`. El hilo no corre hasta `start()`.
- `hilo.start()` arranca el hilo y devuelve de inmediato; `hilo.join()`
  bloquea hasta que ese hilo termine. Un hilo no devuelve nada: lo que
  calcula se deja en una estructura que el hilo principal pueda leer.
- `concurrent.futures.ThreadPoolExecutor(max_workers=n)` y
  `ProcessPoolExecutor(max_workers=n)` reparten trabajo entre `n` hilos o
  `n` procesos. Se usan con `with`, que al salir espera a que todo termine.
- `ejecutor.map(funcion, iterable)` aplica la función a cada elemento y
  devuelve un iterador con los resultados en el orden del iterable,
  aunque terminen en otro orden. Se convierte con `list(...)`. Con varios
  iterables, `map(funcion, xs, ys)` pasa un elemento de cada uno por llamada,
  como el `map` de Python.
- `ejecutor.submit(funcion, arg)` lanza una sola llamada y devuelve un
  `Future`; `futuro.result()` espera y entrega el valor.
  `concurrent.futures.as_completed(futuros)` los entrega según van
  terminando, no en el orden en que se enviaron.
- `multiprocessing.Pool(processes=n)` es la versión más vieja del grupo de
  procesos; `pool.map(funcion, iterable)` devuelve una lista en orden y
  `pool.apply_async(funcion, (a, b))` lanza una sola llamada y devuelve un
  objeto cuyo `get()` espera el resultado. También se usa con `with`.
- `multiprocessing.get_start_method()` dice cómo se arrancan los procesos
  hijos. Con `fork` el hijo nace como copia del padre; con `spawn` y
  `forkserver` nace un intérprete nuevo que importa el módulo principal y
  recibe la función y los argumentos serializados con `pickle`. Linux usa
  `fork` hasta Python 3.13 y `forkserver` desde 3.14; macOS y Windows usan
  `spawn`. Por eso el código que crea procesos va debajo de
  `if __name__ == "__main__":`, y la función que corre en el hijo se define
  en el nivel superior de un módulo.
- El bloqueo global del intérprete (GIL) es un cerrojo que deja ejecutar
  código de Python a un solo hilo a la vez dentro de un proceso, así que
  varios hilos que calculan se turnan en vez de repartirse los núcleos. Se
  libera mientras un hilo espera (`time.sleep`, una lectura de red o de
  disco), y cada proceso tiene su propio intérprete con su propio GIL.
- `time.perf_counter()` da un reloj de alta resolución en segundos; la
  diferencia entre dos lecturas es lo que se mide.

### Ejemplo

Cuatro hilos suman cada uno un tramo de 1 a 1.000. Como un hilo no devuelve
valor, cada uno escribe su parcial en la casilla que le corresponde.

```python
"""Cuatro hilos suman cada uno un tramo de 1..1000 y dejan su parcial en la
posición que le toca; el hilo principal espera a todos y suma los parciales."""
import threading


def suma_tramo(ini, fin, parciales, pos):
    parciales[pos] = sum(range(ini, fin))


parciales = [0] * 4                      # una casilla por hilo, nadie pisa a otro
hilos = []
for i in range(4):
    h = threading.Thread(target=suma_tramo, args=(i * 250 + 1, (i + 1) * 250 + 1, parciales, i))
    hilos.append(h)
    h.start()                            # arranca y sigue sin esperar
for h in hilos:
    h.join()                             # espera a que cada uno termine
print("parciales:", parciales)
print("total:", sum(parciales), "esperado:", 1000 * 1001 // 2)
```

```bash
python hilos_basico.py
```

```
parciales: [31375, 93875, 156375, 218875]
total: 500500 esperado: 500500
```

Los ejecutores reciben tareas sueltas con `submit`, que devuelve un `Future`
por cada una. Este programa lanza a la vez una tarea que calcula y otra que
espera, y después muestra que `as_completed` entrega tres esperas de 0,3,
0,1 y 0,2 segundos por tiempo de llegada, no en el orden en que se enviaron.
Al final, `map` con dos iterables busca en tres tramos el número con la
sucesión de Collatz más larga; ese cálculo gasta procesador y va por
procesos.

```python
"""submit lanza una tarea y devuelve un Future; result() espera su valor.
as_completed entrega los futuros según van terminando. map acepta un iterable
por parámetro de la función y empareja cada resultado con sus argumentos."""
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed


def pasos_collatz(n):
    """Cuántos pasos tarda n en llegar a 1. Gasta procesador."""
    pasos = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        pasos += 1
    return pasos


def espera(segundos):
    time.sleep(segundos)
    return segundos


def mas_largo(ini, fin):
    """El número de [ini, fin) que más pasos tarda, y cuántos son."""
    n = max(range(ini, fin), key=pasos_collatz)
    return n, pasos_collatz(n)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as ejecutor:
        calculo = ejecutor.submit(pasos_collatz, 6171)   # dos tareas distintas a la vez
        pausa = ejecutor.submit(espera, 0.2)
        print("submit:", calculo.result(), "pasos y", pausa.result(), "s de espera")
        futuros = [ejecutor.submit(espera, t) for t in (0.3, 0.1, 0.2)]
        print("as_completed:", [f.result() for f in as_completed(futuros)])

    inicios = [1, 50_000, 100_000]
    finales = [50_000, 100_000, 150_000]
    with ProcessPoolExecutor(max_workers=3) as ejecutor:
        for ini, (n, pasos) in zip(inicios, ejecutor.map(mas_largo, inicios, finales)):
            print(f"desde {ini:>7}: el {n} tarda {pasos} pasos")
```

```bash
python ejecutores.py
```

```
submit: 261 pasos y 0.2 s de espera
as_completed: [0.1, 0.2, 0.3]
desde       1: el 35655 tarda 323 pasos
desde   50000: el 77031 tarda 350 pasos
desde  100000: el 142587 tarda 374 pasos
```

El tercer programa es el efecto del GIL medido: la suma de los pasos de
Collatz de todos los números menores que 240.000, partida en cuatro tramos,
en secuencia, con cuatro hilos y con cuatro procesos de un
`multiprocessing.Pool`. Cada forma devuelve la suma total, así que las tres
tienen que dar el mismo número.

```python
"""La misma cuenta de pasos de Collatz sobre cuatro tramos: en secuencia, con
cuatro hilos y con cuatro procesos. Con el bloqueo global del intérprete los
hilos no reparten el cálculo; los procesos sí."""
import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor

TRAMOS = [(1, 60_000), (60_000, 120_000), (120_000, 180_000), (180_000, 240_000)]


def pasos_en(ini, fin):
    """Suma los pasos de Collatz de todos los números de [ini, fin)."""
    total = 0
    for n in range(ini, fin):
        while n != 1:
            n = n // 2 if n % 2 == 0 else 3 * n + 1
            total += 1
    return total


def todo_en_secuencia():
    return sum(pasos_en(ini, fin) for ini, fin in TRAMOS)


def repartido_en_hilos():
    with ThreadPoolExecutor(max_workers=4) as ejecutor:
        futuros = [ejecutor.submit(pasos_en, ini, fin) for ini, fin in TRAMOS]
        return sum(f.result() for f in futuros)


def repartido_en_procesos():
    with multiprocessing.Pool(processes=4) as pool:
        pendientes = [pool.apply_async(pasos_en, (ini, fin)) for ini, fin in TRAMOS]
        return sum(p.get() for p in pendientes)


def cronometrar(nombre, funcion):
    inicio = time.perf_counter()
    resultado = funcion()
    ms = f"{(time.perf_counter() - inicio) * 1000:8,.1f}".translate(str.maketrans(",.", ".,"))
    print(f"{nombre:10s} {ms} ms  {resultado}")


if __name__ == "__main__":
    print("arranque de procesos:", multiprocessing.get_start_method())
    cronometrar("secuencia", todo_en_secuencia)
    cronometrar("hilos", repartido_en_hilos)
    cronometrar("procesos", repartido_en_procesos)
```

```bash
python pool_y_gil.py
```

```
arranque de procesos: forkserver
secuencia   2.131,4 ms  27969646
hilos       2.124,8 ms  27969646
procesos      737,9 ms  27969646
```

Los cuatro hilos tardan lo mismo que la secuencia: se turnan el GIL. Los
cuatro procesos bajan a cerca de la tercera parte porque cada uno tiene su
intérprete; lo que falta para la cuarta parte es el arranque de los cuatro
intérpretes. Con la tarea de espera pasa lo contrario, y eso es lo que la
tabla del informe tiene que mostrar.

### Lo que suele fallar

- **`start()` y `join()` en el mismo ciclo.** Arrancar un hilo y esperarlo
  antes de arrancar el siguiente es una ejecución secuencial con disfraz.
  Cuatro esperas de un segundo tardan 4,00 s, y el flujo lo dice: *con hilos
  la tarea de espera no bajo a la mitad: revise que con_hilos lance los hilos
  a la vez*. Primero todos los `start()`, después todos los `join()`.
- **Recoger los resultados a medida que llegan.** Con `as_completed`, o
  con una lista a la que cada hilo hace `append` al terminar, el orden es el
  de llegada: `[0.1, 0.2, 0.3]` para `[0.3, 0.1, 0.2]`. La prueba
  `test_el_orden_se_respeta` falla. `map` conserva el orden; con hilos
  sueltos, cada uno escribe en la posición de su argumento.
- **Una `lambda` o una función anidada como tarea de un proceso.** El hijo
  la recibe por `pickle` y `pickle` solo serializa funciones que se puedan
  encontrar por nombre en un módulo: `_pickle.PicklingError: Can't pickle
  <function <lambda> ...>: it's not found as __main__.<lambda>`. La tarea se
  define en el nivel superior del módulo.
- **Crear procesos fuera de `if __name__ == "__main__":`.** Con `spawn` o
  `forkserver` el hijo importa el módulo principal, encuentra el código que
  crea procesos y arranca otro hijo, que hace lo mismo. Python lo corta con
  `RuntimeError: An attempt has been made to start a new process before the
  current process has finished its bootstrapping phase`. En Actions corre
  Python 3.11 con `fork` y no se ve; en su máquina con 3.14 o en macOS, sí.
- **Cero trabajadores.** `ThreadPoolExecutor(max_workers=0)` da
  `ValueError: max_workers must be greater than 0` y `Pool(0)` da
  `ValueError: Number of processes must be at least 1`. Si el número de
  trabajadores sale del largo de la lista, hay que cubrir la lista vacía.

### Enlaces

- [threading: Thread objects](https://docs.python.org/3/library/threading.html#thread-objects):
  la firma de `Thread`, `start`, `join` y `is_alive`.
- [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html):
  `ThreadPoolExecutor`, `ProcessPoolExecutor`, `map`, `submit`, `Future` y
  `as_completed`, con la nota de que `map` respeta el orden.
- [multiprocessing: Pool](https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing.pool):
  `Pool.map`, `imap`, `apply_async` y el cierre con `with`.
- [multiprocessing: Contexts and start methods](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods):
  qué hace cada método de arranque y cuál es el predeterminado en cada
  sistema.
- [Glosario: global interpreter lock](https://docs.python.org/3/glossary.html#term-global-interpreter-lock):
  la definición del GIL en un párrafo.
- [__main__: Idiomatic usage](https://docs.python.org/3/library/__main__.html):
  por qué el código que arranca el programa va debajo de
  `if __name__ == "__main__":`.

## Parte 2: la actualización perdida

### Lo que se usa

- `threading.Lock()` crea un cerrojo. `cerrojo.acquire()` lo toma y, si otro
  hilo lo tiene, espera; `cerrojo.release()` lo suelta. Uno solo lo tiene a
  la vez.
- `with cerrojo:` toma el cerrojo al entrar al bloque y lo suelta al salir,
  también si adentro salta una excepción. Lo que va dentro del bloque
  ocurre sin que otro hilo que use el mismo cerrojo se meta en la mitad.
- El cerrojo es uno solo y lo comparten todos los hilos: se crea afuera y
  se pasa como argumento, igual que la cuenta.
- `threading.Barrier(n)` y `barrera.wait()`: cada hilo que llama a `wait()`
  se queda esperando hasta que hayan llegado `n`; entonces salen todos a la
  vez. En `src/cuenta.py` ya está creada con el número de hilos y se llama
  `arranque`.
- `sys.setswitchinterval(segundos)` fija cada cuánto el intérprete le pide
  al hilo que tiene el GIL que lo suelte para que entre otro; por defecto
  son 0,005 s (`sys.getswitchinterval()`). Con `1e-6` los hilos se alternan
  miles de veces más seguido y la actualización perdida aparece en cada
  corrida.
- `conteo[k] = conteo[k] + 1`, `saldo += 1` y `guardar(consultar() + 1)` son
  tres pasos: leer, sumar, escribir. El GIL hace que cada paso se ejecute
  entero; que los tres vayan juntos es cosa del cerrojo.

### Ejemplo

Cuatro hilos cuentan las letras del mismo texto en un diccionario
compartido. Cada letra debería quedar con cuatro veces su frecuencia; sin
cerrojo, dos hilos que leen el mismo valor se tapan la suma.

```python
"""Cuatro hilos cuentan las letras del mismo texto en un diccionario
compartido. Cada conteo es leer, sumar uno y escribir: sin cerrojo, dos hilos
que leen el mismo valor tapan la suma del otro."""
import sys
import threading

TEXTO = "paralela" * 20000          # 160.000 letras
HILOS = 4


def contar(conteo, cerrojo=None):
    for letra in TEXTO:
        if cerrojo is None:
            conteo[letra] = conteo.get(letra, 0) + 1
        else:
            with cerrojo:             # adquiere al entrar, libera al salir
                conteo[letra] = conteo.get(letra, 0) + 1


def correr(cerrojo):
    conteo = {}
    hilos = [threading.Thread(target=contar, args=(conteo, cerrojo)) for _ in range(HILOS)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    return conteo


if __name__ == "__main__":
    sys.setswitchinterval(1e-6)       # el intérprete cambia de hilo mucho más seguido
    esperado = HILOS * TEXTO.count("a")
    for nombre, cerrojo in (("sin cerrojo", None), ("con cerrojo", threading.Lock())):
        conteo = correr(cerrojo)
        print(f"{nombre}: 'a' esperado {esperado}, obtenido {conteo['a']}, perdidas {esperado - conteo['a']}")
```

```bash
python cerrojo.py
```

```
sin cerrojo: 'a' esperado 240000, obtenido 166556, perdidas 73444
con cerrojo: 'a' esperado 240000, obtenido 240000, perdidas 0
```

Se perdieron 73.444 de 240.000 conteos, algo más del 30 %. Cada corrida
pierde una cantidad distinta: en tres corridas seguidas salieron 80.592,
77.014 y 69.399.

### Lo que suele fallar

- **El cerrojo se crea dentro de la función.** `cerrojo = threading.Lock()`
  en el cuerpo de la función que corre cada hilo le da a cada hilo un
  cerrojo propio, y ninguno protege del otro. Se siguen perdiendo conteos
  (37.535 en una corrida del ejemplo con ese cambio) y en el ejercicio la
  prueba `test_con_cerrojo_no_se_pierde_ninguno` falla. El cerrojo llega por
  argumento y es el mismo para todos.
- **El cerrojo cubre un solo paso.** Proteger solo `consultar()` o solo
  `guardar()` no sirve: la lectura y la escritura tienen que estar dentro
  del mismo `with`, con la suma en la mitad. Si entre leer y escribir el
  cerrojo se suelta, el intervalo sigue abierto.
- **`acquire()` sin `release()`.** Si una rama sale de la función sin
  soltar, los demás hilos esperan para siempre y `join()` nunca vuelve; la
  prueba se corta con `Failed: Timeout (>120.0s) from pytest-timeout`. Con
  `with` no hay forma de olvidarlo.
- **El intervalo de conmutación por defecto.** Con los 0,005 s normales, la
  versión sin cerrojo a veces no pierde nada: en tres corridas del ejemplo
  salieron 0, 0 y 24.960 perdidas. Las pruebas bajan el intervalo en
  `setUp` y lo restauran en `tearDown`; si el script propio no lo baja, los
  números no se parecen a los del informe.
- **Tomar el mismo `Lock` dos veces en el mismo hilo.** `Lock` no sabe quién
  lo tiene: un `with cerrojo:` dentro de otro `with cerrojo:` se queda
  esperando a sí mismo. Para eso existe `threading.RLock`, pero aquí no hace
  falta anidar.

### Enlaces

- [threading: Lock objects](https://docs.python.org/3/library/threading.html#lock-objects):
  `acquire`, `release`, `locked` y la diferencia con `RLock`.
- [threading: Using locks in the with statement](https://docs.python.org/3/library/threading.html#using-locks-conditions-and-semaphores-in-the-with-statement):
  la equivalencia entre `with cerrojo:` y el par `acquire`/`release`.
- [threading: Barrier objects](https://docs.python.org/3/library/threading.html#barrier-objects):
  cómo funciona `wait()` y qué pasa si un hilo no llega.
- [sys.setswitchinterval](https://docs.python.org/3/library/sys.html#sys.setswitchinterval):
  qué controla el intervalo y el valor por defecto.
- [FAQ: What kinds of global value mutation are thread-safe?](https://docs.python.org/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe):
  qué operaciones sí son atómicas bajo el GIL y por qué `x += 1` no lo es.
- [The with statement](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement):
  qué hace `with` con cualquier objeto que tenga `__enter__` y `__exit__`.

## Parte 3: los procesos no comparten memoria

### Lo que se usa

- `multiprocessing.Process(target=funcion, args=(...))`, `start()` y
  `join()`, con la misma forma que `Thread`. La diferencia es que el hijo
  trabaja sobre su propia memoria: una lista que recibe es una copia, y lo
  que le escriba se queda en el hijo.
- `multiprocessing.Array(tipo, n, lock=True)` reserva `n` casillas en
  memoria compartida, que todos los procesos que la reciban ven como la
  misma. El tipo va con los códigos de `array`: `'q'` es entero con signo
  de 64 bits, `'i'` de 32 bits, `'d'` flotante de doble precisión. El
  segundo argumento puede ser un número (casillas en cero) o una lista con
  los valores iniciales.
- Con `lock=True` (el valor por defecto) el arreglo llega envuelto en un
  `SynchronizedArray` que trae su propio cerrojo, `get_lock()`, y el
  arreglo crudo se saca con `get_obj()`. Con `lock=False` llega el arreglo
  de `ctypes` directo. Cuando cada proceso escribe posiciones distintas, el
  cerrojo no hace falta.
- Se lee y se escribe con índices, `arreglo[i] = v`, y tiene `len()`. Para
  devolverlo como lista de Python: `list(arreglo)` o `arreglo[:]`. El
  arreglo no es una lista, y una prueba que pida `list` lo rechaza.
- `multiprocessing.Value(tipo, inicial)` es la versión de una sola casilla:
  se lee y se escribe por `.value`.

### Ejemplo

Cada proceso cuenta los múltiplos de 7 de su tramo y deja el conteo en su
casilla del arreglo compartido; el padre suma las casillas. A la par, el
mismo conteo se suma en una variable normal, que el padre nunca ve cambiar.

```python
"""Cada proceso cuenta los múltiplos de 7 de su tramo y deja el conteo en su
casilla de un arreglo compartido; el padre lo lee y suma. Al lado, la misma
cuenta en una variable normal, que el padre nunca ve cambiar."""
import multiprocessing

N = 10_000_000
PROCESOS = 4
suma_normal = 0                          # cada hijo recibe una copia de esto


def contar_tramo(ini, fin, conteos, pos):
    global suma_normal
    total = sum(1 for i in range(ini, fin) if i % 7 == 0)
    conteos[pos] = total                  # escribe en memoria compartida
    suma_normal += total                  # escribe en la copia del hijo


if __name__ == "__main__":
    conteos = multiprocessing.Array("q", PROCESOS, lock=False)   # 4 enteros de 64 bits
    paso = N // PROCESOS
    hijos = [multiprocessing.Process(target=contar_tramo, args=(p * paso, (p + 1) * paso, conteos, p))
             for p in range(PROCESOS)]
    for h in hijos:
        h.start()
    for h in hijos:
        h.join()
    print("tipo:", type(conteos).__name__, "| largo:", len(conteos))
    print("como lista:", list(conteos))
    print("total compartido:", sum(conteos), "| esperado:", len(range(0, N, 7)))
    print("suma_normal en el padre:", suma_normal)
```

```bash
python arreglo_compartido.py
```

```
tipo: c_long_Array_4 | largo: 4
como lista: [357143, 357143, 357143, 357143]
total compartido: 1428572 | esperado: 1428572
suma_normal en el padre: 0
```

El arreglo volvió lleno y `suma_normal` sigue en cero: los cuatro hijos la
incrementaron en su copia y la copia murió con cada uno.

### Lo que suele fallar

- **Devolver el arreglo en vez de una lista.** `test_devuelve_lista_de_python`
  pide una `list` y con el arreglo dice `AssertionError: <SynchronizedArray
  wrapper for <multiprocessing.sharedctypes.c_long_Array_10 object ...>> is
  not an instance of <class 'list'>`. Se devuelve `list(arreglo)`.
- **Tipo `'i'` en vez de `'q'`.** Un entero de 32 bits guarda hasta
  2.147.483.647 y por encima no avisa: `3_000_000_000` queda como
  `-1294967296`. Con `i * i` alcanza para las pruebas, pero el README pide
  64 bits y con `n` grande el cuadrado se sale.
- **El último tramo no llega a `n`.** Si `n` no es múltiplo del número de
  procesos, `(p + 1) * paso` para el último deja casillas sin tocar y la
  lista vuelve con ceros al final. La prueba con 1.000 casillas y 3 procesos
  lo detecta. `llenar_lista` ya resuelve el reparto y se puede calcar.
- **El arreglo se crea dentro de la función del hijo.** Entonces cada
  proceso reserva el suyo y el padre no recibe ninguno. Se reserva en el
  padre antes de crear los procesos y se pasa por `args`.
- **Leer antes del `join()`.** Sin esperar a los hijos, el padre lee el
  arreglo mientras se está llenando y devuelve ceros a medias. Los
  `join()` van todos antes de `list(arreglo)`.

### Enlaces

- [multiprocessing: Sharing state between processes](https://docs.python.org/3/library/multiprocessing.html#sharing-state-between-processes):
  `Value` y `Array` con un ejemplo de cada uno.
- [multiprocessing.Array](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Array):
  la firma completa, el parámetro `lock` y qué devuelve en cada caso.
- [array: Type codes](https://docs.python.org/3/library/array.html):
  la tabla de códigos de tipo con el tamaño en bytes de cada uno.
- [multiprocessing.Process](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process):
  `start`, `join`, `is_alive`, `exitcode` y `terminate`.
- [multiprocessing.shared_memory](https://docs.python.org/3/library/multiprocessing.shared_memory.html):
  la otra forma de compartir bloques de memoria, con nombre, entre procesos.

## Parte 4: un grupo de procesos con una cola

### Lo que se usa

- `multiprocessing.Queue()` es una cola que varios procesos pueden usar a
  la vez: lo que un proceso pone, otro lo saca. Los objetos viajan
  serializados con `pickle`, así que tuplas, números, cadenas y listas
  pasan sin problema.
- `cola.put(objeto)` encola; `cola.get()` saca el siguiente y, si la cola
  está vacía, espera hasta que llegue algo. `cola.get(timeout=s)` deja
  de esperar a los `s` segundos y lanza `queue.Empty`.
- El centinela es un valor que no puede ser una tarea, por ejemplo `None`.
  Un trabajador que lo saca termina su ciclo; como cada trabajador saca uno
  solo, el padre pone tantos centinelas como trabajadores, después de las
  tareas.
- Los trabajadores toman las tareas según se desocupan y las terminan en
  otro orden. Por eso cada tarea viaja como `(índice, argumento)` y cada
  respuesta como `(índice, resultado)`: el padre reserva una lista del largo
  de los argumentos y guarda cada resultado en su índice.
- `enumerate(argumentos)` entrega los pares `(índice, argumento)` que se
  encolan.
- El padre saca de la cola de respuestas tantas veces como tareas puso, y
  hace `join()` de los trabajadores después de vaciarla, no antes: un proceso que
  puso algo en una cola no termina hasta que eso se haya leído.

### Ejemplo

Tres trabajadores sacan de una cola ocho tareas de costo desigual, dos
largas y seis cortas, y cada uno informa por otra cola cuál hizo. Nadie
reparte de antemano: el que se desocupa toma la siguiente, y al final el
padre cuenta qué le tocó a cada uno.

```python
"""Tres trabajadores sacan tareas de una cola a medida que se desocupan: el
que termina antes toma la siguiente. Cada uno informa por otra cola qué tarea
hizo, y el padre cuenta cuántas le tocaron a cada uno."""
import multiprocessing
import time

DURACIONES = [0.6, 0.1, 0.1, 0.1, 0.6, 0.1, 0.1, 0.1]   # dos largas, seis cortas
TRABAJADORES = 3


def trabajador(tareas, informes):
    nombre = multiprocessing.current_process().name
    while True:
        duracion = tareas.get()            # bloquea hasta que haya algo
        if duracion is None:               # el centinela: no hay más trabajo
            break
        time.sleep(duracion)
        informes.put((nombre, duracion))


if __name__ == "__main__":
    tareas = multiprocessing.Queue()
    informes = multiprocessing.Queue()
    hijos = [multiprocessing.Process(target=trabajador, args=(tareas, informes), name=f"T{i}")
             for i in range(TRABAJADORES)]
    inicio = time.perf_counter()
    for h in hijos:
        h.start()
    for duracion in DURACIONES:
        tareas.put(duracion)
    for _ in hijos:
        tareas.put(None)                   # un centinela por trabajador

    hechas = {h.name: [] for h in hijos}
    for _ in DURACIONES:                   # tantos get como tareas se pusieron
        nombre, duracion = informes.get()
        hechas[nombre].append(duracion)
    for h in hijos:
        h.join()                           # después de vaciar la cola de informes
    for nombre, lista in hechas.items():
        print(f"{nombre}: {lista}  ({sum(lista):.1f} s de trabajo)")
    print(f"total: {time.perf_counter() - inicio:.2f} s; en secuencia serían {sum(DURACIONES):.1f} s")
```

```bash
python cola_trabajadores.py
```

```
T0: [0.6]  (0.6 s de trabajo)
T1: [0.1, 0.1, 0.1, 0.1, 0.1]  (0.5 s de trabajo)
T2: [0.1, 0.6]  (0.7 s de trabajo)
total: 0.75 s; en secuencia serían 1.8 s
```

El reparto cambia de una corrida a otra: en la siguiente, `T0` tomó las
cinco cortas y `T1` la larga. El total se mantiene.

### Lo que suele fallar

- **Sin centinelas.** Los trabajadores se quedan en `get()` esperando una
  tarea que no llega y `join()` nunca vuelve. Corrido con `timeout 5 python
  cola_trabajadores.py` sin los `put(None)`, el padre lee los ocho informes,
  se queda en `join()` y muere con código 124 sin imprimir nada; en `pytest`
  es `Failed: Timeout (>120.0s) from pytest-timeout` y el flujo dice *las
  pruebas de cola no pasan*. Con menos centinelas que trabajadores pasa lo
  mismo con los que se quedaron sin el suyo.
- **Los centinelas antes de las tareas.** La cola es FIFO: cada trabajador
  saca un `None` de entrada y termina, las tareas quedan encoladas sin
  nadie que las tome, y el padre se queda esperando en `get()` de la cola
  de respuestas.
- **`join()` antes de vaciar la cola de respuestas.** Un hijo que puso un
  resultado grande no termina hasta que el padre lo lea; si el padre está
  en `join()`, ninguno avanza. Con una lista de un millón de enteros el
  programa se queda quieto hasta que `timeout` lo mata. Primero todos los
  `get()`, después los `join()`.
- **Guardar los resultados en el orden de llegada.** `resultados.append`
  en cada `get()` deja la lista como fueron terminando: con dos trabajadores
  y las esperas `[0.3, 0.1, 0.2, 0.05]` de la prueba, la de 0,1 s llega antes
  que la de 0,3 s, y `test_el_orden_se_respeta_con_pocos_trabajadores`
  falla. El índice que viaja en la tupla es lo que ordena.
- **`queue.Queue` en vez de `multiprocessing.Queue`.** La del módulo `queue`
  es para hilos; pasarla a un `Process` da `TypeError: cannot pickle
  '_thread.lock' object` con `spawn` o `forkserver`, y con `fork` cada hijo
  recibe una copia en la que nunca aparece nada.
- **Preguntar `cola.empty()` para decidir si terminar.** El trabajador
  puede arrancar antes de que el padre haya encolado algo, ver la cola
  vacía y salir sin trabajar. El centinela es lo que marca el final, no el
  estado de la cola.

### Enlaces

- [multiprocessing: Pipes and Queues](https://docs.python.org/3/library/multiprocessing.html#pipes-and-queues):
  las colas del módulo, con el aviso sobre el `join()` de procesos que
  usan colas.
- [multiprocessing.Queue](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Queue):
  `put`, `get`, `qsize`, `empty`, `close` y `join_thread`, y las
  excepciones `queue.Empty` y `queue.Full`.
- [multiprocessing: Programming guidelines](https://docs.python.org/3/library/multiprocessing.html#programming-guidelines):
  las reglas para no bloquearse: qué serializar, cuándo hacer `join`, el
  resguardo del módulo principal.
- [queue: la cola para hilos](https://docs.python.org/3/library/queue.html):
  la misma interfaz `put`/`get`, para saber cuál no es la de esta parte.
- [pickle: What can be pickled and unpickled?](https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled):
  qué objetos pueden viajar por una cola y por `args`.
- [enumerate](https://docs.python.org/3/library/functions.html#enumerate):
  la función que produce los pares `(índice, elemento)`.

## Cómo compilar y ejecutar en la máquina propia

Todo es biblioteca estándar; lo único que se instala son `pytest` y
`pytest-timeout`, y van dentro de un entorno virtual para no tocar el Python
del sistema.

### Debian y Ubuntu

```bash
sudo apt install python3 python3-venv python3-pip
cd infra-hilos-y-procesos-en-python
python3 -m venv .venv                 # crea la carpeta .venv con su propio python
source .venv/bin/activate             # el prompt cambia a (.venv)
pip install -r requirements.txt       # pytest y pytest-timeout
python -m pytest tests/ -v            # todas las pruebas
python -m scripts.medir               # tiempos de las partes 1 y 4
python -m scripts.carrera             # las diez corridas de la parte 2
deactivate                            # al terminar
```

Sin `python3-venv`, `python3 -m venv` falla con *ensurepip is not
available*. Con el entorno activo, `which python` apunta a `.venv/bin/python`
y `pip list` muestra `pytest` y `pytest-timeout` con su versión.

`requirements.txt` es la lista de paquetes que `pip install -r` instala, uno
por línea, con la versión si se quiere fijar (`pytest==9.1.1`). El
repositorio pide `pytest` y `pytest-timeout` sin versión.

`pytest.ini` es la configuración de `pytest` en la raíz: aquí trae
`timeout = 120`, que el complemento `pytest-timeout` aplica a cada prueba.
Una prueba que se queda esperando, como una cola sin centinelas, falla a los
dos minutos con `Failed: Timeout (>120.0s) from pytest-timeout` en vez de
colgar la sesión. Un archivo con tres pruebas y `timeout = 3`, una que
pasa, una que falla y una que espera para siempre, se ve así:

```
tests/test_ejemplo.py::TestEjemplo::test_falla FAILED                    [ 33%]
tests/test_ejemplo.py::TestEjemplo::test_pasa PASSED                     [ 66%]
tests/test_ejemplo.py::TestEjemplo::test_se_cuelga FAILED                [100%]
E       AssertionError: False != True
E               Failed: Timeout (>3.0s) from pytest-timeout.
========================= 2 failed, 1 passed in 3.04s ==========================
```

Las pruebas del repositorio están escritas con `unittest` y `pytest` las
recoge sin cambios. Con `-v` imprime una línea por prueba; con `-k orden`
corre solo las que tengan esa palabra en el nombre; con `-x` se detiene en
la primera que falle. Una función que todavía tiene `raise
NotImplementedError` sale como `FAILED` con esa excepción en el detalle.

Los comandos se corren desde la raíz del repositorio: `python -m
scripts.medir` importa `src.paralelo`, y desde otra carpeta no lo
encuentra. `python -m pytest` y `pytest` a secas hacen lo mismo aquí porque
`tests/` trae `__init__.py`.

El repositorio no trae `.gitignore`. Antes del primer commit del fork
conviene crear uno con estas líneas, porque `.venv/` pesa 28 MB en 1.859
archivos y no es parte de la solución:

```
.venv/
__pycache__/
.pytest_cache/
```

Python 3.11 en Actions arranca los procesos con `fork`; Ubuntu con 3.12 o
3.13 igual, y con 3.14 con `forkserver`. El código que respeta
`if __name__ == "__main__":` y define las tareas en el nivel superior del
módulo corre igual en todos.

### Windows con WSL2

Se instala Ubuntu desde `wsl --install`, y adentro valen los comandos de
arriba. El clon del repositorio va en el sistema de archivos de WSL, en
`~`, no en `/mnt/c/...`: el acceso a archivos del disco de Windows desde
WSL es lento y las pruebas tardan más en arrancar. En Windows sin WSL el
arranque de procesos es `spawn`, el entorno se activa con
`.venv\Scripts\activate` y el intérprete se llama `python`; el resguardo de
`__main__` y las tareas en el nivel superior del módulo aplican igual que en
macOS.

### macOS

`python3` viene con las herramientas de línea de comandos de Xcode o se
instala desde python.org; los comandos son los mismos de Debian. El arranque
de procesos es `spawn`: sin el resguardo de `__main__` cada hijo vuelve a
lanzar el programa, y una tarea definida dentro de otra función o como
`lambda` no llega al hijo. Los tiempos con procesos incluyen el arranque de
un intérprete nuevo por cada uno, así que con tareas cortas los procesos
tardan más que en Linux.

### Enlaces

- [venv: Creation of virtual environments](https://docs.python.org/3/library/venv.html):
  qué crea `python -m venv` y cómo se activa en cada sistema.
- [pip: Requirements file format](https://pip.pypa.io/en/stable/reference/requirements-file-format/):
  la sintaxis de `requirements.txt`, con y sin versiones.
- [pytest: How to invoke pytest](https://docs.pytest.org/en/stable/how-to/usage.html):
  `-v`, `-k`, `-x` y cómo elegir un archivo o una prueba.
- [pytest: Configuration](https://docs.pytest.org/en/stable/reference/customize.html):
  qué archivos lee `pytest` y dónde va `pytest.ini`.
- [pytest-timeout](https://pypi.org/project/pytest-timeout/):
  la opción `timeout` de `pytest.ini` y el marcador por prueba.
- [Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install):
  la instalación de WSL2 con Ubuntu en Windows.
- [Using Python on macOS](https://docs.python.org/3/using/mac.html):
  de dónde sacar `python3` en macOS y qué trae cada opción.
