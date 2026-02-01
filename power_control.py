import machine
import utime
from ADS1115 import *
from machine import Pin, I2C, PWM
import shared_data

ADS1115_ADDRESS = 0x48
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
adc = ADS1115(ADS1115_ADDRESS, i2c=i2c)

pwmPin = 5  
pwmFrequency = 1000  
pwm = PWM(Pin(pwmPin), freq=pwmFrequency, duty_u16=50000)  

DUTY_MIN = 21000
DUTY_MAX = 63500

adc.setVoltageRange_mV(ADS1115_RANGE_6144)
adc.setConvRate(ADS1115_860_SPS)
adc.setMeasureMode(ADS1115_CONTINUOUS)

set_voltage = shared_data.get_data("set_voltage")
set_current = shared_data.get_data("set_current")

Kp_voltage = 500  # Factor de ajuste para control de voltaje
Kp_current = 800   # Factor de ajuste para control de corriente (más agresivo)
current_threshold = 0.95  # 95% del set_current para activar CC mode

last_update_time = 0
update_interval = 100  # Cada 100 ms

def get_average_voltage(channel, samples=100):
    adc.setCompareChannels(channel)
    utime.sleep_us(500)
    total = sum(adc.getResult_V() for _ in range(samples))
    return total / samples

def measure():
    global last_update_time, set_voltage, set_current
    current_time = utime.ticks_ms()
    
    measured_voltage = get_average_voltage(ADS1115_COMP_3_GND, samples=100)
    measured_current = abs(get_average_voltage(ADS1115_COMP_2_GND, samples=20) * 1)
    
    # Obtener valores actualizados
    set_voltage = shared_data.get_data("set_voltage")
    set_current = shared_data.get_data("set_current")
    
    # Modo Constant Current (si la corriente medida alcanza el 95% del setpoint)
    if measured_current >= set_current * current_threshold:
        # Reducir el voltaje para mantener la corriente constante
        error_current = set_current - measured_current
        voltage_adjustment = int(Kp_current * error_current)
        
        # Calcular nuevo duty cycle basado en corriente (limitado)
        nuevo_duty = max(DUTY_MIN, min(DUTY_MAX, pwm.duty_u16() - voltage_adjustment))
        
        # Actualizar el voltaje establecido para reflejar la reducción
        adjusted_voltage = max(0.2, measured_voltage * 11 + (error_current * 0.1))  # Mínimo 3V
        #shared_data.update_data("set_voltage", adjusted_voltage)
    else:
        # Modo normal de control de voltaje
        error_voltage = set_voltage - measured_voltage * 11
        voltage_adjustment = int(Kp_voltage * error_voltage)
        nuevo_duty = max(DUTY_MIN, min(DUTY_MAX, pwm.duty_u16() - voltage_adjustment))
    
    pwm.duty_u16(nuevo_duty)
    
    # Actualizar datos compartidos
    if utime.ticks_diff(current_time, last_update_time) >= update_interval:
        shared_data.update_data("voltage", measured_voltage * 11)
        shared_data.update_data("current", measured_current)
        shared_data.update_data("pwm", nuevo_duty)
        last_update_time = current_time
    
    utime.sleep_ms(20)