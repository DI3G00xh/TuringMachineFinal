import RPi.GPIO as GPIO
import cv2
import time
import sys

# CONFIGURACIÓN DE PINES 
# Ajustar estos números según cableado 

# Servos para los lápices
PIN_SERVO_NEGRO = 17    # Pin para el lápiz Negro (1)
PIN_SERVO_AMARILLO = 27 # Pin para el lápiz Amarillo/Blanco (0 y B)

# Motores Paso a Paso (Drivers tipo A4988)
PIN_STEP_IZQ = 22
PIN_DIR_IZQ = 23
PIN_STEP_DER = 24
PIN_DIR_DER = 25

# CONSTANTES FÍSICAS 
# Ángulos de los Servos 
# Duty Cycle para PWM 
SERVO_ARRIBA = 5.0 
SERVO_ABAJO = 9.0   

# Movimiento
PASOS_POR_CELDA = 200 
RETARDO_PASO = 0.005 # Velocidad del motor (segundos entre pasos)


# TABLAS DE ESTADOS

tabla_suma = {
    ('Q0', '0'): ('Q1', '1', 'D'),
    ('Q0', '1'): ('Q0', '1', 'D'),
    ('Q0', 'B'): ('Q0', 'B', 'D'),
    ('Q1', '1'): ('Q1', '1', 'D'),
    ('Q1', 'B'): ('Q2', 'B', 'I'), 
    ('Q2', '1'): ('Qf', 'B', 'F')  
}

tabla_resta = {
    ('Q0', 'B'): ('Q1', 'B', 'D'), 
    ('Q1', '0'): ('Q1', '0', 'D'),
    ('Q1', '1'): ('Q1', '1', 'D'),
    ('Q1', 'B'): ('Q2', 'B', 'I'), 
    ('Q2', '1'): ('Q3', 'B', 'I'), 
    ('Q2', '0'): ('Qf', 'B', 'F'), 
    ('Q3', '1'): ('Q3', '1', 'I'),
    ('Q3', '0'): ('Q3', '0', 'I'),
    ('Q3', 'B'): ('Q4', 'B', 'D'), 
    ('Q4', '1'): ('Q1', 'B', 'D'), 
    ('Q4', '0'): ('Qf', 'B', 'F') 
}


# INICIALIZACIÓN DE DISPOSITIVOS

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup Motores
GPIO.setup([PIN_STEP_IZQ, PIN_DIR_IZQ, PIN_STEP_DER, PIN_DIR_DER], GPIO.OUT)

# Setup Servos
GPIO.setup([PIN_SERVO_NEGRO, PIN_SERVO_AMARILLO], GPIO.OUT)
pwm_negro = GPIO.PWM(PIN_SERVO_NEGRO, 50) # 50Hz
pwm_amarillo = GPIO.PWM(PIN_SERVO_AMARILLO, 50)
pwm_negro.start(SERVO_ARRIBA)
pwm_amarillo.start(SERVO_ARRIBA)

# Setup Cámara (OpenCV)
cap = cv2.VideoCapture(0)

cap.set(3, 320) # Ancho
cap.set(4, 240) # Alto


#  FUNCIONES FÍSICAS

def mover_servo(pwm_obj, ciclo_trabajo):
    """Mueve el servo suavemente"""
    pwm_obj.ChangeDutyCycle(ciclo_trabajo)
    time.sleep(0.3) 

def leer_simbolo():
    """Captura imagen real y analiza el color central"""
    ret, frame = cap.read()
    if not ret:
        print("Error: Cámara no detectada")
        return 'B' 
    
    # Convertir a RGB 
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Obtenemos dimensiones
    h, w, _ = frame_rgb.shape
    
    # Leer pixeles centrales 
    center_y, center_x = int(h/2), int(w/2)
    pixel = frame_rgb[center_y, center_x]
    
    r, g, b = pixel[0], pixel[1], pixel[2]
    
    print(f"COLOR VISTO (Real) -> R:{r} G:{g} B:{b}") 

    # UMBRALES DE CALIBRACIÓN 
  
    # Negro
    if r < 80 and g < 80 and b < 80:
        return '1'
        
    # Amarillo
    if r > 150 and g > 150 and b < 100:
        return '0'
        
    # Blanco/Gris 
    return 'B'

def escribir_simbolo(simbolo):
    print(f" -> Acción de Escribir: {simbolo}")
    
    mover_servo(pwm_negro, SERVO_ARRIBA)
    mover_servo(pwm_amarillo, SERVO_ARRIBA)
    
    if simbolo == '1':
        mover_servo(pwm_negro, SERVO_ABAJO)
    elif simbolo == '0':
        mover_servo(pwm_amarillo, SERVO_ABAJO)
    else: 
        mover_servo(pwm_amarillo, SERVO_ABAJO)
    
    time.sleep(0.5) 
    
    mover_servo(pwm_negro, SERVO_ARRIBA)
    mover_servo(pwm_amarillo, SERVO_ARRIBA)

def mover_cabezal(direccion):
    if direccion == 'F': return
    
    print(f" -> Moviendo Motores ({direccion})...")
    
    if direccion == 'D':
        GPIO.output(PIN_DIR_IZQ, GPIO.HIGH)
        GPIO.output(PIN_DIR_DER, GPIO.HIGH) 
    else: # 'I'
        GPIO.output(PIN_DIR_IZQ, GPIO.LOW)
        GPIO.output(PIN_DIR_DER, GPIO.LOW)
        
    for _ in range(PASOS_POR_CELDA):
        GPIO.output(PIN_STEP_IZQ, GPIO.HIGH)
        GPIO.output(PIN_STEP_DER, GPIO.HIGH)
        time.sleep(RETARDO_PASO) # Velocidad
        GPIO.output(PIN_STEP_IZQ, GPIO.LOW)
        GPIO.output(PIN_STEP_DER, GPIO.LOW)
        time.sleep(RETARDO_PASO)
        
    time.sleep(0.5)


# BUCLE PRINCIPAL

try:
    print("--- MÁQUINA DE TURING FÍSICA ---")
    print("Selecciona Modo: Escribe 'S' (Suma) o 'R' (Resta) y pulsa ENTER")
    
    modo = input("Esperando orden: ").upper()
    
    tabla_actual = None
    if modo == 'S': 
        tabla_actual = tabla_suma
        print(">> MODO SUMA (A + B)")
    elif modo == 'R': 
        tabla_actual = tabla_resta
        print(">> MODO RESTA (A - B)")
    else:
        print("Opción no válida. Saliendo.")
        sys.exit()

    estado_actual = 'Q0'

    # Bucle infinito de ejecución
    while True:
        
        # LEER
        simbolo_leido = leer_simbolo()
        
        # CONSULTAR TABLA
        clave = (estado_actual, simbolo_leido)
        
        # Log de Depuración
        print(f"\n[ESTADO: {estado_actual}] LEÍDO: '{simbolo_leido}'")
        
        if clave in tabla_actual:
            nuevo_estado, simbolo_escribir, movimiento = tabla_actual[clave]
            
            print(f" >> REGLA: {clave} -> ({nuevo_estado}, {simbolo_escribir}, {movimiento})")
            
            #  ESCRIBIR 
            if simbolo_escribir != simbolo_leido:
                escribir_simbolo(simbolo_escribir)
            
            # Verificar Final
            if nuevo_estado == 'Qf':
                print("--- OPERACIÓN TERMINADA (Qf Alcanzado) ---")
                break
            
            # MOVERSE
            mover_cabezal(movimiento)
            
            # Actualizar
            estado_actual = nuevo_estado
            
        else:
            print(f"!!! ERROR: BLOQUEO. No hay regla para ({estado_actual}, {simbolo_leido})")
            break

except KeyboardInterrupt:
    print("\nDeteniendo programa...")

finally:
    print("Limpiando GPIO y Cámara...")
    cap.release()
    pwm_negro.stop()
    pwm_amarillo.stop()
    GPIO.cleanup()
