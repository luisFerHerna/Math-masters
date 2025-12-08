import socket
import threading
import json
import random
import time

HOST = '0.0.0.0'
PORT = 5555

CLIENTES = []
VICTORIAS = {1: 0, 2: 0}
PUNTAJES_NIVEL = {}
BARRERA = threading.Barrier(2) # El semáforo para sincronizar a los 2

def generar_nivel(numero_nivel):
    secciones = []
    # Nivel 1 = 12 secciones, Nivel 10 = 21 secciones
    cantidad_secciones = 11 + numero_nivel 
    operaciones = ['+', '-', '*', '/']
    
    for _ in range(cantidad_secciones):
        fila = []
        for _ in range(3):
            op = random.choice(operaciones)
            rango = 10 + (numero_nivel * 2)
            val = random.randint(1, rango)
            if op == '/': val = 2
            if op == '*': val = random.randint(2, 3)
            fila.append({"op": op, "val": val})
        secciones.append(fila)
    return secciones

def manejar_cliente(conn, id_jugador):
    print(f"Jugador {id_jugador} conectado.")
    
    try:
        # BUCLE DE 10 NIVELES
        for nivel_actual in range(1, 11):
            
            # --- PASO 1: Sincronizar inicio de nivel ---
            BARRERA.wait()
            
            # Generar mapa (usamos semilla para que sea idéntico en ambos hilos)
            semilla = nivel_actual * 999
            random.seed(semilla)
            mapa = generar_nivel(nivel_actual)
            velocidad = 6 + (nivel_actual * 1.5)
            
            datos_inicio = {
                "nivel": nivel_actual,
                "mapa": mapa,
                "velocidad": velocidad,
                "victorias": VICTORIAS
            }
            conn.send(json.dumps(datos_inicio).encode())
            
            # --- PASO 2: Recibir puntaje del juego ---
            raw_score = conn.recv(1024).decode()
            if not raw_score: break
            puntaje = int(raw_score)
            PUNTAJES_NIVEL[id_jugador] = puntaje
            
            # --- PASO 3: Esperar al otro jugador (si uno murió rápido) ---
            BARRERA.wait()
            
            # Calcular ganador ronda
            rival_id = 1 if id_jugador == 2 else 2
            pts_rival = PUNTAJES_NIVEL.get(rival_id, 0)
            
            estado = "EMPATE"
            if puntaje > pts_rival: estado = "GANASTE"
            elif puntaje < pts_rival: estado = "PERDISTE"
            
            # Actualizar victorias globales (solo hilo 1 escribe para no duplicar)
            if id_jugador == 1:
                if PUNTAJES_NIVEL[1] > PUNTAJES_NIVEL[2]: VICTORIAS[1] += 1
                elif PUNTAJES_NIVEL[2] > PUNTAJES_NIVEL[1]: VICTORIAS[2] += 1
            
            time.sleep(0.1) # Breve pausa técnica
            
            # Enviar resultados
            datos_fin = {
                "estado": estado,
                "mis_puntos": puntaje,
                "rival_puntos": pts_rival,
                "mis_victorias": VICTORIAS[id_jugador],
                "rival_victorias": VICTORIAS[rival_id]
            }
            conn.send(json.dumps(datos_fin).encode())
            
            # --- PASO 4 (NUEVO): ESPERAR CONFIRMACIÓN MANUAL ---
            # El servidor espera a que el cliente mande "LISTO" (botón clicado)
            msg_confirm = conn.recv(1024).decode() # Bloqueante
            
            # Esperamos a que EL OTRO también haya dado clic
            BARRERA.wait()
            
            # Aquí termina el ciclo y vuelve arriba para el siguiente nivel

    except Exception as e:
        print(f"Error J{id_jugador}: {e}")
    finally:
        conn.close()

def iniciar():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print("SERVIDOR LISTO. Esperando conexiones...")
    print(f"IP: {socket.gethostbyname(socket.gethostname())}")

    for i in range(1, 3):
        c, a = server.accept()
        t = threading.Thread(target=manejar_cliente, args=(c, i))
        t.start()

if __name__ == "__main__":
    iniciar()