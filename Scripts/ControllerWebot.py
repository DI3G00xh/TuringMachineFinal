from controller import Robot,Camera,Motor,PositionSensor,Keyboard

TIME_STEP = 20
RADIO_RUEDA = 0.03   
ANCHO_CELDA = 0.1     #10cm 
VELOCIDAD_MOTOR = 2
RADIANES_POR_CELDA = ANCHO_CELDA / RADIO_RUEDA

# Definicion de Colores en formato HEXADECIMAL (0xRRGGBB)
COLOR_1 = 0x000000  # Negro = 1
COLOR_0 = 0xFFFF00  # Amrillo = 0
COLOR_B = 0xFFFFFF  # Blanco = B 


# TABLA DE ESTADOS 
# Formato: (EstadoActual, Leido): (NuevoEstado, Escribir, Direccion)
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

robot = Robot()

teclado = Keyboard()
teclado.enable(TIME_STEP)

# Motores y Sensores de Posicion 
motor_izq = robot.getDevice('motor_izq')
motor_der = robot.getDevice('motor_der')
ps_izq = robot.getDevice('encoder_izq') 
ps_der = robot.getDevice('encoder_der')

ps_izq.enable(TIME_STEP)
ps_der.enable(TIME_STEP)

# Control de posicion Motores
motor_izq.setPosition(float('inf'))
motor_der.setPosition(float('inf'))
motor_izq.setVelocity(0)
motor_der.setVelocity(0)

# Camara
camara = robot.getDevice('robot_camera')
camara.enable(TIME_STEP)

#Lapiz (Cabezal de Escritura
lapiz = robot.getDevice('robot_pen')
lapiz.setInkColor(0x000000, 1) 
lapiz.write(False)              


def leer_simbolo():

    img = camara.getImage()
    w = camara.getWidth()
    h = camara.getHeight()  
    

    r = Camera.imageGetRed(img, w, int(w/2), int(h/2))
    g = Camera.imageGetGreen(img, w, int(w/2), int(h/2))
    b = Camera.imageGetBlue(img, w, int(w/2), int(h/2))

    print(f"COLOR VISTO -> R:{r} G:{g} B:{b}") 

    # Decide qué simbolo es según los valores vistos
    if r < 100 and b < 100:  # Negro
        return '1'      
    if r > 220 and b < 120: # Amarillo
        return '0'      
    return 'B'          # Blnaco
    
def escribir_simbolo(simbolo):

    #setInkColor(COLOR_HEX, DENSIDAD)
    if simbolo == '1':
        lapiz.setInkColor(COLOR_1, 1)
    elif simbolo == '0':
        lapiz.setInkColor(COLOR_0, 1.0)
    else: 
        lapiz.setInkColor(COLOR_B, 1.0)
    
    lapiz.write(True) 
    
    for _ in range(10): robot.step(TIME_STEP)

    lapiz.write(False) 

def mover_cabezal(direccion):
 
    if direccion == 'F': return 
   
    pos_actual = ps_izq.getValue()
    signo = 1 if direccion == 'D' else -1
    meta = pos_actual + (RADIANES_POR_CELDA * signo)
    
    motor_izq.setPosition(meta)
    motor_der.setPosition(meta)
    motor_izq.setVelocity(VELOCIDAD_MOTOR) 
    motor_der.setVelocity(VELOCIDAD_MOTOR)
    
    while robot.step(TIME_STEP) != -1:
        diff = abs(ps_izq.getValue() - meta)
        if diff < 0.01: 
            break
            
    motor_izq.setVelocity(0)
    motor_der.setVelocity(0)
    
    for _ in range(10): robot.step(TIME_STEP)
    

# SELECCIÓN DE MODO
tabla_actual = None
modo_seleccionado = False

print("--- ESPERANDO ORDEN ---")
print("Presiona 'S' para SUMA")
print("Presiona 'R' para RESTA")

while robot.step(TIME_STEP) != -1:
    key = teclado.getKey()
    
    if key == ord('S'):
        tabla_actual = tabla_suma
        print(">>SUMA (A + B)")
        modo_seleccionado = True
        break
    elif key == ord('R'):
        tabla_actual = tabla_resta
        print(">>RESTA (A - B)")
        modo_seleccionado = True
        break


# EJECUCION DE LA MAQUINA 
estado_actual = 'Q0'

if modo_seleccionado:
    while robot.step(TIME_STEP) != -1:
        
        # LEER
        simbolo_leido = leer_simbolo()
        print(f"Estado: {estado_actual} | Leído: {simbolo_leido}") 
        
        # CONSULTAR LA TABLA
        clave = (estado_actual, simbolo_leido)
        
        if clave in tabla_actual:
            # Recuperamos los datos de la regla
            nuevo_estado, simbolo_escribir, movimiento = tabla_actual[clave]
            
            #  DEPURACION
            print("\n" + "="*40)
            print(f"   DIAGNÓSTICO DE TRANSICIÓN")
            print(f"   [1] Estado Actual:   {estado_actual}")
            print(f"   [2] Símbolo Leído:   '{simbolo_leido}'")
            print(f"   [3] Regla Aplicada:  {clave}  --->  {tabla_actual[clave]}")
            print(f"   >>  PRÓXIMO ESTADO:  {nuevo_estado}")
            print(f"   >>  ACCIÓN:          Escribir '{simbolo_escribir}' y Mover '{movimiento}'")
            print("="*40 + "\n")
            

            if simbolo_escribir != simbolo_leido:
                escribir_simbolo(simbolo_escribir)
            
            if nuevo_estado == 'Qf':
                print(f"--- OPERACIÓN TERMINADA ---")
                break
                
            mover_cabezal(movimiento)
            estado_actual = nuevo_estado
        
        else:
            print("\n" + "!"*40)
            print(f"ERROR FATAL: BLOQUEO DETECTADO")
            print(f"   No existe regla para: Estado {estado_actual} leyendo '{simbolo_leido}'")
            print(f"   Revisa tu tabla o los umbrales de la cámara.")
            print("!"*40 + "\n")
            break
