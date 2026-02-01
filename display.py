import shared_data
import time
import gc
import st7789
import tft_config
from machine import Pin

import vga1_16x32 as font2
import vga1_8x8 as font1

bg_Color = st7789.color565(23,23,23)
GREY = st7789.color565(128,128,128)
tft = tft_config.config(3, buffer_size=64*62*2)   # configure display driver


select = False
editing = False
editor = ["voltage","current","edit"]

cursor_editor = 0
cursor_select = 0

pruebaPID = True

buttons = {
    "left": Pin(19, Pin.IN),
    "right": Pin(23, Pin.IN),
    "arriba": Pin(4, Pin.IN),
    "abajo": Pin(15, Pin.IN),
    "center": Pin(18, Pin.IN),
    "A": Pin(17, Pin.IN),
    "B": Pin(16, Pin.IN)
}



last_press_time = {"left": 0, "right": 0, "arriba": 0, "abajo": 0, "center": 0, "A": 0, "B": 0}
debounce_time = 100  # Tiempo de debounce en milisegundos

def update_selection():
    if editor[cursor_editor] == "voltage" and editing:
        tft.rect(103, 44, 157 - 103, 10, st7789.RED)
    elif editor[cursor_editor] == "current" and editing:
        tft.rect(103, 59, 157 - 103, 10, st7789.CYAN)

    if editor[cursor_editor] == "voltage" and select:
        set_v = shared_data.get_data("set_voltage")
        str_value = "{:06.3f}".format(set_v)  # asegura longitud consistente
        if str_value[cursor_select] == ".":
            return  # por seguridad, aunque con tu nuevo código no debería pasar

        # Construir cadena con espacio en la posición del cursor
        display_str = str_value[:cursor_select] + " " + str_value[cursor_select + 1:]

        base_x = 105
        y_text = 45
        char_width = 8

        tft.text(font1, display_str, base_x, y_text, st7789.WHITE, bg_Color)

        digit_x = base_x + cursor_select * char_width
        tft.fill_rect(digit_x, y_text, 8, 8, st7789.color565(58, 0, 0))
        tft.text(font1, str_value[cursor_select], digit_x, y_text, st7789.RED, st7789.color565(58, 0, 0))

    elif editor[cursor_editor] == "current" and select:
        set_c = shared_data.get_data("set_current")
        str_value = "{:06.3f}".format(set_c)
        if str_value[cursor_select] == ".":
            return

        display_str = str_value[:cursor_select] + " " + str_value[cursor_select + 1:]

        base_x = 105
        y_text = 60
        char_width = 8

        tft.text(font1, display_str, base_x, y_text, st7789.WHITE, bg_Color)

        digit_x = base_x + cursor_select * char_width
        tft.fill_rect(digit_x, y_text, 8, 8, st7789.color565(0, 0, 58))
        tft.text(font1, str_value[cursor_select], digit_x, y_text, st7789.CYAN, st7789.color565(0, 0, 58))

        
def clean_selection():
    tft.fill_rect(98,38,160-98,78-38,bg_Color)
    set_v = shared_data.get_data("set_voltage")
    set_a = shared_data.get_data("set_current")
    tft.text(font1, "{:05.3f}".format(set_v), 105, 45, st7789.WHITE, bg_Color)
    tft.text(font1, "{:05.3f}".format(set_a), 105, 60, st7789.WHITE, bg_Color)


def update_voltage():
    """Actualiza el voltaje en shared_data basado en la selección actual."""
    shared_data.update_data("set_voltage", voltages[cursor])

def draw_screen():
    """Dibuja la interfaz en la pantalla."""
    tft.init()
    tft.fill(bg_Color)
    
    
    #lineas divisorias horizontales
    tft.hline(1, 9, 90, st7789.CYAN)
    tft.hline(95, 9, 158-95, st7789.GREEN)
    tft.hline(95, 27, 158-95, st7789.GREEN)
    tft.hline(1, 111, 90, GREY)
    
    
    #lineas divisorias verticales
    tft.vline(95, 1, 125, GREY)
    
    
    tft.fill_rect(11,12,91-54,21-10,GREY)
    tft.fill_rect(54,11,16,10,GREY)
    

    
    
    
    tft.text(font1, "99%", 121, 1, st7789.GREEN, bg_Color)
    
    tft.text(font1, "ON", 12, 13, st7789.WHITE, GREY)
    tft.text(font1, "CV  CC", 56, 13, st7789.RED, GREY)
    
    tft.text(font1, "v", 80, 28, st7789.RED, bg_Color)
    tft.text(font1, "A", 80, 54, st7789.CYAN, bg_Color)
    tft.text(font1, "W", 80, 79, st7789.YELLOW, bg_Color)
    
    
    tft.text(font1, "SET", 100, 30, st7789.WHITE, bg_Color)
    set_v = shared_data.get_data("set_voltage")
    set_a = shared_data.get_data("set_current")
    tft.text(font1, "{:05.3f}".format(set_v), 105, 45, st7789.WHITE, bg_Color)
    tft.text(font1, "{:05.3f}".format(set_a), 105, 60, st7789.WHITE, bg_Color)

def update_display():
    """Actualiza la pantalla con los datos actuales y maneja la lógica de los botones."""
    global cursor, select, editing, editor, cursor_editor,cursor_select
    
    
    
    last_update = time.ticks_ms()

    while True:
        current_time = time.ticks_ms()
        delta_time = time.ticks_diff(current_time, last_update)
        

        
        
        if buttons["center"].value() and time.ticks_diff(current_time, last_press_time["center"]) > 50 and editing==False:
            editing = True
            update_selection()
            last_press_time["center"] = current_time
            
        if editing == True and select!=True:
            #BACK
            if buttons["B"].value() and time.ticks_diff(current_time, last_press_time["B"]) > 50:                
                editing=False
                cursor_editor=0
                clean_selection()
                update_selection()
                last_press_time["B"] = current_time
            
            #abajo
            if buttons["abajo"].value() and time.ticks_diff(current_time, last_press_time["abajo"]) > 50:
                cursor_editor = (cursor_editor + 1) % len(editor)
                #print("abajo")
                clean_selection()
                update_selection()
                last_press_time["abajo"] = current_time

            #ARRIBA
            if buttons["arriba"].value() and time.ticks_diff(current_time, last_press_time["arriba"]) > 50:
                cursor_editor = (cursor_editor - 1) % len(editor)
                #print("arriba")
                clean_selection()
                update_selection()
                last_press_time["arriba"] = current_time
            
            #Selection
            if buttons["center"].value() and time.ticks_diff(current_time, last_press_time["center"]) > 50:
                select = True
                editing = False
                update_selection()
                last_press_time["center"] = current_time
                
        if select:
            
            
            
           # Mover cursor a la izquierda
            if buttons["left"].value() and time.ticks_diff(current_time, last_press_time["left"]) > 50:
                if editor[cursor_editor] == "voltage":
                    set_v = list("{:06.3f}".format(shared_data.get_data("set_voltage")))
                    while cursor_select > 0:
                        cursor_select -= 1
                        if set_v[cursor_select] != '.':
                            break
                elif editor[cursor_editor] == "current":
                    set_c = list("{:06.3f}".format(shared_data.get_data("set_current")))
                    while cursor_select > 0:
                        cursor_select -= 1
                        if set_c[cursor_select] != '.':
                            break
                update_selection()
                last_press_time["left"] = current_time

            # Mover cursor a la derecha
            if buttons["right"].value() and time.ticks_diff(current_time, last_press_time["right"]) > 50:
                if editor[cursor_editor] == "voltage":
                    set_v = list("{:06.3f}".format(shared_data.get_data("set_voltage")))
                    while cursor_select < len(set_v) - 1:
                        cursor_select += 1
                        if set_v[cursor_select] != '.':
                            break
                elif editor[cursor_editor] == "current":
                    set_c = list("{:06.3f}".format(shared_data.get_data("set_current")))
                    while cursor_select < len(set_c) - 1:
                        cursor_select += 1
                        if set_c[cursor_select] != '.':
                            break
                update_selection()
                last_press_time["right"] = current_time

            # Incrementar dígito (arriba)
            if buttons["arriba"].value() and time.ticks_diff(current_time, last_press_time["arriba"]) > 50:
                if editor[cursor_editor] == "voltage":
                    set_v = list("{:06.3f}".format(shared_data.get_data("set_voltage")))
                    if set_v[cursor_select].isdigit():
                        digit = int(set_v[cursor_select])
                        digit = (digit + 1) % 10
                        
                        # Validación para voltaje (máximo 25V)
                        if cursor_select == 0:  # Primer dígito (decenas)
                            if digit > 2:
                                digit = 0
                        elif cursor_select == 1:  # Segundo dígito (unidades)
                            if set_v[0] == '2' and digit > 5:  # Si el primer dígito es 2, el segundo no puede ser >5
                                digit = 0
                        
                        set_v[cursor_select] = str(digit)
                        new_value = float("".join(set_v))
                        if new_value <= 25.0 and new_value >= 3.0:  # Validación de ambos límites
                            shared_data.update_data("set_voltage", new_value)
                        else:
                            set_v[cursor_select] = str((digit - 1) % 10)  # Revertir cambio
                            
                elif editor[cursor_editor] == "current":
                    set_c = list("{:06.3f}".format(shared_data.get_data("set_current")))
                    if set_c[cursor_select].isdigit():
                        digit = int(set_c[cursor_select])
                        digit = (digit + 1) % 10
                        
                        # Validación para corriente (máximo 3A)
                        if cursor_select == 0 and digit > 3:  # Primer dígito no puede ser >3
                            digit = 0
                            
                        set_c[cursor_select] = str(digit)
                        new_value = float("".join(set_c))
                        if new_value <= 3.0 and new_value >= 0.0:  # Corriente mínima 0A
                            shared_data.update_data("set_current", new_value)
                        else:
                            set_c[cursor_select] = str((digit - 1) % 10)  # Revertir cambio
                            
                update_selection()
                last_press_time["arriba"] = current_time

            # Decrementar dígito (abajo)
            if buttons["abajo"].value() and time.ticks_diff(current_time, last_press_time["abajo"]) > 50:
                if editor[cursor_editor] == "voltage":
                    set_v = list("{:06.3f}".format(shared_data.get_data("set_voltage")))
                    if set_v[cursor_select].isdigit():
                        digit = int(set_v[cursor_select])
                        digit = (digit - 1) % 10
                        
                        # Validación para voltaje (mínimo 3V)
                        if cursor_select == 0:  # Primer dígito
                            if digit < 0:
                                digit = 2  # Máximo 2 en primer dígito
                            elif digit == 0 and int(set_v[1]) < 3:  # Si primer dígito es 0, segundo no puede ser <3
                                digit = 0  # Mantener en 0 (pero el valor total será validado)
                        elif cursor_select == 1:  # Segundo dígito
                            if set_v[0] == '0' and digit < 3:  # Si primer dígito es 0, segundo no puede ser <3
                                digit = 9  # Permitir rollover pero será validado
                        
                        set_v[cursor_select] = str(digit)
                        new_value = float("".join(set_v))
                        
                        # Validación final del valor (3.0V a 25.0V)
                        if new_value >= 3.0 and new_value <= 25.0:
                            shared_data.update_data("set_voltage", new_value)
                        else:
                            # Ajustar al límite más cercano si se excede
                            if new_value < 3.0:
                                shared_data.update_data("set_voltage", 3.0)
                            elif new_value > 25.0:
                                shared_data.update_data("set_voltage", 25.0)
                            
                elif editor[cursor_editor] == "current":
                    set_c = list("{:06.3f}".format(shared_data.get_data("set_current")))
                    if set_c[cursor_select].isdigit():
                        digit = int(set_c[cursor_select])
                        digit = (digit - 1) % 10
                        
                        # Validación para corriente (mínimo 0A)
                        if cursor_select == 0 and digit > 3:  # Primer dígito no puede ser >3
                            digit = 3
                            
                        set_c[cursor_select] = str(digit)
                        new_value = float("".join(set_c))
                        if new_value >= 0.0 and new_value <= 3.0:  # Validación de ambos límites
                            shared_data.update_data("set_current", new_value)
                        else:
                            # Ajustar al límite más cercano
                            if new_value < 0.0:
                                shared_data.update_data("set_current", 0.0)
                            elif new_value > 3.0:
                                shared_data.update_data("set_current", 3.0)
                            
                update_selection()
                last_press_time["abajo"] = current_time
                        
                        
            
            
            if buttons["B"].value() and time.ticks_diff(current_time, last_press_time["B"]) > 50:                
                select=False
                editing = True
                cursor_select=0
                clean_selection()
                update_selection()
                last_press_time["B"] = current_time

            
                
            
        

        # Manejo de botones con debounce
#         if buttons["left"].value() and time.ticks_diff(current_time, last_press_time["left"]) > 20:
#             cursor = max(0, cursor - 1)
#             update_voltage()
#             last_press_time["left"] = current_time
# 
#         if buttons["right"].value() and time.ticks_diff(current_time, last_press_time["right"]) > 20:
#             cursor = min(len(voltages) - 1, cursor + 1)
#             update_voltage()
#             last_press_time["right"] = current_time

        # Actualizar pantalla cada 100ms
        if delta_time >= 100:

            last_update = current_time
            #print(editing)
            #print(editor[cursor_editor])
            #time
            now = time.localtime()
            time_str = "{:02d}-{:02d}{:02d}:{:02d}:{:02d}".format(now[1], now[2], now[3], now[4], now[5])
            tft.text(font1, time_str, 0, 0, st7789.CYAN, bg_Color)

            voltage = shared_data.get_data("voltage")
            current = shared_data.get_data("current")
            power = voltage * current  # Se calcula en lugar de almacenarlo
            pwm = shared_data.get_data("pwm")

            # Mostrar valores en pantalla
            tft.text(font2, "{:.3f}".format(voltage) if voltage < 10 else "{:.2f}".format(voltage), 0, 22, st7789.RED, bg_Color)
            tft.text(font2, "{:.3f}".format(current) if current < 10 else "{:.2f}".format(current), 0, 50, st7789.CYAN, bg_Color)
            tft.text(font2, "{:.3f}".format(power) if power < 10 else "{:.2f}".format(power), 0, 78, st7789.YELLOW, bg_Color)
            tft.text(font1, str(pwm), 1, 117, st7789.WHITE, bg_Color)

                        
            

            gc.collect()  # Recolector de memoria

        time.sleep_ms(20)  # Mantener la lectura fluida sin sobrecargar

def run():
    draw_screen()
    update_display()
