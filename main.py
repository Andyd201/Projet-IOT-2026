# main.py
import serial
import time
import outils  

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600

last_button_state = 1  
control_enabled = False

try:
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1) as ser:
        time.sleep(2)  
        
        last_led_x_state = False
        last_led_y_state = False
        
        while True:
            data = outils.get_position(ser)
            
            if data is not None:
                button_state = data["BOUTON"]
                x_value = data["X"]
                y_value = data["Y"]
                
                # Affiche STRICTEMENT et UNIQUEMENT les positions X et Y
                print(f"\rX: {x_value:4d} | Y: {y_value:4d}", end="", flush=True)

                if button_state == 0 and last_button_state == 1:
                    control_enabled = not control_enabled
                    
                    if not control_enabled:
                        outils.eteindre_les_deux_leds(ser)
                        last_led_x_state = False
                        last_led_y_state = False
                    time.sleep(0.2)
                
                last_button_state = button_state
                
                if control_enabled:
                    led_x_actuelle = (x_value > 600)
                    led_y_actuelle = (x_value < 400)
                    
                    if led_x_actuelle != last_led_x_state:
                        outils.allumer_led_x(ser, led_x_actuelle)
                        last_led_x_state = led_x_actuelle
                        
                    if led_y_actuelle != last_led_y_state:
                        outils.allumer_led_y(ser, led_y_actuelle)
                        last_led_y_state = led_y_actuelle
            
            time.sleep(0.01)

except serial.SerialException:
    pass
except KeyboardInterrupt:
    print()
