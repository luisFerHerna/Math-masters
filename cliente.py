import pygame
import socket
import json
import threading
import time

# --- CONFIGURACIÓN ---
ANCHO, ALTO = 800, 600
TITULO = "Math Masters - Entrega Final"

# Colores
BLANCO = (240, 240, 240)
NEGRO = (20, 20, 20)
AZUL = (50, 100, 255)
ROJO = (255, 80, 80)
VERDE = (50, 200, 100)
GRIS = (200, 200, 200)
DORADO = (255, 215, 0)

IP_SERVIDOR = '127.0.0.1' 
PUERTO = 5555

pygame.init()
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(TITULO)
f_grande = pygame.font.SysFont("Arial", 40, bold=True)
f_media = pygame.font.SysFont("Arial", 28)
f_chica = pygame.font.SysFont("Arial", 20)

# --- CLASES ---
class Boton:
    def __init__(self, txt, x, y, w, h, col, acc=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.txt = txt
        self.col = col
        self.acc = acc
        self.sel = False 

    def dibujar(self, surf):
        color = DORADO if self.sel else self.col
        grosor = 5 if self.sel else 0
        pygame.draw.rect(surf, color, self.rect, border_radius=10)
        if self.sel: pygame.draw.rect(surf, NEGRO, self.rect, 2, border_radius=10)
        t = f_media.render(self.txt, True, BLANCO if not self.sel else NEGRO)
        surf.blit(t, t.get_rect(center=self.rect.center))

    def clic(self, pos):
        return self.acc if self.rect.collidepoint(pos) else None

def texto_centrado(txt, y, fuente, col=NEGRO):
    obj = fuente.render(txt, True, col)
    ventana.blit(obj, obj.get_rect(center=(ANCHO//2, y)))

# --- WORKERS (HILOS) ---
def worker_recibir_nivel(sock, cont):
    try:
        raw = sock.recv(16384).decode()
        cont['data'] = json.loads(raw) if raw else "ERROR"
    except: cont['data'] = "ERROR"

def worker_enviar_resultado(sock, pts, cont):
    try:
        sock.send(str(pts).encode())
        raw = sock.recv(2048).decode()
        cont['data'] = json.loads(raw) if raw else "ERROR"
    except: cont['data'] = "ERROR"

def worker_confirmar_siguiente(sock, cont):
    """Envía señal de listo y espera que el servidor libere la barrera"""
    try:
        sock.send("LISTO".encode())
        # No esperamos respuesta inmediata aquí, el flujo sigue a esperar nivel
        cont['data'] = "OK"
    except: cont['data'] = "ERROR"

# --- PANTALLA DE CARGA (Evita congelamiento) ---
def esperar_con_pantalla_carga(target, msg1, msg2):
    cont = {'data': None}
    t = threading.Thread(target=target, args=(cont,))
    t.start()
    
    clock = pygame.time.Clock()
    anim = 0
    while t.is_alive():
        clock.tick(30)
        anim += 1
        pts = "." * ((anim // 15) % 4)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "SALIR"

        ventana.fill(BLANCO)
        texto_centrado(f"{msg1}{pts}", ALTO//2 - 20, f_grande, AZUL)
        texto_centrado(msg2, ALTO//2 + 30, f_chica, GRIS)
        pygame.display.update()
        
    return cont['data']

# --- JUGABILIDAD ---
def jugar_nivel(mapa, vel, control, num_nivel):
    unidades = 10
    carril = 1
    y_puerta = -150
    idx = 0
    total = len(mapa)
    clock = pygame.time.Clock()
    run = True
    feed_txt, feed_timer = "", 0
    
    while run:
        clock.tick(30)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "SALIR"
            if e.type == pygame.KEYDOWN:
                izq, der = False, False
                if control == "FLECHAS":
                    if e.key == pygame.K_LEFT: izq = True
                    if e.key == pygame.K_RIGHT: der = True
                else:
                    if e.key == pygame.K_a: izq = True
                    if e.key == pygame.K_d: der = True
                if izq and carril > 0: carril -= 1
                if der and carril < 2: carril += 1

        y_puerta += vel
        if y_puerta >= 450:
            if idx < total:
                p = mapa[idx][carril]
                op, val = p['op'], p['val']
                ant = unidades
                if op == '+': unidades += val
                elif op == '-': unidades = max(0, unidades - val)
                elif op == '*': unidades *= val
                elif op == '/': unidades //= val
                
                if unidades > ant: feed_txt, feed_timer = "¡BIEN!", 20
                else: feed_txt, feed_timer = "¡MAL!", 20
                idx += 1
                y_puerta = -200
            else: run = False
        
        if unidades <= 0: unidades, run = 0, False

        ventana.fill(BLANCO)
        w = ANCHO // 3
        pygame.draw.line(ventana, GRIS, (w,0), (w,ALTO), 2)
        pygame.draw.line(ventana, GRIS, (w*2,0), (w*2,ALTO), 2)
        
        if idx < total:
            for i in range(3):
                d = mapa[idx][i]
                x = i * w + 20
                c = AZUL if d['op'] in ['+', '*'] else ROJO
                pygame.draw.rect(ventana, c, (x, y_puerta, w-40, 80), 0, 10)
                t = f_grande.render(f"{d['op']} {d['val']}", True, BLANCO)
                ventana.blit(t, (x+40, y_puerta+20))
        
        x_j = carril * w + (w//2)
        pygame.draw.circle(ventana, VERDE, (x_j, 500), 30)
        tn = f_chica.render(str(unidades), True, NEGRO)
        ventana.blit(tn, tn.get_rect(center=(x_j, 500)))
        
        texto_centrado(f"NIVEL {num_nivel}/10", 30, f_grande)
        texto_centrado(f"Progreso: {idx}/{total}", 70, f_chica)
        if feed_timer > 0:
            c = VERDE if feed_txt == "¡BIEN!" else ROJO
            t = f_grande.render(feed_txt, True, c)
            ventana.blit(t, (x_j+40, 450))
            feed_timer -= 1
        pygame.display.update()
        
    return unidades

# --- LOOP PRINCIPAL ---
def gestor_partida(sock, controles):
    victorias_yo = 0
    victorias_rival = 0
    
    for i in range(1, 11):
        # 1. Esperar Nivel
        w_niv = lambda c: worker_recibir_nivel(sock, c)
        data = esperar_con_pantalla_carga(w_niv, f"Cargando Nivel {i}", "Sincronizando...")
        if data in ["ERROR", "SALIR", None]: return "MENU"
        
        # 2. Jugar
        pts = jugar_nivel(data["mapa"], data["velocidad"], controles, i)
        if pts == "SALIR": return "MENU"
        
        # 3. Enviar Puntaje y Esperar Resultado
        msg_w = "Esperando al rival..." if pts > 0 else "Has perdido. Esperando rival..."
        w_res = lambda c: worker_enviar_resultado(sock, pts, c)
        res = esperar_con_pantalla_carga(w_res, "Calculando", msg_w)
        if res in ["ERROR", "SALIR", None]: return "MENU"
        
        # 4. MOSTRAR RESULTADOS Y ESPERAR CLICK
        esperando_click = True
        btn_next = Boton("SIGUIENTE NIVEL", ANCHO//2 - 125, 500, 250, 60, AZUL, "NEXT")
        
        while esperando_click:
            pos = pygame.mouse.get_pos()
            for e in pygame.event.get():
                if e.type == pygame.QUIT: return "MENU"
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if btn_next.clic(pos):
                        # Enviar confirmación al servidor
                        w_conf = lambda c: worker_confirmar_siguiente(sock, c)
                        # Esto es rápido, pero necesario para liberar la barrera
                        esperar_con_pantalla_carga(w_conf, "Confirmando...", "")
                        esperando_click = False

            ventana.fill(BLANCO)
            est = res["estado"]
            col = VERDE if est == "GANASTE" else ROJO if est == "PERDISTE" else AZUL
            
            texto_centrado(f"FIN DEL NIVEL {i}", 50, f_media)
            texto_centrado(est, 120, f_grande, col)
            
            texto_centrado(f"Tú: {res['mis_puntos']}", 200, f_media)
            texto_centrado(f"Rival: {res['rival_puntos']}", 240, f_media)
            
            v_yo, v_riv = res["mis_victorias"], res["rival_victorias"]
            victorias_yo, victorias_rival = v_yo, v_riv
            
            texto_centrado("--- GLOBAL ---", 320, f_chica, GRIS)
            texto_centrado(f"{v_yo} - {v_riv}", 350, f_grande, DORADO)
            
            # Botón de espera
            btn_next.dibujar(ventana)
            pygame.display.update()

    # --- FINAL DEL JUEGO (NIVEL 10 ACABADO) ---
    btn_salir = Boton("SALIR AL MENU", ANCHO//2 - 100, 500, 200, 60, ROJO, "SALIR")
    while True:
        pos = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "MENU"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_salir.clic(pos): return "MENU"

        ventana.fill(BLANCO)
        texto_centrado("JUEGO TERMINADO", 100, f_grande, AZUL)
        
        msg = "¡VICTORIA TOTAL!" if victorias_yo > victorias_rival else "DERROTA"
        col = VERDE if victorias_yo > victorias_rival else ROJO
        if victorias_yo == victorias_rival: msg, col = "EMPATE", AZUL
        
        texto_centrado(msg, 250, f_grande, col)
        texto_centrado(f"Marcador Final: {victorias_yo} - {victorias_rival}", 350, f_media)
        
        btn_salir.dibujar(ventana)
        pygame.display.update()

def main():
    est = "MENU"
    ctrl = "FLECHAS"
    b_play = Boton("JUGAR", ANCHO//2-100, 450, 200, 60, AZUL, "JUGAR")
    b_arr = Boton("Flechas", ANCHO//2-160, 350, 150, 50, GRIS)
    b_wsd = Boton("WASD", ANCHO//2+10, 350, 150, 50, GRIS)
    b_arr.sel = True

    run = True
    while run:
        pos = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: run = False
            if e.type == pygame.MOUSEBUTTONDOWN and est == "MENU":
                if b_arr.clic(pos): ctrl, b_arr.sel, b_wsd.sel = "FLECHAS", True, False
                elif b_wsd.clic(pos): ctrl, b_arr.sel, b_wsd.sel = "WASD", False, True
                
                if b_play.clic(pos):
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((IP_SERVIDOR, PUERTO))
                        est = gestor_partida(s, ctrl)
                        s.close()
                    except: est = "ERROR"
            
            if e.type == pygame.MOUSEBUTTONDOWN and est == "ERROR": est = "MENU"

        ventana.fill(BLANCO)
        if est == "MENU":
            texto_centrado("MATH MASTERS", 150, f_grande, AZUL)
            texto_centrado("Elige Controles:", 300, f_chica)
            b_arr.dibujar(ventana)
            b_wsd.dibujar(ventana)
            b_play.dibujar(ventana)
        elif est == "ERROR":
            texto_centrado("Error de conexión", ALTO//2, f_media, ROJO)
        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    main()