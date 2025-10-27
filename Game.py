# game.py
import pygame
import random
import math
from PPlay.window import *
from Constants import *
from Entities import *
from Ui_manager import *

# ======================================================================================
# --- MANAGER CLASSES (GAME) ---
# ======================================================================================
class Game:
    def __init__(self):
        self.window = Window(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.window.set_title(WINDOW_TITLE)
        self.keyboard = Window.get_keyboard()
        pygame.mixer.init()

        self.state = GameState.MAIN_MENU
        self.game_mode = None
        self.difficulty = None
        self.input_locks = {key: False for key in ['escape', 'p', '1', '2', '3', 'return', 'left', 'right', 'a', 'd', 'r']}

        self.clock = pygame.time.Clock()
        self.ui_manager = UIManager(self.window)
        self.player1 = None
        self.player2 = None
        self.ball = None

        # Criar os power-ups com tipos específicos
        self.speed_boost_powerup = PowerUp(BOOST_IMAGE, 'SPEED_BOOST')
        self.slow_ball_powerup = PowerUp(SLOW_BALL_IMAGE, 'SLOW_BALL')
        self.powerup_types = [self.speed_boost_powerup, self.slow_ball_powerup]
        self.powerup_weights = [0.65, 0.35]  # 65% chance para speed boost, 35% para slow
        self.active_powerup = None
        self.scores = {"left": 0, "right": 0}
        self.powerup_spawn_timer = 0
        self.powerup_on_screen_timer = 0
        self.last_scorer = "right"
        self.goal_pause_timer = 0
        self.match_time = 0
        self.ball_trails = []
        self.trail_spawn_timer = 0
        self.trail_effect_timer = 0
        self.screen_shake_timer = 0
        self.screen_shake_intensity = 8
        self.p1_char_index = 0
        self.p2_char_index = 1
        self.selecting_for = 1
        self._load_sounds()

    def _load_sounds(self):
        try:
            self.start_whistle_sound = pygame.mixer.Sound(START_WHISTLE_SOUND)
            self.start_whistle_sound.set_volume(0.1)
            self.end_whistle_sound = pygame.mixer.Sound(END_WHISTLE_SOUND)
            self.end_whistle_sound.set_volume(0.1)
            self.kick_sound = pygame.mixer.Sound(KICK_SOUND)
            self.kick_sound.set_volume(0.1)
            self.goal_sound = pygame.mixer.Sound(GOAL_SOUND)
            self.goal_sound.set_volume(0.1)
        except pygame.error as e:
            print(f"WARNING: Could not load one or more audio files. Error: {e}")
            self.start_whistle_sound = self.end_whistle_sound = self.kick_sound = self.goal_sound = None

    def reset_game(self):
        self.scores = {"left": 0, "right": 0}
        p1_image = CHARACTERS[self.p1_char_index]["image_path"]
        p2_image = CHARACTERS[self.p2_char_index]["image_path"]
        
        self.player1 = Paddle(p1_image, "left", self.window)
        if self.game_mode == GameMode.PVE:
            ai_difficulty = DIFFICULTY_SETTINGS[self.difficulty]
            self.player2 = AI(p2_image, "right", self.window, PLAYER_INITIAL_SPEED, ai_difficulty)
        elif self.game_mode == GameMode.PVP:
            self.player2 = Paddle(p2_image, "right", self.window)
            
        self.ball = Ball(BALL_IMAGE)
        self.state = GameState.PLAYING
        self.match_time = 0
        self.ball_trails = []
        self.reset_round()

    def reset_round(self):
        direction = 1 if self.last_scorer == "right" else -1
        self.ball.reset(self.window, direction)
        self.player1.reset_position()
        self.player2.reset_position()
        if self.active_powerup: self.active_powerup.is_active = False
        self.trail_effect_timer = 0
        self.ball_trails.clear()
        if self.start_whistle_sound: self.start_whistle_sound.play()

    def run(self):
        while True:
            delta_time = self.window.delta_time()
            self.clock.tick(FPS_LIMIT)

            self.handle_input()
            self.update(delta_time)

            game_data = {
                "scores": self.scores, "match_time": self.match_time, "player1": self.player1,
                "player2": self.player2, "ball": self.ball, "ball_trails": self.ball_trails,
                "active_powerup": self.active_powerup, "screen_shake_timer": self.screen_shake_timer,
                "screen_shake_intensity": self.screen_shake_intensity,
                "p1_char_index": self.p1_char_index, "p2_char_index": self.p2_char_index,
                "selecting_for": self.selecting_for, "game_mode": self.game_mode,
                "delta_time": delta_time
            }
            self.ui_manager.draw(self.state, game_data)

            self.window.update()

    def handle_input(self):
        for key in self.input_locks:
            if not self.keyboard.key_pressed(key.upper()):
                self.input_locks[key] = False

        if self._is_key_pressed('escape'):
            if self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GOAL, GameState.GAME_OVER, GameState.RULES, GameState.CHARACTER_SELECTION, GameState.DIFFICULTY_MENU]:
                self.state = GameState.MAIN_MENU
                self.selecting_for = 1
            else:
                self.window.close()
        
        if self.state == GameState.MAIN_MENU:
            if self._is_key_pressed('1'): self.game_mode, self.state = GameMode.PVE, GameState.CHARACTER_SELECTION
            elif self._is_key_pressed('2'): self.game_mode, self.state = GameMode.PVP, GameState.CHARACTER_SELECTION
            elif self._is_key_pressed('3'): self.state = GameState.RULES
        
        elif self.state == GameState.CHARACTER_SELECTION:
            if self.game_mode == GameMode.PVE: self._handle_pve_character_selection()
            elif self.game_mode == GameMode.PVP: self._handle_pvp_character_selection()
        
        elif self.state == GameState.DIFFICULTY_MENU:
            if self._is_key_pressed('1'): self.difficulty = "Easy"; self.reset_game()
            elif self._is_key_pressed('2'): self.difficulty = "Medium"; self.reset_game()
            elif self._is_key_pressed('3'): self.difficulty = "Hard"; self.reset_game()
        
        elif self.state == GameState.PLAYING:
            self.player1.move("W", "S", self.keyboard)
            if self.game_mode == GameMode.PVP: self.player2.move("UP", "DOWN", self.keyboard)
            if self._is_key_pressed('p'): self.state = GameState.PAUSED
        
        elif self.state == GameState.PAUSED:
            if self._is_key_pressed('p'):
                self.state = GameState.PLAYING
            if self._is_key_pressed('r'):
                self.reset_game()
            
        elif self.state == GameState.GAME_OVER:
            if self._is_key_pressed('return'): self.reset_game()

    def _is_key_pressed(self, key):
        if self.keyboard.key_pressed(key.upper()) and not self.input_locks[key]:
            self.input_locks[key] = True
            return True
        return False
    
    def _handle_pve_character_selection(self):
        if self._is_key_pressed('right'):
            if self.selecting_for == 1: self.p1_char_index = (self.p1_char_index + 1) % len(CHARACTERS)
            elif self.selecting_for == 2: self.p2_char_index = (self.p2_char_index + 1) % len(CHARACTERS)
        if self._is_key_pressed('left'):
            if self.selecting_for == 1: self.p1_char_index = (self.p1_char_index - 1) % len(CHARACTERS)
            elif self.selecting_for == 2: self.p2_char_index = (self.p2_char_index - 1) % len(CHARACTERS)
        if self._is_key_pressed('return'):
            self.selecting_for += 1
            if self.selecting_for > 2:
                self.state = GameState.DIFFICULTY_MENU

    def _handle_pvp_character_selection(self):
        if self._is_key_pressed('d'): self.p1_char_index = (self.p1_char_index + 1) % len(CHARACTERS)
        if self._is_key_pressed('a'): self.p1_char_index = (self.p1_char_index - 1) % len(CHARACTERS)
        if self._is_key_pressed('right'): self.p2_char_index = (self.p2_char_index + 1) % len(CHARACTERS)
        if self._is_key_pressed('left'): self.p2_char_index = (self.p2_char_index - 1) % len(CHARACTERS)
        if self._is_key_pressed('return'):
            self.reset_game()

    def update(self, delta_time):
        if self.screen_shake_timer > 0: self.screen_shake_timer -= delta_time
        
        if self.state == GameState.PLAYING:
            self.match_time += delta_time
            if self.game_mode == GameMode.PVE: self.player2.move(self.ball)
            self.player1.update_effects(delta_time)
            self.player2.update_effects(delta_time)

            if self.trail_effect_timer > 0:
                self.trail_effect_timer -= delta_time
                self.trail_spawn_timer += delta_time
                if self.trail_spawn_timer > 0.02:
                    self.ball_trails.append(BallTrail(self.ball.image, (self.ball.x, self.ball.y)))
                    self.trail_spawn_timer = 0
            
            self.ball_trails = [trail for trail in self.ball_trails if trail.lifespan > 0]
            for trail in self.ball_trails:
                trail.update(delta_time)

            ball_status = self.ball.move(self.window)
            if ball_status:
                self._handle_goal(ball_status)
                return

            collided_p1 = self.ball.handle_paddle_collision(self.player1)
            collided_p2 = self.ball.handle_paddle_collision(self.player2)
            if collided_p1 or collided_p2:
                if collided_p1: self.player1.trigger_squash()
                if collided_p2: self.player2.trigger_squash()
                if self.kick_sound: self.kick_sound.play()
            
            self._update_powerups(delta_time)
            
        elif self.state == GameState.GOAL:
            self.goal_pause_timer -= delta_time
            if self.goal_pause_timer <= 0:
                self.state = GameState.PLAYING
                self.reset_round()

    def _handle_goal(self, ball_status):
        if self.goal_sound: self.goal_sound.play()
        self.screen_shake_timer = 0.3
        scoring_side = "left" if ball_status == "goal_left" else "right"
        self.last_scorer = "left" if scoring_side == "right" else "right"
        self.scores[scoring_side] += 1
        
        if self.scores[scoring_side] >= MAX_SCORE:
            self.state = GameState.GAME_OVER
            if self.end_whistle_sound: self.end_whistle_sound.play()
        else:
            self.state = GameState.GOAL
            self.goal_pause_timer = 1.5

    def _update_powerups(self, delta_time):
        if self.active_powerup and self.active_powerup.is_active:
            self.powerup_on_screen_timer += delta_time
            if self.powerup_on_screen_timer >= POWERUP_ON_SCREEN_DURATION:
                self.active_powerup.is_active = False
                self.powerup_on_screen_timer = 0
        else:
            self.powerup_spawn_timer += delta_time
            if self.powerup_spawn_timer >= POWERUP_SPAWN_TIME:
                self.powerup_spawn_timer = 0
                self.powerup_on_screen_timer = 0
                
                # Verificar se a bola está com velocidade maior que a inicial
                current_speed = math.sqrt(self.ball.velocity_x**2 + self.ball.velocity_y**2)
                # Só pode aparecer SLOW_BALL se a velocidade for pelo menos 20% maior que a inicial
                is_boosted = current_speed > self.ball.initial_speed * 1.2
                
                if not is_boosted:
                    # Se a bola está na velocidade inicial ou menor, só pode aparecer SPEED_BOOST
                    self.active_powerup = self.speed_boost_powerup
                else:
                    # Se a bola está boosted, pode aparecer qualquer power-up com as probabilidades normais
                    self.active_powerup = random.choices(self.powerup_types, self.powerup_weights, k=1)[0]
                
                self.active_powerup.spawn(self.window)

        if self.active_powerup and self.active_powerup.is_active and self.ball.collided(self.active_powerup):
            if self.active_powerup.type == 'SPEED_BOOST':
                self.trail_effect_timer = TRAIL_EFFECT_DURATION
            self.active_powerup.apply_effect(self.ball)
            self.powerup_on_screen_timer = 0