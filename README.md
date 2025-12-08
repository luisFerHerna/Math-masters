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

