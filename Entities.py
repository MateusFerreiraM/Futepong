# entities.py
import pygame
import random
import math
from PPlay.sprite import *
from PPlay.gameimage import *
from Constants import *

# ======================================================================================
# --- ENTITY CLASSES (PLAYERS, BALL, ETC.) ---
# ======================================================================================
class Paddle(Sprite):
    def __init__(self, image_file, side, window, speed=PLAYER_INITIAL_SPEED):
        super().__init__(image_file, 1)
        self.image = self.image.convert_alpha()
        self.window = window
        self.original_image = self.image.copy()
        self.original_width = self.width
        self.original_height = self.height
        
        self.squash_timer = 0
        self.squash_duration = 0.25
        self.squash_intensity = 0.30

        self.tilt_angle = 0
        self.max_tilt = 8
        self.is_moving_up = False
        self.is_moving_down = False

        self.initial_speed = speed
        self.speed = speed
        self.side = side

        self.shadow = GameImage(SHADOW_IMAGE)
        shadow_size = int(self.width * 1.2)
        self.shadow.image = pygame.transform.scale(self.shadow.image, (shadow_size, shadow_size))
        self.shadow.width, self.shadow.height = shadow_size, shadow_size

        self.reset_position()

    def reset_position(self):
        if self.side == "left":
            self.x = PLAYER_OFFSET_X
        else:
            self.x = WINDOW_WIDTH - self.original_width - PLAYER_OFFSET_X
        self.y = (WINDOW_HEIGHT / 2) - (self.original_height / 2)

    def move(self, up_key, down_key, keyboard):
        self.is_moving_up = False
        self.is_moving_down = False
        if keyboard.key_pressed(up_key):
            self.y -= self.speed * self.window.delta_time()
            self.is_moving_up = True
        if keyboard.key_pressed(down_key):
            self.y += self.speed * self.window.delta_time()
            self.is_moving_down = True
        self._keep_in_bounds()

    def _keep_in_bounds(self):
        if self.y < 0: self.y = 0
        if self.y + self.original_height > self.window.height:
            self.y = self.window.height - self.original_height

    def trigger_squash(self):
        self.squash_timer = self.squash_duration

    def update_effects(self, delta_time):
        if self.squash_timer > 0:
            self.squash_timer = max(0, self.squash_timer - delta_time)

        target_angle = 0
        if self.is_moving_up:
            target_angle = self.max_tilt
        elif self.is_moving_down:
            target_angle = -self.max_tilt
        self.tilt_angle += (target_angle - self.tilt_angle) * TILT_SPEED * delta_time

    def draw(self):
        transformed_image = self.original_image
        if self.squash_timer > 0:
            progress = 1 - (self.squash_timer / self.squash_duration)
            factor = math.sin(progress * math.pi)
            scale_x = 1 + self.squash_intensity * factor
            scale_y = 1 - self.squash_intensity * factor
            new_size = (int(self.original_width * scale_x), int(self.original_height * scale_y))
            transformed_image = pygame.transform.scale(transformed_image, new_size)

        if abs(self.tilt_angle) > 0.1:
            transformed_image = pygame.transform.rotate(transformed_image, self.tilt_angle)

        final_rect = transformed_image.get_rect()
        final_rect.center = (self.x + self.original_width / 2, self.y + self.original_height / 2)

        self.shadow.x = final_rect.x + 4
        self.shadow.y = final_rect.y + final_rect.height - (self.shadow.height / 2)
        self.shadow.draw()

        self.window.screen.blit(transformed_image, final_rect)

class AI(Paddle):
    def __init__(self, image_file, side, window, speed, difficulty):
        super().__init__(image_file, side, window, speed)
        self.difficulty = difficulty

    def move(self, ball):
        target_y = ball.y + ball.height / 2
        paddle_center = self.y + self.original_height / 2
        dead_zone = 5
        diff = target_y - paddle_center

        self.is_moving_up = False
        self.is_moving_down = False

        if abs(diff) > dead_zone:
            move_speed = self.speed * self.difficulty * self.window.delta_time()
            if diff > 0:
                self.y += move_speed
                self.is_moving_down = True
            else:
                self.y -= move_speed
                self.is_moving_up = True
        self._keep_in_bounds()

class Ball(Sprite):
    def __init__(self, image_file, speed=BALL_INITIAL_SPEED):
        super().__init__(image_file, 1)
        self.image = self.image.convert_alpha()
        self.initial_speed = speed
        self.velocity_x = speed
        self.velocity_y = speed
        self.shadow = GameImage(SHADOW_IMAGE)
        shadow_size = int(self.width * 1.5)
        self.shadow.image = pygame.transform.scale(self.shadow.image, (shadow_size, shadow_size))
        self.shadow.width, self.shadow.height = shadow_size, shadow_size

    def reset(self, window, direction=1):
        self.x = window.width / 2 - self.width / 2
        self.y = window.height / 2 - self.height / 2
        self.velocity_x = self.initial_speed * direction
        self.velocity_y = self.initial_speed * random.choice([-1, 1])

    def move(self, window):
        self.x += self.velocity_x * window.delta_time()
        self.y += self.velocity_y * window.delta_time()
        if self.y <= 0 or self.y + self.height >= window.height:
            self.velocity_y *= -1
            self.y = 0 if self.y <= 0 else window.height - self.height
        if self.x + self.width < 0: return "goal_right"
        if self.x > window.width: return "goal_left"
        return None

    def handle_paddle_collision(self, paddle):
        if self.collided(paddle):
            if self.velocity_x < 0: self.x = paddle.x + paddle.original_width
            else: self.x = paddle.x - self.width
            
            current_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            self.velocity_x *= -1
            
            offset = (self.y + self.height / 2) - (paddle.y + paddle.original_height / 2)
            normalized_offset = offset / (paddle.original_height / 2)
            self.velocity_y = current_speed * normalized_offset * 0.7
            
            new_magnitude = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            if new_magnitude > 0:
                dir_x = self.velocity_x / new_magnitude
                dir_y = self.velocity_y / new_magnitude
                self.velocity_x = dir_x * current_speed
                self.velocity_y = dir_y * current_speed
            return True
        return False

    def draw(self):
        self.shadow.x = self.x + 3
        self.shadow.y = self.y + 3
        self.shadow.draw()
        super().draw()

class PowerUp(Sprite):
    def __init__(self, image_file, power_type, size=(40, 40)):
        try:
            super().__init__(image_file, 1)
        except pygame.error:
            print(f"WARNING: Image file not found at '{image_file}'.")
            super().__init__("images/boost/bola.png", 1)
            self.image.set_alpha(0)

        self.image = self.image.convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.type = power_type
        self.is_active = False

    def spawn(self, window):
        self.x = random.randint(int(window.width * 0.25), int(window.width * 0.75) - self.width)
        self.y = random.randint(int(window.height * 0.1), int(window.height * 0.9) - self.height)
        self.is_active = True

    def apply_effect(self, ball):
        self.is_active = False
        current_velocity_magnitude = math.sqrt(ball.velocity_x**2 + ball.velocity_y**2)
        if current_velocity_magnitude == 0: return
        dir_x = ball.velocity_x / current_velocity_magnitude
        dir_y = ball.velocity_y / current_velocity_magnitude
        if self.type == 'SPEED_BOOST':
            new_speed = current_velocity_magnitude * 1.3
            ball.velocity_x = dir_x * new_speed
            ball.velocity_y = dir_y * new_speed
        elif self.type == 'SLOW_BALL':
            ball.velocity_x = dir_x * ball.initial_speed
            ball.velocity_y = dir_y * ball.initial_speed

class BallTrail(Sprite):
    def __init__(self, image, position):
        super().__init__("images/boost/bola.png", 1)
        self.image = image.copy()
        self.image = self.image.convert_alpha()
        self.x, self.y = position
        self.lifespan = 0.4
        self.initial_alpha = 120

    def update(self, delta_time):
        self.lifespan -= delta_time
        self.alpha = self.initial_alpha * (self.lifespan / 0.4)
        if self.alpha < 0: self.alpha = 0
        self.image.set_alpha(self.alpha)