import os
from enum import Enum

# ======================================================================================
# --- 1. CONFIGURATION & CONSTANTS ---
# ======================================================================================
# WINDOW
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
WINDOW_TITLE = "FutePong"
FPS_LIMIT = 120

# COLORS
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_BLACK = (0, 0, 0)

# ASSET PATHS
# Ajustado para usar a pasta 'Assets' como base
BASE_ASSETS_PATH = "Assets/"

IMAGE_PATH = os.path.join(BASE_ASSETS_PATH, "Images/")
PLAYERS_PATH = os.path.join(IMAGE_PATH, "Players/")
FLAGS_PATH = os.path.join(IMAGE_PATH, "Flags/")
FONT_PATH = os.path.join(BASE_ASSETS_PATH, "Fonts/")
SOUND_PATH = os.path.join(BASE_ASSETS_PATH, "Sounds/")
BOOST_PATH = os.path.join(IMAGE_PATH, "Boost/")

# IMAGE FILES
BACKGROUND_IMAGE = os.path.join(IMAGE_PATH, "fundo.png")
MENU_BACKGROUND_IMAGE = os.path.join(IMAGE_PATH, "fundo_menu.png")
BALL_IMAGE = os.path.join(BOOST_PATH, "bola.png")
SHADOW_IMAGE = os.path.join(IMAGE_PATH, "shadow.png")
SCOREBOARD_IMAGE = os.path.join(IMAGE_PATH, "placar.png")
BOOST_IMAGE = os.path.join(BOOST_PATH, "boost_fogo.png")
SLOW_BALL_IMAGE = os.path.join(BOOST_PATH, "boost_gelo.png")
GOAL_ANIMATION_GIF = os.path.join(IMAGE_PATH, "gol_animacao.gif")

# Player Images
# Corrigido o caminho para a pasta 'Players'
NEYMAR_IMAGE = os.path.join(PLAYERS_PATH, "neymar.png")
MESSI_IMAGE = os.path.join(PLAYERS_PATH, "messi.png")
CR7_IMAGE = os.path.join(PLAYERS_PATH, "ronaldo.png")
MBAPPE_IMAGE = os.path.join(PLAYERS_PATH, "mbappe.png")
MORATA_IMAGE = os.path.join(PLAYERS_PATH, "morata.png")
MULLER_IMAGE = os.path.join(PLAYERS_PATH, "muller.png")

# Flag Images
# Corrigido o caminho para a pasta 'Flags'
FLAG_BRAZIL_IMAGE = os.path.join(FLAGS_PATH, "bandeira_brasil.png")
FLAG_ARGENTINA_IMAGE = os.path.join(FLAGS_PATH, "bandeira_argentina.png")
FLAG_PORTUGAL_IMAGE = os.path.join(FLAGS_PATH, "bandeira_portugal.png")
FLAG_FRANCE_IMAGE = os.path.join(FLAGS_PATH, "bandeira_franca.png")
FLAG_SPAIN_IMAGE = os.path.join(FLAGS_PATH, "bandeira_espanha.png")
FLAG_GERMANY_IMAGE = os.path.join(FLAGS_PATH, "bandeira_alemanha.png")

# CHARACTERS DATA STRUCTURE
CHARACTERS = [
    {"name": "Neymar", "image_path": NEYMAR_IMAGE, "team_name": "BRASIL", "flag_path": FLAG_BRAZIL_IMAGE},
    {"name": "Messi", "image_path": MESSI_IMAGE, "team_name": "ARGENTINA", "flag_path": FLAG_ARGENTINA_IMAGE},
    {"name": "Ronaldo", "image_path": CR7_IMAGE, "team_name": "PORTUGAL", "flag_path": FLAG_PORTUGAL_IMAGE},
    {"name": "Mbappé", "image_path": MBAPPE_IMAGE, "team_name": "FRANÇA", "flag_path": FLAG_FRANCE_IMAGE},
    {"name": "Morata", "image_path": MORATA_IMAGE, "team_name": "ESPANHA", "flag_path": FLAG_SPAIN_IMAGE},
    {"name": "Muller", "image_path": MULLER_IMAGE, "team_name": "ALEMANHA", "flag_path": FLAG_GERMANY_IMAGE},
]

# FONT FILES
# Corrigido o caminho para a pasta 'Fonts'
FONT_MAIN_TITLE = os.path.join(FONT_PATH, "superstar_m54/Superstar M54.ttf")
FONT_SECTION_TITLE = os.path.join(FONT_PATH, "KenVector Future 2/kenvector_future.ttf")
FONT_BODY = os.path.join(FONT_PATH, "kenney-mini-square/kenney_mini_square.otf")
FONT_SCORE = os.path.join(FONT_PATH, "score_font/score_font.ttf")

# SOUND FILES
# Corrigido o caminho para a pasta 'Sounds'
START_WHISTLE_SOUND = os.path.join(SOUND_PATH, "apito_inicio.wav")
END_WHISTLE_SOUND = os.path.join(SOUND_PATH, "apito_fim.wav")
KICK_SOUND = os.path.join(SOUND_PATH, "chute.wav")
GOAL_SOUND = os.path.join(SOUND_PATH, "gol.wav")

# GAME SETTINGS
MAX_SCORE = 5
PLAYER_INITIAL_SPEED = 400
BALL_INITIAL_SPEED = 424  # Velocidade ajustada para manter a mesma sensação anterior
PLAYER_OFFSET_X = 10
POWERUP_SPAWN_TIME = 10
POWERUP_ON_SCREEN_DURATION = 7
TRAIL_EFFECT_DURATION = 2.0
DIFFICULTY_SETTINGS = {"Easy": 0.6, "Medium": 0.8, "Hard": 1.0}
TILT_SPEED = 15
GOAL_ANIM_SPEED = 15

# ======================================================================================
# --- ENUMS (STATES & TYPES) ---
# ======================================================================================
class GameState(Enum):
    MAIN_MENU = 1
    DIFFICULTY_MENU = 2
    RULES = 3
    CHARACTER_SELECTION = 4
    PLAYING = 5
    PAUSED = 6
    GOAL = 7
    GAME_OVER = 8

class GameMode(Enum):
    PVE = 1
    PVP = 2