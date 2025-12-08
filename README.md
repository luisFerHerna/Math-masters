# ➗ Math Masters

Proyecto educativo Cliente-Servidor desarrollado en Python como entrega final de la materia "Redes de Computadoras II".

Math Masters es un juego multijugador (2 jugadores) donde los participantes resuelven operaciones matemáticas mientras avanzan por niveles sincronizados por un servidor.

---

## Requisitos

- Python 3.8 o superior
- `pygame` (interfaz gráfica)

Instalar dependencias:

```bash
pip install pygame
```

---

## Estructura del repositorio

- `servidor.py` : Código del servidor (acepta conexiones, sincroniza niveles, genera mapas y preguntas)
- `cliente.py`  : Código del cliente (interfaz del jugador, comunicación con el servidor)
- `README.md`   : Documentación del proyecto

---

## Uso (modo rápido)

1. Ejecutar el servidor (máquina anfitriona):

```bash
python3 servidor.py
```

El servidor quedará esperando las conexiones de los clientes (2 jugadores).

2. Ejecutar cada cliente (en la misma máquina o en otra dentro de la misma red):

```bash
python3 cliente.py
```

Si el servidor se ejecuta en otra máquina, editar en `cliente.py` la variable que contiene la dirección IP del servidor (por ejemplo `IP_SERVIDOR = '192.168.1.X'`).

---

## Configuración de red

- Local (misma máquina): dejar `IP_SERVIDOR = '127.0.0.1'` en `cliente.py`.
- Red local (LAN): obtener la IP del servidor con `ifconfig` o `ip a` y usarla en `cliente.py`.

Nota: Asegúrate de que el puerto usado esté permitido por el firewall local.

---

## Controles

- Esquema 1: Flechas (`←`, `→`)
- Esquema 2: `A` y `D` (o `WASD` según implementación)
- Confirmar/Seleccionar: clic izquierdo del ratón

Las opciones de control se seleccionan desde el menú inicial del cliente.

---

## Contribuir

Si quieres contribuir, abre un issue o un pull request con mejoras, correcciones o nuevas características. Para cambios grandes, crea primero un issue describiendo la propuesta.

---

## Créditos

- Universidad Tecnológica de la Mixteca — Asignatura: Redes de Computadoras II
- Profesor: M.C. Mónica E. García García
- Autor: Luis Fernando Hernández

---

## Licencia

Este repositorio no incluye una licencia explícita. Si planeas compartir o usar el código públicamente, considera añadir una licencia (por ejemplo, MIT) en un archivo `LICENSE`.
# ➗ Math Masters - Multiplayer Math Runner

> **Proyecto Ordinario:** Redes de Computadoras II  
> **Universidad Tecnológica de la Mixteca (UTM)**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green?style=for-the-badge&logo=python)
![Sockets](https://img.shields.io/badge/Network-Sockets_TCP%2FIP-red?style=for-the-badge)

## 📋 Descripción del Proyecto

**Math Masters** es un videojuego educativo multijugador en tiempo real desarrollado en Python. Implementa una arquitectura **Cliente-Servidor** utilizando **Sockets (TCP/IP)** para sincronizar partidas entre dos jugadores simultáneos.

El objetivo del juego es resolver operaciones matemáticas rápidas (suma, resta, multiplicación, división) mientras se avanza por un carril de obstáculos, compitiendo por obtener el puntaje más alto al final de **10 niveles progresivos**.

Este proyecto fue desarrollado como entrega final para la materia de **Redes de Computadoras II**.

---

## ⚙️ Arquitectura y Tecnologías

El sistema cumple con los requisitos técnicos de una aplicación multiusuario:

* **Comunicación:** Uso de Sockets de Berkeley (módulo `socket` de Python) para transmisión de datos.
* **Modelo:** Cliente-Servidor. El servidor es la autoridad que gestiona el estado, genera los niveles y arbitra los resultados.
* **Concurrencia:**
    * **Servidor:** Uso de `threading` y `threading.Barrier` para sincronizar el inicio y fin de cada nivel, asegurando que ambos jugadores vean lo mismo al mismo tiempo.
    * **Cliente:** Implementación de hilos (workers) para la comunicación de red en segundo plano, evitando que la interfaz gráfica (GUI) se congele durante las esperas (Anti-Freeze).
* **Interfaz Gráfica:** Librería `pygame` para renderizado visual.

---

## 🚀 Características Principales

* **Modo Multijugador Real:** 2 jugadores conectados a la misma red compiten en tiempo real.
* **10 Niveles Progresivos:** La dificultad y la velocidad aumentan con cada nivel.
* **Generación Procedural:** Los mapas se generan aleatoriamente en el servidor y se envían idénticos a ambos clientes.
* **Sincronización de Estados:** Sistema de "Handshake" manual al finalizar cada nivel; el juego no avanza hasta que ambos jugadores confirman estar listos.
* **Temática Educativa:** Enfocado en agilidad mental matemática (operaciones básicas) para un rango de edad de 10-15 años.

---

## 🛠️ Instalación y Ejecución

### Prerrequisitos
Tener Python 3.x instalado y la librería Pygame:
```bash
pip install pygame
1. Configuración de RedLocal (1 PC): Dejar IP_SERVIDOR = '127.0.0.1' en cliente.py.LAN (2 PCs): 1. Ejecutar el servidor en una máquina y obtener su IP (ej. ipconfig o ifconfig).2. Editar cliente.py y cambiar IP_SERVIDOR por la IP de la máquina servidor.2. Ejecutar el ServidorEn la terminal de la máquina anfitriona:Bashpython servidor.py
El servidor quedará en espera de 2 conexiones.3. Ejecutar los ClientesEn las terminales de los jugadores (o nuevas terminales):Bashpython cliente.py
🎮 ControlesAl iniciar, cada cliente puede seleccionar su esquema de control preferido desde el menú:AcciónEsquema 1 (Flechas)Esquema 2 (WASD)Mover Izquierda⬅️ Flecha IzquierdaAMover Derecha➡️ Flecha DerechaDConfirmar/SalirClick Izquierdo del MouseClick Izquierdo del Mouse🎓 Créditos AcadémicosUniversidad Tecnológica de la Mixteca Ingeniería en Computación / DiseñoMateria: Redes de Computadoras IIProfesor: M.C. Mónica E. García GarcíaAlumno: Luis Fernando HernándezFecha: Diciembre 2025
---

### Parte 2: Comandos para hacerlo desde VS Code

Sigue estos pasos en tu Visual Studio Code. Usaremos la terminal integrada para todo, que es la forma más rápida.

#### 1. Abre la Terminal Integrada
Si no la ves, presiona `Ctrl` + `ñ` (o `Ctrl` + `J`).

#### 2. Crea y abre el archivo
Escribe este comando. `code` es el comando mágico de VS Code que abre un archivo inmediatamente para editarlo.

```bash
code README.md