"""
PRACTICA 1 - PROGRAMACION PARALELA
Apellidos: Ballester Navarro
Nombre:    Teresa
"""
from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from multiprocessing import Manager
from time import sleep
from random import random, randint

N = 10 # Veces que consumes ( equivalente al numero de veces que puede producir cada productor)
NPROD = 3 # Numero de prodcutores
K = 5 #cada productor puede tener k elementos en el almacen

def delay(factor = 3): #Para detener temporalmente el programa 
    sleep(random()/factor)

##############################PROCESO PRODUCIR#################################

def add_data(almacen, index, data, mutex):
    """
    Funcion que añade un numero al almacen del productor, siendo 
    index el tamaño del almacen del productor i. 
    El mutex sirve para impedir que un productor y consumidor acuten a la vez,
    hay un mutex para cada productor.
    """
    mutex.acquire() 
    try:
        almacen[index.value] = data 
        delay(6)
        index.value += 1 #Se añade un elemento al buffer del productor
    finally :
        mutex.release() 

def producer(almacen, index, empty, non_empty, mutex):
    """
    Proceso que añade N veces al almacen un valor creciente, siempre que no
    haya un valor producido y siempre que no este produciendo alguien mas o 
    consumiendo. 
    """
    cota = 1
    for i in range(N): 
        delay(6)
        empty.acquire() #Espera hasta que pueda meter un elemento (que haya un hueco vacio
        v = randint(cota,10*(i+1))
        print(f"producer {current_process().name} produciendo {v}")
        add_data(almacen ,index ,v ,mutex)
        cota = v #Actualizamos la cota, para que sean nums distintos
        non_empty.release() #Ha llenado ese hueco de su almacen
        #print ("El almacen queda",almacen[:])
        print (f"producer {current_process().name} almacenado {v}")
        print("\n")
        delay(6)
        
    #Cuando el proceso termina se introduce -1
    empty.acquire() 
    add_data(almacen,index, -1, mutex)
    non_empty.release()
    print (f"producer {current_process().name} almacenado {-1}")

##############################PROCESO CONSUMIR#################################

def get_data(almacen, index, mutex):
    """
    Funcion que consume el primer elemento de un productor (de tamaño index).
    La usamos en el proceso consumer(), de forma que el consumidor 'coge' el 
    elemento mínimo del almacen. De aquel productor del cual se coja el mínimo,
    hemos de eliminar ese elemento e introducir en la última posición del buffer
    de este prodcutor un -2 indicando que está vacío ese 'hueco' del buffer.
    """   
    mutex.acquire()
    try:
        #data = almacen[0]
        index.value = index.value - 1
        delay()
        for i in range(index.value):
            almacen[i] = almacen[i + 1]
        almacen[index.value] = -2
    finally:
        mutex.release()

def no_fin(almacen):
    for i in range(NPROD):
        if (almacen[i][0] != -1):
            return True
    return False

def minimo(almacen, index):
    """
    Funcion que coge el mínimo de cada proceso, es decir, el primer elemento de 
    la lista y calcula el mínimo de estos. Esta función me devuelve el productor
    del cual obtenemos el mínimo que es el elemento que vamos a consumir y además,
    almacena este mínimo en lst_consumidos que es nuestra lista final.
    """
    mins = []
    indices = []
    for i in range(NPROD):
        if (almacen[i][0] != -1):
            mins.append(almacen[i][0])
            indices.append(i)
    dato = min(mins)
    pos_min = indices[mins.index(dato)]
    return pos_min, dato

def consumer(almacen, index, empty, non_empty, mutex, lst_consumidos):
    #Espera hasta que todos los almacenes hayan producido para poder consumir
    for i in range(NPROD):
        non_empty[i].acquire()
    
    while no_fin(almacen):
        print (f"consumer {current_process().name} desalmacenando")
        pos_min, dato = minimo(almacen, index)
        get_data(almacen[pos_min], index[pos_min], mutex[pos_min])
        lst_consumidos.append(dato)
        empty[pos_min].release()
        print (f"consumer {current_process().name} consumiendo {dato} del producer {pos_min}")
        non_empty[pos_min].acquire()
        delay()
    
    print("La lista resultante de prodcutos consumidos es:", f"{lst_consumidos}")

###############################################################################

def main():
    almacen = [Array('i', K) for i in range(NPROD)]
    #Lista del tamaño de elementos producidos por cada proceso
    index = [Value('i', 0) for i in range(NPROD)]
    # NPROD = lenght(indexs) = length(almacen)
    
    # Inicializamos todos los almacenes, con todos sus elementos = -2, ya que -2
    #indica que un 'hueco' del alamcén está vacío.
    for i in range(NPROD):
        for j in range(K):
            almacen[i][j] = -2
        print (f"almacen inicial del productor {i} es", almacen[i][:], "y su índice es", index[i].value)
    
    non_empty = [Semaphore(0) for _ in range(NPROD)]
    empty = [BoundedSemaphore(K) for _ in range(NPROD)]
    mutex = [Lock() for _ in range(NPROD)]

    manager = Manager()
    lst_consumidos = manager.list() #Lista que me va a mostrar los elementos consumidos (en orden)
    
    productores = [Process(target=producer,
                        name=f'prod_{i}',
                        args=(almacen[i], index[i], empty[i], non_empty[i], mutex[i]))
                for i in range(NPROD) ]

    consumidor = Process(target=consumer,
                        name="consumidor", 
                        args=(almacen, index, empty, non_empty, mutex, lst_consumidos))

  
    for p in productores:
       print(f"Inicializando productor {p.name}", "\n")
       p.start()
       
    print(f"Arrancando consumidor {consumidor.name}")
    consumidor.start()

    for p in productores:
        p.join()
    consumidor.join()
    

if __name__ == '__main__':
    main()
