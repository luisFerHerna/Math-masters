import pygame
import socket
import json
import threading
import time

# --- CONFIGURACIÓN Y COLORES ---
ANCHO, ALTO = 800, 600
TITULO = "Math Masters - Entrega Final"

# Paleta de colores (Estilo Neón/Oscuro)
FONDO = (30, 30, 40)
FONDO_GRID = (50, 50, 70)
BLANCO = (240, 240, 240)
NEGRO = (20, 20, 20)
# Colores de puertas
NEON_AZUL = (56, 209, 209)       # Operaciones buenas (+, *)
NEON_ROJO = (255, 50, 80)       # Operaciones malas (-, /)
NEON_VERDE = (50, 255, 100)     # Feedback positivo
DORADO = (255, 215, 0)          # Selección / Victoria

# Opciones de color para la nave del jugador
COLORES_NAVE = [
    (0, 255, 0),    # Verde Matrix
    (255, 0, 255),  # Magenta
    (255, 165, 0),  # Naranja
    (0, 191, 255)   # Azul Cielo
]

IP_SERVIDOR = '127.0.0.1' 
PUERTO = 5555

pygame.init()
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(TITULO)

# Fuentes
f_titulo = pygame.font.SysFont("Verdana", 50, bold=True)
f_grande = pygame.font.SysFont("Verdana", 35, bold=True)
f_media = pygame.font.SysFont("Verdana", 24)
f_chica = pygame.font.SysFont("Verdana", 18)

# --- CLASES UI ---
class Boton:
    def __init__(self, txt, x, y, w, h, col, acc=None, es_icono=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.txt = txt
        self.col = col
        self.acc = acc
        self.sel = False 
        self.es_icono = es_icono

    def dibujar(self, surf):
        # Efecto de brillo si está seleccionado
        color_borde = BLANCO if self.sel else self.col
        grosor_borde = 3 if self.sel else 0
        
        # Fondo del botón
        pygame.draw.rect(surf, self.col, self.rect, border_radius=12)
        # Borde
        pygame.draw.rect(surf, color_borde, self.rect, 3, border_radius=12)
        
        # Texto
        color_texto = NEGRO if self.col == DORADO else BLANCO
        fuente = f_grande if self.es_icono else f_media
        t = fuente.render(self.txt, True, color_texto)
        surf.blit(t, t.get_rect(center=self.rect.center))

    def clic(self, pos):
        return self.acc if self.rect.collidepoint(pos) else None

class SelectorColor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.seleccionado = 0 # Índice del color
        self.radios = []
        for i, c in enumerate(COLORES_NAVE):
            cx = x + (i * 60)
            self.radios.append({"rect": pygame.Rect(cx, y, 40, 40), "col": c})

    def dibujar(self, surf):
        texto_centrado("Elige tu color:", self.y - 30, f_chica, BLANCO)
        for i, item in enumerate(self.radios):
            pygame.draw.rect(surf, item["col"], item["rect"], border_radius=50)
            # Indicar selección
            if i == self.seleccionado:
                pygame.draw.circle(surf, BLANCO, item["rect"].center, 25, 3)

    def clic(self, pos):
        for i, item in enumerate(self.radios):
            if item["rect"].collidepoint(pos):
                self.seleccionado = i

def texto_centrado(txt, y, fuente, col=BLANCO):
    obj = fuente.render(txt, True, col)
    # Sombra negra simple para contraste
    sombra = fuente.render(txt, True, NEGRO)
    ventana.blit(sombra, sombra.get_rect(center=(ANCHO//2 + 2, y + 2)))
    ventana.blit(obj, obj.get_rect(center=(ANCHO//2, y)))

# --- WORKERS (RED) ---
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
    try:
        sock.send("LISTO".encode())
        cont['data'] = "OK"
    except: cont['data'] = "ERROR"

# --- PANTALLA DE CARGA ---
def esperar_con_pantalla_carga(target, msg1, msg2):
    cont = {'data': None}
    t = threading.Thread(target=target, args=(cont,))
    t.start()
    
    clock = pygame.time.Clock()
    anim = 0
    while t.is_alive():
        clock.tick(30)
        anim += 1
        pts = "." * ((anim // 10) % 4)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "SALIR"

        ventana.fill(FONDO)
        # Dibujar un spinner simple
        cx, cy = ANCHO//2, ALTO//2 - 50
        pygame.draw.arc(ventana, NEON_AZUL, (cx-30, cy-30, 60, 60), anim*0.1, anim*0.1 + 1.5, 5)
        
        texto_centrado(f"{msg1}{pts}", ALTO//2 + 20, f_grande, BLANCO)
        texto_centrado(msg2, ALTO//2 + 60, f_chica, (150, 150, 150))
        pygame.display.update()
        
    return cont['data']

# --- AYUDA ---
def mostrar_ayuda():
    mostrar = True
    while mostrar:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return False # Cierra todo el juego
            if e.type == pygame.MOUSEBUTTONDOWN: mostrar = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: mostrar = False

        ventana.fill(FONDO)
        # Cuadro de dialogo
        rect_info = pygame.Rect(100, 80, 600, 440)
        pygame.draw.rect(ventana, (40, 40, 50), rect_info, border_radius=20)
        pygame.draw.rect(ventana, NEON_AZUL, rect_info, 3, border_radius=20)
        
        texto_centrado("CÓMO JUGAR", 110, f_grande, DORADO)
        
        instrucciones = [
            "1. Objetivo: Acumular la mayor cantidad de unidades.",
            "2. Controles: Usa las FLECHAS (Izquierda/Derecha).",
            "3. Matemáticas:",
            "   [+] Suma unidades (BUENO)",
            "   [*] Multiplica unidades (MUY BUENO)",
            "   [-] Resta unidades (EVITALO)",
            "   [/] Divide unidades (PELIGRO)",
            "",
            "4. Gana quien tenga más puntos al final de la ronda.",
            "5. El primero en ganar más rondas gana la partida.",
            "",
            "(Haz clic o presiona ESC para volver)"
        ]
        
        y_txt = 170
        for linea in instrucciones:
            col = NEON_VERDE if "BUENO" in linea else NEON_ROJO if "PELIGRO" in linea else BLANCO
            ren = f_media.render(linea, True, col)
            ventana.blit(ren, (140, y_txt))
            y_txt += 30
            
        pygame.display.update()
    return True

# --- FUNCIONES DE DIBUJO ---
def dibujar_nave(surf, x, y, color):
    # Dibuja un triángulo estilizado (nave)
    puntos = [(x, y - 20), (x - 15, y + 20), (x + 15, y + 20)]
    pygame.draw.polygon(surf, color, puntos)
    # Borde blanco para resaltar
    pygame.draw.polygon(surf, BLANCO, puntos, 2)
    # Efecto de motor
    pygame.draw.circle(surf, (255, 100, 0), (x, y+20), 5)

def dibujar_fondo_grid(surf, offset_y):
    # Efecto de movimiento en el suelo
    gap = 100
    offset_y = offset_y % gap
    for y in range(int(offset_y) - gap, ALTO, gap):
        pygame.draw.line(surf, FONDO_GRID, (0, y), (ANCHO, y), 1)
    
    # Líneas verticales de carriles
    w = ANCHO // 3
    pygame.draw.line(surf, (100, 100, 120), (w, 0), (w, ALTO), 2)
    pygame.draw.line(surf, (100, 100, 120), (w*2, 0), (w*2, ALTO), 2)

# --- JUGABILIDAD ---
def jugar_nivel(mapa, vel, num_nivel, color_jugador):
    unidades = 10
    carril = 1
    y_puerta = -150
    idx = 0
    total = len(mapa)
    clock = pygame.time.Clock()
    run = True
    feed_txt, feed_timer = "", 0
    offset_grid = 0
    
    while run:
        clock.tick(30)
        offset_grid += vel 
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "SALIR"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT and carril > 0: carril -= 1
                if e.key == pygame.K_RIGHT and carril < 2: carril += 1

        y_puerta += vel
        # Lógica de colisión
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
                else: feed_txt, feed_timer = "¡DAÑO!", 20
                idx += 1
                y_puerta = -200
            else: run = False
        
        if unidades <= 0: unidades, run = 0, False

        # --- DIBUJADO ---
        ventana.fill(FONDO)
        dibujar_fondo_grid(ventana, offset_grid)
        
        w = ANCHO // 3
        
        # Dibujar Puertas
        if idx < total:
            for i in range(3):
                d = mapa[idx][i]
                x = i * w + 20
                # Color basado en si es bueno o malo
                es_bueno = d['op'] in ['+', '*']
                c_relleno = (0, 100, 100) if es_bueno else (100, 0, 0) # Oscuro
                c_borde = NEON_AZUL if es_bueno else NEON_ROJO # Neón
                
                rect_puerta = pygame.Rect(x, y_puerta, w-40, 80)
                
                # Relleno semitransparente (simulado) y borde neón
                pygame.draw.rect(ventana, c_relleno, rect_puerta, border_radius=10)
                pygame.draw.rect(ventana, c_borde, rect_puerta, 3, border_radius=10)
                
                txt_op = f"{d['op']} {d['val']}"
                ren = f_grande.render(txt_op, True, BLANCO)
                ventana.blit(ren, ren.get_rect(center=rect_puerta.center))
        
        # Dibujar Jugador
        x_j = carril * w + (w//2)
        dibujar_nave(ventana, x_j, 500, color_jugador)
        
        # Texto flotante de unidades
        tn = f_media.render(f"{unidades}", True, BLANCO)
        ventana.blit(tn, (x_j - tn.get_width()//2, 530))
        
        # UI Superior
        pygame.draw.rect(ventana, (0,0,0), (0,0, ANCHO, 90)) # Barra negra sup
        texto_centrado(f"NIVEL {num_nivel}/10", 25, f_grande, DORADO)
        # Barra de progreso
        ancho_barra = 400
        progreso = (idx / total) * ancho_barra
        pygame.draw.rect(ventana, (100,100,100), (ANCHO//2 - 200, 60, ancho_barra, 10))
        pygame.draw.rect(ventana, NEON_AZUL, (ANCHO//2 - 200, 60, progreso, 10))
        
        # Feedback visual
        if feed_timer > 0:
            c = NEON_VERDE if feed_txt == "¡BIEN!" else NEON_ROJO
            t = f_grande.render(feed_txt, True, c)
            ventana.blit(t, (x_j+40, 480))
            feed_timer -= 1
        pygame.display.update()
        
    return unidades

# --- LOOP DE PARTIDA COMPLETA ---
def gestor_partida(sock, color_jugador):
    victorias_yo = 0
    victorias_rival = 0
    
    for i in range(1, 11):
        # 1. Esperar Nivel
        w_niv = lambda c: worker_recibir_nivel(sock, c)
        data = esperar_con_pantalla_carga(w_niv, f"Cargando Nivel {i}", "Sincronizando con servidor...")
        if data in ["ERROR", "SALIR", None]: return "MENU"
        
        # 2. Jugar
        pts = jugar_nivel(data["mapa"], data["velocidad"], i, color_jugador)
        if pts == "SALIR": return "MENU"
        
        # 3. Enviar Puntaje
        msg_w = "Esperando al rival..."
        w_res = lambda c: worker_enviar_resultado(sock, pts, c)
        res = esperar_con_pantalla_carga(w_res, "Procesando Resultados", msg_w)
        if res in ["ERROR", "SALIR", None]: return "MENU"
        
        # 4. RESULTADOS DE RONDA
        esperando_click = True
        btn_next = Boton("SIGUIENTE NIVEL", ANCHO//2 - 125, 500, 250, 60, NEON_AZUL, "NEXT")
        
        while esperando_click:
            pos = pygame.mouse.get_pos()
            for e in pygame.event.get():
                if e.type == pygame.QUIT: return "MENU"
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if btn_next.clic(pos):
                        w_conf = lambda c: worker_confirmar_siguiente(sock, c)
                        esperar_con_pantalla_carga(w_conf, "Esperando al otro jugador", "")
                        esperando_click = False

            ventana.fill(FONDO)
            est = res["estado"]
            col = NEON_VERDE if est == "GANASTE" else NEON_ROJO if est == "PERDISTE" else BLANCO
            
            texto_centrado(f"RESULTADO NIVEL {i}", 50, f_media, BLANCO)
            texto_centrado(est, 120, f_titulo, col)
            
            # Tarjeta de stats
            pygame.draw.rect(ventana, (40,40,50), (ANCHO//2-150, 180, 300, 120), border_radius=15)
            texto_centrado(f"Tú: {res['mis_puntos']}", 210, f_media, color_jugador)
            texto_centrado(f"Rival: {res['rival_puntos']}", 250, f_media, (200,200,200))
            
            victorias_yo, victorias_rival = res["mis_victorias"], res["rival_victorias"]
            
            texto_centrado("--- MARCADOR GLOBAL ---", 340, f_chica, (150,150,150))
            texto_centrado(f"{victorias_yo} - {victorias_rival}", 370, f_grande, DORADO)
            
            btn_next.dibujar(ventana)
            pygame.display.update()

    # --- FINAL DEL JUEGO ---
    btn_salir = Boton("VOLVER AL MENÚ", ANCHO//2 - 125, 500, 250, 60, NEON_ROJO, "SALIR")
    while True:
        pos = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "MENU"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_salir.clic(pos): return "MENU"

        ventana.fill(FONDO)
        texto_centrado("JUEGO TERMINADO", 100, f_titulo, NEON_AZUL)
        
        msg = "¡VICTORIA SUPREMA!" if victorias_yo > victorias_rival else "DERROTA"
        col = NEON_VERDE if victorias_yo > victorias_rival else NEON_ROJO
        if victorias_yo == victorias_rival: msg, col = "EMPATE TÉCNICO", BLANCO
        
        texto_centrado(msg, 250, f_titulo, col)
        texto_centrado(f"Marcador Final: {victorias_yo} - {victorias_rival}", 350, f_grande, BLANCO)
        
        btn_salir.dibujar(ventana)
        pygame.display.update()

def main():
    est = "MENU"
    
    # Elementos del Menu
    b_play = Boton("CONECTAR Y JUGAR", ANCHO//2-150, 480, 300, 70, NEON_AZUL, "JUGAR")
    b_help = Boton("?", ANCHO - 70, 20, 50, 50, DORADO, "HELP", es_icono=True)
    selector = SelectorColor(ANCHO//2 - 100, 350)

    run = True
    while run:
        pos = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: run = False
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                if est == "MENU":
                    selector.clic(pos) # Actualizar selección de color
                    
                    if b_help.clic(pos):
                        continuar = mostrar_ayuda()
                        if not continuar: run = False # Si cierra la ayuda con X
                    
                    elif b_play.clic(pos):
                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.connect((IP_SERVIDOR, PUERTO))
                            # Obtenemos color seleccionado
                            col_elegido = selector.radios[selector.seleccionado]["col"]
                            est = gestor_partida(s, col_elegido)
                            s.close()
                        except Exception as ex:
                            print(ex)
                            est = "ERROR"
                
                elif est == "ERROR":
                    est = "MENU"

        ventana.fill(FONDO)
        if est == "MENU":
            # Título con sombra
            texto_centrado("MATH MASTERS", 150, f_titulo, NEON_AZUL)
            texto_centrado("Edición Multijugador", 200, f_media, BLANCO)
            
            selector.dibujar(ventana)
            b_play.dibujar(ventana)
            b_help.dibujar(ventana)
            
            # Dibujar preview del jugador
            col_act = selector.radios[selector.seleccionado]["col"]
            dibujar_nave(ventana, ANCHO//2, 280, col_act)

        elif est == "ERROR":
            texto_centrado("NO SE PUDO CONECTAR", ALTO//2 - 30, f_grande, NEON_ROJO)
            texto_centrado("Asegúrate que servidor.py esté corriendo", ALTO//2 + 20, f_chica, BLANCO)
            texto_centrado("Haz clic para volver", ALTO - 100, f_media, (150,150,150))
            
        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    main()