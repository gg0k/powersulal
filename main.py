import _thread
import power_control
import display
#import inputs
import time
import shared_data
def core_0_task():
    """Tarea principal del núcleo 0: regulación de la fuente"""
    print("core 0 task")
    while True:
        power_control.measure()
    
    
    time.sleep(2)

def core_1_task():
    """Tarea principal del núcleo 1: interfaz y control de usuario"""
    display.run()
    #inputs.listen_buttons()

# Iniciar el núcleo 0
_thread.start_new_thread(core_0_task, ())

# Iniciar el núcleo 1 en el hilo principal
core_1_task()
