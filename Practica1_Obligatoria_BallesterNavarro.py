"""
PRACTICA 1 - PROGRAMACION PARALELA
Apellidos: Ballester Navarro
Nombre:    Teresa
"""
from multiprocessing import Process
from multiprocessing import Semaphore
from multiprocessing import current_process
from multiprocessing import Array
from multiprocessing import Manager
from time import sleep
from random import random, randint


N = 5 # Veces que consumes ( equivalente al numero de veces que puede producir cada productor)
NPROD = 3 # Numero de prodcutores
# K = 1, cada productor puede tener un elemento en el almacen

def delay(factor = 3): #Para detener temporalmente el programa 
    sleep(random()/factor)

##############################PROCESO PRODUCIR#################################
def producer(almacen, empty, non_empty,pos):
    """
    Proceso que añade N veces al almacen un valor creciente, siempre que no
    haya un valor producido y siempre que no este produciendo alguien mas o 
    consumiendo. 
    """
    cota = 1
    for i in range(N): 
        delay(6)
        v = randint(cota,10*(i+1))
        empty.acquire() #Espera hasta que pueda meter un elemento (que haya un hueco vacio)
        print(f"producer {current_process().name} produciendo {v}")
        almacen[pos] = v 
        cota = v #Actualizamos la cota, para que sean nums distintos
        non_empty.release() #Ha llenado ese hueco de su almacen
        print ("El almacen queda",almacen[:])
        print("\n")
        delay(6)
        
    #Cuando el proceso termina se introduce -1
    empty.acquire()
    print (f"producer {current_process().name} terminando")
    almacen[pos] = -1
    print ("El almacen queda",almacen[:])
    non_empty.release()

##############################PROCESO CONSUMIR#################################
def get_data(almacen, lst_consumidos):
    #Función que encuentra la posicion del minimo no negativo del almacen y 
    #lo guarda en la lista resultante: lst_consumidos
    pos_min = 0
    lst_val_pos = [x for x in almacen if x >= 0]
    for i in range(len(almacen)):
         if almacen[i] == min(lst_val_pos):
             pos_min = i
    #Almacenamos en la lista resultante el elemento consumido
    lst_consumidos.append(almacen[pos_min])
    delay(6)
    return pos_min
   
def fin(almacen):
    products = True
    i = 0
    while products and i < len(almacen):
        products = products and almacen[i] == -1
        i = i + 1
    return products

def consumer(almacen, lst_consumidos, empty, non_empty):
    #Espera hasta que todos los almacenes hayan producido para poder consumir
    for w in range(NPROD):
        non_empty.acquire()
    # Hay que consumir los N*NPROD productos
    print(f"{[x for x in almacen]}")
    while not fin(almacen):
        delay(6)
        pos_min = get_data(almacen, lst_consumidos)
        empty[pos_min].release()
        non_empty.acquire()
    print("La lista resultante de prodcutos consumidos es:", f"{lst_consumidos}")


def main():
    almacen = Array('i',NPROD)
        
    # Inicializamos todos los almacenes, con todos sus elementos = -2, ya que -2
    # indica que un 'hueco' del alamcén está vacío.
    for i in range(NPROD):
        almacen[i] = -2 
            
    
    manager = Manager()
    lst_consumidos = manager.list() #Lista que me va a mostrar los elementos consumidos (en orden)
    
    non_empty = Semaphore(0)
    empty = [Semaphore(1) for i in range(NPROD)]
    
    productos = [ Process(target=producer,
                                  name=f"{i}",
                                  args = (almacen, empty[i], non_empty,i) ) for i in range(NPROD) ]

    consumidor = Process(target=consumer,name="consumidor",args=(almacen, lst_consumidos, empty, non_empty))
  
    for p in productos:
       print(f"Inicializando productor {p.name}", "\n")
       p.start()
    print(f"Arrancando consumidor {consumidor.name}")
    consumidor.start()

    for p in productos:
        p.join()
    consumidor.join()

if __name__ == '__main__':
    main()