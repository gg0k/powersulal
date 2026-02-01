
import _thread

# Datos compartidos
data = {
    "voltage": 12.000,
    "current": 1.090,
    "power": 712,
    "pwm": 65000,
    "set_voltage" : 12,
    "set_current" : 1
}

# Lock para acceso seguro
lock = _thread.allocate_lock()

def update_data(key, value):
    """Actualiza un valor en la data compartida de forma segura."""
    with lock:
        data[key] = value

def get_data(key):
    """Obtiene un valor de la data compartida de forma segura."""
    with lock:
        return data.get(key, None)
