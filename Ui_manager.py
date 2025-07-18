# ui_manager.py
import pygame
import random
from PPlay.gameimage import *
from Constants import *

# ======================================================================================
# --- MANAGER CLASSES (UI) ---
# ======================================================================================
class UIManager:
    def __init__(self, window):
        self.window = window

        # --- FUNÇÃO ATUALIZADA ---
        # Agora ela otimiza as imagens no carregamento
        def _load_image(path, use_alpha=False):
            """Tenta carregar e otimizar uma imagem, retornando None em caso de erro."""
            try:
                image = GameImage(path)
                if use_alpha:
                    image.image = image.image.convert_alpha()
                else:
                    image.image = image.image.convert()
                return image
            except pygame.error:
                print(f"WARNING: Image file not found at '{path}'.")
                return None
        # --- FIM DA ATUALIZAÇÃO ---

        # Carregando assets usando a função auxiliar otimizada
        self.background = _load_image(BACKGROUND_IMAGE)
        self.menu_background = _load_image(MENU_BACKGROUND_IMAGE)
        if not self.menu_background:
            self.menu_background = self.background

        # Scoreboard tem transparência, então use_alpha=True
        self.scoreboard_image = _load_image(SCOREBOARD_IMAGE, use_alpha=True) 
        if self.scoreboard_image:
            new_width, new_height = 318, 44
            self.scoreboard_image.image = pygame.transform.scale(self.scoreboard_image.image, (new_width, new_height))
            self.scoreboard_image.width, self.scoreboard_image.height = new_width, new_height
            self.scoreboard_image.x = (self.window.width - self.scoreboard_image.width) / 2
            self.scoreboard_image.y = 0

        # Power-ups têm transparência
        self.boost_fire_img = _load_image(BOOST_IMAGE, use_alpha=True)
        self.boost_ice_img = _load_image(SLOW_BALL_IMAGE, use_alpha=True)

        # Personagens e bandeiras têm transparência
        self.character_images = [_load_image(char["image_path"], use_alpha=True) for char in CHARACTERS]
        self.flag_images = {char["flag_path"]: _load_image(char["flag_path"], use_alpha=True) for char in CHARACTERS}

        # Carregamento do GIF continua igual
        self.goal_animation_frames = []
        try:
            from PIL import Image
            with Image.open(GOAL_ANIMATION_GIF) as img:
                for i in range(img.n_frames):
                    img.seek(i)
                    frame = img.copy().convert("RGBA")
                    # Otimiza cada frame do GIF
                    py_frame = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
                    self.goal_animation_frames.append(py_frame)
        except (ImportError, FileNotFoundError) as e:
            print(f"WARNING: Could not load goal GIF. Pillow not installed or file not found. Error: {e}")
            self.goal_animation_frames = None
        self.goal_animation_timer = 0
        self.current_goal_frame = 0

        # Carregamento das fontes continua igual
        try:
            self.font_main_title = pygame.font.Font(FONT_MAIN_TITLE, 70)
            self.font_section_title = pygame.font.Font(FONT_SECTION_TITLE, 30)
            self.font_body = pygame.font.Font(FONT_BODY, 19)
            self.font_score_numbers = pygame.font.Font(FONT_SCORE, 25)
        except pygame.error as e:
            print(f"WARNING: Custom fonts not found, falling back to system default. Error: {e}")
            self.font_main_title = pygame.font.SysFont('Arial', 70, bold=True)
            self.font_section_title = pygame.font.SysFont('Arial', 30, bold=True)
            self.font_body = pygame.font.SysFont('Arial', 19, bold=True)
            self.font_score_numbers = pygame.font.SysFont('Arial', 25, bold=True)

    def draw(self, game_state, game_data):
        is_menu_state = game_state in [GameState.MAIN_MENU, GameState.DIFFICULTY_MENU, GameState.RULES, GameState.CHARACTER_SELECTION]
        if is_menu_state:
            self.menu_background.draw()
        else:
            render_offset = [0, 0]
            if game_data.get("screen_shake_timer", 0) > 0:
                intensity = game_data.get("screen_shake_intensity", 0)
                render_offset[0] = random.randint(-intensity, intensity)
                render_offset[1] = random.randint(-intensity, intensity)
            self.background.x, self.background.y = render_offset[0], render_offset[1]
            self.background.draw()

        if not is_menu_state:
            self._draw_game_elements(game_data)
            self._draw_game_ui(game_data)

        state_draw_map = {
            GameState.MAIN_MENU: self._draw_main_menu,
            GameState.DIFFICULTY_MENU: self._draw_difficulty_menu,
            GameState.RULES: self._draw_rules_screen,
            GameState.CHARACTER_SELECTION: lambda: self._draw_character_selection(game_data),
            GameState.GOAL: lambda: self._draw_goal_overlay(game_data),
            GameState.PAUSED: self._draw_pause_overlay,
            GameState.GAME_OVER: lambda: self._draw_game_over_overlay(game_data),
        }
        draw_function = state_draw_map.get(game_state)
        if draw_function:
            draw_function()

    def _draw_text_with_shadow(self, text, font, y_pos, x_center=None, main_color=COLOR_WHITE, shadow_color=COLOR_BLACK, offset=2):
        if x_center is None: x_center = self.window.width / 2
        text_surface = font.render(text, True, main_color)
        shadow_surface = font.render(text, True, shadow_color)
        text_rect = text_surface.get_rect(center=(x_center, y_pos))
        shadow_rect = shadow_surface.get_rect(center=(x_center + offset, y_pos + offset))
        self.window.screen.blit(shadow_surface, shadow_rect)
        self.window.screen.blit(text_surface, text_rect)

    def _draw_main_menu(self):
        panel_width = 550
        panel_height = 380
        panel_x = (self.window.width - panel_width) / 2
        panel_y = (self.window.height - panel_height) / 2

        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(150)
        panel_surface.fill(COLOR_BLACK)
        self.window.screen.blit(panel_surface, (panel_x, panel_y))

        self._draw_text_with_shadow("FutePong", self.font_main_title, 150, main_color=COLOR_YELLOW)
        self._draw_text_with_shadow("[1] Jogador vs IA", self.font_section_title, 250)
        self._draw_text_with_shadow("[2] Jogador vs Jogador", self.font_section_title, 300)
        self._draw_text_with_shadow("[3] Regras do Jogo", self.font_section_title, 350)
        self._draw_text_with_shadow("Pressione ESC para Sair", self.font_body, 440, main_color=COLOR_RED)

    def _draw_rules_screen(self):
        self._draw_text_with_shadow("Regras do Jogo", self.font_main_title, 80, main_color=COLOR_YELLOW)
        y_pos = 180
        self._draw_text_with_shadow("Controles", self.font_section_title, y_pos, main_color=COLOR_YELLOW)
        y_pos += 45
        self._draw_text_with_shadow("Jogador 1: Teclas W e S", self.font_body, y_pos)
        y_pos += 30
        self._draw_text_with_shadow("Jogador 2: Setas Cima e Baixo", self.font_body, y_pos)
        y_pos += 30
        self._draw_text_with_shadow("Pressione [P] para Pausar o Jogo", self.font_body, y_pos)
        
        y_pos += 50
        self._draw_text_with_shadow("Power-ups", self.font_section_title, y_pos, main_color=COLOR_YELLOW)
        y_pos += 40
        if self.boost_fire_img:
            self.boost_fire_img.x, self.boost_fire_img.y = 300, y_pos
            self.boost_fire_img.draw()
            self._draw_text_with_shadow("Aumenta a velocidade da bola", self.font_body, y_pos + 15, x_center=510)
        y_pos += 40
        if self.boost_ice_img:
            self.boost_ice_img.x, self.boost_ice_img.y = 280, y_pos
            self.boost_ice_img.draw()
            self._draw_text_with_shadow("Retorna a bola à velocidade inicial", self.font_body, y_pos + 15, x_center=510)
        y_pos += 60
        self._draw_text_with_shadow("Objetivo", self.font_section_title, y_pos, main_color=COLOR_YELLOW)
        y_pos += 30
        self._draw_text_with_shadow(f"Marque {MAX_SCORE} gols para vencer a partida!", self.font_body, y_pos)
        y_pos += 40
        self._draw_text_with_shadow("Pressione ESC para Voltar", self.font_body, y_pos, main_color=COLOR_RED)

    def _draw_difficulty_menu(self):
        self._draw_text_with_shadow("Selecione a Dificuldade", self.font_main_title, 160, main_color=COLOR_YELLOW)
        self._draw_text_with_shadow("[1] Fácil", self.font_section_title, 270)
        self._draw_text_with_shadow("[2] Médio", self.font_section_title, 320)
        self._draw_text_with_shadow("[3] Difícil", self.font_section_title, 370)
        self._draw_text_with_shadow("Pressione ESC para Voltar", self.font_body, 440, main_color=COLOR_RED)

    def _draw_character_selection(self, game_data):
        self._draw_text_with_shadow("Escolha os Jogadores", self.font_main_title, 70, main_color=COLOR_YELLOW)

        panel_width = 320
        panel_height = 380
        panel_y = 125
        p1_panel_x = (self.window.width * 0.25) - (panel_width / 2)
        p2_panel_x = (self.window.width * 0.75) - (panel_width / 2)

        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(150)  
        panel_surface.fill(COLOR_BLACK)
        pygame.draw.rect(panel_surface, COLOR_YELLOW, panel_surface.get_rect(), 3)

        self.window.screen.blit(panel_surface, (p1_panel_x, panel_y))
        self.window.screen.blit(panel_surface, (p2_panel_x, panel_y))

        p1_index = game_data.get("p1_char_index", 0)
        p2_index = game_data.get("p2_char_index", 1)
        selecting_for = game_data.get("selecting_for", 1)
        game_mode = game_data.get("game_mode")
        is_p1_selecting = (selecting_for == 1 or game_mode == GameMode.PVP)
        is_p2_selecting = (selecting_for == 2 or game_mode == GameMode.PVP)

        self._draw_player_selection_box(p1_index, 1, is_p1_selecting, game_mode)
        self._draw_player_selection_box(p2_index, 2, is_p2_selecting, game_mode)

        instr_panel_width = 350
        instr_panel_height = 90
        instr_panel_x = (self.window.width - instr_panel_width) / 2
        instr_panel_y = 510

        instr_panel_surface = pygame.Surface((instr_panel_width, instr_panel_height))
        instr_panel_surface.fill(COLOR_BLACK)
        self.window.screen.blit(instr_panel_surface, (instr_panel_x, instr_panel_y))

        y_pos_nav = 525
        y_pos_action = 550
        y_pos_esc = 575

        if game_mode == GameMode.PVP:
            self._draw_text_with_shadow("A/D e Setas para Mudar", self.font_body, y_pos_nav)
            self._draw_text_with_shadow("Pressione ENTER para Iniciar!", self.font_body, y_pos_action)
        else: # PVE
            if selecting_for > 2:
                 self._draw_text_with_shadow("Pressione ENTER para escolher a Dificuldade", self.font_body, y_pos_action)
            else:
                self._draw_text_with_shadow("Setas para Mudar", self.font_body, y_pos_nav)
                self._draw_text_with_shadow("Pressione ENTER para Confirmar", self.font_body, y_pos_action)
        
        self._draw_text_with_shadow("Pressione ESC para Voltar", self.font_body, y_pos_esc, main_color=COLOR_RED)

    def _draw_player_selection_box(self, char_index, player_num, is_selected, game_mode=None):
        char_data = CHARACTERS[char_index]
        char_img = self.character_images[char_index]
        flag_img = self.flag_images.get(char_data["flag_path"])
        box_x_center = self.window.width * (0.25 if player_num == 1 else 0.75)

        line_half_width = 150
        line_color = COLOR_YELLOW
        line_thickness = 2
        
        pygame.draw.line(self.window.screen, line_color, (box_x_center - line_half_width, 185), (box_x_center + line_half_width, 185), line_thickness)
        
        pygame.draw.line(self.window.screen, line_color, (box_x_center - line_half_width, 340), (box_x_center + line_half_width, 340), line_thickness)

        title = f"Jogador {player_num}" if player_num == 1 or game_mode == GameMode.PVP else "Oponente (IA)"
        self._draw_text_with_shadow(title, self.font_body, 160, x_center=box_x_center)

        char_img.x = box_x_center - char_img.width / 2
        char_img.y = 205
        char_img.draw()

        self._draw_text_with_shadow(char_data["name"], self.font_section_title, 310, x_center=box_x_center)

        if flag_img:
            flag_img.x = box_x_center - flag_img.width / 2
            flag_img.y = 355
            flag_img.draw()

        self._draw_text_with_shadow(char_data["team_name"], self.font_body, 430, x_center=box_x_center)

        if is_selected:
            controls = "<   >" if player_num == 1 and game_mode == GameMode.PVP else "<   >"
            self._draw_text_with_shadow(controls, self.font_section_title, 470, x_center=box_x_center, main_color=COLOR_YELLOW)

    def _draw_game_ui(self, game_data):
        if not self.scoreboard_image: return
        self.scoreboard_image.draw()

        p1_data = CHARACTERS[game_data.get("p1_char_index", 0)]
        p2_data = CHARACTERS[game_data.get("p2_char_index", 1)]
        scores = game_data.get("scores", {"left": 0, "right": 0})
        match_time = game_data.get("match_time", 0)
        scoreboard_y_offset = 13

        p1_flag_img = self.flag_images.get(p1_data["flag_path"])
        if p1_flag_img:
            flag_surface = pygame.transform.scale(p1_flag_img.image, (int(25 * (p1_flag_img.width / p1_flag_img.height)), 25))
            flag_x = self.scoreboard_image.x + 6
            self.window.screen.blit(flag_surface, (flag_x, scoreboard_y_offset))
            abbr_x = flag_x + flag_surface.get_width() + 10
            abbr_surface = self.font_body.render(p1_data["team_name"][:3], True, COLOR_WHITE)
            self.window.screen.blit(abbr_surface, (abbr_x, scoreboard_y_offset))

        p2_flag_img = self.flag_images.get(p2_data["flag_path"])
        if p2_flag_img:
            flag_surface = pygame.transform.scale(p2_flag_img.image, (int(25 * (p2_flag_img.width / p2_flag_img.height)), 25))
            flag_x = self.scoreboard_image.x + self.scoreboard_image.width - flag_surface.get_width() - 6
            self.window.screen.blit(flag_surface, (flag_x, scoreboard_y_offset))
            abbr_surface = self.font_body.render(p2_data["team_name"][:3], True, COLOR_WHITE)
            abbr_x = flag_x - abbr_surface.get_width() - 10
            self.window.screen.blit(abbr_surface, (abbr_x, scoreboard_y_offset))

        score_text = f"{scores['left']}   -   {scores['right']}"
        score_surface = self.font_score_numbers.render(score_text, True, COLOR_WHITE)
        score_rect = score_surface.get_rect(center=(self.scoreboard_image.x + self.scoreboard_image.width / 2, scoreboard_y_offset + 11))
        self.window.screen.blit(score_surface, score_rect)

        minutes, seconds = divmod(int(match_time), 60)
        time_text = f"{minutes:02d}:{seconds:02d}"
        time_surface = self.font_body.render(time_text, True, COLOR_BLACK)
        time_rect = time_surface.get_rect(center=(self.scoreboard_image.x + self.scoreboard_image.width / 2, 7))
        self.window.screen.blit(time_surface, time_rect)

    def _draw_game_elements(self, game_data):
        for trail in game_data.get("ball_trails", []): trail.draw()
        for entity in ["player1", "player2", "ball"]:
            if game_data.get(entity): game_data[entity].draw()
        active_powerup = game_data.get("active_powerup")
        if active_powerup and active_powerup.is_active: active_powerup.draw()

    def _draw_goal_overlay(self, game_data):
        overlay = pygame.Surface((self.window.width, self.window.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.window.screen.blit(overlay, (0, 0))

        if self.goal_animation_frames:
            self.goal_animation_timer += game_data.get("delta_time", 0) * GOAL_ANIM_SPEED
            self.current_goal_frame = int(self.goal_animation_timer) % len(self.goal_animation_frames)
            frame_image = self.goal_animation_frames[self.current_goal_frame]
            frame_rect = frame_image.get_rect(center=(self.window.width / 2, self.window.height / 2))
            self.window.screen.blit(frame_image, frame_rect)
        else:
            self._draw_text_with_shadow("GOL!", self.font_main_title, self.window.height / 2 - 60, main_color=COLOR_YELLOW)

    def _draw_game_over_overlay(self, game_data):
        overlay = pygame.Surface((self.window.width, self.window.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.window.screen.blit(overlay, (0, 0))
        
        scores = game_data.get("scores", {"left": 0, "right": 0})
        p1_data = CHARACTERS[game_data.get("p1_char_index", 0)]
        p2_data = CHARACTERS[game_data.get("p2_char_index", 1)]
        winner_name = p1_data["team_name"] if scores['left'] > scores['right'] else p2_data["team_name"]
        match_time = game_data.get("match_time", 0)
        
        y_pos = 120
        self._draw_text_with_shadow("FIM DE JOGO", self.font_main_title, y_pos)
        y_pos += 80
        self._draw_text_with_shadow(f"{winner_name} VENCEU!", self.font_section_title, y_pos, main_color=COLOR_YELLOW)
        y_pos += 120
        
        score_left_surface = self.font_main_title.render(str(scores['left']), True, COLOR_WHITE)
        score_right_surface = self.font_main_title.render(str(scores['right']), True, COLOR_WHITE)
        separator_surface = self.font_main_title.render("X", True, COLOR_WHITE)
        
        center_x = self.window.width / 2
        
        score_offset = 60
        flag_offset = 120
        
        score_left_rect = score_left_surface.get_rect(center=(center_x - score_offset, y_pos))
        score_right_rect = score_right_surface.get_rect(center=(center_x + score_offset, y_pos))
        separator_rect = separator_surface.get_rect(center=(center_x, y_pos))

        p1_flag_img = self.flag_images.get(p1_data["flag_path"])
        if p1_flag_img:
            flag_height = 50
            p1_flag_surface = pygame.transform.scale(p1_flag_img.image, (int(flag_height * (p1_flag_img.width / p1_flag_img.height)), flag_height))
            p1_flag_rect = p1_flag_surface.get_rect(center=(center_x - flag_offset, y_pos))
            self.window.screen.blit(p1_flag_surface, p1_flag_rect)

        p2_flag_img = self.flag_images.get(p2_data["flag_path"])
        if p2_flag_img:
            flag_height = 50
            p2_flag_surface = pygame.transform.scale(p2_flag_img.image, (int(flag_height * (p2_flag_img.width / p2_flag_img.height)), flag_height))
            p2_flag_rect = p2_flag_surface.get_rect(center=(center_x + flag_offset, y_pos))
            self.window.screen.blit(p2_flag_surface, p2_flag_rect)

        self.window.screen.blit(score_left_surface, score_left_rect)
        self.window.screen.blit(score_right_surface, score_right_rect)
        self.window.screen.blit(separator_surface, separator_rect)
        
        y_pos += 80
        minutes, seconds = divmod(int(match_time), 60)
        time_text = f"Tempo de Partida: {minutes:02d}:{seconds:02d}"
        self._draw_text_with_shadow(time_text, self.font_section_title, y_pos)
        y_pos += 80
        self._draw_text_with_shadow("Pressione ENTER para Jogar Novamente", self.font_body, y_pos)
        self._draw_text_with_shadow("Pressione ESC para o Menu Principal", self.font_body, y_pos + 40, main_color=COLOR_RED)

    def _draw_pause_overlay(self):
        overlay = pygame.Surface((self.window.width, self.window.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.window.screen.blit(overlay, (0, 0))
        
        y_pos_title = 200
        y_pos_continue = 300
        y_pos_restart = 350
        y_pos_menu = 400

        self._draw_text_with_shadow("JOGO PAUSADO", self.font_main_title, y_pos_title, main_color=COLOR_YELLOW)
        
        self._draw_text_with_shadow("[P] para Continuar", self.font_section_title, y_pos_continue)
        self._draw_text_with_shadow("[R] para Reiniciar", self.font_section_title, y_pos_restart)
        self._draw_text_with_shadow("[ESC] para Voltar ao Menu", self.font_section_title, y_pos_menu, main_color=COLOR_RED)