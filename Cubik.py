#Creado Por Mariano Alejandro Orrego - Inspirado e en Geometry Dash
from tkinter import *
import random
import math
import time
from threading import Thread
import pygame
import numpy as np
from collections import deque


pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)


SONIDOS_CACHE = {}

ANCHO_VENTANA = 1400
ALTO_VENTANA = 700
TAMANO_JUGADOR = 30
GRAVEDAD = 1.8
FUERZA_SALTO = -20
SUELO_Y = ALTO_VENTANA - 150
LIMITE_SUPERIOR = 100  # Límite superior donde está el HUD (línea de colores)
FPS = 120  
TAMANO_BLOQUE = 40


MAX_PARTICULAS = 150  
MAX_TRAILS = 15  
RUNWAY_DISTANCE = 1000
INTERPOLACION_FISICA = True  


JUGADOR_X_FIJO = 200


TEMA_NEON = True  
ANIMACIONES_MENU = True 
PARTICULAS_FONDO = True  
FONDO_ANIMADO = True  
GLOW_INTENSO = True  


VELOCIDADES = {
    "x1": 3,   
    "x2": 4.5, 
    "x3": 6,   
    "x4": 7.5  
}


MODOS_JUEGO = {
    "cube": {"nombre": "Cube", "gravedad": 0.9, "salto": -13, "puede_mantener": False},
    "ship": {"nombre": "Ship", "gravedad": 0.4, "salto": -0.8, "puede_mantener": True},
    "ball": {"nombre": "Ball", "gravedad": 0.9, "salto": -13, "puede_mantener": False},
    "ufo": {"nombre": "UFO", "gravedad": 0.5, "salto": -8, "puede_mantener": False},
    "wave": {"nombre": "Wave", "gravedad": 0, "salto": 0, "puede_mantener": True},
    "robot": {"nombre": "Robot", "gravedad": 0.75, "salto": -13, "puede_mantener": False}
}


EFECTOS_VISUALES = {
    "glow": True,
    "screen_shake_intenso": True,
    "particulas_mejoradas": True,
    "motion_blur": True,
    "chromatic_aberration": False,  
    "camera_zoom": True
}


COLORES = {
    1: {"bg1": "#0a0e27", "bg2": "#1a1e3e", "suelo": "#2d4059", "player": "#00ff88", 
        "obstaculo": "#ff0080", "plataforma": "#00d9ff", "moneda": "#ffea00"},
    2: {"bg1": "#1a0a00", "bg2": "#2d1500", "suelo": "#3d2000", "player": "#ff4500", 
        "obstaculo": "#ff0000", "plataforma": "#ffaa00", "moneda": "#ffea00"},
    3: {"bg1": "#001a33", "bg2": "#002d4d", "suelo": "#004d66", "player": "#00ffff", 
        "obstaculo": "#ff1493", "plataforma": "#4dffc3", "moneda": "#ffea00"},
    4: {"bg1": "#1a0a1a", "bg2": "#2d152d", "suelo": "#4d2d4d", "player": "#ffea00", 
        "obstaculo": "#ff0066", "plataforma": "#ff00ff", "moneda": "#00ffff"}
}


def generar_sonido_sintetico(frecuencia, duracion, tipo="sine"):
    """Genera sonidos sintéticos de alta calidad con pygame"""
    sample_rate = 44100
    n_samples = int(sample_rate * duracion)
    t = np.linspace(0, duracion, n_samples, False)
    
    if tipo == "sine":
        wave = np.sin(2 * np.pi * frecuencia * t)
    elif tipo == "square":
        wave = np.sign(np.sin(2 * np.pi * frecuencia * t))
    elif tipo == "triangle":
        wave = 2 * np.abs(2 * ((frecuencia * t) % 1) - 1) - 1
    else:
        wave = np.sin(2 * np.pi * frecuencia * t)
    
   
    attack = int(n_samples * 0.1)
    decay = int(n_samples * 0.2)
    sustain_level = 0.7
    release = int(n_samples * 0.3)
    
    envelope = np.ones(n_samples)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[attack:attack+decay] = np.linspace(1, sustain_level, decay)
    envelope[-release:] = np.linspace(sustain_level, 0, release)
    
    wave = wave * envelope * 0.3 
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    
    return pygame.sndarray.make_sound(stereo_wave)

def inicializar_sonidos():
    """Inicializa y cachea todos los sonidos del juego"""
    global SONIDOS_CACHE
    print("Inicializando sonidos...")
    
    SONIDOS_CACHE = {
        "salto": generar_sonido_sintetico(800, 0.05, "square"),
        "muerte": generar_sonido_sintetico(200, 0.2, "sine"),
        "moneda": generar_sonido_sintetico(1200, 0.08, "triangle"),
        "victoria": generar_sonido_sintetico(1500, 0.3, "sine"),
        "checkpoint": generar_sonido_sintetico(600, 0.1, "square"),
        "explosion": generar_sonido_sintetico(100, 0.15, "square"),
        "whoosh": generar_sonido_sintetico(400, 0.1, "triangle")
    }
    print("Sonidos listos!")


SONIDOS = {
    "salto": (800, 50),
    "muerte": (200, 200),
    "moneda": (1200, 80),
    "victoria": (1500, 300),
    "checkpoint": (600, 100)
}


def crear_nivel_1():
    """Nivel 1: PLATAFORMAS - Domina los saltos y obstáculos básicos"""
    return {
        "nombre": "PLATFORM MASTER",
        "numero": 1,
        "velocidad_inicial": "x1",
        "longitud": 5450,
        "objetos": [
            {"tipo": "bloque", "x": 1200, "altura": 1},
            {"tipo": "bloque", "x": 1400, "altura": 1},
            {"tipo": "bloque", "x": 1600, "altura": 1},
            {"tipo": "moneda", "x": 1600, "y": 470, "id": 1},
            {"tipo": "bloque", "x": 1800, "altura": 1},
            {"tipo": "bloque", "x": 2000, "altura": 1},
            {"tipo": "pincho", "x": 2150},
            {"tipo": "bloque", "x": 2300, "altura": 1},
            {"tipo": "pincho", "x": 2450},
            {"tipo": "bloque", "x": 2600, "altura": 1},
            {"tipo": "bloque", "x": 2900, "altura": 1},
            {"tipo": "bloque", "x": 3000, "altura": 1},
            {"tipo": "bloque", "x": 3000, "altura": 2},
            {"tipo": "bloque", "x": 3080, "altura": 1},
            {"tipo": "moneda", "x": 3080, "y": 480, "id": 2},
            {"tipo": "plataforma", "x": 3080, "y": 400, "ancho": 100},
            {"tipo": "plataforma", "x": 3120, "y": 400, "ancho": 100},
            {"tipo": "plataforma", "x": 3200, "y": 400, "ancho": 100},
            {"tipo": "plataforma", "x": 3320, "y": 520, "ancho": 100},
            {"tipo": "pincho", "x": 3440},
            {"tipo": "pincho", "x": 3480},
            {"tipo": "plataforma", "x": 3480, "y": 480, "ancho": 100},
            {"tipo": "plataforma", "x": 3520, "y": 480, "ancho": 100},
            {"tipo": "plataforma", "x": 3600, "y": 480, "ancho": 100},
            {"tipo": "plataforma", "x": 3800, "y": 440, "ancho": 100},
            {"tipo": "plataforma", "x": 3840, "y": 440, "ancho": 100},
            {"tipo": "moneda", "x": 3880, "y": 520, "id": 3},
            {"tipo": "plataforma", "x": 4000, "y": 460, "ancho": 120},
            {"tipo": "plataforma", "x": 4160, "y": 440, "ancho": 100},
            {"tipo": "plataforma", "x": 4200, "y": 440, "ancho": 100},
            {"tipo": "pincho", "x": 4440},
            {"tipo": "bloque", "x": 4600, "altura": 1},
            {"tipo": "pincho", "x": 4680},
            {"tipo": "bloque", "x": 4800, "altura": 1},
            {"tipo": "end", "x": 4950}
        ]
    }

def crear_nivel_2():
    """Nivel 2: SHIP HELL - Túnel infernal con sierras"""
    return {
        "nombre": "SHIP HELL",
        "numero": 2,
        "velocidad_inicial": "x1",
        "longitud": 5950,
        "objetos": [
            {"tipo": "bloque", "x": 1200, "altura": 1},
            {"tipo": "bloque", "x": 1400, "altura": 1},
            {"tipo": "moneda", "x": 1400, "y": 470, "id": 1},
            {"tipo": "portal_ship", "x": 1600},
            {"tipo": "pincho", "x": 1760},
            {"tipo": "pincho", "x": 1800},
            {"tipo": "pincho", "x": 1840},
            {"tipo": "pincho", "x": 1880},
            {"tipo": "plataforma", "x": 1900, "y": 300, "ancho": 150},
            {"tipo": "pincho", "x": 1920},
            {"tipo": "pincho", "x": 1960},
            {"tipo": "pincho", "x": 2000},
            {"tipo": "pincho", "x": 2040},
            {"tipo": "pincho", "x": 2080},
            {"tipo": "pincho", "x": 2120},
            {"tipo": "pincho", "x": 2160},
            {"tipo": "plataforma", "x": 2200, "y": 370, "ancho": 150},
            {"tipo": "pincho", "x": 2200},
            {"tipo": "pincho", "x": 2240},
            {"tipo": "moneda", "x": 2275, "y": 320, "id": 2},
            {"tipo": "pincho", "x": 2280},
            {"tipo": "pincho", "x": 2320},
            {"tipo": "pincho", "x": 2360},
            {"tipo": "pincho", "x": 2400},
            {"tipo": "pincho", "x": 2440},
            {"tipo": "pincho", "x": 2480},
            {"tipo": "plataforma", "x": 2500, "y": 250, "ancho": 150},
            {"tipo": "pincho", "x": 2520},
            {"tipo": "pincho", "x": 2560},
            {"tipo": "pincho", "x": 2600},
            {"tipo": "pincho", "x": 2640},
            {"tipo": "pincho", "x": 2680},
            {"tipo": "pincho", "x": 2720},
            {"tipo": "pincho", "x": 2760},
            {"tipo": "plataforma", "x": 2800, "y": 350, "ancho": 150},
            {"tipo": "pincho", "x": 2800},
            {"tipo": "pincho", "x": 2840},
            {"tipo": "pincho", "x": 2880},
            {"tipo": "pincho", "x": 2920},
            {"tipo": "pincho", "x": 2960},
            {"tipo": "pincho", "x": 3000},
            {"tipo": "pincho", "x": 3040},
            {"tipo": "pincho", "x": 3080},
            {"tipo": "plataforma", "x": 3100, "y": 290, "ancho": 150},
            {"tipo": "pincho", "x": 3120},
            {"tipo": "pincho", "x": 3160},
            {"tipo": "portal_cube", "x": 3200},
            {"tipo": "bloque", "x": 3400, "altura": 1},
            {"tipo": "pincho", "x": 3550},
            {"tipo": "bloque", "x": 3700, "altura": 1},
            {"tipo": "bloque", "x": 3900, "altura": 2},
            {"tipo": "portal_ship", "x": 4100},
            {"tipo": "pincho", "x": 4200},
            {"tipo": "pincho", "x": 4240},
            {"tipo": "pincho", "x": 4280},
            {"tipo": "sierra", "x": 4280, "y": 120},
            {"tipo": "pincho", "x": 4320},
            {"tipo": "pincho", "x": 4360},
            {"tipo": "pincho", "x": 4400},
            {"tipo": "pincho", "x": 4440},
            {"tipo": "sierra", "x": 4440, "y": 440},
            {"tipo": "pincho", "x": 4480},
            {"tipo": "pincho", "x": 4520},
            {"tipo": "pincho", "x": 4560},
            {"tipo": "pincho", "x": 4600},
            {"tipo": "pincho", "x": 4640},
            {"tipo": "pincho", "x": 4680},
            {"tipo": "moneda", "x": 4680, "y": 280},
            {"tipo": "sierra", "x": 4680, "y": 80},
            {"tipo": "pincho", "x": 4720},
            {"tipo": "pincho", "x": 4760},
            {"tipo": "pincho", "x": 4800},
            {"tipo": "sierra", "x": 4800, "y": 440},
            {"tipo": "pincho", "x": 4840},
            {"tipo": "pincho", "x": 4880},
            {"tipo": "pincho", "x": 4920},
            {"tipo": "sierra", "x": 4920, "y": 160},
            {"tipo": "pincho", "x": 4960},
            {"tipo": "pincho", "x": 5000},
            {"tipo": "sierra", "x": 5000, "y": 440},
            {"tipo": "pincho", "x": 5040},
            {"tipo": "sierra", "x": 5040, "y": 200},
            {"tipo": "pincho", "x": 5080},
            {"tipo": "pincho", "x": 5120},
            {"tipo": "pincho", "x": 5160},
            {"tipo": "portal_cube", "x": 5200},
            {"tipo": "bloque", "x": 5350, "altura": 1},
            {"tipo": "end", "x": 5450}
        ]
    }

def crear_nivel_4():
   
    return {
        "nombre": "TILL MADNESS",
        "numero": 99,
        "velocidad_inicial": "x1",
        "longitud": 9950,
        "objetos": [
            {"tipo": "bloque", "x": 1200, "altura": 1},
            {"tipo": "bloque", "x": 1350, "altura": 2},
            {"tipo": "pincho", "x": 1500},
            {"tipo": "bloque", "x": 1650, "altura": 1},
            {"tipo": "moneda", "x": 1650, "y": 470, "id": 1},
            {"tipo": "pincho", "x": 1800},
            {"tipo": "plataforma", "x": 1950, "y": 480, "ancho": 100},
            {"tipo": "bloque", "x": 2100, "altura": 1},
            {"tipo": "portal_gravedad", "x": 2200},
            {"tipo": "bloque_techo", "x": 2400, "altura": 1},
            {"tipo": "pincho_suelo", "x": 2550},
            {"tipo": "bloque_techo", "x": 2700, "altura": 2},
            {"tipo": "sierra", "x": 2900, "y": 300},
            {"tipo": "bloque_techo", "x": 3050, "altura": 1},
            {"tipo": "pincho_suelo", "x": 3200},
            {"tipo": "plataforma", "x": 3350, "y": 120, "ancho": 100},
            {"tipo": "sierra", "x": 3500, "y": 250},
            {"tipo": "bloque_techo", "x": 3650, "altura": 1},
            {"tipo": "portal_gravedad", "x": 3800},
            {"tipo": "portal_ship", "x": 4000},
            {"tipo": "pincho", "x": 4120},
            {"tipo": "pincho", "x": 4160},
            {"tipo": "sierra", "x": 4200, "y": 400},
            {"tipo": "plataforma", "x": 4250, "y": 300, "ancho": 120},
            {"tipo": "pincho", "x": 4320},
            {"tipo": "pincho", "x": 4360},
            {"tipo": "sierra", "x": 4400, "y": 150},
            {"tipo": "pincho", "x": 4480},
            {"tipo": "plataforma", "x": 4520, "y": 250, "ancho": 120},
            {"tipo": "sierra", "x": 4600, "y": 450},
            {"tipo": "pincho", "x": 4680},
            {"tipo": "pincho", "x": 4720},
            {"tipo": "sierra", "x": 4760, "y": 200},
            {"tipo": "moneda", "x": 4800, "y": 300},
            {"tipo": "sierra", "x": 4880, "y": 480},
            {"tipo": "sierra", "x": 4920, "y": 120},
            {"tipo": "pincho", "x": 5000},
            {"tipo": "sierra", "x": 5040, "y": 440},
            {"tipo": "pincho", "x": 5120},
            {"tipo": "sierra", "x": 5280, "y": 180},
            {"tipo": "sierra", "x": 5280, "y": 440},
            {"tipo": "pincho", "x": 5360},
            {"tipo": "pincho", "x": 5480},
            {"tipo": "plataforma", "x": 5550, "y": 240, "ancho": 120},
            {"tipo": "sierra", "x": 5640, "y": 140},
            {"tipo": "pincho", "x": 5720},
            {"tipo": "portal_cube", "x": 5800},
            {"tipo": "bloque", "x": 6000, "altura": 1},
            {"tipo": "portal_ship", "x": 6150},
            {"tipo": "plataforma", "x": 6300, "y": 350, "ancho": 100},
            {"tipo": "portal_gravedad", "x": 6450},
            {"tipo": "plataforma", "x": 6700, "y": 150, "ancho": 100},
            {"tipo": "sierra", "x": 6850, "y": 240},
            {"tipo": "plataforma", "x": 7000, "y": 120, "ancho": 100},
            {"tipo": "moneda", "x": 7050, "y": 200, "id": 3},
            {"tipo": "sierra", "x": 7160, "y": 280},
            {"tipo": "plataforma", "x": 7300, "y": 140, "ancho": 100},
            {"tipo": "sierra", "x": 7440, "y": 240},
            {"tipo": "plataforma", "x": 7600, "y": 160, "ancho": 100},
            {"tipo": "portal_gravedad", "x": 7750},
            {"tipo": "portal_cube", "x": 7800},
            {"tipo": "bloque", "x": 8000, "altura": 1},
            {"tipo": "pincho", "x": 8150},
            {"tipo": "bloque", "x": 8300, "altura": 2},
            {"tipo": "sierra", "x": 8450, "y": 450},
            {"tipo": "portal_gravedad", "x": 8550},
            {"tipo": "bloque_techo", "x": 8700, "altura": 1},
            {"tipo": "sierra", "x": 8800, "y": 250},
            {"tipo": "pincho_suelo", "x": 8900},
            {"tipo": "bloque_techo", "x": 9050, "altura": 2},
            {"tipo": "sierra", "x": 9150, "y": 350},
            {"tipo": "portal_gravedad", "x": 9250},
            {"tipo": "bloque", "x": 9350, "altura": 1},
            {"tipo": "end", "x": 9450}
        ]
    }

def crear_nivel_3():
       return {
        "nombre": "GRAVITY TIME",
        "numero": 3,
        "velocidad_inicial": "x1",
        "longitud": 6450,
        "objetos": [
            {"tipo": "bloque", "x": 1200, "altura": 1},
            {"tipo": "pincho", "x": 1350},
            {"tipo": "bloque", "x": 1500, "altura": 1},
            {"tipo": "moneda", "x": 1500, "y": 470, "id": 1},
            {"tipo": "portal_gravedad", "x": 1700},
            {"tipo": "bloque_techo", "x": 1900, "altura": 1},
            {"tipo": "bloque_techo", "x": 2100, "altura": 1},
            {"tipo": "pincho_suelo", "x": 2250},
            {"tipo": "plataforma", "x": 2360, "y": 120, "ancho": 100},
            {"tipo": "bloque_techo", "x": 2520, "altura": 1},
            {"tipo": "sierra", "x": 2720, "y": 200},
            {"tipo": "pincho_suelo", "x": 2840},
            {"tipo": "portal_gravedad", "x": 3000},
            {"tipo": "portal_ship", "x": 3200},
            {"tipo": "sierra", "x": 3320, "y": 520},
            {"tipo": "sierra", "x": 3360, "y": 480},
            {"tipo": "sierra", "x": 3400, "y": 440},
            {"tipo": "sierra", "x": 3440, "y": 400},
            {"tipo": "sierra", "x": 3480, "y": 360},
            {"tipo": "sierra", "x": 3520, "y": 360},
            {"tipo": "sierra", "x": 3560, "y": 360},
            {"tipo": "sierra", "x": 3600, "y": 360},
            {"tipo": "plataforma", "x": 3600, "y": 280, "ancho": 100},
            {"tipo": "sierra", "x": 3640, "y": 360},
            {"tipo": "sierra", "x": 3680, "y": 360},
            {"tipo": "sierra", "x": 3720, "y": 360},
            {"tipo": "sierra", "x": 3760, "y": 360},
            {"tipo": "sierra", "x": 3800, "y": 360},
            {"tipo": "sierra", "x": 3840, "y": 360},
            {"tipo": "moneda", "x": 3840, "y": 280},
            {"tipo": "sierra", "x": 3880, "y": 360},
            {"tipo": "sierra", "x": 3920, "y": 360},
            {"tipo": "sierra", "x": 3960, "y": 360},
            {"tipo": "sierra", "x": 4000, "y": 360},
            {"tipo": "plataforma", "x": 4000, "y": 280, "ancho": 100},
            {"tipo": "sierra", "x": 4040, "y": 360},
            {"tipo": "sierra", "x": 4080, "y": 360},
            {"tipo": "sierra", "x": 4120, "y": 360},
            {"tipo": "sierra", "x": 4160, "y": 360},
            {"tipo": "sierra", "x": 4200, "y": 360},
            {"tipo": "sierra", "x": 4240, "y": 360},
            {"tipo": "plataforma", "x": 4240, "y": 280, "ancho": 100},
            {"tipo": "sierra", "x": 4280, "y": 360},
            {"tipo": "sierra", "x": 4320, "y": 360},
            {"tipo": "sierra", "x": 4360, "y": 360},
            {"tipo": "sierra", "x": 4400, "y": 360},
            {"tipo": "sierra", "x": 4440, "y": 360},
            {"tipo": "plataforma", "x": 4440, "y": 320, "ancho": 100},
            {"tipo": "sierra", "x": 4480, "y": 360},
            {"tipo": "plataforma", "x": 4480, "y": 320, "ancho": 100},
            {"tipo": "portal_cube", "x": 4500},
            {"tipo": "bloque", "x": 4700, "altura": 1},
            {"tipo": "bloque", "x": 4900, "altura": 2},
            {"tipo": "portal_gravedad", "x": 5050},
            {"tipo": "bloque_techo", "x": 5200, "altura": 1},
            {"tipo": "pincho_suelo", "x": 5350},
            {"tipo": "bloque_techo", "x": 5500, "altura": 1},
            {"tipo": "moneda", "x": 5500, "y": 150, "id": 3},
            {"tipo": "portal_gravedad", "x": 5700},
            {"tipo": "bloque", "x": 5850, "altura": 1},
            {"tipo": "end", "x": 5950}
        ]
    }

# ==================== CLASE PRINCIPAL DEL JUEGO ====================
class Cubik:
    def __init__(self):
        # Inicializar sistema de sonidos primero
        inicializar_sonidos()
        
        self.ventana = Tk()
        self.ventana.title(" CUBIK" )
        self.ventana.resizable(False, False)
        
        self.canvas = Canvas(self.ventana, width=ANCHO_VENTANA, height=ALTO_VENTANA,
                            bg="#0a0e27", highlightthickness=0)
        self.canvas.pack()
        
        # Variables globales
        self.nivel_actual = 1
        self.niveles_desbloqueados = 4  # Todos los niveles desbloqueados
        self.en_menu = True
        self.nivel_data = None
        
        # Variables para efectos visuales
        self.particulas = []
        self.trail_cubo = []
        self.rotacion_cubo = 0
        self.frame_count = 0
        
        # Física mejorada
        self.tocando_techo = False
        self.ultimo_bloque_tocado = None
        self.tecla_presionada = False  # Para mantener presionado y saltar automáticamente
        
        # Variables del editor
        self.en_editor = False
        self.editor_objetos = []
        self.editor_objeto_seleccionado = None
        self.editor_scroll_x = 0
        self.editor_tipo_actual = "bloque"
        self.editor_altura_actual = 1
        self.editor_grid_size = 40
        self.probando_nivel_editor = False  # Nueva variable para rastrear modo prueba
        
        # Estadísticas y tiempo
        self.tiempo_inicio_nivel = 0
        self.mejor_tiempo = {1: float('inf'), 2: float('inf'), 3: float('inf')}
        self.total_intentos = {1: 0, 2: 0, 3: 0}
        self.estadisticas = {
            "tiempo_total": 0,
            "muertes_totales": 0,
            "niveles_completados": 0
        }
        
        # SISTEMA DE LOGROS
        self.logros = {
            "primera_muerte": False,
            "primera_victoria": False,
            "combo_10": False,
            "combo_25": False,
            "velocidad_maxima": False,
            "checkpoint_maestro": False,
            "perfeccionista": False,  # Nivel sin morir
            "speedrunner": False,  # Nivel en tiempo récord
            "coleccionista": False  # Todas las monedas
        }
        self.logros_pendientes_mostrar = []  # Cola de logros para mostrar
        
        # Efectos visuales
        self.shake_amount = 0
        self.flash_alpha = 0
        self.particulas_fondo = []
        
        # Efectos avanzados con pygame
        self.efecto_velocidad = []  # Líneas de velocidad
        self.efecto_glow_intensidad = 0  # Intensidad del brillo
        self.combo_count = 0  # Contador de combo (OBSTÁCULOS sorteados, no saltos)
        self.ultimo_porcentaje_muerte = 0
        self.obstaculos_sorteados = []  # Lista de obstáculos ya pasados (para combos)
        
        # Sistema de interpolación de física para 120 FPS
        self.posicion_anterior_y = 0
        self.interpolacion_t = 0
        self.jugador_y_visual = 0  # Posición interpolada para renderizado
        
        # Sistema de camera zoom cinemático
        self.camera_zoom = 1.0  # Escala actual (1.0 = normal)
        self.camera_zoom_target = 1.0  # Objetivo de zoom
        self.camera_zoom_speed = 0.1  # Velocidad de transición
        
        # Mostrar menú inicial
        self.mostrar_menu_seleccion()
        
        # Eventos
        self.ventana.bind("<space>", self.saltar)
        self.ventana.bind("<KeyPress-space>", self.tecla_abajo)
        self.ventana.bind("<KeyRelease-space>", self.tecla_arriba)
        self.ventana.bind("<Button-1>", self.mouse_abajo)
        self.ventana.bind("<ButtonRelease-1>", self.mouse_arriba)
        self.ventana.bind("<Escape>", lambda e: self.volver_menu())
        self.ventana.bind("<r>", lambda e: self.reiniciar_nivel())
        # Bindings para modo práctica - DESHABILITADO TEMPORALMENTE
        # TODO: Reactivar cuando se arreglen los bugs
        # self.ventana.bind("<q>", lambda e: self.colocar_checkpoint_manual())
        # self.ventana.bind("<e>", lambda e: self.eliminar_checkpoint_cercano())
        
        print("╔════════════════════════════════════╗")
        print("║     C U B I K                    ║")
        print("║  CUBIK                             ║")
        print("╠════════════════════════════════════╣")
        print("║  ESPACIO/Click : Saltar            ║")
        print("║ Creado Por Mariano Alejandro Orrego║")
        # print("║  Q             : Checkpoint (Prác.)║")  # DESHABILITADO
        # print("║  E             : Eliminar Checkpoint║")  # DESHABILITADO
        print("║  R             : Reiniciar         ║")
        print("║  ESC           : Menú              ║")
        print("╚════════════════════════════════════╝\n")
        
        self.ventana.mainloop()
    
    def mostrar_menu_seleccion(self):
        """Menú AAA ultra profesional con animaciones y efectos neon"""
        self.en_menu = True
        self.canvas.delete("all")
        
        # ========== FONDO ANIMADO MULTI-CAPA ==========
        # Capa 1: Gradiente oscuro base
        for i in range(0, ALTO_VENTANA, 10):
            intensidad = int(5 + (i / ALTO_VENTANA) * 15)
            color = f"#{intensidad:02x}{intensidad:02x}{min(intensidad + 5, 25):02x}"
            self.canvas.create_rectangle(0, i, ANCHO_VENTANA, i + 10,
                                         fill=color, outline="", tags="fondo_menu")
        
        # Capa 2: Grid cyberpunk con líneas
        for i in range(0, ANCHO_VENTANA, 80):
            self.canvas.create_line(i, 0, i, ALTO_VENTANA,
                                   fill="#00ff88", width=1, stipple="gray25", tags="fondo_menu")
        for i in range(0, ALTO_VENTANA, 80):
            self.canvas.create_line(0, i, ANCHO_VENTANA, i,
                                   fill="#00d9ff", width=1, stipple="gray25", tags="fondo_menu")
        
        # Capa 3: Partículas neon flotantes (más cantidad)
        for _ in range(60):
            x = random.randint(0, ANCHO_VENTANA)
            y = random.randint(0, ALTO_VENTANA)
            tamaño = random.randint(2, 8)
            color = random.choice(["#00ff88", "#00d9ff", "#ffea00", "#ff00ff", "#ff0088"])
            # Partícula con glow
            self.canvas.create_oval(x - tamaño*2, y - tamaño*2, x + tamaño*2, y + tamaño*2,
                                   fill=color, outline="", stipple="gray12", tags="fondo_menu")
            self.canvas.create_oval(x - tamaño, y - tamaño, x + tamaño, y + tamaño,
                                   fill=color, outline="", tags="fondo_menu")
        
        # ========== TÍTULO ÉPICO CON EFECTOS 3D ==========
        titulo = "C U B I K"
        
        # Sombra profunda 3D (múltiples capas)
        for offset in [(10, 10), (8, 8), (6, 6), (4, 4), (2, 2)]:
            alpha = int((6 - offset[0] / 2) * 20)
            shadow_color = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
            self.canvas.create_text(ANCHO_VENTANA // 2 + offset[0], 120 + offset[1],
                                   text=titulo, fill=shadow_color, 
                                   font=("Arial Black", 58, "bold"), tags="titulo")
        
        # Glow exterior brillante
        for offset_x in [-3, -2, -1, 0, 1, 2, 3]:
            for offset_y in [-3, -2, -1, 0, 1, 2, 3]:
                if offset_x == 0 and offset_y == 0:
                    continue
                self.canvas.create_text(ANCHO_VENTANA // 2 + offset_x, 120 + offset_y,
                                       text=titulo, fill="#00ff88", 
                                       font=("Arial Black", 58, "bold"), stipple="gray25", tags="titulo")
        
        # Texto principal brillante con gradiente simulado
        self.canvas.create_text(ANCHO_VENTANA // 2, 120,
                               text=titulo, fill="#00ffaa", 
                               font=("Arial Black", 58, "bold"), tags="titulo")
        
        # ========== TARJETAS DE NIVELES ULTRA MODERNAS ==========
        niveles = [crear_nivel_1(), crear_nivel_2(), crear_nivel_3(), crear_nivel_4()]
        card_w = 300
        total_width = 4 * card_w + 3 * 20  # 4 tarjetas + 3 espacios de 20px entre ellas
        x_start = (ANCHO_VENTANA - total_width) // 2 + card_w // 2  # Centrado perfecto
        spacing = card_w + 20  # Ancho de tarjeta + espacio
        
        for i, nivel in enumerate(niveles):
            x = x_start + i * spacing
            y = 380
            card_h = 340
            
            bloqueado = i + 1 > self.niveles_desbloqueados
            color_principal = COLORES[i+1]["player"] if not bloqueado else "#444444"
            
            # === SOMBRA ULTRA PROFUNDA ===
            for shadow_offset in range(15, 0, -2):
                alpha = int((15 - shadow_offset) * 5)
                shadow_col = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
                self.canvas.create_rectangle(
                    x - card_w//2 + shadow_offset, y - card_h//2 + shadow_offset,
                    x + card_w//2 + shadow_offset, y + card_h//2 + shadow_offset,
                    fill=shadow_col, outline="", tags="menu_card")
            
            # === FONDO DE TARJETA CON GRADIENTE ===
            for grad_i in range(0, card_h, 8):
                grad_intensity = int(15 + (grad_i / card_h) * 15)
                grad_color = f"#{grad_intensity:02x}{grad_intensity:02x}{grad_intensity+10:02x}"
                self.canvas.create_rectangle(
                    x - card_w//2, y - card_h//2 + grad_i,
                    x + card_w//2, y - card_h//2 + grad_i + 8,
                    fill=grad_color if not bloqueado else "#0a0a0f", outline="", tags="menu_card")
            
            # === BORDE NEON BRILLANTE ===
            if not bloqueado:
                # Glow exterior del borde
                for glow_w in range(8, 0, -1):
                    glow_alpha = int(glow_w * 10)
                    glow_color = self._hex_add_alpha(color_principal, glow_alpha)
                    self.canvas.create_rectangle(
                        x - card_w//2 - glow_w, y - card_h//2 - glow_w,
                        x + card_w//2 + glow_w, y + card_h//2 + glow_w,
                        fill="", outline=glow_color, width=2, tags="menu_card")
            
            # Borde principal
            self.canvas.create_rectangle(
                x - card_w//2, y - card_h//2,
                x + card_w//2, y + card_h//2,
                fill="", outline=color_principal, width=4, tags="menu_card")
            
            # === DECORACIONES INTERNAS ===
            # Esquinas decorativas
            corner_size = 20
            for cx, cy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                corner_x = x + cx * (card_w//2 - corner_size)
                corner_y = y + cy * (card_h//2 - corner_size)
                self.canvas.create_line(
                    corner_x, corner_y - cy * corner_size,
                    corner_x, corner_y,
                    corner_x + cx * corner_size, corner_y,
                    fill=color_principal, width=3, tags="menu_card")
            
            # === NÚMERO DEL NIVEL GIGANTE ===
            # Sombra del número
            self.canvas.create_text(x + 4, y - 90 + 4,
                                   text=str(i + 1),
                                   fill="#000000", font=("Impact", 90, "bold"), tags="menu_card")
            # Número con glow
            self.canvas.create_text(x, y - 90,
                                   text=str(i + 1),
                                   fill=color_principal, font=("Impact", 90, "bold"), tags="menu_card")
            
            # === NOMBRE DEL NIVEL ===
            self.canvas.create_text(x, y - 10,
                                   text=nivel["nombre"].upper(),
                                   fill="#ffffff" if not bloqueado else "#666666",
                                   font=("Arial Black", 20, "bold"), tags="menu_card")
            
            # === LÍNEA SEPARADORA ===
            self.canvas.create_line(x - 120, y + 15, x + 120, y + 15,
                                   fill=color_principal, width=2, tags="menu_card")
            
            # === ESTADÍSTICAS DEL NIVEL ===
            monedas = sum(1 for obj in nivel["objetos"] if obj["tipo"] == "moneda")
            
            # Longitud
            self.canvas.create_text(x, y + 35,
                                   text=f"{nivel['longitud']}px",
                                   fill="#aaaaaa" if not bloqueado else "#555555",
                                   font=("Arial", 12), tags="menu_card")
            
            # Dificultad con estrellas
            estrellas = "*" * (i + 1) + "o" * (3 - i - 1)
            self.canvas.create_text(x, y + 55,
                                   text=estrellas,
                                   fill="#ffea00" if not bloqueado else "#666666",
                                   font=("Arial", 16), tags="menu_card")
            
            # Monedas
            self.canvas.create_text(x, y + 80,
                                   text=f"{monedas} COINS",
                                   fill="#00ffff" if not bloqueado else "#666666",
                                   font=("Arial", 13, "bold"), tags="menu_card")
            
            # === BOTÓN O CANDADO ===
            if bloqueado:
                # Candado grande
                self.canvas.create_text(x, y + 125,
                                       text="LOCKED",
                                       fill="#666666", font=("Arial", 40), tags="menu_card")
                self.canvas.create_text(x, y + 155,
                                       text="LOCKED",
                                       fill="#666666", font=("Arial", 14, "bold"), tags="menu_card")
            else:
                # Botón ultra moderno con animación
                btn_y = y + 130
                
                # Sombra del botón
                self.canvas.create_rectangle(x - 110, btn_y - 22, x + 110, btn_y + 22,
                                            fill="#000000", outline="", tags="menu_card")
                
                # Glow del botón
                self.canvas.create_rectangle(x - 105, btn_y - 20, x + 105, btn_y + 20,
                                            fill=color_principal, outline="",
                                            stipple="gray25", tags="menu_card")
                
                # Botón principal
                boton = self.canvas.create_rectangle(x - 100, btn_y - 18, x + 100, btn_y + 18,
                                                     fill=color_principal, 
                                                     outline="#ffffff", width=3,
                                                     tags=f"nivel_{i+1}")
                
                # Texto del botón con sombra
                self.canvas.create_text(x + 2, btn_y + 2,
                                       text="▶ PLAY",
                                       fill="#000000", 
                                       font=("Arial Black", 14, "bold"),
                                       tags=f"nivel_{i+1}")
                texto = self.canvas.create_text(x, btn_y,
                                               text="▶ PLAY",
                                               fill="#ffffff", 
                                               font=("Arial Black", 14, "bold"),
                                               tags=f"nivel_{i+1}")
                
                self.canvas.tag_bind(f"nivel_{i+1}", "<Button-1>",
                                    lambda e, n=i+1: self.iniciar_nivel(n, False) if n <= self.niveles_desbloqueados else None)
        
        # ========== PANEL DE CONTROLES MODERNOS ==========
        panel_y = ALTO_VENTANA - 110
        panel_h = 90
        
        # Sombra del panel
        self.canvas.create_rectangle(280, panel_y + 5, ANCHO_VENTANA - 280, ALTO_VENTANA - 15,
                                     fill="#000000", outline="", tags="menu_footer")
        
        # Panel con gradiente
        for grad_i in range(0, panel_h, 5):
            grad_val = int(20 + (grad_i / panel_h) * 10)
            self.canvas.create_rectangle(
                280, panel_y + grad_i, ANCHO_VENTANA - 280, panel_y + grad_i + 5,
                fill=f"#{grad_val:02x}{grad_val:02x}{grad_val+10:02x}", outline="", tags="menu_footer")
        
        # Borde neon del panel
        self.canvas.create_rectangle(280, panel_y, ANCHO_VENTANA - 280, ALTO_VENTANA - 20,
                                     fill="", outline="#00ff88", width=4, tags="menu_footer")
        
        # Título del panel
        self.canvas.create_text(ANCHO_VENTANA // 2, panel_y + 20,
                               text="⌨  CONTROLS  ⌨",
                               fill="#00ff88", font=("Arial Black", 14, "bold"), tags="menu_footer")
        
        # Controles con iconos
        self.canvas.create_text(ANCHO_VENTANA // 2, panel_y + 50,
                               text="[ SPACE / LEFT CLICK ]  Jump  •  [ ESC ]  Menu  •  [ R ]  Restart",
                               fill="#ffffff", font=("Arial", 13), tags="menu_footer")
        
        # ========== BOTÓN EDITOR ULTRA MODERNO ==========
        editor_x, editor_y = 130, ALTO_VENTANA - 115
        editor_w, editor_h = 210, 55
        
        # Sombra profunda del botón
        for shadow in range(8, 0, -1):
            alpha = shadow * 8
            self.canvas.create_rectangle(
                editor_x - editor_w//2 + shadow, editor_y - editor_h//2 + shadow,
                editor_x + editor_w//2 + shadow, editor_y + editor_h//2 + shadow,
                fill=f"#{alpha:02x}{alpha:02x}{alpha:02x}", outline="", tags="editor_btn")
        
        # Glow naranja
        self.canvas.create_rectangle(
            editor_x - editor_w//2 - 3, editor_y - editor_h//2 - 3,
            editor_x + editor_w//2 + 3, editor_y + editor_h//2 + 3,
            fill="#ffaa00", outline="", stipple="gray25", tags="editor_btn")
        
        # Botón principal
        editor_btn_rect = self.canvas.create_rectangle(
            editor_x - editor_w//2, editor_y - editor_h//2,
            editor_x + editor_w//2, editor_y + editor_h//2,
            fill="#2a2a4a", outline="#ffaa00", width=4, tags="editor_btn"
        )
        
        # Texto del botón
        self.canvas.create_text(editor_x + 2, editor_y + 2,
                               text="LEVEL EDITOR",
                               fill="#000000", font=("Arial Black", 13, "bold"), tags="editor_btn")
        self.canvas.create_text(editor_x, editor_y,
                               text="LEVEL EDITOR",
                               fill="#ffaa00", font=("Arial Black", 13, "bold"), tags="editor_btn")
        
        self.canvas.tag_bind("editor_btn", "<Button-1>", lambda e: self.abrir_editor())
        self.canvas.tag_bind("editor_btn", "<Enter>", lambda e: self.canvas.itemconfig(editor_btn_rect, fill="#3a3a6a"))
        self.canvas.tag_bind("editor_btn", "<Leave>", lambda e: self.canvas.itemconfig(editor_btn_rect, fill="#2a2a4a"))
        
        # ========== BOTÓN EDITAR NIVELES PRINCIPALES ==========
        edit_x, edit_y = 370, ALTO_VENTANA - 115
        edit_w, edit_h = 210, 55
        
        # Sombra
        for shadow in range(8, 0, -1):
            alpha = shadow * 8
            self.canvas.create_rectangle(
                edit_x - edit_w//2 + shadow, edit_y - edit_h//2 + shadow,
                edit_x + edit_w//2 + shadow, edit_y + edit_h//2 + shadow,
                fill=f"#{alpha:02x}{alpha:02x}{alpha:02x}", outline="", tags="edit_main_btn")
        
        # Glow cyan
        self.canvas.create_rectangle(
            edit_x - edit_w//2 - 3, edit_y - edit_h//2 - 3,
            edit_x + edit_w//2 + 3, edit_y + edit_h//2 + 3,
            fill="#00d9ff", outline="", stipple="gray25", tags="edit_main_btn")
        
        # Botón
        edit_main_btn_rect = self.canvas.create_rectangle(
            edit_x - edit_w//2, edit_y - edit_h//2,
            edit_x + edit_w//2, edit_y + edit_h//2,
            fill="#2a2a4a", outline="#00d9ff", width=4, tags="edit_main_btn"
        )
        
        # Texto
        self.canvas.create_text(edit_x + 2, edit_y + 2,
                               text="EDIT LEVELS",
                               fill="#000000", font=("Arial Black", 13, "bold"), tags="edit_main_btn")
        self.canvas.create_text(edit_x, edit_y,
                               text="EDIT LEVELS",
                               fill="#00d9ff", font=("Arial Black", 13, "bold"), tags="edit_main_btn")
        
        self.canvas.tag_bind("edit_main_btn", "<Button-1>", lambda e: self.menu_editar_niveles())
        self.canvas.tag_bind("edit_main_btn", "<Enter>", lambda e: self.canvas.itemconfig(edit_main_btn_rect, fill="#3a3a6a"))
        self.canvas.tag_bind("edit_main_btn", "<Leave>", lambda e: self.canvas.itemconfig(edit_main_btn_rect, fill="#2a2a4a"))
        
        # Créditos con estilo
        self.canvas.create_text(ANCHO_VENTANA - 15, ALTO_VENTANA - 10,
                               text="Python 3.11 + Pygame + Tkinter",
                               fill="#666666", font=("Arial", 9), anchor="se", tags="menu_footer")
        
        # Iniciar animación del menú
        if ANIMACIONES_MENU:
            self.animar_menu()
    
    def _hex_add_alpha(self, hex_color, alpha):
        """Función auxiliar para agregar alpha a color hex (simula transparencia)"""
        # Extrae RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        # Reduce intensidad según alpha (0-255)
        factor = alpha / 255
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def animar_menu(self):
        """Anima partículas del menú de fondo"""
        if not self.en_menu:
            return
        
        # Mover partículas ligeramente
        for obj in self.canvas.find_withtag("fondo_menu"):
            coords = self.canvas.coords(obj)
            if len(coords) == 4:  # Es un oval
                # Movimiento suave aleatorio
                dx = random.uniform(-0.5, 0.5)
                dy = random.uniform(-0.5, 0.5)
                self.canvas.move(obj, dx, dy)
                
                # Mantener dentro de límites
                if coords[0] < -20 or coords[0] > ANCHO_VENTANA + 20:
                    self.canvas.move(obj, -coords[0] + ANCHO_VENTANA // 2, 0)
                if coords[1] < -20 or coords[1] > ALTO_VENTANA + 20:
                    self.canvas.move(obj, 0, -coords[1] + ALTO_VENTANA // 2)
        
        # Continuar animación
        self.ventana.after(50, self.animar_menu)
    
    # Función mostrar_menu_modo eliminada - El juego ahora inicia directamente en modo normal
    
    def iniciar_nivel(self, numero_nivel, modo_practica=False):
        """Inicia un nivel específico con el modo seleccionado"""
        self.en_menu = False
        self.nivel_actual = numero_nivel
        self.modo_practica = modo_practica
        
        # Cargar datos del nivel (solo si no es nivel personalizado)
        if numero_nivel != 99:  # 99 es el nivel personalizado del editor
            if numero_nivel == 1:
                self.nivel_data = crear_nivel_1()
            elif numero_nivel == 2:
                self.nivel_data = crear_nivel_2()
            elif numero_nivel == 3:
                self.nivel_data = crear_nivel_3()
            else:
                self.nivel_data = crear_nivel_4()
        # Si es 99, self.nivel_data ya fue establecido por probar_nivel_editor()
        
        # Inicializar variables del juego
        # Usar colores del nivel si existe, sino colores por defecto
        if numero_nivel in COLORES:
            self.colores = COLORES[numero_nivel]
        else:
            self.colores = COLORES[1]  # Colores por defecto del nivel 1
        
        self.jugador_y = SUELO_Y - TAMANO_JUGADOR
        self.velocidad_y = 0
        self.en_suelo = True
        self.rotacion_cubo = 0  # Ángulo de rotación del cubo
        self.ultimo_en_suelo = True  # Para detectar aterrizajes
        self.velocidad_juego = VELOCIDADES[self.nivel_data["velocidad_inicial"]]
        self.offset_camara = -RUNWAY_DISTANCE  # Empezar antes para runway
        self.juego_activo = True
        self.gravedad_invertida = False
        self.intentos = 0
        self.porcentaje = 0
        self.monedas_recolectadas = []
        self.objetos_interactuados = []
        self.tiempo_inicio_nivel = time.time()  # Cronómetro
        
        # Variables de efectos visuales
        self.particulas = []
        self.trail_cubo = []
        self.frame_count = 0
        self.coyote_time = 0
        self.tocando_techo = False
        self.ultimo_bloque_tocado = None
        self.rotacion_cubo = 0
        self.frame_count = 0
        self.pulso_fondo = 0
        
        # Resetear zoom cinemático al iniciar nivel
        self.camera_zoom = 1.0
        self.camera_zoom_target = 1.0
        self.ultimo_zoom = 1.0
        
        # Sistema de modos de juego
        self.modo_actual = "cube"
        self.modo_config = MODOS_JUEGO["cube"].copy()
        self.velocidad_wave = 0  # Para el modo wave
        
        # Sistema de checkpoints (mantener modo si ya se configuró)
        self.checkpoints = []
        self.checkpoint_actual = None
        self.checkpoint_ids = []
        self.ultimo_checkpoint_auto = 0  # Para checkpoints automáticos
        self.distancia_checkpoint_auto = 800  # Cada 800px en modo práctica
        
        # Crear nivel
        self.crear_nivel_visual()
        self.crear_jugador()
        self.crear_hud()
        
        # Reproducir música de fondo del nivel
        self.iniciar_musica_nivel(numero_nivel)
        
        # Registrar checkpoints predeterminados del nivel en modo práctica
        if self.modo_practica:
            for obj in self.nivel_data["objetos"]:
                if obj["tipo"] == "checkpoint":
                    if obj["x"] not in self.checkpoints:
                        self.checkpoints.append(obj["x"])
            self.checkpoints.sort()
        
        print(f"\nIniciando {self.nivel_data['nombre']}...")
        print(f"Longitud: {self.nivel_data['longitud']}px")
        print(f"Velocidad inicial: {self.nivel_data['velocidad_inicial']}")
        print()
        
        # Iniciar loop del juego
        self.actualizar()
    
    def crear_nivel_visual(self):
        """Crea todos los elementos visuales del nivel"""
        self.canvas.delete("all")
        
        # Fondo con gradiente
        num_lineas = 40
        for i in range(num_lineas):
            y = (SUELO_Y / num_lineas) * i
            factor = i / num_lineas
            # Interpolación entre bg1 y bg2
            self.canvas.create_line(0, y, ANCHO_VENTANA, y,
                                   fill=self.colores["bg1"], width=SUELO_Y//num_lineas + 2,
                                   tags="fondo")
        
        # Estrellas
        for _ in range(60):
            x = random.randint(0, ANCHO_VENTANA)
            y = random.randint(0, SUELO_Y - 50)
            size = random.randint(1, 3)
            self.canvas.create_oval(x, y, x+size, y+size,
                                   fill="#ffffff", outline="", tags="fondo")
        
        # Suelo (INMÓVIL - sin tag fondo para evitar que se mueva con parallax)
        self.canvas.create_rectangle(0, SUELO_Y, ANCHO_VENTANA, ALTO_VENTANA,
                                     fill=self.colores["suelo"], outline="", tags="suelo_fijo")
        
        # Línea del suelo (INMÓVIL)
        self.canvas.create_line(0, SUELO_Y, ANCHO_VENTANA, SUELO_Y,
                               fill=self.colores["plataforma"], width=4, tags="suelo_fijo")
        
        # Línea límite superior MORTAL (debajo del HUD) - INMÓVIL
        self.canvas.create_line(0, LIMITE_SUPERIOR, ANCHO_VENTANA, LIMITE_SUPERIOR,
                               fill="#ff0000", width=3, tags="techo_fijo")  # Rojo para indicar peligro
        # Efecto glow en límite superior (INMÓVIL)
        self.canvas.create_line(0, LIMITE_SUPERIOR - 2, ANCHO_VENTANA, LIMITE_SUPERIOR - 2,
                               fill="#ff6600", width=1, stipple="gray50", tags="techo_fijo")
        self.canvas.create_line(0, LIMITE_SUPERIOR + 2, ANCHO_VENTANA, LIMITE_SUPERIOR + 2,
                               fill="#ff6600", width=1, stipple="gray50", tags="techo_fijo")
        
        # Crear objetos del nivel
        self.objetos_nivel = []
        for obj_data in self.nivel_data["objetos"]:
            obj = self.crear_objeto(obj_data)
            if obj:
                self.objetos_nivel.append({"data": obj_data, "visual": obj})
    
    def crear_objeto(self, obj_data):
        """Crea un objeto del nivel"""
        tipo = obj_data["tipo"]
        x = obj_data["x"]
        ids = []
        
        if tipo == "bloque":
            # Bloque sólido con estilo CUBIK - un solo rectángulo grande según la altura
            altura = obj_data.get("altura", 1)
            altura_total = altura * TAMANO_BLOQUE
            y = SUELO_Y - altura_total
            
            # Sombra profunda
            sombra = self.canvas.create_rectangle(
                x + 4, y + 4, x + TAMANO_BLOQUE + 4, SUELO_Y + 4,
                fill="#000000", outline="", stipple="gray50", tags="nivel")
            
            # GLOW izquierdo magenta
            self.canvas.create_rectangle(
                x - 2, y, x, SUELO_Y,
                fill="#ff00ff", outline="", tags="nivel")
            
            # Bloque grande con color base
            bloque = self.canvas.create_rectangle(
                x, y, x + TAMANO_BLOQUE, SUELO_Y,
                fill=self.colores["plataforma"], outline="", tags="nivel")
            
            # Borde brillante cyan
            borde_exterior = self.canvas.create_rectangle(
                x, y, x + TAMANO_BLOQUE, SUELO_Y,
                fill="", outline="#00ffff", width=3, tags="nivel")
            
            ids.append(borde_exterior)
            
            # Líneas divisorias horizontales brillantes para mostrar los "bloques" apilados
            for i in range(1, altura):
                y_linea = SUELO_Y - (i * TAMANO_BLOQUE)
                linea = self.canvas.create_line(
                    x, y_linea, x + TAMANO_BLOQUE, y_linea,
                    fill="#ffffff", width=2, tags="nivel")
                ids.append(linea)
            
            return [sombra, bloque] + ids
        
        elif tipo == "pincho":
            # Pincho triangular en el suelo con efecto neon
            y_base = SUELO_Y
            altura = 40
            ancho = 30
            # Sombra
            sombra = self.canvas.create_polygon(
                x + 3, y_base + 3,
                x + ancho + 3, y_base + 3,
                x + ancho/2 + 3, y_base - altura + 3,
                fill="#000000", outline="", stipple="gray50", tags="nivel")
            
            # GLOW EXTERIOR ROJO (efecto neon peligroso)
            for offset in [3, 2, 1]:
                self.canvas.create_polygon(
                    x - offset, y_base + offset,
                    x + ancho + offset, y_base + offset,
                    x + ancho/2, y_base - altura - offset,
                    fill="", outline="#ff0000", width=1, tags="nivel")
            
            # Pincho visual (más grande) con color brillante
            pincho = self.canvas.create_polygon(
                x, y_base,
                x + ancho, y_base,
                x + ancho/2, y_base - altura,
                fill=self.colores["obstaculo"], outline="#ffffff", width=2, tags="nivel")
            
            # Hitbox MUCHO más reducido - solo la punta superior del pincho
            hitbox = self.canvas.create_polygon(
                x + 10, y_base - 8,
                x + ancho - 10, y_base - 8,
                x + ancho/2, y_base - altura + 12,
                fill="", outline="", tags="nivel")
            return [sombra, pincho, hitbox]
        
        elif tipo == "pincho_techo":
            # Pincho en el techo de una plataforma
            altura_base = obj_data.get("altura_base", 1)
            y_base = SUELO_Y - altura_base * TAMANO_BLOQUE
            altura = 40
            ancho = 30
            # Pincho visual invertido
            pincho = self.canvas.create_polygon(
                x, y_base,
                x + ancho, y_base,
                x + ancho/2, y_base - altura,
                fill=self.colores["obstaculo"], outline="#ffffff", width=2, tags="nivel")
            # Hitbox MUCHO más reducido
            hitbox = self.canvas.create_polygon(
                x + 10, y_base - 8,
                x + ancho - 10, y_base - 8,
                x + ancho/2, y_base - altura + 12,
                fill="", outline="", tags="nivel")
            return [pincho, hitbox]
        
        elif tipo == "pincho_suelo":
            # Pincho en el techo (para gravedad invertida)
            # Apunta hacia abajo desde el LIMITE_SUPERIOR
            y_base = LIMITE_SUPERIOR
            altura = 40
            ancho = 30
            # Pincho visual
            pincho = self.canvas.create_polygon(
                x, y_base,
                x + ancho, y_base,
                x + ancho/2, y_base + altura,
                fill=self.colores["obstaculo"], outline="#ffffff", width=2, tags="nivel")
            # Hitbox MUCHO más reducido
            hitbox = self.canvas.create_polygon(
                x + 10, y_base + 8,
                x + ancho - 10, y_base + 8,
                x + ancho/2, y_base + altura - 12,
                fill="", outline="", tags="nivel")
            return [pincho, hitbox]
        
        elif tipo == "plataforma":
            # Plataforma flotante con estilo CUBIK neon
            y = obj_data.get("y", SUELO_Y - 120)
            ancho = obj_data.get("ancho", 100)
            
            # Sombra profunda
            sombra = self.canvas.create_rectangle(
                x + 3, y + 3, x + ancho + 3, y + 23,
                fill="#000000", outline="", stipple="gray50", tags="nivel")
            
            # GLOW inferior cyan
            self.canvas.create_rectangle(
                x - 1, y + 21, x + ancho + 1, y + 24,
                fill="#00ffff", outline="", tags="nivel")
            
            # Plataforma base
            plat = self.canvas.create_rectangle(
                x, y, x + ancho, y + 20,
                fill=self.colores["plataforma"], outline="", tags="nivel")
            
            # Borde superior brillante
            borde = self.canvas.create_rectangle(
                x, y, x + ancho, y + 20,
                fill="", outline="#00ffff", width=3, tags="nivel")
            
            return [sombra, plat, borde]
        
        elif tipo == "moneda":
            # Moneda coleccionable con efecto neon dorado
            y = obj_data.get("y", SUELO_Y - 60)
            radio = 15
            
            # GLOW EXTERIOR DORADO (efecto brillante)
            for offset in [4, 3, 2]:
                self.canvas.create_oval(
                    x - radio - offset, y - radio - offset, 
                    x + radio + offset, y + radio + offset,
                    fill="", outline="#ffaa00", width=1, tags="nivel")
            
            # Círculo exterior con borde grueso
            circulo1 = self.canvas.create_oval(
                x - radio, y - radio, x + radio, y + radio,
                fill=self.colores["moneda"], outline="#ffaa00", width=4, tags="nivel")
            
            # Círculo interior brillante
            circulo2 = self.canvas.create_oval(
                x - radio + 5, y - radio + 5, x + radio - 5, y + radio - 5,
                fill="#fff5cc", outline="", tags="nivel")
            
            # Punto central ultra brillante
            circulo3 = self.canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill="#ffffff", outline="", tags="nivel")
            
            return [circulo1, circulo2, circulo3]
        
        elif tipo == "sierra":
            # Sierra circular rotatoria con efecto neon peligroso
            y = obj_data.get("y", SUELO_Y - 60)
            radio = 25
            
            # GLOW EXTERIOR ROJO (efecto neon mortal)
            for offset in [4, 3, 2]:
                self.canvas.create_oval(
                    x - radio - offset, y - radio - offset, 
                    x + radio + offset, y + radio + offset,
                    fill="", outline="#ff0000", width=1, tags="nivel")
            
            # Círculo base con color intenso
            circulo = self.canvas.create_oval(
                x - radio, y - radio, x + radio, y + radio,
                fill=self.colores["obstaculo"], outline="#ffffff", width=3, tags="nivel")
            
            # Líneas de sierra brillantes
            linea1 = self.canvas.create_line(
                x - radio, y, x + radio, y,
                fill="#ffffff", width=3, tags="nivel")
            linea2 = self.canvas.create_line(
                x, y - radio, x, y + radio,
                fill="#ffffff", width=3, tags="nivel")
            
            # Líneas diagonales adicionales para efecto de sierra
            linea3 = self.canvas.create_line(
                x - radio*0.7, y - radio*0.7, x + radio*0.7, y + radio*0.7,
                fill="#ffcccc", width=2, tags="nivel")
            linea4 = self.canvas.create_line(
                x - radio*0.7, y + radio*0.7, x + radio*0.7, y - radio*0.7,
                fill="#ffcccc", width=2, tags="nivel")
            
            return [circulo, linea1, linea2, linea3, linea4]
        
        elif tipo == "orbe_amarillo":
            # Orbe amarillo (salto extra al tocar)
            y = obj_data.get("y", SUELO_Y - 100)
            radio = 18
            circulo = self.canvas.create_oval(
                x - radio, y - radio, x + radio, y + radio,
                fill="#ffea00", outline="#ffffff", width=3, tags="nivel")
            return [circulo]
        
        elif tipo == "orbe_rosa":
            # Orbe rosa (salto grande al tocar)
            y = obj_data.get("y", SUELO_Y - 100)
            radio = 20
            circulo = self.canvas.create_oval(
                x - radio, y - radio, x + radio, y + radio,
                fill="#ff1493", outline="#ffffff", width=3, tags="nivel")
            return [circulo]
        
        elif tipo == "portal_velocidad":
            # Portal que cambia la velocidad
            velocidad = obj_data.get("velocidad", "x1")
            # Marco del portal
            marco = self.canvas.create_rectangle(
                x, SUELO_Y - 100, x + 60, SUELO_Y,
                fill="", outline=self.colores["plataforma"], width=4, tags="nivel")
            # Texto de velocidad
            texto = self.canvas.create_text(
                x + 30, SUELO_Y - 50,
                text=velocidad,
                fill=self.colores["plataforma"], font=("Arial", 16, "bold"), tags="nivel")
            return [marco, texto]
        
        elif tipo == "portal_gravedad":
            # Portal de gravedad invertida - Hitbox COMPLETA en todo el eje Y
            marco = self.canvas.create_rectangle(
                x, LIMITE_SUPERIOR, x + 60, SUELO_Y,
                fill="", outline="#ff00ff", width=4, tags="nivel")
            # Flechas arriba/abajo en el centro
            flecha = self.canvas.create_text(
                x + 30, (LIMITE_SUPERIOR + SUELO_Y) // 2,
                text="⇅",
                fill="#ff00ff", font=("Arial", 32, "bold"), tags="nivel")
            return [marco, flecha]
        
        elif tipo == "portal_ship":
            # Portal modo Ship - Hitbox COMPLETA en todo el eje Y
            marco = self.canvas.create_rectangle(
                x, LIMITE_SUPERIOR, x + 60, SUELO_Y,
                fill="", outline="#00d9ff", width=4, tags="nivel")
            icono = self.canvas.create_polygon(
                x + 45, (LIMITE_SUPERIOR + SUELO_Y) // 2,
                x + 15, (LIMITE_SUPERIOR + SUELO_Y) // 2 - 15,
                x + 15, (LIMITE_SUPERIOR + SUELO_Y) // 2 + 15,
                fill="#00d9ff", outline="", tags="nivel")
            return [marco, icono]
        
        elif tipo == "portal_cube":
            # Portal modo Cube - Hitbox COMPLETA en todo el eje Y
            marco = self.canvas.create_rectangle(
                x, LIMITE_SUPERIOR, x + 60, SUELO_Y,
                fill="", outline="#00ff88", width=4, tags="nivel")
            icono = self.canvas.create_rectangle(
                x + 20, (LIMITE_SUPERIOR + SUELO_Y) // 2 - 10,
                x + 40, (LIMITE_SUPERIOR + SUELO_Y) // 2 + 10,
                fill="#00ff88", outline="", tags="nivel")
            return [marco, icono]
        
        elif tipo == "portal_ball":
            # Portal modo Ball
            marco = self.canvas.create_rectangle(
                x, SUELO_Y - 120, x + 60, SUELO_Y,
                fill="", outline="#ff00ff", width=4, tags="nivel")
            icono = self.canvas.create_oval(
                x + 15, SUELO_Y - 80, x + 45, SUELO_Y - 50,
                fill="#ff00ff", outline="", tags="nivel")
            return [marco, icono]
        
        elif tipo == "portal_ufo":
            # Portal modo UFO
            marco = self.canvas.create_rectangle(
                x, SUELO_Y - 120, x + 60, SUELO_Y,
                fill="", outline="#ffff00", width=4, tags="nivel")
            icono = self.canvas.create_oval(
                x + 15, SUELO_Y - 75, x + 45, SUELO_Y - 55,
                fill="#ffff00", outline="", tags="nivel")
            return [marco, icono]
        
        elif tipo == "portal_wave":
            # Portal modo Wave
            marco = self.canvas.create_rectangle(
                x, SUELO_Y - 120, x + 60, SUELO_Y,
                fill="", outline="#00ffff", width=4, tags="nivel")
            icono = self.canvas.create_polygon(
                x + 30, SUELO_Y - 75,
                x + 45, SUELO_Y - 65,
                x + 30, SUELO_Y - 55,
                x + 15, SUELO_Y - 65,
                fill="#00ffff", outline="", tags="nivel")
            return [marco, icono]
        
        elif tipo == "portal_robot":
            # Portal modo Robot
            marco = self.canvas.create_rectangle(
                x, SUELO_Y - 120, x + 60, SUELO_Y,
                fill="", outline="#ff6600", width=4, tags="nivel")
            icono = self.canvas.create_rectangle(
                x + 20, SUELO_Y - 70, x + 40, SUELO_Y - 55,
                fill="#ff6600", outline="", tags="nivel")
            cabeza = self.canvas.create_rectangle(
                x + 23, SUELO_Y - 78, x + 37, SUELO_Y - 68,
                fill="#ff6600", outline="", tags="nivel")
            return [marco, icono, cabeza]
        
        elif tipo == "checkpoint":
            # Checkpoint - punto de guardado (SOLO VISIBLE EN MODO PRÁCTICA)
            if not self.modo_practica:
                # En modo normal, no mostrar checkpoints
                return []
            
            # Poste
            poste = self.canvas.create_rectangle(
                x + 25, SUELO_Y - 80, x + 35, SUELO_Y,
                fill="#888888", outline="#ffffff", width=2, tags="nivel")
            # Bandera
            bandera = self.canvas.create_polygon(
                x + 35, SUELO_Y - 75,
                x + 65, SUELO_Y - 60,
                x + 35, SUELO_Y - 45,
                fill="#00ff88", outline="#ffffff", width=2, tags="nivel")
            # Texto
            texto = self.canvas.create_text(
                x + 30, SUELO_Y - 90,
                text="OK",
                fill="#00ff88", font=("Arial", 20, "bold"), tags="nivel")
            self.checkpoint_ids.extend([poste, bandera, texto])
            return [poste, bandera, texto]
        
        elif tipo == "bloque_techo":
            # Bloque que cuelga del techo (para gravedad invertida)
            # Comienza desde LIMITE_SUPERIOR hacia abajo
            altura = obj_data.get("altura", 1)
            altura_total = altura * TAMANO_BLOQUE
            y = LIMITE_SUPERIOR
            
            ids = []
            
            # Sombra del bloque completo
            sombra = self.canvas.create_rectangle(
                x + 4, y + 4, x + TAMANO_BLOQUE + 4, y + altura_total + 4,
                fill="#000000", outline="", stipple="gray50", tags="nivel")
            ids.append(sombra)
            
            # Bloque sólido completo (UN SOLO RECTÁNGULO como los bloques normales)
            bloque = self.canvas.create_rectangle(
                x, y, x + TAMANO_BLOQUE, y + altura_total,
                fill=self.colores["plataforma"], outline="", tags="nivel")
            ids.append(bloque)
            
            # Degradado interior
            bloque_degradado = self.canvas.create_rectangle(
                x, y, x + TAMANO_BLOQUE, y + altura_total,
                fill=self.colores["player"], outline="", stipple="gray25", tags="nivel")
            ids.append(bloque_degradado)
            
            # Borde brillante cyan
            borde_exterior = self.canvas.create_rectangle(
                x, y, x + TAMANO_BLOQUE, y + altura_total,
                fill="", outline="#00ffff", width=3, tags="nivel")
            ids.append(borde_exterior)
            
            # Líneas divisorias horizontales para mostrar los "bloques" apilados
            for i in range(1, altura):
                y_linea = LIMITE_SUPERIOR + (i * TAMANO_BLOQUE)
                linea = self.canvas.create_line(
                    x, y_linea, x + TAMANO_BLOQUE, y_linea,
                    fill="#ffffff", width=2, tags="nivel")
                ids.append(linea)
            
            return [sombra, bloque] + ids
        
        elif tipo == "end":
            # Fin del nivel
            rect = self.canvas.create_rectangle(
                x, SUELO_Y - 200, x + 100, SUELO_Y,
                fill="#00ff88", outline="#ffffff", width=4, tags="nivel")
            texto = self.canvas.create_text(
                x + 50, SUELO_Y - 100,
                text="FIN",
                fill="#000000", font=("Arial", 24, "bold"), tags="nivel")
            return [rect, texto]
        
        return None
    
    def crear_jugador(self):
        """Crea el jugador con diseño CUBIK neon brillante"""
        x = JUGADOR_X_FIJO
        y = self.jugador_y
        tam = TAMANO_JUGADOR
        
        # Sombra con efecto difuminado profundo
        self.sombra_jugador = self.canvas.create_oval(
            x + 2, y + tam - 2, x + tam - 2, y + tam + 8,
            fill="#000000", outline="", stipple="gray25", tags="jugador")
        
        # Fondo del cubo con color base (sin glow azul)
        self.jugador_fondo = self.canvas.create_rectangle(
            x, y, x + tam, y + tam,
            fill=self.colores["player"], outline="", tags="jugador")
        
        # Borde interior con gradiente simulado
        self.jugador_borde = self.canvas.create_rectangle(
            x + 3, y + 3, x + tam - 3, y + tam - 3,
            fill="", outline="#ff00ff", width=2, tags="jugador")
        
        # Centro brillante con efecto de luz
        self.jugador_centro = self.canvas.create_rectangle(
            x + 10, y + 10, x + tam - 10, y + tam - 10,
            fill="#ffffff", outline="", tags="jugador")
        
        # Contorno negro grueso para definir bordes
        self.jugador_contorno = self.canvas.create_rectangle(
            x, y, x + tam, y + tam,
            fill="", outline="#000000", width=4, tags="jugador")
        
        # IMPORTANTE: Elevar jugador para que se vea encima del nivel
        self.canvas.tag_raise("jugador")
        
        # Detalles adicionales para otros modos
        self.detalles_modo = []
    
    def crear_hud(self):
        """Crea la interfaz de usuario mejorada"""
        # Panel superior oscuro semi-transparente
        self.canvas.create_rectangle(0, 0, ANCHO_VENTANA, 100,
                                     fill="#000000", stipple="gray50", tags="hud")
        
        # Borde decorativo inferior del panel
        self.canvas.create_line(0, 100, ANCHO_VENTANA, 100,
                               fill=self.colores["player"], width=3, tags="hud")
        
        # SECCIÓN IZQUIERDA: Intentos y nivel
        # Icono de nivel
        self.canvas.create_rectangle(15, 15, 55, 55,
                                     fill=self.colores["player"],
                                     outline="#ffffff", width=2, tags="hud")
        self.canvas.create_text(35, 35,
                               text=str(self.nivel_actual),
                               fill="#000000", font=("Arial", 24, "bold"), tags="hud")
        
        # Intentos con icono
        self.canvas.create_text(70, 25,
                               text="Intentos",
                               fill="#aaaaaa", font=("Arial", 10), anchor="w", tags="hud")
        self.texto_intentos = self.canvas.create_text(70, 45,
                                                      text=f"{self.intentos}",
                                                      fill="#ffffff", 
                                                      font=("Arial", 18, "bold"),
                                                      anchor="w", tags="hud")
        
        # Timer (cronómetro)
        self.canvas.create_text(70, 65,
                               text="Tiempo",
                               fill="#aaaaaa", font=("Arial", 10), anchor="w", tags="hud")
        self.texto_timer = self.canvas.create_text(70, 83,
                                                   text="0:00",
                                                   fill="#ffaa00", 
                                                   font=("Arial", 14, "bold"),
                                                   anchor="w", tags="hud")
        
        # SECCIÓN CENTRAL: Nombre del nivel y porcentaje
        # Titulo del nivel estilo CUBIK simple
        titulo_nivel = f"{self.nivel_data['nombre'].upper()}"
        
        # Texto principal único magenta sin duplicados
        self.canvas.create_text(ANCHO_VENTANA // 2, 25,
                               text=titulo_nivel,
                               fill="#ff00ff", 
                               font=("Impact", 22, "bold"), tags="hud")
        
        # Barra de progreso estilo CUBIK - Diseño futurista
        barra_x = ANCHO_VENTANA // 2 - 200
        barra_y = 55
        barra_ancho = 400
        barra_alto = 25
        
        # Sombra profunda de la barra
        self.canvas.create_rectangle(barra_x + 3, barra_y + 3, 
                                     barra_x + barra_ancho + 3, barra_y + barra_alto + 3,
                                     fill="#000000", outline="", tags="hud")
        
        # Fondo de la barra con gradiente oscuro
        self.canvas.create_rectangle(barra_x, barra_y, 
                                     barra_x + barra_ancho, barra_y + barra_alto,
                                     fill="#0a0a1e", outline="", tags="hud")
        
        # Borde exterior cyan brillante
        self.canvas.create_rectangle(barra_x, barra_y, 
                                     barra_x + barra_ancho, barra_y + barra_alto,
                                     fill="", outline="#00ffff", width=3, tags="hud")
        
        # Borde interior magenta
        self.canvas.create_rectangle(barra_x + 2, barra_y + 2, 
                                     barra_x + barra_ancho - 2, barra_y + barra_alto - 2,
                                     fill="", outline="#ff00ff", width=1, tags="hud")
        
        # Barra de progreso (se actualizará) con gradiente simulado
        self.barra_progreso = self.canvas.create_rectangle(
            barra_x + 4, barra_y + 4,
            barra_x + 4, barra_y + barra_alto - 4,
            fill="#ff00ff", outline="", tags="hud")
        
        # Porcentaje sobre la barra con efecto glow
        # Sombra del porcentaje
        self.canvas.create_text(ANCHO_VENTANA // 2 + 2, barra_y + barra_alto // 2 + 2,
                               text="0%", fill="#000000",
                               font=("Impact", 16, "bold"), tags="hud")
        
        # Texto porcentaje principal
        self.texto_porcentaje = self.canvas.create_text(
            ANCHO_VENTANA // 2, barra_y + barra_alto // 2,
            text="0%",
            fill="#00ffff",
            font=("Impact", 16, "bold"), tags="hud")
        
        # SECCION DERECHA: Panel cyberpunk de monedas y estadísticas
        # Sombra del panel
        self.canvas.create_rectangle(ANCHO_VENTANA - 198, 13,
                                     ANCHO_VENTANA - 13, 73,
                                     fill="#000000", outline="", tags="hud")
        
        # Panel de monedas con fondo oscuro
        self.canvas.create_rectangle(ANCHO_VENTANA - 200, 10,
                                     ANCHO_VENTANA - 15, 70,
                                     fill="#0a0a1e", outline="", tags="hud")
        
        # Borde exterior cyan brillante
        self.canvas.create_rectangle(ANCHO_VENTANA - 200, 10,
                                     ANCHO_VENTANA - 15, 70,
                                     fill="", outline="#ffaa00", width=3, tags="hud")
        
        # Borde interior magenta
        self.canvas.create_rectangle(ANCHO_VENTANA - 198, 12,
                                     ANCHO_VENTANA - 17, 68,
                                     fill="", outline="#ff00ff", width=1, tags="hud")
        
        # Etiqueta "COINS" estilo CUBIK
        self.canvas.create_text(ANCHO_VENTANA - 107, 25,
                               text="◈ COINS ◈",
                               fill="#00ffff", font=("Impact", 11, "bold"), tags="hud")
        
        # Contador de monedas con sombra
        self.canvas.create_text(ANCHO_VENTANA - 106, 49,
                               text=f"COINS {len(self.monedas_recolectadas)}/3",
                               fill="#000000",
                               font=("Impact", 18, "bold"), tags="hud")
        
        self.texto_monedas = self.canvas.create_text(ANCHO_VENTANA - 107, 48,
                                                     text=f"COINS {len(self.monedas_recolectadas)}/3",
                                                     fill="#ffaa00",
                                                     font=("Impact", 18, "bold"), tags="hud")
        
        # Indicador de velocidad estilo CUBIK
        # Sombra
        self.canvas.create_text(ANCHO_VENTANA - 106, 88,
                               text="SPEED",
                               fill="#000000", font=("Impact", 10), tags="hud")
        # Texto
        self.canvas.create_text(ANCHO_VENTANA - 107, 87,
                               text="SPEED",
                               fill="#888888", font=("Impact", 10), tags="hud")
        
        # Velocidad con sombra
        self.canvas.create_text(ANCHO_VENTANA - 106, 104,
                               text="x1", fill="#000000",
                               font=("Impact", 14, "bold"), tags="hud")
        self.texto_velocidad = self.canvas.create_text(ANCHO_VENTANA - 107, 103,
                                                       text="x1",
                                                       fill="#00ff88",
                                                       font=("Impact", 14, "bold"), tags="hud")
        
        # Indicador de modo práctica
        modo_texto = "PRÁCTICA" if self.modo_practica else ""
        color_modo = "#00ff00" if self.modo_practica else "white"
        self.texto_modo_practica = self.canvas.create_text(
            ANCHO_VENTANA // 2, ALTO_VENTANA - 20,
            text=modo_texto,
            fill=color_modo,
            font=("Arial", 14, "bold"), tags="hud")
        
        # Control de checkpoint manual (solo en modo práctica)
        if self.modo_practica:
            self.canvas.create_text(
                ANCHO_VENTANA - 100, ALTO_VENTANA - 40,
                text="[Q] Checkpoint",
                fill="#88ff88",
                font=("Arial", 11), tags="hud")
            self.canvas.create_text(
                ANCHO_VENTANA - 100, ALTO_VENTANA - 60,
                text="[E] Eliminar",
                fill="#ff8888",
                font=("Arial", 11), tags="hud")
        
        # ========== BARRA DE COMBO EPICA CUBIK - Diseño AAA ==========
        adrenalina_x = 15
        adrenalina_y = ALTO_VENTANA - 60  # Esquina inferior izquierda
        adrenalina_w = 220
        adrenalina_h = 30
        
        # Sombra profunda
        self.canvas.create_rectangle(
            adrenalina_x + 3, adrenalina_y + 3,
            adrenalina_x + adrenalina_w + 3, adrenalina_y + adrenalina_h + 3,
            fill="#000000", outline="", tags="hud")
        
        # Fondo oscuro
        self.canvas.create_rectangle(
            adrenalina_x, adrenalina_y,
            adrenalina_x + adrenalina_w, adrenalina_y + adrenalina_h,
            fill="#0a0a1e", outline="", tags="hud")
        
        # Borde exterior verde brillante
        self.canvas.create_rectangle(
            adrenalina_x, adrenalina_y,
            adrenalina_x + adrenalina_w, adrenalina_y + adrenalina_h,
            fill="", outline="#00ff88", width=3, tags="hud")
        
        # Borde interior cyan
        self.canvas.create_rectangle(
            adrenalina_x + 2, adrenalina_y + 2,
            adrenalina_x + adrenalina_w - 2, adrenalina_y + adrenalina_h - 2,
            fill="", outline="#00ffff", width=1, tags="hud")
        
        # Barra de progreso (se llenará con combo) con gradiente verde brillante
        self.barra_adrenalina = self.canvas.create_rectangle(
            adrenalina_x + 4, adrenalina_y + 4,
            adrenalina_x + 4, adrenalina_y + adrenalina_h - 4,
            fill="#00ff88", outline="", tags="hud")
        
        # Etiqueta permanente de COMBO METER unificada
        self.canvas.create_text(adrenalina_x + adrenalina_w // 2, adrenalina_y + adrenalina_h // 2,
                               text="COMBO METER",
                               fill="#ffffff", font=("Arial Black", 11, "bold"),
                               tags="hud")
    
    def desbloquear_logro(self, nombre_logro):
        """Desbloquea un logro y lo agrega a la cola para mostrarlo"""
        if nombre_logro in self.logros and not self.logros[nombre_logro]:
            self.logros[nombre_logro] = True
            self.logros_pendientes_mostrar.append(nombre_logro)
            
            # Mostrar inmediatamente si no hay otros mostrándose
            if len(self.logros_pendientes_mostrar) == 1:
                self.mostrar_logro_siguiente()
    
    def mostrar_logro_siguiente(self):
        """Muestra el siguiente logro de la cola"""
        if not self.logros_pendientes_mostrar:
            return
        
        logro = self.logros_pendientes_mostrar[0]
        
        # Diccionario de logros con emoji e info
        info_logros = {
            "primera_muerte": ("MUERTE", "Primera Muerte", "¡Todos empezamos así!"),
            "primera_victoria": ("VICTORIA", "Primera Victoria", "¡Primer nivel completado!"),
            "combo_10": ("RACHA", "En Racha", "¡10 saltos sin morir!"),
            "combo_25": ("IMPARABLE", "Imparable", "¡25 saltos sin morir!"),
            "velocidad_maxima": ("RAPIDO", "Velocidad Máxima", "¡Alcanzaste x4!"),
            "checkpoint_maestro": ("CHECKPOINT", "Maestro Checkpoints", "¡5 checkpoints en un nivel!"),
            "perfeccionista": ("PERFECTO", "Perfeccionista", "¡Nivel sin morir!"),
            "speedrunner": ("RECORD", "Speedrunner", "¡Tiempo récord!"),
            "coleccionista": ("COLECCIONISTA", "Coleccionista", "¡Todas las monedas!")
        }
        
        if logro in info_logros:
            emoji, titulo, descripcion = info_logros[logro]
            
            # Crear notificación animada
            x = ANCHO_VENTANA - 250
            y = 120
            
            # Panel de logro
            panel = self.canvas.create_rectangle(
                x, y, x + 230, y + 80,
                fill="#1a1a2e", outline="#ffaa00", width=3, tags="logro_notif"
            )
            
            # Emoji
            emoji_text = self.canvas.create_text(
                x + 30, y + 40,
                text=emoji, font=("Arial", 32), tags="logro_notif"
            )
            
            # Título
            titulo_text = self.canvas.create_text(
                x + 70, y + 25,
                text=f"{titulo}", fill="#ffaa00",
                font=("Arial", 14, "bold"), anchor="w", tags="logro_notif"
            )
            
            # Descripción
            desc_text = self.canvas.create_text(
                x + 70, y + 50,
                text=descripcion, fill="#aaaaaa",
                font=("Arial", 10), anchor="w", tags="logro_notif"
            )
            
            # Reproducir sonido
            self.reproducir_sonido("checkpoint")
            
            # Eliminar notificación después de 3 segundos
            def eliminar_y_siguiente():
                self.canvas.delete("logro_notif")
                self.logros_pendientes_mostrar.pop(0)
                # Mostrar siguiente si hay
                if self.logros_pendientes_mostrar:
                    self.ventana.after(500, self.mostrar_logro_siguiente)
            
            self.ventana.after(3000, eliminar_y_siguiente)
    
    def verificar_logros(self):
        """Verifica y desbloquea logros según el progreso"""
        # Primera muerte
        if self.estadisticas["muertes_totales"] == 1:
            self.desbloquear_logro("primera_muerte")
        
        # Combo de saltos
        if self.combo_count == 10:
            self.desbloquear_logro("combo_10")
        elif self.combo_count == 25:
            self.desbloquear_logro("combo_25")
        
        # Velocidad máxima
        if self.velocidad_juego >= VELOCIDADES["x4"]:
            self.desbloquear_logro("velocidad_maxima")
        
        # Checkpoints
        if len(self.checkpoints) >= 5:
            self.desbloquear_logro("checkpoint_maestro")
        
        # Todas las monedas
        if len(self.monedas_recolectadas) == 3:
            self.desbloquear_logro("coleccionista")
    
    def reproducir_sonido(self, tipo):
       
        if tipo in SONIDOS_CACHE:
            try:
                SONIDOS_CACHE[tipo].play()
            except:
                pass  # Si hay error, no bloquear el juego
    
    def screen_shake(self, intensidad=10):
        """Aplica efecto de vibración a la pantalla"""
        self.shake_amount = intensidad
    
    def flash_screen(self, intensidad=1.0):
        """Flash blanco en la pantalla"""
        self.flash_alpha = intensidad
    
    def iniciar_musica_nivel(self, numero_nivel):
        """Inicia la música electrónica del nivel usando pygame"""
        # Detener música anterior si existe
        self.detener_musica()
        
        # Crear thread para música electrónica
        if numero_nivel == 1:
            # NIVEL 1 - CUBE BASICS - Estilo Faded (Alan Walker)
            self.musica_thread = Thread(target=self.musica_nivel_1, daemon=True)
        elif numero_nivel == 2:
            # NIVEL 2 - SHIP FLIGHT - Estilo Mission Impossible
            self.musica_thread = Thread(target=self.musica_nivel_2, daemon=True)
        elif numero_nivel == 3:
            # NIVEL 3 - GRAVITY FLIP - Estilo Titanium (David Guetta)
            self.musica_thread = Thread(target=self.musica_nivel_3, daemon=True)
        else:
            # NIVEL 4 - THE GAUNTLET - Estilo The Spectre (Alan Walker)
            self.musica_thread = Thread(target=self.musica_nivel_4, daemon=True)
        
        self.musica_activa = True
        self.musica_thread.start()
    
    def detener_musica(self):
        """Detiene la música de fondo"""
        self.musica_activa = False
        try:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
        except:
            pass
    
    def generar_tono(self, frecuencia, duracion, volumen=0.3):
        """Genera un tono sintético para música electrónica"""
        sample_rate = 22050
        num_samples = int(sample_rate * duracion)
        t = np.linspace(0, duracion, num_samples, False)
        
        # Onda cuadrada para sonido más electrónico
        wave = np.sign(np.sin(2 * np.pi * frecuencia * t)) * volumen
        wave = (wave * 32767).astype(np.int16)
        
        # Convertir a stereo
        stereo_wave = np.column_stack((wave, wave))
        
        # Crear sonido de pygame
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound
    
    def musica_nivel_1(self):
       
        # Progresión de Faded: F#m - D - A - E
        try:
            # Piano principal (melodía iconica de Faded)
            piano_melody = [
                # "You were the shadow to my light"
                self.generar_tono(740, 0.4, 0.3),   # F#
                self.generar_tono(659, 0.4, 0.3),   # E
                self.generar_tono(587, 0.4, 0.3),   # D
                self.generar_tono(494, 0.4, 0.3),   # B
                self.generar_tono(440, 0.4, 0.3),   # A
                self.generar_tono(494, 0.4, 0.3),   # B
                self.generar_tono(587, 0.6, 0.3),   # D (hold)
            ]
            
            # Bajo profundo
            bass_notes = [
                self.generar_tono(185, 0.5, 0.4),   # F# bajo
                self.generar_tono(147, 0.5, 0.4),   # D bajo
                self.generar_tono(220, 0.5, 0.4),   # A bajo
                self.generar_tono(165, 0.5, 0.4),   # E bajo
            ]
            
            beat = 0
            while self.musica_activa:
                if not self.musica_activa:
                    break
                
                # Bajo cada 2 beats
                if beat % 2 == 0:
                    bass_notes[(beat // 2) % len(bass_notes)].play()
                
                # Melodía de piano
                piano_melody[beat % len(piano_melody)].play()
                
                time.sleep(0.4)
                beat += 1
        except Exception as e:
            print(f"Error en música nivel 1: {e}")
    
    def musica_nivel_2(self):
        # Tema icónico de Mission Impossible en 5/4
        try:
            # Melodía principal (dum dum, da-dum, dum dum, da-dum)
            theme_melody = [
                self.generar_tono(392, 0.15, 0.35),  # G
                self.generar_tono(415, 0.15, 0.35),  # G#
                self.generar_tono(392, 0.3, 0.35),   # G (hold)
                self.generar_tono(370, 0.15, 0.35),  # F#
                self.generar_tono(392, 0.15, 0.35),  # G
                self.generar_tono(415, 0.15, 0.35),  # G#
                self.generar_tono(392, 0.3, 0.35),   # G (hold)
                self.generar_tono(349, 0.15, 0.35),  # F
            ]
            
            # Bajo pulsante
            bass_pulse = self.generar_tono(98, 0.2, 0.5)  # G bajo
            
            # Snare fuerte
            snare = self.generar_tono(250, 0.05, 0.4)
            
            beat = 0
            while self.musica_activa:
                if not self.musica_activa:
                    break
                
                # Bajo en cada beat
                bass_pulse.play()
                
                # Tema principal
                theme_melody[beat % len(theme_melody)].play()
                
                # Snare cada 4 beats
                if beat % 4 == 2:
                    snare.play()
                
                time.sleep(0.2)
                beat += 1
        except Exception as e:
            print(f"Error en música nivel 2: {e}")
    
    def musica_nivel_3(self):
        
        # Progresión: Em - C - G - D
        try:
            # Sintetizador principal (drop de Titanium)
            synth_lead = [
                self.generar_tono(659, 0.25, 0.35),  # E
                self.generar_tono(784, 0.25, 0.35),  # G
                self.generar_tono(988, 0.25, 0.35),  # B
                self.generar_tono(784, 0.25, 0.35),  # G
                self.generar_tono(659, 0.25, 0.35),  # E
                self.generar_tono(523, 0.25, 0.35),  # C
                self.generar_tono(587, 0.5, 0.35),   # D (hold)
            ]
            
            # Kick electrónico potente
            kick = self.generar_tono(50, 0.12, 0.6)
            
            # Bass wobble
            bass_wobble = [
                self.generar_tono(82, 0.15, 0.5),   # E bajo
                self.generar_tono(98, 0.15, 0.5),   # G bajo
                self.generar_tono(65, 0.15, 0.5),   # C bajo
                self.generar_tono(73, 0.15, 0.5),   # D bajo
            ]
            
            # Snare potente
            snare = self.generar_tono(200, 0.08, 0.45)
            
            beat = 0
            while self.musica_activa:
                if not self.musica_activa:
                    break
                
                # Kick en cada beat
                kick.play()
                
                # Bass wobble
                bass_wobble[beat % len(bass_wobble)].play()
                
                # Sintetizador lead
                synth_lead[beat % len(synth_lead)].play()
                
                # Snare en beats 2 y 4
                if beat % 4 == 1 or beat % 4 == 3:
                    snare.play()
                
                time.sleep(0.18)
                beat += 1
        except Exception as e:
            print(f"Error en música nivel 3: {e}")
    
    def musica_nivel_4(self):
       
        # Progresión épica: Am - F - C - G
        try:
            # Sintetizador épico principal
            epic_synth = [
                self.generar_tono(880, 0.3, 0.35),   # A
                self.generar_tono(1047, 0.3, 0.35),  # C
                self.generar_tono(1175, 0.3, 0.35),  # D
                self.generar_tono(1319, 0.3, 0.35),  # E
                self.generar_tono(1397, 0.3, 0.35),  # F
                self.generar_tono(1319, 0.3, 0.35),  # E
                self.generar_tono(1175, 0.3, 0.35),  # D
                self.generar_tono(1047, 0.6, 0.35),  # C (hold)
            ]
            
            # Bajo potente
            bass_drop = [
                self.generar_tono(110, 0.25, 0.55),  # A bajo
                self.generar_tono(87, 0.25, 0.55),   # F bajo
                self.generar_tono(131, 0.25, 0.55),  # C bajo
                self.generar_tono(98, 0.25, 0.55),   # G bajo
            ]
            
            # Kick masivo
            mega_kick = self.generar_tono(45, 0.15, 0.65)
            
            # Snare explosivo
            explosive_snare = self.generar_tono(220, 0.1, 0.5)
            
            beat = 0
            while self.musica_activa:
                if not self.musica_activa:
                    break
                
                # Kick masivo
                mega_kick.play()
                
                # Bajo drop
                bass_drop[beat % len(bass_drop)].play()
                
                # Sintetizador épico
                epic_synth[beat % len(epic_synth)].play()
                
                # Snare cada 4 beats
                if beat % 4 == 2:
                    explosive_snare.play()
                
                time.sleep(0.25)
                beat += 1
        except Exception as e:
            print(f"Error en música nivel 4: {e}")
    
    def crear_particula(self, x, y, color, velocidad_x=0, velocidad_y=0, vida=20, con_glow=True):
        """Crea una partícula de efecto mejorada con glow opcional"""
        # Limitar partículas para mejor rendimiento
        if len(self.particulas) > MAX_PARTICULAS:
            if self.particulas:
                old = self.particulas.pop(0)
                self.canvas.delete(old["id"])
                if old.get("glow_id"):
                    self.canvas.delete(old["glow_id"])
        
        size = random.randint(3, 6)
        
        # Crear glow (halo) si está habilitado
        glow_id = None
        if con_glow and EFECTOS_VISUALES["glow"]:
            glow_size = size + 4
            glow_id = self.canvas.create_oval(
                x - glow_size, y - glow_size, x + glow_size, y + glow_size,
                fill=color, outline="", stipple="gray25", tags="particula"
            )
        
        # Crear partícula principal
        particula_id = self.canvas.create_oval(
            x - size, y - size, x + size, y + size,
            fill=color, outline="", tags="particula"
        )
        
        self.particulas.append({
            "id": particula_id,
            "glow_id": glow_id,
            "vx": velocidad_x,
            "vy": velocidad_y,
            "vida": vida,
            "vida_max": vida,
            "size": size
        })
    
    def crear_explosion_particulas(self, x, y, color, cantidad=12):
        """Crea una explosión de partículas mejorada"""
        cantidad = min(cantidad, 12)  # Más partículas con pygame
        for i in range(cantidad):
            angulo = (360 / cantidad) * i
            velocidad = random.uniform(3, 7)
            vx = math.cos(math.radians(angulo)) * velocidad
            vy = math.sin(math.radians(angulo)) * velocidad
            self.crear_particula(x, y, color, vx, vy, vida=25, con_glow=True)
    
    def actualizar_particulas(self):
        """Actualiza todas las partículas con efectos mejorados"""
        for particula in self.particulas[:]:
            particula["vida"] -= 1
            
            if particula["vida"] <= 0:
                self.canvas.delete(particula["id"])
                if particula.get("glow_id"):
                    self.canvas.delete(particula["glow_id"])
                self.particulas.remove(particula)
            else:
                # Mover partícula
                self.canvas.move(particula["id"], particula["vx"], particula["vy"])
                if particula.get("glow_id"):
                    self.canvas.move(particula["glow_id"], particula["vx"], particula["vy"])
                
                # Aplicar gravedad a la partícula
                particula["vy"] += 0.3
                
                # Desacelerar horizontalmente (friction)
                particula["vx"] *= 0.97
                
                # Fade out con scale down
                factor = particula["vida"] / particula["vida_max"]
                if factor < 0.4:
                    # Reducir tamaño gradualmente
                    coords = self.canvas.coords(particula["id"])
                    if coords:
                        cx = (coords[0] + coords[2]) / 2
                        cy = (coords[1] + coords[3]) / 2
                        new_size = particula["size"] * factor
                        self.canvas.coords(particula["id"],
                                         cx - new_size, cy - new_size,
                                         cx + new_size, cy + new_size)
                        
                        # Actualizar glow también
                        if particula.get("glow_id"):
                            glow_size = new_size + 3
                            self.canvas.coords(particula["glow_id"],
                                             cx - glow_size, cy - glow_size,
                                             cx + glow_size, cy + glow_size)
    
    def agregar_trail(self):
        
        # Limitar trails activos con la constante global
        if len(self.trail_cubo) > MAX_TRAILS:
            old = self.trail_cubo.pop(0)
            self.canvas.delete(old["id"])
        
        x = JUGADOR_X_FIJO
        y = self.jugador_y
        tam = TAMANO_JUGADOR
        
        # MOTION BLUR EN ALTA VELOCIDAD (x3 y x4)
        if EFECTOS_VISUALES["motion_blur"] and self.velocidad_juego >= VELOCIDADES["x3"]:
            # Crear múltiples trails para efecto de motion blur
            num_blur_trails = 3 if self.velocidad_juego >= VELOCIDADES["x4"] else 2
            
            for i in range(num_blur_trails):
                offset_x = -(i + 1) * 15  # Trails detrás del jugador
                blur_alpha = "gray12" if i == 0 else "gray25"  # Más transparente mientras más atrás
                
                trail_id = self.canvas.create_rectangle(
                    x + offset_x + 5, y + 5, x + offset_x + tam - 5, y + tam - 5,
                    fill=self.colores["player"], outline="",
                    stipple=blur_alpha, tags="trail"
                )
                
                self.trail_cubo.append({"id": trail_id, "vida": 3 + i})  # Vida variable
        else:
            # Trail normal (sin motion blur)
            trail_id = self.canvas.create_rectangle(
                x + 5, y + 5, x + tam - 5, y + tam - 5,
                fill=self.colores["player"], outline="",
                stipple="gray25", tags="trail"
            )
            
            self.trail_cubo.append({"id": trail_id, "vida": 5})
    
    def actualizar_trail(self):
        """Actualiza el trail del cubo"""
        for trail in self.trail_cubo[:]:
            trail["vida"] -= 1
            if trail["vida"] <= 0:
                self.canvas.delete(trail["id"])
                self.trail_cubo.remove(trail)
    
    def actualizar_pulso_fondo(self):
        """Crea efecto de pulso en el fondo"""
        self.pulso_fondo = (self.pulso_fondo + 1) % 60
        
        # Efecto de líneas pulsantes en el suelo
        if self.pulso_fondo % 10 == 0:
            # Las líneas ya existen, solo las hacemos "pulsar" visualmente
            pass
    
    def actualizar_efectos_visuales(self):
        """Actualiza efectos visuales mejorados como shake, flash y ZOOM CINEMÁTICO"""
        # SISTEMA DE CAMERA ZOOM CINEMÁTICO
        if EFECTOS_VISUALES["camera_zoom"]:
            # Interpolar suavemente hacia el zoom objetivo
            if abs(self.camera_zoom - self.camera_zoom_target) > 0.001:
                self.camera_zoom += (self.camera_zoom_target - self.camera_zoom) * self.camera_zoom_speed
                
                # Aplicar zoom (escalar canvas - simulado moviendo objetos)
                # Nota: tkinter no tiene zoom real, usamos escala visual ajustando posiciones
                # Para simplicidad, solo reportamos el zoom (podrías escalar objetos individuales)
                if hasattr(self, 'ultimo_zoom') and self.ultimo_zoom != self.camera_zoom:
                    zoom_delta = self.camera_zoom - self.ultimo_zoom
                    # Efecto visual: más grande = más cerca, más pequeño = más lejos
                    # (Implementación simplificada - en producción usarías transformaciones canvas)
                    pass
                
                self.ultimo_zoom = self.camera_zoom
            else:
                # Snap cuando está muy cerca
                self.camera_zoom = self.camera_zoom_target
        
        # Screen shake mejorado con decay exponencial
        if self.shake_amount > 0:
            if EFECTOS_VISUALES["screen_shake_intenso"]:
                # Shake más intenso y natural
                dx = random.randint(-self.shake_amount, self.shake_amount)
                dy = random.randint(-self.shake_amount, self.shake_amount)
            else:
                dx = random.randint(-self.shake_amount, self.shake_amount) // 2
                dy = random.randint(-self.shake_amount, self.shake_amount) // 2
            
            # Mover todo excepto el HUD y jugador
            for obj in self.canvas.find_withtag("nivel"):
                self.canvas.move(obj, dx, dy)
            for obj in self.canvas.find_withtag("fondo"):
                self.canvas.move(obj, dx // 2, dy // 2)  # Fondo se mueve menos (paralax)
            
            # Reducir shake con decay exponencial (más natural)
            self.shake_amount = int(self.shake_amount * 0.85)
            
            # Restaurar posición para el siguiente frame
            for obj in self.canvas.find_withtag("nivel"):
                self.canvas.move(obj, -dx, -dy)
            for obj in self.canvas.find_withtag("fondo"):
                self.canvas.move(obj, -dx // 2, -dy // 2)
        
        # Flash screen mejorado con colores
        if self.flash_alpha > 0:
            # Crear flash overlay temporal
            if not hasattr(self, 'flash_overlay') or not self.canvas.coords(self.flash_overlay):
                # Color del flash según la situación
                flash_color = "#ffffff"  # Blanco por defecto
                if hasattr(self, 'flash_color'):
                    flash_color = self.flash_color
                
                self.flash_overlay = self.canvas.create_rectangle(
                    0, 0, ANCHO_VENTANA, ALTO_VENTANA,
                    fill=flash_color, stipple="gray75", tags="flash")
            
            # Reducir flash gradualmente
            self.flash_alpha = max(0, self.flash_alpha - 0.15)
            
            # Eliminar overlay cuando termine
            if self.flash_alpha <= 0:
                self.canvas.delete("flash")
                if hasattr(self, 'flash_color'):
                    delattr(self, 'flash_color')
    
    def animar_sierras(self):
        """Anima la rotación de las sierras"""
        # Buscar todas las sierras y rotar sus líneas
        for obj_info in self.objetos_nivel:
            if obj_info["data"]["tipo"] == "sierra" and obj_info["visual"]:
                visual_ids = obj_info["visual"]
                if len(visual_ids) >= 3:
                    # Las líneas son los elementos 1 y 2
                    linea1 = visual_ids[1]
                    linea2 = visual_ids[2]
                    
                    # Obtener centro de la sierra (del círculo)
                    circulo_coords = self.canvas.coords(visual_ids[0])
                    if circulo_coords and len(circulo_coords) >= 4:
                        cx = (circulo_coords[0] + circulo_coords[2]) / 2
                        cy = (circulo_coords[1] + circulo_coords[3]) / 2
                        radio = (circulo_coords[2] - circulo_coords[0]) / 2
                        
                        # Rotar las líneas (simulado cambiando entre horizontal/vertical/diagonal)
                        # Esto es una simplificación de rotación
                        angulo = (self.frame_count * 5) % 360
                        
                        if 0 <= angulo < 45 or 315 <= angulo < 360:
                            # Horizontal
                            self.canvas.coords(linea1, cx - radio, cy, cx + radio, cy)
                            self.canvas.coords(linea2, cx, cy - radio, cx, cy + radio)
                        elif 45 <= angulo < 90:
                            # Diagonal 1
                            self.canvas.coords(linea1, cx - radio*0.7, cy - radio*0.7, 
                                             cx + radio*0.7, cy + radio*0.7)
                            self.canvas.coords(linea2, cx - radio*0.7, cy + radio*0.7, 
                                             cx + radio*0.7, cy - radio*0.7)
                        elif 90 <= angulo < 135:
                            # Vertical
                            self.canvas.coords(linea1, cx, cy - radio, cx, cy + radio)
                            self.canvas.coords(linea2, cx - radio, cy, cx + radio, cy)
                        elif 135 <= angulo < 180:
                            # Diagonal 2
                            self.canvas.coords(linea1, cx - radio*0.7, cy + radio*0.7, 
                                             cx + radio*0.7, cy - radio*0.7)
                            self.canvas.coords(linea2, cx - radio*0.7, cy - radio*0.7, 
                                             cx + radio*0.7, cy + radio*0.7)
                        elif 180 <= angulo < 225:
                            # Horizontal invertido
                            self.canvas.coords(linea1, cx - radio, cy, cx + radio, cy)
                            self.canvas.coords(linea2, cx, cy - radio, cx, cy + radio)
                        elif 225 <= angulo < 270:
                            # Diagonal 3
                            self.canvas.coords(linea1, cx - radio*0.7, cy - radio*0.7, 
                                             cx + radio*0.7, cy + radio*0.7)
                            self.canvas.coords(linea2, cx - radio*0.7, cy + radio*0.7, 
                                             cx + radio*0.7, cy - radio*0.7)
                        else:
                            # Vertical invertido
                            self.canvas.coords(linea1, cx, cy - radio, cx, cy + radio)
                            self.canvas.coords(linea2, cx - radio, cy, cx + radio, cy)
    
    def actualizar_efecto_velocidad(self):
        """Crea líneas de velocidad cuando el jugador va rápido"""
        # Limpiar líneas antiguas
        for linea_id in self.efecto_velocidad[:]:
            try:
                self.canvas.delete(linea_id)
                self.efecto_velocidad.remove(linea_id)
            except:
                pass
        
        # Solo crear líneas si la velocidad es x2 o superior
        if self.velocidad_juego not in ["x2", "x3", "x4"]:
            return
        
        # Intensidad basada en velocidad
        num_lineas = {"x2": 3, "x3": 5, "x4": 8}.get(self.velocidad_juego, 3)
        
        # Crear líneas de velocidad detrás del jugador
        for i in range(num_lineas):
            x_start = JUGADOR_X_FIJO - (i * 20) - random.randint(-10, 10)
            y = self.jugador_y + random.randint(0, TAMANO_JUGADOR)
            longitud = random.randint(20, 60)
            
            # Color más brillante cuanto más rápido
            alpha_simulado = "gray" + str(50 - i * 5)  # Más transparente al alejarse
            
            linea_id = self.canvas.create_line(
                x_start, y, x_start - longitud, y,
                fill=self.colores["player"], width=2,
                stipple=alpha_simulado, tags="efecto_vel"
            )
            self.efecto_velocidad.append(linea_id)
    
    def actualizar_combo_visual(self):
        """Actualiza visualización de combo Y barra de adrenalina con nuevo diseño """
        # Actualizar barra de adrenalina según combo
        max_combo_visual = 50  # Máximo para llenar la barra
        progreso = min(1.0, self.combo_count / max_combo_visual)
        barra_w = 220
        barra_ancho = int(progreso * (barra_w - 8))
        
        # Actualizar ancho de la barra con nuevas dimensiones (ESQUINA INFERIOR IZQUIERDA)
        adrenalina_x = 15
        adrenalina_y = ALTO_VENTANA - 60  # Esquina inferior izquierda
        self.canvas.coords(self.barra_adrenalina,
                          adrenalina_x + 4, adrenalina_y + 4,
                          adrenalina_x + 4 + barra_ancho, adrenalina_y + 26)
        
        # Color según nivel de combo
        if self.combo_count >= 40:
            color_barra = "#ff00ff"  # Morado épico
        elif self.combo_count >= 25:
            color_barra = "#ff0000"  # Rojo intenso
        elif self.combo_count >= 10:
            color_barra = "#ffaa00"  # Naranja
        else:
            color_barra = "#00ff88"  # Verde base
        
        self.canvas.itemconfig(self.barra_adrenalina, fill=color_barra)
        
        # Mostrar contador de combo al lado del combo meter (esquina inferior izquierda)
        # Eliminar texto anterior
        self.canvas.delete("combo_text")
        
        if self.combo_count >= 5:
            # Texto de combo al lado derecho de la barra de combo meter
            combo_text = f"x{self.combo_count}"
            combo_x = adrenalina_x + barra_w + 15  # A la derecha de la barra
            combo_y = adrenalina_y + 15  # Centrado verticalmente con la barra
            
            # Sombra
            self.canvas.create_text(
                combo_x + 2, combo_y + 2,
                text=combo_text,
                fill="#000000",
                font=("Arial Black", 16, "bold"),
                anchor="w",
                tags=("hud", "combo_text")
            )
            
            # Texto principal con el mismo tamaño de fuente
            self.canvas.create_text(
                combo_x, combo_y,
                text=combo_text,
                fill=color_barra,
                font=("Arial Black", 16, "bold"),
                anchor="w",
                tags=("hud", "combo_text")
            )
    
    def incrementar_combo(self):
        """Incrementa el combo con efectos visuales ÉPICOS"""
        self.combo_count += 1
        
        # Calcular posición del texto de combo según gravedad
        combo_x = JUGADOR_X_FIJO + TAMANO_JUGADOR // 2
        if self.gravedad_invertida:
            combo_y = self.jugador_y + TAMANO_JUGADOR + 40  # Debajo del jugador cuando está arriba
        else:
            combo_y = self.jugador_y - 40  # Arriba del jugador cuando está abajo
        
        # Efecto visual según el nivel de combo
        if self.combo_count % 25 == 0:
            # MEGA COMBO! Efecto masivo
            self.crear_explosion_particulas(combo_x, combo_y, "#ff00ff", cantidad=20)
            self.screen_shake(15)
            self.flash_color = "#ff00ff"
            self.flash_screen(0.5)
            self.reproducir_sonido("whoosh")
            # Texto flotante "MEGA COMBO!"
            self.mostrar_texto_flotante(combo_x, combo_y, "MEGA COMBO!", "#ff00ff", 36)
        elif self.combo_count % 10 == 0:
            # SUPER COMBO! Efecto grande
            self.crear_explosion_particulas(combo_x, combo_y, "#ffaa00", cantidad=15)
            self.screen_shake(8)
            self.reproducir_sonido("moneda")
            self.mostrar_texto_flotante(combo_x, combo_y, "SUPER!", "#ffaa00", 28)
        elif self.combo_count % 5 == 0:
            # COMBO! Efecto normal
            self.crear_explosion_particulas(combo_x, combo_y, "#00ff88", cantidad=10)
            self.mostrar_texto_flotante(combo_x, combo_y, f"x{self.combo_count}", "#00ff88", 24)
    
    def mostrar_texto_flotante(self, x, y, texto, color, tamaño):
        """Muestra texto que flota y desaparece"""
        # Crear texto con glow
        glow_id = self.canvas.create_text(x, y,
                                         text=texto,
                                         fill=color,
                                         font=("Arial Black", tamaño, "bold"),
                                         stipple="gray25",
                                         tags="texto_flotante")
        
        text_id = self.canvas.create_text(x, y,
                                         text=texto,
                                         fill=color,
                                         font=("Arial Black", tamaño, "bold"),
                                         tags="texto_flotante")
        
        # Animar (mover hacia arriba y desvanecer)
        def animar_texto(step=0):
            if step < 30:
                try:
                    self.canvas.move(text_id, 0, -2)
                    self.canvas.move(glow_id, 0, -2)
                    # Fade out (simulado reduciendo tamaño)
                    if step > 20:
                        new_size = int(tamaño * (1 - (step - 20) / 10))
                        if new_size > 0:
                            self.canvas.itemconfig(text_id, font=("Arial Black", new_size, "bold"))
                            self.canvas.itemconfig(glow_id, font=("Arial Black", new_size, "bold"))
                    self.ventana.after(33, lambda: animar_texto(step + 1))
                except:
                    pass
            else:
                self.canvas.delete(text_id)
                self.canvas.delete(glow_id)
        
        animar_texto()
    
    def resetear_combo(self):
        """Resetea el combo cuando el jugador muere"""
        self.combo_count = 0
        self.canvas.delete("combo_text")
    
    def saltar(self, event):
        """Maneja el evento de salto - intenta múltiples veces para asegurar respuesta"""
        if not hasattr(self, 'juego_activo') or not self.juego_activo or self.en_menu:
            return
        
        # Intentar saltar inmediatamente
        self.realizar_salto()
        
        # Programar 4 intentos adicionales en los próximos frames (5 intentos totales)
        for i in range(1, 5):
            self.ventana.after(int((1000/FPS) * i), self.realizar_salto)
    
    def realizar_salto(self):
        """Ejecuta el salto del jugador según el modo actual"""
        if not self.juego_activo or self.en_menu:
            return
        
        salto_exitoso = False  # Para reproducir sonido solo si saltó
        
        # MODO CUBE
        if self.modo_actual == "cube":
            if not self.en_suelo:
                return
            if self.gravedad_invertida:
                # En gravedad invertida, el salto empuja HACIA EL TECHO (negativo)
                # Como la física invierte Y, usar negativo para subir hacia techo
                self.velocidad_y = self.modo_config["salto"]  # Valor negativo (salta hacia arriba/techo)
            else:
                # En gravedad normal, el salto empuja HACIA ARRIBA (negativo)
                self.velocidad_y = self.modo_config["salto"]  # Valor negativo
            self.en_suelo = False
            salto_exitoso = True
        
        # MODO SHIP (mantener presionado para volar)
        elif self.modo_actual == "ship":
            # El ship se controla de forma continua en actualizar(), no con clicks individuales
            pass
        
        # MODO BALL (invierte gravedad al tocar)
        elif self.modo_actual == "ball":
            if self.en_suelo or self.tocando_techo:
                self.gravedad_invertida = not self.gravedad_invertida
                # Ball siempre usa velocidad negativa (empuja en dirección opuesta a gravedad)
                self.velocidad_y = self.modo_config["salto"]
                self.en_suelo = False
                self.tocando_techo = False
                salto_exitoso = True
        
        # MODO UFO (impulso pequeño cada click)
        elif self.modo_actual == "ufo":
            # UFO siempre impulsa en dirección opuesta a gravedad (usar negativo)
            self.velocidad_y = self.modo_config["salto"]
            salto_exitoso = True
        
        # MODO WAVE (movimiento continuo)
        elif self.modo_actual == "wave":
            if self.gravedad_invertida:
                self.velocidad_wave = 5  # Subir
            else:
                self.velocidad_wave = -5  # Bajar
            salto_exitoso = True
        
        # MODO ROBOT (salto alto)
        elif self.modo_actual == "robot":
            if not self.en_suelo:
                return
            # Robot siempre usa velocidad negativa (empuja contra gravedad)
            self.velocidad_y = self.modo_config["salto"]
            self.en_suelo = False
            salto_exitoso = True
        
        # Reproducir sonido si el salto fue exitoso
        if salto_exitoso:
            self.reproducir_sonido("salto")
            # YA NO incrementar combo por saltos - solo por obstáculos sorteados
            # self.incrementar_combo()  # DESACTIVADO
        
        # Crear partículas al saltar
        x = JUGADOR_X_FIJO + TAMANO_JUGADOR // 2
        if self.gravedad_invertida:
            y = self.jugador_y  # Techo
        else:
            y = self.jugador_y + TAMANO_JUGADOR  # Suelo
        
        # Partículas de salto
        for i in range(6):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-2, 1) if not self.gravedad_invertida else random.uniform(-1, 2)
            self.crear_particula(x, y, self.colores["plataforma"], vx, vy, vida=15)
    
    def tecla_abajo(self, event):
        """Detecta cuando se presiona la tecla"""
        self.tecla_presionada = True
    
    def tecla_arriba(self, event):
        """Detecta cuando se suelta la tecla"""
        self.tecla_presionada = False
    
    def mouse_abajo(self, event):
        """Detecta cuando se presiona el mouse"""
        self.tecla_presionada = True
        self.saltar(event)
    
    def mouse_arriba(self, event):
        """Detecta cuando se suelta el mouse"""
        self.tecla_presionada = False
    
    def actualizar(self):
        """Loop principal del juego"""
        if self.en_menu or not self.juego_activo:
            return
        
        self.frame_count += 1
        
        # MODO WAVE - Movimiento especial
        if self.modo_actual == "wave":
            # Movimiento continuo hacia arriba o abajo
            if self.tecla_presionada:
                if self.gravedad_invertida:
                    self.velocidad_wave = 5
                else:
                    self.velocidad_wave = -5
            else:
                if self.gravedad_invertida:
                    self.velocidad_wave = -5
                else:
                    self.velocidad_wave = 5
            
            self.jugador_y += self.velocidad_wave
            
            # Límites para wave
            if self.jugador_y < 0:
                self.jugador_y = 0
            if self.jugador_y > SUELO_Y - TAMANO_JUGADOR:
                self.jugador_y = SUELO_Y - TAMANO_JUGADOR
        
        # MODO SHIP - Control continuo como nave
        elif self.modo_actual == "ship":
            # Si está presionado, empujar hacia arriba (reducir velocidad_y)
            if self.tecla_presionada:
                self.velocidad_y += self.modo_config["salto"]  # Empuje hacia arriba
            
            # Aplicar gravedad del ship
            gravedad_actual = self.modo_config["gravedad"]
            
            if self.gravedad_invertida:
                self.velocidad_y -= gravedad_actual
                self.jugador_y -= self.velocidad_y
            else:
                self.velocidad_y += gravedad_actual
                self.jugador_y += self.velocidad_y
            
            # Límite de velocidad para ship
            if self.velocidad_y > 12:
                self.velocidad_y = 12
            if self.velocidad_y < -12:
                self.velocidad_y = -12
            
            # Límites de pantalla para ship
            if self.jugador_y < LIMITE_SUPERIOR:
                # MUERTE INSTANTÁNEA - Tocó el límite superior
                self.morir()
                return
            if self.jugador_y > SUELO_Y - TAMANO_JUGADOR:
                self.jugador_y = SUELO_Y - TAMANO_JUGADOR
                self.velocidad_y = 0
        
        # OTROS MODOS - Física con gravedad normal
        else:
            # Aplicar gravedad dinámica según el modo
            gravedad_actual = self.modo_config["gravedad"]
            
            if self.gravedad_invertida:
                # Gravedad invertida: el jugador cae hacia ARRIBA (techo es el suelo)
                self.velocidad_y += gravedad_actual  # Aplicar gravedad hacia arriba
                self.jugador_y -= self.velocidad_y  # Mover hacia arriba (y negativo)
            else:
                # Gravedad normal: el jugador cae hacia ABAJO
                self.velocidad_y += gravedad_actual  # Aplicar gravedad hacia abajo
                self.jugador_y += self.velocidad_y  # Mover hacia abajo (y positivo)
        
        # Verificar colisión con suelo (excepto wave y ship que tienen límites propios)
        if self.modo_actual not in ["wave", "ship"]:
            if not self.gravedad_invertida:
                # Gravedad normal - suelo abajo
                if self.jugador_y >= SUELO_Y - TAMANO_JUGADOR:
                    if not self.en_suelo:
                        # Aterrizaje - crear partículas SOLO la primera vez
                        x = JUGADOR_X_FIJO + TAMANO_JUGADOR // 2
                        y = SUELO_Y
                        for i in range(4):
                            vx = random.uniform(-2, 2)
                            vy = random.uniform(-3, -1)
                            self.crear_particula(x, y, self.colores["plataforma"], vx, vy, vida=12)
                    
                    # Fijar posición exacta sin oscilar
                    self.jugador_y = SUELO_Y - TAMANO_JUGADOR
                    self.velocidad_y = 0
                    self.en_suelo = True
                    
                    # Salto automático si mantiene presionado (solo ciertos modos)
                    if self.tecla_presionada and not self.modo_config["puede_mantener"]:
                        self.realizar_salto()
                # No resetear en_suelo aquí - se manejará en verificar_colisiones()
            else:
                # Gravedad invertida - techo arriba es el "suelo"
                if self.jugador_y <= LIMITE_SUPERIOR:
                    if not self.en_suelo:
                        # Aterrizaje en techo SOLO la primera vez
                        x = JUGADOR_X_FIJO + TAMANO_JUGADOR // 2
                        y = LIMITE_SUPERIOR
                        for i in range(4):
                            vx = random.uniform(-2, 2)
                            vy = random.uniform(1, 3)
                            self.crear_particula(x, y, self.colores["plataforma"], vx, vy, vida=12)
                    
                    # Fijar posición exacta sin oscilar
                    self.jugador_y = LIMITE_SUPERIOR
                    self.velocidad_y = 0
                    self.en_suelo = True
                    
                    # Salto automático si mantiene presionado
                    if self.tecla_presionada and not self.modo_config["puede_mantener"]:
                        self.realizar_salto()
                # No resetear en_suelo aquí - se manejará en verificar_colisiones()
        
        # Verificación CRÍTICA: Límite superior mortal para TODOS los modos (excepto gravedad invertida en techo)
        if not self.gravedad_invertida:
            # Gravedad normal - si toca el límite superior MUERE
            if self.jugador_y <= LIMITE_SUPERIOR:
                self.morir()
                return
        
        # Mover cámara (desplazar el mundo)
        self.offset_camara += self.velocidad_juego
        
        # Calcular porcentaje
        self.porcentaje = int((self.offset_camara / self.nivel_data["longitud"]) * 100)
        self.porcentaje = min(100, max(0, self.porcentaje))
        
        # Actualizar HUD
        self.canvas.itemconfig(self.texto_porcentaje, text=f"{self.porcentaje}%")
        
        # Actualizar timer
        if self.tiempo_inicio_nivel > 0 and self.juego_activo:
            tiempo_transcurrido = time.time() - self.tiempo_inicio_nivel
            minutos = int(tiempo_transcurrido // 60)
            segundos = int(tiempo_transcurrido % 60)
            self.canvas.itemconfig(self.texto_timer, text=f"{minutos}:{segundos:02d}")
        
        # Actualizar barra de progreso con nuevo diseño
        barra_x = ANCHO_VENTANA // 2 - 200
        barra_ancho = 400
        progreso_ancho = int((barra_ancho - 8) * (self.porcentaje / 100))
        self.canvas.coords(self.barra_progreso,
                          barra_x + 4, 59,
                          barra_x + 4 + progreso_ancho, 76)
        
        # Mover todos los objetos del nivel
        for obj in self.canvas.find_withtag("nivel"):
            self.canvas.move(obj, -self.velocidad_juego, 0)
        
        # Actualizar posición del jugador visualmente
        self.actualizar_jugador_visual()
        
        # PARTICULAS DE SUELO AL CORRER (efecto profesional)
        if self.en_suelo and self.frame_count % 4 == 0:
            # Crear partículas de polvo detrás del jugador
            dust_x = JUGADOR_X_FIJO - 10
            dust_y = SUELO_Y if not self.gravedad_invertida else 10
            for _ in range(2):
                vx = random.uniform(-3, -1)
                vy = random.uniform(-2, 0) if not self.gravedad_invertida else random.uniform(0, 2)
                self.crear_particula(dust_x, dust_y, "#666666", vx, vy, vida=10, con_glow=False)
        
        # Actualizar efectos visuales (optimizado)
        self.actualizar_particulas()
        self.actualizar_pulso_fondo()
        self.actualizar_efectos_visuales()
        
        # Nuevos efectos avanzados
        if self.frame_count % 2 == 0:
            self.actualizar_efecto_velocidad()
        self.actualizar_combo_visual()
        
        # Animar sierras (rotación) - cada 4 frames en lugar de 2
        if self.frame_count % 4 == 0:
            self.animar_sierras()
        
        # Agregar trail cada pocos frames
        if self.frame_count % 3 == 0:
            self.agregar_trail()
        self.actualizar_trail()
        
        # Verificar colisiones e interacciones
        self.verificar_colisiones()
        
        # Verificar logros cada cierto número de frames (optimización)
        if self.frame_count % 60 == 0:  # Cada segundo aprox en 120 FPS
            self.verificar_logros()
        
        # Verificar si completó el nivel
        if self.porcentaje >= 100:
            self.nivel_completado()
            return
        
        # Continuar el loop
        self.ventana.after(int(1000/FPS), self.actualizar)
    
    def actualizar_jugador_visual(self):
        
        x = JUGADOR_X_FIJO
        tam = TAMANO_JUGADOR
        
        # INTERPOLACIÓN DE FÍSICA para movimiento ultra suave en 120 FPS
        if INTERPOLACION_FISICA:
            # Guardar posición anterior si cambió
            if self.jugador_y != self.posicion_anterior_y:
                self.posicion_anterior_y = self.jugador_y_visual if hasattr(self, 'jugador_y_visual') and self.jugador_y_visual else self.jugador_y
            
            # Interpolar entre posición anterior y actual (suavizado exponencial)
            self.interpolacion_t = min(1.0, self.interpolacion_t + 0.25)
            self.jugador_y_visual = self.posicion_anterior_y + (self.jugador_y - self.posicion_anterior_y) * self.interpolacion_t
            
            # Usar posición interpolada para renderizado
            y = self.jugador_y_visual
            
            # Reset interpolación cuando alcanza el destino
            if abs(self.jugador_y_visual - self.jugador_y) < 0.5:
                self.jugador_y_visual = self.jugador_y
                self.posicion_anterior_y = self.jugador_y
                self.interpolacion_t = 0
        else:
            # Sin interpolación (modo clásico)
            y = self.jugador_y
        
        # Actualizar sombra
        self.canvas.coords(self.sombra_jugador, x + 2, y + tam - 2, x + tam - 2, y + tam + 8)
        
        # Rotación simulada del cubo
        if not self.en_suelo:
            if self.gravedad_invertida:
                self.rotacion_cubo -= 6
            else:
                self.rotacion_cubo += 6
        else:
            # En el suelo, alinear a múltiplo de 90 grados
            target = round(self.rotacion_cubo / 90) * 90
            if abs(self.rotacion_cubo - target) > 1:
                self.rotacion_cubo += (target - self.rotacion_cubo) * 0.3
            else:
                self.rotacion_cubo = target
        
        # Cambiar apariencia según la rotación (simulado)
        angulo = int(self.rotacion_cubo % 360)
        
        # Actualizar posiciones base con coordenadas interpoladas
        self.canvas.coords(self.jugador_fondo, x, y, x + tam, y + tam)
        self.canvas.coords(self.jugador_borde, x + 4, y + 4, x + tam - 4, y + tam - 4)
        self.canvas.coords(self.jugador_contorno, x, y, x + tam, y + tam)
        
        # Animar centro para simular rotación
        if 45 <= angulo < 135 or 225 <= angulo < 315:
            # Posición "diagonal"
            self.canvas.coords(self.jugador_centro, x + 8, y + 12, x + tam - 12, y + tam - 8)
        else:
            # Posición "recta"
            self.canvas.coords(self.jugador_centro, x + 10, y + 10, x + tam - 10, y + tam - 10)
        
        # Asegurar que el jugador siempre esté visible encima del nivel
        self.canvas.tag_raise("jugador")
    
    def verificar_colisiones(self):
        """Verifica colisiones con objetos del nivel (OPTIMIZADO con culling)"""
        # Resetear en_suelo solo si el jugador NO está tocando el límite
        # Esto permite saltar en gravedad invertida
        if not self.gravedad_invertida:
            # Gravedad normal: resetear si está por encima del suelo
            if self.jugador_y < SUELO_Y - TAMANO_JUGADOR - 3:
                self.en_suelo = False
        else:
            # Gravedad invertida: resetear si está por debajo del techo
            # CRÍTICO: Solo resetear si está MUY lejos del techo (10px+)
            if self.jugador_y > 10:
                self.en_suelo = False
        
        # Hitbox más ajustado para colisiones más precisas
        hitbox_margen = 0  # Sin margen para colisiones visuales exactas
        j_x1 = JUGADOR_X_FIJO + hitbox_margen
        j_y1 = self.jugador_y + hitbox_margen
        j_x2 = j_x1 + TAMANO_JUGADOR - (hitbox_margen * 2)
        j_y2 = j_y1 + TAMANO_JUGADOR - (hitbox_margen * 2)
        
        for obj_info in self.objetos_nivel:
            obj_data = obj_info["data"]
            obj_visual = obj_info["visual"]
            
            if not obj_visual:
                continue
            
            tipo = obj_data["tipo"]
            
            # Para pinchos, usar el HITBOX (último elemento) no la sombra
            if tipo in ["pincho", "pincho_techo", "pincho_suelo"]:
                # El último elemento es el hitbox real (más pequeño)
                coords = self.canvas.coords(obj_visual[-1])
            else:
                # Para otros objetos, usar el primer elemento visual
                coords = self.canvas.coords(obj_visual[0])
            
            if not coords or len(coords) < 2:
                continue
            
            # Calcular bounding box del objeto
            if len(coords) == 4:  # Rectángulo
                o_x1, o_y1, o_x2, o_y2 = coords
            else:  # Polígono
                o_x1 = min(coords[0::2])
                o_x2 = max(coords[0::2])
                o_y1 = min(coords[1::2])
                o_y2 = max(coords[1::2])
            
            # Verificar overlap básico
            if (j_x1 >= o_x2 or j_x2 <= o_x1 or 
                j_y1 >= o_y2 or j_y2 <= o_y1):
                # No hay colisión
                
                # SISTEMA DE COMBOS POR OBSTÁCULOS SORTEADOS
                # Si el jugador pasó completamente un obstáculo mortal (está a la derecha)
                if tipo in ["pincho", "pincho_techo", "pincho_suelo", "sierra"]:
                    obstaculo_id = f"{tipo}_{obj_data['x']}"
                    
                    # Si el jugador está a la derecha del obstáculo y no lo ha contado
                    if j_x1 > o_x2 and obstaculo_id not in self.obstaculos_sorteados:
                        # Marcar como sorteado
                        self.obstaculos_sorteados.append(obstaculo_id)
                        # Incrementar combo!
                        self.incrementar_combo()
                        # Verificar logros
                        self.verificar_logros()
                        
                        # Mini efecto visual al sortear
                        cx = (o_x1 + o_x2) / 2
                        cy = (o_y1 + o_y2) / 2
                        for _ in range(3):
                            vx = random.uniform(-1, 1)
                            vy = random.uniform(-2, 0)
                            self.crear_particula(cx, cy, "#00ff88", vx, vy, vida=12, con_glow=True)
                
                # Verificar NEAR MISS para bonus extra
                if tipo in ["pincho", "sierra"]:
                    # Calcular distancia al obstáculo
                    dist_x = min(abs(j_x1 - o_x2), abs(j_x2 - o_x1))
                    dist_y = min(abs(j_y1 - o_y2), abs(j_y2 - o_y1))
                    total_dist = (dist_x**2 + dist_y**2)**0.5
                    
                    # Si pasó MUY cerca (menos de 40px) mostrar PERFECT!
                    if total_dist < 40 and dist_x < 30:
                        if not hasattr(self, '_last_near_miss_frame') or self.frame_count - self._last_near_miss_frame > 30:
                            self._last_near_miss_frame = self.frame_count
                            # Mostrar texto "PERFECT!" en la parte inferior
                            perfect_y = ALTO_VENTANA - 120
                            self.mostrar_texto_flotante(ANCHO_VENTANA // 2, perfect_y, "PERFECT!", "#00ffff", 22)
                            # Bonus de combo EXTRA
                            self.incrementar_combo()
                            # Mini explosión de partículas (mantener en obstáculo para feedback visual)
                            cx = (o_x1 + o_x2) / 2
                            cy = (o_y1 + o_y2) / 2
                            for _ in range(3):
                                vx = random.uniform(-2, 2)
                                vy = random.uniform(-2, 2)
                                self.crear_particula(cx, cy, "#00ffff", vx, vy, vida=15, con_glow=True)
                
                continue  # No hay colisión
                
            # HAY COLISIÓN - procesar según tipo
            
            # BLOQUES Y PLATAFORMAS - Colisión sólida
            if tipo in ["bloque", "bloque_techo", "plataforma"]:
                # Calcular superposición en cada eje
                overlap_x = min(j_x2, o_x2) - max(j_x1, o_x1)
                overlap_y = min(j_y2, o_y2) - max(j_y1, o_y1)
                
                # Determinar dirección de colisión
                # Si overlap X es mucho menor que Y, es colisión lateral
                if overlap_x < overlap_y - 5:  # Aumentar margen para evitar muertes en bordes
                    # Colisión lateral - solo matar si el overlap es significativo (no solo rozando borde)
                    if overlap_x > 3:  # Solo matar si penetra más de 3px lateralmente
                        self.morir()
                        return
                    # Si solo roza el borde (<=3px), dejar pasar
                else:
                    # Colisión vertical - verificar dirección
                    if not self.gravedad_invertida:
                        # Gravedad normal - solo aterriza si está cayendo
                        if self.velocidad_y >= 0:  # Cayendo o en suelo
                            # Verificar si el aterrizaje es demasiado brusco (caída muy alta)
                            # Nota: En Geometry Dash original NO mueres por caídas, así que comentamos esto
                            # if self.velocidad_y > 25:  # Velocidad muy alta
                            #     self.morir()
                            #     return
                            # Aterrizando desde arriba - ajustar posición EXACTA
                            nueva_y = o_y1 - TAMANO_JUGADOR
                            # SIEMPRE ajustar si hay overlap vertical
                            self.jugador_y = nueva_y
                            self.velocidad_y = 0
                            self.en_suelo = True
                            
                            # Partículas al aterrizar
                            if random.random() < 0.15:
                                for _ in range(2):
                                    self.crear_particula(
                                        JUGADOR_X_FIJO + random.randint(5, TAMANO_JUGADOR-5),
                                        self.jugador_y + TAMANO_JUGADOR,
                                        self.colores["plataforma"],
                                        random.uniform(-1, 1), random.uniform(-2, -1)
                                    )
                        else:
                            # Subiendo y golpea algo = muerte
                            self.morir()
                            return
                    else:
                        # Gravedad invertida - solo aterriza si está "cayendo" hacia arriba
                        # En gravedad invertida: velocidad_y > 0 = cayendo hacia techo (válido)
                        #                        velocidad_y < 0 = subiendo desde techo (choque)
                        if self.velocidad_y > 0:  # Cayendo hacia el techo (aterrizaje válido)
                            # Aterrizando en el techo/bloque - ajustar posición EXACTA
                            nueva_y = o_y2  # Posicionar debajo del bloque (pegado al techo del bloque)
                            self.jugador_y = nueva_y
                            self.velocidad_y = 0
                            self.en_suelo = True
                            
                            # Partículas al aterrizar en techo
                            if random.random() < 0.15:
                                for _ in range(2):
                                    self.crear_particula(
                                        JUGADOR_X_FIJO + random.randint(5, TAMANO_JUGADOR-5),
                                        self.jugador_y,  # En la parte superior del jugador
                                        self.colores["plataforma"],
                                        random.uniform(-1, 1), random.uniform(1, 2)  # Partículas hacia abajo
                                    )
                        else:
                            # Subiendo desde el techo y golpea algo por debajo = muerte
                            self.morir()
                            return
            
            # OBSTÁCULOS MORTALES
            elif tipo in ["pincho", "pincho_techo", "pincho_suelo", "sierra"]:
                self.morir()
                return
            
            elif tipo == "moneda":
                # Recoger moneda
                moneda_id = obj_data.get("id")
                if moneda_id not in self.monedas_recolectadas:
                    self.monedas_recolectadas.append(moneda_id)
                    self.canvas.itemconfig(self.texto_monedas,
                                         text=f"⬢ {len(self.monedas_recolectadas)}/3")
                    
                    # Reproducir sonido de moneda
                    self.reproducir_sonido("moneda")
                    
                    # Efecto visual de recolección
                    if len(coords) >= 4:
                        cx = (o_x1 + o_x2) / 2
                        cy = (o_y1 + o_y2) / 2
                        self.crear_explosion_particulas(cx, cy, self.colores["moneda"], cantidad=8)
                    
                    # Eliminar moneda
                    for vid in obj_visual:
                        self.canvas.delete(vid)
                    obj_info["visual"] = None
                    print(f"Moneda {moneda_id} recolectada!")
            
            elif tipo == "orbe_amarillo":
                # Salto extra al tocar
                if obj_data["x"] not in self.objetos_interactuados:
                    self.objetos_interactuados.append(obj_data["x"])
                    if self.gravedad_invertida:
                        self.velocidad_y = abs(FUERZA_SALTO) * 0.8
                    else:
                        self.velocidad_y = FUERZA_SALTO * 0.8
                    self.en_suelo = False
                    
                    # Partículas de orbe
                    if len(coords) >= 4:
                        cx = (o_x1 + o_x2) / 2
                        cy = (o_y1 + o_y2) / 2
                        for i in range(6):
                            angle = (360 / 6) * i
                            vx = math.cos(math.radians(angle)) * 3
                            vy = math.sin(math.radians(angle)) * 3
                            self.crear_particula(cx, cy, "#ffea00", vx, vy, vida=20)
            
            elif tipo == "orbe_rosa":
                # Salto grande al tocar
                if obj_data["x"] not in self.objetos_interactuados:
                    self.objetos_interactuados.append(obj_data["x"])
                    if self.gravedad_invertida:
                        self.velocidad_y = abs(FUERZA_SALTO) * 1.5
                    else:
                        self.velocidad_y = FUERZA_SALTO * 1.5
                    self.en_suelo = False
                    
                    # Partículas de orbe rosa
                    if len(coords) >= 4:
                        cx = (o_x1 + o_x2) / 2
                        cy = (o_y1 + o_y2) / 2
                        for i in range(8):
                            angle = (360 / 8) * i
                            vx = math.cos(math.radians(angle)) * 4
                            vy = math.sin(math.radians(angle)) * 4
                            self.crear_particula(cx, cy, "#ff1493", vx, vy, vida=25)
            
            elif tipo == "portal_velocidad":
                # Cambiar velocidad
                if obj_data["x"] not in self.objetos_interactuados:
                    self.objetos_interactuados.append(obj_data["x"])
                    nueva_vel = obj_data.get("velocidad", "x1")
                    self.velocidad_juego = VELOCIDADES[nueva_vel]
                    print(f"Velocidad cambiada a {nueva_vel}")
                    
                    # Actualizar indicador de velocidad en HUD
                    self.canvas.itemconfig(self.texto_velocidad, text=nueva_vel)
                    
                    # Efecto visual de cambio de velocidad
                    if len(coords) >= 4:
                        cx = (o_x1 + o_x2) / 2
                        cy = (o_y1 + o_y2) / 2
                        self.crear_explosion_particulas(cx, cy, self.colores["plataforma"], cantidad=12)
            
            elif tipo == "portal_gravedad":
                # Invertir gravedad SOLO UNA VEZ
                if obj_data["x"] not in self.objetos_interactuados:
                    self.objetos_interactuados.append(obj_data["x"])
                    self.gravedad_invertida = not self.gravedad_invertida
                    self.velocidad_y = 0  # Resetear velocidad completamente
                    self.en_suelo = False  # Forzar recalcular suelo
                    
                    # Ajustar posición del jugador según el tipo de gravedad
                    if self.gravedad_invertida:
                        # Al invertir: colocar jugador cerca del techo (pero DEBAJO del límite)
                        self.jugador_y = LIMITE_SUPERIOR + 10  # Posición segura justo debajo del límite
                    else:
                        # Al volver a normal: colocar jugador cerca del suelo
                        self.jugador_y = SUELO_Y - TAMANO_JUGADOR - 100
                    
                    print(f"Gravedad {'INVERTIDA' if self.gravedad_invertida else 'NORMAL'}")
                    
                    # Efecto visual espiral de gravedad
                    if len(coords) >= 4:
                        cx = (o_x1 + o_x2) / 2
                        cy = (o_y1 + o_y2) / 2
                        for i in range(16):
                            angle = (360 / 16) * i
                            vx = math.cos(math.radians(angle)) * 5
                            vy = math.sin(math.radians(angle)) * 5
                            self.crear_particula(cx, cy, "#ff00ff", vx, vy, vida=30)
            
            # PORTALES DE MODO
            elif tipo in ["portal_cube", "portal_ship", "portal_ball", "portal_ufo", "portal_wave", "portal_robot"]:
                if obj_data["x"] not in self.objetos_interactuados:
                    self.objetos_interactuados.append(obj_data["x"])
                    nuevo_modo = tipo.replace("portal_", "")
                    self.cambiar_modo(nuevo_modo)
                    
                    # Efecto visual de cambio de modo
                    if len(coords) >= 4:
                        cx = (o_x1 + o_x2) / 2
                        cy = (o_y1 + o_y2) / 2
                        self.crear_explosion_particulas(cx, cy, self.colores["player"], cantidad=15)
            
            # CHECKPOINT
            elif tipo == "checkpoint":
                # Los checkpoints SOLO funcionan en modo práctica
                if self.modo_practica:
                    checkpoint_pos = obj_data["x"]
                    # Guardar checkpoint cuando lo atravesamos
                    if checkpoint_pos not in self.objetos_interactuados:
                        self.objetos_interactuados.append(checkpoint_pos)
                        self.guardar_checkpoint(checkpoint_pos)
                        
                        # Efecto visual de checkpoint activado
                        if len(coords) >= 4:
                            cx = (o_x1 + o_x2) / 2
                            cy = (o_y1 + o_y2) / 2
                            for i in range(12):
                                    angle = (360 / 12) * i
                                    vx = math.cos(math.radians(angle)) * 3
                                    vy = math.sin(math.radians(angle)) * 3
                                    self.crear_particula(cx, cy, "#00ff00", vx, vy, vida=20)
                            
                            print(f"Checkpoint guardado en {int((checkpoint_pos/self.nivel_data['longitud'])*100)}%")
            
            elif tipo == "end":
                # Fin del nivel
                self.nivel_completado()
                return
        
        # SALTO AUTOMÁTICO: Si mantiene click y acaba de aterrizar
        if self.en_suelo and not self.ultimo_en_suelo and self.tecla_presionada:
            if self.modo_actual == "cube":
                self.realizar_salto()
        
        # Actualizar estado anterior
        self.ultimo_en_suelo = self.en_suelo
    
    def morir(self):
        """Maneja la muerte del jugador - VERSIÓN CINEMÁTICA"""
        self.juego_activo = False
        
        # Resetear combo y lista de obstáculos sorteados
        self.resetear_combo()
        self.obstaculos_sorteados.clear()  # Limpiar obstáculos al morir
        
        # Detener música (se reiniciará al respawnear/reiniciar)
        self.detener_musica()
        
        # Coordenadas del jugador
        x = JUGADOR_X_FIJO + TAMANO_JUGADOR // 2
        y = self.jugador_y + TAMANO_JUGADOR // 2
        
        # EXPLOSION MASIVA DE PARTICULAS
        # Múltiples explosiones superpuestas para efecto épico
        for i in range(5):
            offset = i * 2
            self.crear_explosion_particulas(x + offset, y + offset, self.colores["player"], cantidad=12)
        
        # Añadir partículas adicionales con diferentes velocidades
        for _ in range(20):
            angulo = random.uniform(0, 360)
            velocidad = random.uniform(5, 12)
            vx = math.cos(math.radians(angulo)) * velocidad
            vy = math.sin(math.radians(angulo)) * velocidad
            color = random.choice([self.colores["player"], "#ffffff", "#ffaa00"])
            self.crear_particula(x, y, color, vx, vy, vida=30, con_glow=True)
        
        # SONIDOS EPICOS
        self.reproducir_sonido("explosion")
        self.ventana.after(100, lambda: self.reproducir_sonido("muerte"))
        
        # EFECTOS VISUALES INTENSOS
        self.screen_shake(30)  # Shake masivo
        self.flash_color = "#ff0000"  # Flash rojo de muerte
        self.flash_screen(1.2)  # Flash largo
        
        # ZOOM IN DRAMATICO en la muerte
        if EFECTOS_VISUALES["camera_zoom"]:
            self.camera_zoom_target = 1.15  # Zoom in dramático
        
        # SLOW-MOTION EFFECT (simulado con delay entre frames)
        if hasattr(self, 'update_velocidad'):
            old_velocidad = self.update_velocidad
            self.update_velocidad = 32  # Más lento (era ~16)
            self.ventana.after(600, lambda: setattr(self, 'update_velocidad', old_velocidad))
        
        # Actualizar estadísticas
        self.estadisticas["muertes_totales"] += 1
        
        # Verificar logros (primera muerte, etc)
        self.verificar_logros()
        
        # En modo práctica, respawn en el último checkpoint
        if self.modo_practica and self.checkpoint_actual:
            self.intentos += 1
            self.total_intentos[self.nivel_actual] = self.total_intentos.get(self.nivel_actual, 0) + 1
            print(f"Muerte EPICA en {self.porcentaje}% - Respawn en checkpoint")
            
            # Efecto de muerte en jugador
            self.canvas.itemconfig(self.jugador_fondo, fill="#ff0000")
            self.canvas.itemconfig(self.jugador_borde, fill="#ff0000")
            
            # Respawn en el checkpoint después del espectáculo
            self.ventana.after(800, self.respawn_checkpoint)
        else:
            # Modo normal: reiniciar nivel completo
            self.intentos += 1
            self.total_intentos[self.nivel_actual] = self.total_intentos.get(self.nivel_actual, 0) + 1
            print(f"Muerte EPICA en {self.porcentaje}% - Intento #{self.intentos}")
            
            # Efecto de muerte - cambiar color temporalmente
            self.canvas.itemconfig(self.jugador_fondo, fill="#ff0000")
            self.canvas.itemconfig(self.jugador_borde, fill="#ff0000")
            
            # Limpiar partículas y trails después del espectáculo (no inmediatamente)
            def limpiar_efectos():
                self.canvas.delete("particula")
                self.canvas.delete("trail")
                self.particulas.clear()
                self.trail_cubo.clear()
            
            self.ventana.after(600, limpiar_efectos)
            
            # Reiniciar después del espectáculo completo
            self.ventana.after(1000, self.reiniciar_nivel)
    
    def cambiar_modo(self, nuevo_modo):
        """Cambia el modo de juego del jugador"""
        if nuevo_modo not in MODOS_JUEGO:
            return
        
        self.modo_actual = nuevo_modo
        self.modo_config = MODOS_JUEGO[nuevo_modo].copy()
        
        # Resetear velocidad al cambiar de modo
        self.velocidad_y = 0
        self.velocidad_wave = 0
        
        # Si no está en el suelo, ajustar la física
        if not self.en_suelo:
            if nuevo_modo == "wave":
                self.velocidad_wave = 0
            elif nuevo_modo == "ship":
                self.velocidad_y = 0
        
        print(f"Modo cambiado a: {MODOS_JUEGO[nuevo_modo]['nombre']}")
    
    def toggle_modo_practica(self):
        """Activa/desactiva el modo práctica"""
        if not hasattr(self, 'juego_activo') or self.en_menu:
            return
        
        self.modo_practica = not self.modo_practica
        
        if self.modo_practica:
            print("MODO PRACTICA ACTIVADO")
            print("   • Los checkpoints se guardan automáticamente")
            print("   • Respawn en el último checkpoint al morir")
            print("   • ¡No cuenta para desbloquear niveles!")
            # Cambiar color de los checkpoints a verde brillante
            for checkpoint_id in self.checkpoint_ids:
                try:
                    self.canvas.itemconfig(checkpoint_id, fill="#00ff00")
                except:
                    pass
            # Actualizar indicador en HUD
            self.canvas.itemconfig(self.texto_modo_practica, text="MODO PRACTICA ACTIVO")
        else:
            print("MODO NORMAL ACTIVADO")
            print("   • Sin checkpoints")
            print("   • Reinicia desde el inicio al morir")
            # Restaurar color original de checkpoints
            for checkpoint_id in self.checkpoint_ids:
                try:
                    self.canvas.itemconfig(checkpoint_id, fill="#00ff88")
                except:
                    pass
            # Limpiar checkpoints guardados
            self.checkpoint_actual = None
            # Actualizar indicador en HUD
            self.canvas.itemconfig(self.texto_modo_practica, text="")
    
    def colocar_checkpoint_manual(self):
        """Coloca un checkpoint en la posición actual del jugador"""
        if not self.modo_practica or not self.juego_activo or self.en_menu:
            return
        
        # Posición actual en el mundo
        pos_x = self.offset_camara + JUGADOR_X_FIJO
        
        # Verificar que no haya otro checkpoint muy cerca (al menos 300px)
        for checkpoint in self.checkpoints:
            if abs(checkpoint - pos_x) < 300:
                print("Ya hay un checkpoint cerca. Muevete mas adelante.")
                return
        
        # Agregar checkpoint
        self.checkpoints.append(pos_x)
        self.checkpoints.sort()
        
        # Crear visual del checkpoint
        self.crear_checkpoint_visual(pos_x)
        
        # Guardar estado en este checkpoint
        self.guardar_checkpoint(pos_x)
        
        # Feedback visual
        x_pantalla = pos_x - self.offset_camara
        self.crear_explosion_particulas(x_pantalla, SUELO_Y - 60, "#00ff00", cantidad=12)
        
        print(f"Checkpoint colocado en {int((pos_x/self.nivel_data['longitud'])*100)}%")
    
    def eliminar_checkpoint_cercano(self):
        """Elimina el checkpoint más cercano al jugador"""
        if not self.modo_practica or not self.juego_activo or self.en_menu:
            return
        
        # Posición actual del jugador
        pos_x = self.offset_camara + JUGADOR_X_FIJO
        
        # Buscar el checkpoint más cercano
        checkpoint_cercano = None
        distancia_minima = 400  # Rango máximo para eliminar (400px)
        
        for checkpoint in self.checkpoints:
            distancia = abs(checkpoint - pos_x)
            if distancia < distancia_minima:
                distancia_minima = distancia
                checkpoint_cercano = checkpoint
        
        if checkpoint_cercano is None:
            print("No hay ningun checkpoint cerca para eliminar")
            return
        
        # Eliminar el checkpoint de la lista
        self.checkpoints.remove(checkpoint_cercano)
        
        # Eliminar del nivel_data
        self.nivel_data["objetos"] = [obj for obj in self.nivel_data["objetos"] 
                                       if not (obj["tipo"] == "checkpoint" and obj["x"] == checkpoint_cercano)]
        
        # Si era el checkpoint actual, limpiarlo
        if self.checkpoint_actual and self.checkpoint_actual.get("x_checkpoint") == checkpoint_cercano:
            self.checkpoint_actual = None
            print("El checkpoint activo fue eliminado")
        
        # Eliminar visualmente: encontrar y borrar los objetos del checkpoint
        objetos_a_eliminar = []
        for obj_id in self.canvas.find_withtag("nivel"):
            # Obtener las coordenadas del objeto
            coords = self.canvas.coords(obj_id)
            if coords:
                x_objeto = coords[0] + self.offset_camara
                # Si el objeto está en la posición del checkpoint, marcarlo para eliminar
                if abs(x_objeto - checkpoint_cercano) < 50:
                    tipo = self.canvas.type(obj_id)
                    # Verificar que sea parte de un checkpoint (rectángulo, polígono o texto)
                    if tipo in ["rectangle", "polygon", "text"]:
                        objetos_a_eliminar.append(obj_id)
        
        # Eliminar los objetos visuales
        for obj_id in objetos_a_eliminar:
            self.canvas.delete(obj_id)
            if obj_id in self.checkpoint_ids:
                self.checkpoint_ids.remove(obj_id)
        
        # Feedback visual
        x_pantalla = checkpoint_cercano - self.offset_camara
        self.crear_explosion_particulas(x_pantalla, SUELO_Y - 60, "#ff0000", cantidad=10)
        
        porcentaje = int((checkpoint_cercano/self.nivel_data['longitud'])*100)
        print(f"Checkpoint eliminado ({porcentaje}%)")
    
    def crear_checkpoint_visual(self, pos_x):
        """Crea el elemento visual de un checkpoint y lo registra en el nivel"""
        # Agregar checkpoint a los objetos del nivel para que se renderice correctamente
        checkpoint_obj = {
            "tipo": "checkpoint",
            "x": pos_x
        }
        self.nivel_data["objetos"].append(checkpoint_obj)
        
        # Crear el visual inmediatamente si está en pantalla
        x_pantalla = pos_x - self.offset_camara
        if -100 <= x_pantalla <= ANCHO_VENTANA + 100:
            # Poste
            color_poste = "#00ff00" if self.modo_practica else "#888888"
            poste = self.canvas.create_rectangle(
                x_pantalla + 25, SUELO_Y - 80, x_pantalla + 35, SUELO_Y,
                fill=color_poste, outline="#ffffff", width=2, tags="nivel")
            
            # Bandera
            color_bandera = "#00dd00" if self.modo_practica else "#00ff88"
            bandera = self.canvas.create_polygon(
                x_pantalla + 35, SUELO_Y - 75,
                x_pantalla + 65, SUELO_Y - 60,
                x_pantalla + 35, SUELO_Y - 45,
                fill=color_bandera, outline="#ffffff", width=2, tags="nivel")
            
            # Texto
            texto = self.canvas.create_text(
                x_pantalla + 30, SUELO_Y - 90,
                text="OK",
                fill="#00ff00" if self.modo_practica else "#00ff88", 
                font=("Arial", 20, "bold"), tags="nivel")
            
            self.checkpoint_ids.extend([poste, bandera, texto])
    
    def guardar_checkpoint(self, x_checkpoint):
        """Guarda un checkpoint con el estado actual del juego"""
        checkpoint_data = {
            "offset_camara": self.offset_camara,
            "jugador_y": self.jugador_y,
            "velocidad_y": self.velocidad_y,
            "modo_actual": self.modo_actual,
            "gravedad_invertida": self.gravedad_invertida,
            "velocidad_juego": self.velocidad_juego,
            "monedas_recolectadas": self.monedas_recolectadas.copy(),
            "objetos_interactuados": self.objetos_interactuados.copy(),
            "porcentaje": self.porcentaje,
            "x_checkpoint": x_checkpoint
        }
        self.checkpoint_actual = checkpoint_data
        porcentaje_checkpoint = int((x_checkpoint/self.nivel_data['longitud'])*100)
        print(f"Checkpoint guardado en {porcentaje_checkpoint}%")
        
        # Reproducir sonido de checkpoint
        self.reproducir_sonido("checkpoint")
    
    def respawn_checkpoint(self):
        """Respawnea al jugador en el último checkpoint"""
        if not self.checkpoint_actual:
            self.reiniciar_nivel()
            return
        
        # SOLO limpiar objetos del nivel, NO el jugador ni HUD
        self.canvas.delete("nivel")
        self.canvas.delete("particula")
        self.canvas.delete("trail")
        self.canvas.delete("efecto_vel")
        
        # Restaurar estado del checkpoint
        self.offset_camara = self.checkpoint_actual["offset_camara"]
        self.jugador_y = self.checkpoint_actual["jugador_y"]
        self.velocidad_y = self.checkpoint_actual["velocidad_y"]
        self.modo_actual = self.checkpoint_actual["modo_actual"]
        self.modo_config = MODOS_JUEGO[self.modo_actual].copy()
        self.gravedad_invertida = self.checkpoint_actual["gravedad_invertida"]
        self.velocidad_juego = self.checkpoint_actual["velocidad_juego"]
        self.monedas_recolectadas = self.checkpoint_actual["monedas_recolectadas"].copy()
        self.objetos_interactuados = self.checkpoint_actual["objetos_interactuados"].copy()
        self.porcentaje = self.checkpoint_actual["porcentaje"]
        
        # Resetear variables de control
        self.tecla_presionada = False
        self.en_suelo = False
        self.tocando_suelo = False
        self.tocando_techo = False
        self.velocidad_wave = 0
        
        # Limpiar arrays de efectos
        self.particulas = []
        self.trail_cubo = []
        self.efecto_velocidad = []
        
        # Recrear SOLO los objetos del nivel usando la función crear_objeto
        self.objetos_nivel = []
        for obj_data in self.nivel_data["objetos"]:
            obj = self.crear_objeto(obj_data)
            if obj:
                self.objetos_nivel.append({"data": obj_data, "visual": obj})
        
        # Restaurar color del jugador (por si estaba rojo)
        self.canvas.itemconfig(self.jugador_fondo, fill=self.colores["player"])
        self.canvas.itemconfig(self.jugador_borde, fill=self.colores["player"])
        if hasattr(self, 'jugador_centro'):
            self.canvas.itemconfig(self.jugador_centro, fill=self.colores["player"])
        
        # Actualizar HUD con valores restaurados
        self.canvas.itemconfig(self.texto_porcentaje, text=f"{self.porcentaje}%")
        self.canvas.itemconfig(self.texto_intentos, text=f"#{self.intentos}")
        self.canvas.itemconfig(self.texto_monedas, text=f"⬢ {len(self.monedas_recolectadas)}/3")
        self.canvas.itemconfig(self.texto_velocidad, text=self.velocidad_juego)
        
        # Reposicionar jugador visualmente
        self.actualizar_jugador_visual()
        
        # Reactivar el juego
        self.juego_activo = True
        
        # Reiniciar música del nivel
        self.iniciar_musica_nivel(self.nivel_actual)
        
        print(f"Respawn en checkpoint ({self.porcentaje}%)")
        
        # Reiniciar el loop de actualización
        self.actualizar()
    
    def reiniciar_nivel(self):
        """Reinicia el nivel actual"""
        if not self.en_menu:
            print("\nReiniciando nivel...\n")
            # Limpiar obstáculos sorteados al reiniciar
            self.obstaculos_sorteados.clear()
            # Preservar el modo práctica actual
            modo_actual = self.modo_practica
            self.iniciar_nivel(self.nivel_actual, modo_actual)
    
    def nivel_completado(self):
        """Maneja la completación del nivel con efectos CINEMÁTICOS"""
        self.juego_activo = False
        
        # Detener música del nivel
        self.detener_musica()
        
        # ZOOM OUT CINEMATICO
        if EFECTOS_VISUALES["camera_zoom"]:
            self.camera_zoom_target = 0.85  # Zoom out suave
        
        # Reproducir sonido de victoria
        self.reproducir_sonido("victoria")
        
        # EXPLOSION MASIVA DE CELEBRACION
        x = JUGADOR_X_FIJO + TAMANO_JUGADOR // 2
        y = self.jugador_y + TAMANO_JUGADOR // 2
        for i in range(8):
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            self.crear_explosion_particulas(x + offset_x, y + offset_y, 
                                          random.choice(["#ffaa00", "#00ff88", "#ff00ff"]), 
                                          cantidad=15)
        
        # Efectos visuales: flash brillante dorado
        self.flash_color = "#ffaa00"  # Flash dorado de victoria
        self.flash_screen(1.2)
        self.screen_shake(20)
        
        # Actualizar estadísticas
        self.estadisticas["niveles_completados"] += 1
        
        # Verificar logros
        if self.intentos == 1:  # Nivel sin morir
            self.desbloquear_logro("perfeccionista")
        if len(self.monedas_recolectadas) == 3:
            self.desbloquear_logro("coleccionista")
        if self.estadisticas["niveles_completados"] == 1:
            self.desbloquear_logro("primera_victoria")
        
        # Calcular y guardar tiempo del nivel
        if self.tiempo_inicio_nivel > 0:
            tiempo_nivel = time.time() - self.tiempo_inicio_nivel
            if tiempo_nivel < self.mejor_tiempo.get(self.nivel_actual, float('inf')):
                self.mejor_tiempo[self.nivel_actual] = tiempo_nivel
                print(f"Nuevo mejor tiempo: {tiempo_nivel:.2f}s!")
                # Logro speedrunner si es un tiempo increíble (< 30s)
                if tiempo_nivel < 30:
                    self.desbloquear_logro("speedrunner")
        
        # NO desbloquear niveles si estamos probando desde el editor
        if not self.probando_nivel_editor:
            print(f"\nNIVEL {self.nivel_actual} COMPLETADO EPICAMENTE!")
            print(f"Intentos: {self.intentos}")
            print(f"Monedas: {len(self.monedas_recolectadas)}/3\n")
            
            # Desbloquear siguiente nivel
            if self.nivel_actual < 3 and self.niveles_desbloqueados <= self.nivel_actual:
                self.niveles_desbloqueados = self.nivel_actual + 1
                print(f"Nivel {self.niveles_desbloqueados} desbloqueado!\n")
        else:
            print(f"\nNivel de prueba completado!")
        
        # Mostrar pantalla de victoria
        self.mostrar_pantalla_victoria()
    
    def mostrar_pantalla_victoria(self):
        """Muestra la pantalla de nivel completado con efectos"""
        # Celebración con partículas
        for _ in range(30):
            x = random.randint(100, ANCHO_VENTANA - 100)
            y = random.randint(50, SUELO_Y)
            color = random.choice([self.colores["player"], self.colores["moneda"], 
                                  self.colores["plataforma"], "#ffffff"])
            vx = random.uniform(-3, 3)
            vy = random.uniform(-8, -3)
            self.crear_particula(x, y, color, vx, vy, vida=60)
        
        # Oscurecer pantalla
        self.canvas.create_rectangle(0, 0, ANCHO_VENTANA, ALTO_VENTANA,
                                     fill="#000000", stipple="gray50", tags="victoria")
        
        # Panel con efecto de brillo
        panel_w, panel_h = 600, 400
        panel_x = (ANCHO_VENTANA - panel_w) // 2
        panel_y = (ALTO_VENTANA - panel_h) // 2
        
        # Sombra del panel
        self.canvas.create_rectangle(panel_x + 8, panel_y + 8, 
                                     panel_x + panel_w + 8, panel_y + panel_h + 8,
                                     fill="#000000", outline="", tags="victoria")
        
        # Panel principal
        self.canvas.create_rectangle(panel_x, panel_y, panel_x + panel_w, panel_y + panel_h,
                                     fill="#0d1117", outline="", tags="victoria")
        
        # Borde neón triple
        self.canvas.create_rectangle(panel_x, panel_y, panel_x + panel_w, panel_y + panel_h,
                                     fill="", outline=self.colores["player"], width=6, tags="victoria")
        self.canvas.create_rectangle(panel_x + 5, panel_y + 5, 
                                     panel_x + panel_w - 5, panel_y + panel_h - 5,
                                     fill="", outline=self.colores["plataforma"], width=3, tags="victoria")
        self.canvas.create_rectangle(panel_x + 10, panel_y + 10, 
                                     panel_x + panel_w - 10, panel_y + panel_h - 10,
                                     fill="", outline="#ffffff", width=1, tags="victoria")
        
        # Título con sombra
        self.canvas.create_text(ANCHO_VENTANA // 2 + 3, panel_y + 63,
                               text="¡NIVEL COMPLETADO!",
                               fill="#000000", font=("Arial", 36, "bold"), tags="victoria")
        self.canvas.create_text(ANCHO_VENTANA // 2, panel_y + 60,
                               text="¡NIVEL COMPLETADO!",
                               fill=self.colores["player"], font=("Arial", 36, "bold"),
                               tags="victoria")
        
        # Línea decorativa
        self.canvas.create_line(panel_x + 80, panel_y + 110,
                               panel_x + panel_w - 80, panel_y + 110,
                               fill=self.colores["plataforma"], width=3, tags="victoria")
        
        # Estadísticas detalladas
        y = panel_y + 160
        self.canvas.create_text(ANCHO_VENTANA // 2, y,
                               text=f"Intentos: {self.intentos}",
                               fill="#ffffff", font=("Arial", 22), tags="victoria")
        
        # Estrellas según intentos (menos intentos = más estrellas)
        estrellas = 3 if self.intentos <= 10 else (2 if self.intentos <= 25 else 1)
        estrellas_texto = "*" * estrellas + "o" * (3 - estrellas)
        self.canvas.create_text(ANCHO_VENTANA // 2, y + 40,
                               text=estrellas_texto,
                               fill="#ffea00", font=("Arial", 28), tags="victoria")
        
        # Monedas
        monedas_texto = "$" * len(self.monedas_recolectadas) + "o" * (3 - len(self.monedas_recolectadas))
        self.canvas.create_text(ANCHO_VENTANA // 2, y + 80,
                               text=monedas_texto,
                               fill=self.colores["moneda"], font=("Arial", 28), tags="victoria")
        
        self.canvas.create_text(ANCHO_VENTANA // 2, y + 115,
                               text=f"Monedas: {len(self.monedas_recolectadas)}/3",
                               fill="#ffffff", font=("Arial", 16), tags="victoria")
        
        # Mensaje especial si recogió todas las monedas
        if len(self.monedas_recolectadas) == 3:
            self.canvas.create_text(ANCHO_VENTANA // 2, y + 145,
                                   text="¡TODAS LAS MONEDAS!",
                                   fill=self.colores["moneda"], 
                                   font=("Arial", 18, "bold"), tags="victoria")
        
        # Botones mejorados
        btn_y = panel_y + panel_h - 80
        
        # Botón reiniciar
        self.canvas.create_rectangle(panel_x + 60, btn_y, panel_x + 260, btn_y + 55,
                                     fill=self.colores["plataforma"], 
                                     outline="#ffffff", width=3,
                                     tags=["victoria", "btn_reiniciar"])
        self.canvas.create_text(panel_x + 160, btn_y + 27,
                               text="↻ REINTENTAR",
                               fill="#000000", font=("Arial", 18, "bold"),
                               tags=["victoria", "btn_reiniciar"])
        
        # Botón menú (cambia texto si estamos probando desde editor)
        texto_boton = "⟲ EDITOR" if self.probando_nivel_editor else "⌂ MENÚ"
        self.canvas.create_rectangle(panel_x + 340, btn_y, panel_x + 540, btn_y + 55,
                                     fill=self.colores["player"], 
                                     outline="#ffffff", width=3,
                                     tags=["victoria", "btn_menu"])
        self.canvas.create_text(panel_x + 440, btn_y + 27,
                               text=texto_boton,
                               fill="#000000", font=("Arial", 18, "bold"),
                               tags=["victoria", "btn_menu"])
        
        self.canvas.tag_bind("btn_reiniciar", "<Button-1>",
                            lambda e: self.reiniciar_nivel())
        self.canvas.tag_bind("btn_menu", "<Button-1>",
                            lambda e: self.volver_menu())
    
    def volver_menu(self):
        """Vuelve al menú de selección o al editor"""
        # DETENER EL JUEGO COMPLETAMENTE
        self.juego_activo = False
        self.en_menu = True
        
        # Detener música del nivel
        self.detener_musica()
        
        self.canvas.delete("all")
        
        # Si estábamos probando un nivel del editor, volver al editor
        if self.probando_nivel_editor:
            self.probando_nivel_editor = False
            self.en_editor = True
            self.crear_interfaz_editor()
            self.dibujar_editor()
        else:
            # Sino, volver al menú normal
            self.en_editor = False
            self.mostrar_menu_seleccion()
    
    # ==================== EDITOR DE NIVELES ====================
    
    def abrir_editor(self):
        """Abre el editor de niveles"""
        self.en_editor = True
        self.en_menu = False
        self.editor_objetos = []
        self.editor_scroll_x = 0
        self.editor_tipo_actual = "bloque"
        self.editor_altura_actual = 1
        
        self.crear_interfaz_editor()
        self.dibujar_editor()
    
    def menu_editar_niveles(self):
        """Muestra menú para seleccionar qué nivel editar"""
        print("\n" + "="*60)
        print("  EDITAR NIVELES PRINCIPALES")
        print("="*60)
        print("\nSelecciona el nivel que quieres editar:")
        print("  [1] CUBE BASICS")
        print("  [2] SHIP FLIGHT")
        print("  [3] GRAVITY FLIP")
        print("  [4] THE GAUNTLET")
    
        print("\nInstrucciones:")
        print("   • Se abrirá el editor con los objetos del nivel")
        print("   • Edita lo que necesites (agregar/quitar objetos)")
        print("   • Presiona [G] para guardar")
        print("   • Copia el código que aparece en la terminal")
      
        print("="*60)
        
        # Agregar bindings temporales para seleccionar nivel
        def cargar_nivel_en_editor(num):
            niveles = [crear_nivel_1(), crear_nivel_2(), crear_nivel_3(), crear_nivel_4()]
            nivel_seleccionado = niveles[num - 1]
            
            self.en_editor = True
            self.en_menu = False
            self.editor_objetos = nivel_seleccionado["objetos"].copy()
            self.editor_scroll_x = 0
            self.editor_tipo_actual = "bloque"
            self.editor_altura_actual = 1
            
            print(f"\nNivel {num} cargado en el editor")
            print(f"{len(self.editor_objetos)} objetos cargados")
            print("Edita libremente y presiona [G] para guardar\n")
            
            self.crear_interfaz_editor()
            self.dibujar_editor()
        
        self.canvas.bind("1", lambda e: cargar_nivel_en_editor(1))
        self.canvas.bind("2", lambda e: cargar_nivel_en_editor(2))
        self.canvas.bind("3", lambda e: cargar_nivel_en_editor(3))
        self.canvas.bind("4", lambda e: cargar_nivel_en_editor(4))
    
    def crear_interfaz_editor(self):
        """Crea la interfaz del editor"""
        self.canvas.delete("all")
        
        # Fondo
        for i in range(ALTO_VENTANA):
            intensidad = int(10 + (i / ALTO_VENTANA) * 30)
            color = f"#{intensidad:02x}{intensidad:02x}{min(intensidad + 15, 40):02x}"
            self.canvas.create_line(0, i, ANCHO_VENTANA, i, fill=color, tags="fondo_editor")
        
        # Línea del suelo
        self.canvas.create_line(0, SUELO_Y, ANCHO_VENTANA, SUELO_Y,
                               fill="#ffffff", width=2, tags="editor_ui")
        
        # Grid
        for x in range(0, ANCHO_VENTANA, self.editor_grid_size):
            self.canvas.create_line(x, 0, x, ALTO_VENTANA,
                                   fill="#ffffff", width=1, stipple="gray25", tags="editor_grid")
        for y in range(0, ALTO_VENTANA, self.editor_grid_size):
            self.canvas.create_line(0, y, ANCHO_VENTANA, y,
                                   fill="#ffffff", width=1, stipple="gray25", tags="editor_grid")
        
        # Panel superior
        self.canvas.create_rectangle(0, 0, ANCHO_VENTANA, 80,
                                     fill="#1a1a2e", outline="#ffaa00", width=2, tags="editor_ui")
        
        # Título
        self.canvas.create_text(ANCHO_VENTANA // 2, 25,
                               text="EDITOR DE NIVELES",
                               font=("Arial", 24, "bold"),
                               fill="#ffaa00", tags="editor_ui")
        
        # Controles
        self.canvas.create_text(ANCHO_VENTANA // 2, 55,
                               text="Click: Colocar | Click Der: Eliminar | ←→: Navegar | ↑↓: Altura | 0-9,-: Objetos | ESC: Salir | G: Guardar | P: Probar",
                               font=("Arial", 11),
                               fill="#aaaaaa", tags="editor_ui")
        
        # Panel de herramientas (izquierda)
        self.crear_panel_herramientas()
        
        # Bindings del editor (solo mouse)
        self.canvas.bind("<Button-1>", self.editor_click)
        self.canvas.bind("<Button-3>", self.editor_click_derecho)
        
        # Bindings de teclado para el editor - VERIFICAN si estamos en editor
        # Navegación
        self.canvas.bind("<Left>", lambda e: self.editor_scroll(-100) if self.en_editor else None)
        self.canvas.bind("<Right>", lambda e: self.editor_scroll(100) if self.en_editor else None)
        self.canvas.bind("<Up>", lambda e: self.editor_cambiar_altura(1) if self.en_editor else None)
        self.canvas.bind("<Down>", lambda e: self.editor_cambiar_altura(-1) if self.en_editor else None)
        
        # Herramientas 0-9 y -
        self.canvas.bind("0", lambda e: self.editor_seleccionar_herramienta(0) if self.en_editor else None)
        self.canvas.bind("-", lambda e: self.editor_seleccionar_herramienta("-") if self.en_editor else None)
        for num in range(1, 10):
            self.canvas.bind(str(num), lambda e, n=num: self.editor_seleccionar_herramienta(n) if self.en_editor else None)
        
        # Comandos (G=Guardar, P=Probar, ESC=Salir con confirmación)
        self.canvas.bind("g", lambda e: self.guardar_nivel_editor() if self.en_editor else None)
        self.canvas.bind("G", lambda e: self.guardar_nivel_editor() if self.en_editor else None)
        self.canvas.bind("p", lambda e: self.probar_nivel_editor() if self.en_editor else None)
        self.canvas.bind("P", lambda e: self.probar_nivel_editor() if self.en_editor else None)
        self.canvas.bind("<Escape>", lambda e: self.confirmar_salir_editor() if self.en_editor else None)
        
        # Dar foco al canvas
        self.canvas.focus_set()
    
    def crear_panel_herramientas(self):
        """Crea el panel de herramientas lateral"""
        panel_x = 10
        panel_y = 100
        
        herramientas = [
            ("1", "bloque", "Bloque"),
            ("2", "pincho", "Pincho"),
            ("3", "plataforma", "Plataforma"),
            ("4", "moneda", "Moneda"),
            ("5", "sierra", "Sierra"),
            ("6", "orbe_amarillo", "Orbe"),
            ("7", "portal_ship", "Ship"),
            ("8", "portal_cube", "Cube"),
            ("9", "portal_gravedad", "Gravity"),
            ("0", "bloque_techo", "Techo"),
            ("-", "pincho_suelo", "P.Inv")
        ]
        
        for i, (tecla, tipo, nombre) in enumerate(herramientas):
            y = panel_y + i * 50  
            
            color = "#3a3a5a" if tipo == self.editor_tipo_actual else "#2a2a4a"
            borde = "#ffaa00" if tipo == self.editor_tipo_actual else "#666666"
            
            self.canvas.create_rectangle(panel_x, y, panel_x + 150, y + 45, 
                                        fill=color, outline=borde, width=2,
                                        tags=["editor_ui", f"tool_{tipo}"])
            self.canvas.create_text(panel_x + 20, y + 22,  
                                   text=f"[{tecla}]",
                                   font=("Arial", 10, "bold"),  
                                   fill="#ffaa00", tags="editor_ui")
            self.canvas.create_text(panel_x + 90, y + 22, 
                                   text=nombre,
                                   font=("Arial", 10), 
                                   fill="white", tags="editor_ui")
        
        # Indicador de altura para bloques - Movido más abajo para no tapar botones 9 y 0
        if self.editor_tipo_actual in ["bloque", "bloque_techo"]:
            altura_y = panel_y + 560  
            self.canvas.create_rectangle(panel_x, altura_y, panel_x + 150, altura_y + 60,
                                        fill="#1a1a2e", outline="#ffaa00", width=2,
                                        tags="editor_ui")
            self.canvas.create_text(panel_x + 75, altura_y + 15,
                                   text="ALTURA BLOQUE",
                                   font=("Arial", 10, "bold"),
                                   fill="#ffaa00", tags="editor_ui")
            self.canvas.create_text(panel_x + 75, altura_y + 40,
                                   text=f"↕️ {self.editor_altura_actual}",
                                   font=("Arial", 16, "bold"),
                                   fill="#00ff88", tags="editor_ui")
    
    def dibujar_editor(self):
        """Dibuja los objetos del editor"""
        # Borrar objetos anteriores
        self.canvas.delete("editor_objeto")
        
        # Dibujar cada objeto
        for obj in self.editor_objetos:
            x = obj["x"] - self.editor_scroll_x
            if -200 <= x <= ANCHO_VENTANA + 200:
                self.dibujar_objeto_editor(obj, x)
    
    def dibujar_objeto_editor(self, obj, x):
        """Dibuja un objeto en el editor"""
        tipo = obj["tipo"]
        
        if tipo == "bloque":
            altura = obj.get("altura", 1)
            y = SUELO_Y - altura * TAMANO_BLOQUE
            self.canvas.create_rectangle(x, y, x + TAMANO_BLOQUE, SUELO_Y,
                                         fill="#00d9ff", outline="white", width=2,
                                         tags="editor_objeto")
        
        elif tipo == "pincho":
            y = SUELO_Y
            self.canvas.create_polygon(x, y, x + 30, y, x + 15, y - 40,
                                       fill="#ff0080", outline="white", width=2,
                                       tags="editor_objeto")
        
        elif tipo == "pincho_suelo":
            # Pincho invertido que cuelga del techo
            y = LIMITE_SUPERIOR
            self.canvas.create_polygon(x, y, x + 30, y, x + 15, y + 40,
                                       fill="#ff0080", outline="white", width=2,
                                       tags="editor_objeto")
        
        elif tipo == "plataforma":
            y = obj.get("y", SUELO_Y - 120)
            ancho = obj.get("ancho", 100)
            self.canvas.create_rectangle(x, y, x + ancho, y + 20,
                                         fill="#00d9ff", outline="white", width=2,
                                         tags="editor_objeto")
        
        elif tipo == "moneda":
            y = obj.get("y", SUELO_Y - 60)
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15,
                                   fill="#ffea00", outline="white", width=2,
                                   tags="editor_objeto")
        
        elif tipo == "sierra":
            y = obj.get("y", SUELO_Y - 60)
            self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25,
                                   fill="#ff0080", outline="white", width=2,
                                   tags="editor_objeto")
        
        elif tipo == "orbe_amarillo":
            y = obj.get("y", SUELO_Y - 100)
            self.canvas.create_oval(x - 18, y - 18, x + 18, y + 18,
                                   fill="#ffea00", outline="white", width=2,
                                   tags="editor_objeto")
        
        elif tipo == "portal_gravedad":
            self.canvas.create_rectangle(x, LIMITE_SUPERIOR, x + 60, SUELO_Y,
                                         fill="", outline="#ff00ff", width=3,
                                         tags="editor_objeto")
            self.canvas.create_text(x + 30, (LIMITE_SUPERIOR + SUELO_Y) // 2,
                                   text="⇅", fill="#ff00ff", font=("Arial", 24, "bold"),
                                   tags="editor_objeto")
        
        elif tipo == "portal_ship":
            self.canvas.create_rectangle(x, LIMITE_SUPERIOR, x + 60, SUELO_Y,
                                         fill="", outline="#00d9ff", width=3,
                                         tags="editor_objeto")
            self.canvas.create_polygon(x + 45, (LIMITE_SUPERIOR + SUELO_Y) // 2,
                                      x + 15, (LIMITE_SUPERIOR + SUELO_Y) // 2 - 15,
                                      x + 15, (LIMITE_SUPERIOR + SUELO_Y) // 2 + 15,
                                      fill="#00d9ff", tags="editor_objeto")
        
        elif tipo == "portal_cube":
            self.canvas.create_rectangle(x, LIMITE_SUPERIOR, x + 60, SUELO_Y,
                                         fill="", outline="#ffaa00", width=3,
                                         tags="editor_objeto")
            self.canvas.create_rectangle(x + 20, (LIMITE_SUPERIOR + SUELO_Y) // 2 - 10,
                                        x + 40, (LIMITE_SUPERIOR + SUELO_Y) // 2 + 10,
                                        fill="#ffaa00", tags="editor_objeto")
        
        elif tipo == "bloque_techo":
            altura = obj.get("altura", 1)
            for i in range(altura):
                y = LIMITE_SUPERIOR + (i * TAMANO_BLOQUE)
                self.canvas.create_rectangle(x, y, x + TAMANO_BLOQUE, y + TAMANO_BLOQUE,
                                           fill="#00d9ff", outline="white", width=2,
                                           tags="editor_objeto")
        
        elif tipo == "end":
            # Marcador de fin del nivel - bandera de meta
            # Poste
            self.canvas.create_rectangle(x, SUELO_Y - 100, x + 10, SUELO_Y,
                                         fill="#ffffff", outline="white", width=2,
                                         tags="editor_objeto")
            # Bandera
            self.canvas.create_polygon(x + 10, SUELO_Y - 100,
                                      x + 60, SUELO_Y - 85,
                                      x + 10, SUELO_Y - 70,
                                      fill="#00ff88", outline="white", width=2,
                                      tags="editor_objeto")
            # Texto "FIN"
            self.canvas.create_text(x + 35, SUELO_Y - 85,
                                   text="FIN", fill="#000000",
                                   font=("Arial", 12, "bold"),
                                   tags="editor_objeto")
    
    def editor_click(self, evento):
        """Maneja el click en el editor"""
        if not self.en_editor:  # Solo funciona si estamos en editor
            return
        if evento.y < 80 or evento.x < 170:  # UI del editor
            return
        
        # Calcular posición en la grilla
        x_mundo = (evento.x + self.editor_scroll_x) // self.editor_grid_size * self.editor_grid_size
        y_mundo = evento.y // self.editor_grid_size * self.editor_grid_size
        
        # Crear objeto
        nuevo_obj = {"tipo": self.editor_tipo_actual, "x": x_mundo}
        
        if self.editor_tipo_actual in ["bloque", "bloque_techo"]:
            nuevo_obj["altura"] = self.editor_altura_actual
        elif self.editor_tipo_actual in ["plataforma", "moneda", "sierra", "orbe_amarillo"]:
            nuevo_obj["y"] = y_mundo
            if self.editor_tipo_actual == "plataforma":
                nuevo_obj["ancho"] = 100
        
        # Para bloques, permitir apilar (solo verificar si es el MISMO bloque exacto)
        # Para otros objetos, verificar posición
        for obj in self.editor_objetos:
            if obj["tipo"] == "bloque" and nuevo_obj["tipo"] == "bloque":
                # Bloques: solo prevenir si tienen la MISMA x Y altura
                if obj["x"] == x_mundo and obj.get("altura", 1) == nuevo_obj.get("altura", 1):
                    return  # Ya existe este bloque exacto
            elif obj["tipo"] == nuevo_obj["tipo"]:
                # Otros objetos: verificar posición x e y
                if obj["x"] == x_mundo and obj.get("y", SUELO_Y) == nuevo_obj.get("y", SUELO_Y):
                    return  # Ya existe este objeto
        
        self.editor_objetos.append(nuevo_obj)
        self.dibujar_editor()
        
        altura_info = f" (altura {self.editor_altura_actual})" if self.editor_tipo_actual == "bloque" else ""
        print(f"Objeto '{self.editor_tipo_actual}' colocado en x={x_mundo}{altura_info}")
    
    def editor_click_derecho(self, evento):
        """Elimina objetos con click derecho"""
        if not self.en_editor:  # Solo funciona si estamos en editor
            return
        if evento.y < 80 or evento.x < 170:
            return
        
        x_mundo = evento.x + self.editor_scroll_x
        y_mundo = evento.y
        
        # Buscar objeto más cercano al click
        objeto_mas_cercano = None
        distancia_minima = float('inf')
        
        for obj in self.editor_objetos:
            obj_x = obj["x"] - self.editor_scroll_x
            
            # Para portales (que ocupan todo el eje Y), usar el centro vertical
            if obj["tipo"] in ["portal_ship", "portal_cube", "portal_gravedad"]:
                obj_y = (LIMITE_SUPERIOR + SUELO_Y) // 2  # Centro del portal
            # Para pincho_suelo, usar posición del techo
            elif obj["tipo"] == "pincho_suelo":
                obj_y = LIMITE_SUPERIOR + 20  # Centro del pincho invertido
            # Para bloque_techo, usar posición desde el techo
            elif obj["tipo"] == "bloque_techo":
                altura = obj.get("altura", 1)
                obj_y = LIMITE_SUPERIOR + (altura * TAMANO_BLOQUE // 2)  # Centro del bloque techo
            else:
                obj_y = obj.get("y", SUELO_Y)
            
            # Calcular distancia
            distancia = ((obj_x - evento.x) ** 2 + (obj_y - y_mundo) ** 2) ** 0.5
            
            # Para portales, aumentar el rango de detección
            rango = 100 if obj["tipo"] in ["portal_ship", "portal_cube", "portal_gravedad"] else 60
            
            if distancia < rango and distancia < distancia_minima:
                distancia_minima = distancia
                objeto_mas_cercano = obj
        
        if objeto_mas_cercano:
            self.editor_objetos.remove(objeto_mas_cercano)
            self.dibujar_editor()
            print(f"Objeto '{objeto_mas_cercano['tipo']}' eliminado")
    
    def editor_scroll(self, delta):
        """Desplaza la vista del editor"""
        self.editor_scroll_x += delta
        if self.editor_scroll_x < 0:
            self.editor_scroll_x = 0
        self.dibujar_editor()
    
    def editor_seleccionar_herramienta(self, numero):
        """Selecciona una herramienta por número"""
        herramientas = {
            0: "bloque_techo",
            1: "bloque",
            2: "pincho",
            3: "plataforma",
            4: "moneda",
            5: "sierra",
            6: "orbe_amarillo",
            7: "portal_ship",
            8: "portal_cube",
            9: "portal_gravedad",
            "-": "pincho_suelo"
        }
        
        if numero in herramientas:
            self.editor_tipo_actual = herramientas[numero]
            self.crear_panel_herramientas()
            print(f"Herramienta seleccionada: {self.editor_tipo_actual}")
    
    def editor_cambiar_altura(self, delta):
        """Cambia la altura de los bloques"""
        if self.editor_tipo_actual not in ["bloque", "bloque_techo"]:
            return
            
        self.editor_altura_actual = max(1, min(10, self.editor_altura_actual + delta))
        print(f"Altura de bloque: {self.editor_altura_actual}")
        # Actualizar panel de herramientas para mostrar nueva altura
        self.crear_panel_herramientas()
    
    def editor_tecla(self, evento):
        """Maneja las teclas del editor (DEPRECADO - usar bindings individuales)"""
        pass
    
    def guardar_nivel_editor(self):
        """Guarda el nivel creado"""
        if not self.editor_objetos:
            print("No hay objetos para guardar")
            return
        
        # Ordenar objetos por posición X
        self.editor_objetos.sort(key=lambda obj: obj["x"])
        
        # Calcular longitud del nivel
        max_x = max(obj["x"] for obj in self.editor_objetos)
        longitud = max_x + 500
        
        # Agregar objeto de fin si no existe
        tiene_fin = any(obj["tipo"] == "end" for obj in self.editor_objetos)
        if not tiene_fin:
            self.editor_objetos.append({"tipo": "end", "x": longitud - 100})
        
        # Crear estructura del nivel
        nivel_guardado = {
            "nombre": "NIVEL PERSONALIZADO",
            "numero": 99,
            "velocidad_inicial": "x1",
            "longitud": longitud,
            "objetos": self.editor_objetos.copy()
        }
        
        print("\n" + "="*50)
        print("NIVEL GUARDADO EXITOSAMENTE")
        print("="*50)
        print(f"Objetos: {len(self.editor_objetos)}")
        print(f"Longitud: {longitud}px")
        print(f"Codigo del nivel:")
        print("="*50)
        print(f"\nNIVEL_PERSONALIZADO = {nivel_guardado}")
        print("\n" + "="*50)
        print("Copia este codigo para usarlo despues")
        print("="*50 + "\n")
    
    def probar_nivel_editor(self):
        """Prueba el nivel en modo juego"""
        if not self.editor_objetos:
            print("No hay objetos para probar")
            return
        
        # Ordenar objetos
        self.editor_objetos.sort(key=lambda obj: obj["x"])
        
        # Calcular longitud
        max_x = max(obj["x"] for obj in self.editor_objetos)
        longitud = max_x + 500
        
        # Agregar fin si no existe
        tiene_fin = any(obj["tipo"] == "end" for obj in self.editor_objetos)
        if not tiene_fin:
            self.editor_objetos.append({"tipo": "end", "x": longitud - 100})
        
        # Crear nivel temporal
        self.nivel_data = {
            "nombre": "PRUEBA",
            "numero": 99,
            "velocidad_inicial": "x1",
            "longitud": longitud,
            "objetos": self.editor_objetos.copy()
        }
        
        self.nivel_actual = 99
        self.en_editor = False
        self.probando_nivel_editor = True  # Marcar que estamos probando desde el editor
        
        print("\nProbando nivel personalizado...\n")
        
        # Iniciar el juego con el nivel personalizado
        self.iniciar_nivel(99, False)
    
    def confirmar_salir_editor(self):
        """Muestra diálogo de confirmación antes de salir del editor"""
        if not self.en_editor:
            return
        
        # Oscurecer fondo
        self.canvas.create_rectangle(0, 0, ANCHO_VENTANA, ALTO_VENTANA,
                                     fill="#000000", stipple="gray50",
                                     tags="dialogo_confirm")
        
        # Panel de diálogo
        panel_w = 500
        panel_h = 250
        panel_x = (ANCHO_VENTANA - panel_w) // 2
        panel_y = (ALTO_VENTANA - panel_h) // 2
        
        self.canvas.create_rectangle(panel_x, panel_y, panel_x + panel_w, panel_y + panel_h,
                                     fill="#1a1a2e", outline="#ffaa00", width=4,
                                     tags="dialogo_confirm")
        
        # Título
        self.canvas.create_text(panel_x + panel_w // 2, panel_y + 50,
                               text="SALIR DEL EDITOR",
                               font=("Arial", 24, "bold"),
                               fill="#ffaa00", tags="dialogo_confirm")
        
        # Mensaje
        self.canvas.create_text(panel_x + panel_w // 2, panel_y + 110,
                               text="¿Desea volver al menú?\n(Los cambios no guardados se perderán)",
                               font=("Arial", 14),
                               fill="#ffffff", tags="dialogo_confirm", justify="center")
        
        # Botón SÍ
        btn_w = 180
        btn_h = 50
        btn_y = panel_y + panel_h - 80
        
        self.canvas.create_rectangle(panel_x + 40, btn_y, panel_x + 40 + btn_w, btn_y + btn_h,
                                     fill="#ff4444", outline="#ffffff", width=3,
                                     tags=["dialogo_confirm", "btn_si"])
        self.canvas.create_text(panel_x + 40 + btn_w // 2, btn_y + btn_h // 2,
                               text="SI",
                               fill="#ffffff", font=("Arial", 18, "bold"),
                               tags=["dialogo_confirm", "btn_si"])
        
        # Botón NO
        self.canvas.create_rectangle(panel_x + 280, btn_y, panel_x + 280 + btn_w, btn_y + btn_h,
                                     fill="#44ff44", outline="#ffffff", width=3,
                                     tags=["dialogo_confirm", "btn_no"])
        self.canvas.create_text(panel_x + 280 + btn_w // 2, btn_y + btn_h // 2,
                               text="NO",
                               fill="#000000", font=("Arial", 18, "bold"),
                               tags=["dialogo_confirm", "btn_no"])
        
        # Bindings
        self.canvas.tag_bind("btn_si", "<Button-1>", lambda e: self.salir_editor_confirmado())
        self.canvas.tag_bind("btn_no", "<Button-1>", lambda e: self.cancelar_salir_editor())
        
        # Hover effects
        self.canvas.tag_bind("btn_si", "<Enter>", lambda e: self.canvas.itemconfig("btn_si", fill="#ff6666"))
        self.canvas.tag_bind("btn_si", "<Leave>", lambda e: self.canvas.itemconfig("btn_si", fill="#ff4444"))
        self.canvas.tag_bind("btn_no", "<Enter>", lambda e: self.canvas.itemconfig("btn_no", fill="#66ff66"))
        self.canvas.tag_bind("btn_no", "<Leave>", lambda e: self.canvas.itemconfig("btn_no", fill="#44ff44"))
    
    def salir_editor_confirmado(self):
        """Sale del editor después de confirmar"""
        self.canvas.delete("dialogo_confirm")
        self.en_editor = False
        self.editor_objetos = []  # Limpiar objetos
        self.volver_menu()
    
    def cancelar_salir_editor(self):
        """Cancela la salida del editor"""
        self.canvas.delete("dialogo_confirm")

if __name__ == "__main__":
    juego = Cubik()
