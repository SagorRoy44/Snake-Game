import pygame
from pygame.locals import *
import time
import random

SIZE = 40
BACKGROUND_COLOR = (110, 110, 5)


DIFFICULTY_SETTINGS = {
    "Easy": {"speed": 0.2, "obstacles": 0},
    "Medium": {"speed": 0.15, "obstacles": 2},
    "Hard": {"speed": 0.1, "obstacles": 4},
    "Advance": {"speed": 0.08, "obstacles": 6}
}

class Apple:
    def __init__(self, parent_screen):
        self.image = pygame.image.load("resources/apple.jpg").convert()
        self.parent_screen = parent_screen
        self.move()

    def draw(self):
        self.parent_screen.blit(self.image, (self.x, self.y))
        pygame.display.flip()
    
    def move(self):
        self.x = random.randint(0, 24) * SIZE
        self.y = random.randint(0, 19) * SIZE


class Snake:
    def __init__(self, parent_screen, length):
        self.length = length
        self.parent_screen = parent_screen
        self.block = pygame.image.load("resources/block.jpg").convert()
        self.x = [SIZE] * length
        self.y = [SIZE] * length
        self.direction = 'right'
        
    def increase_length(self):
        self.length += 1
        self.x.append(-1)
        self.y.append(-1)
        
    def draw(self):
        for i in range(self.length):
            self.parent_screen.blit(self.block, (self.x[i], self.y[i]))
        pygame.display.flip()
    
    def move_left(self):
        self.direction = 'left'
        
    def move_right(self):
        self.direction = 'right'
    
    def move_up(self):
        self.direction = 'up'
    
    def move_down(self):
        self.direction = 'down'
    
    def walk(self):
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        if self.direction == 'up':
            self.y[0] -= SIZE
        if self.direction == 'down':
            self.y[0] += SIZE
        if self.direction == 'left':
            self.x[0] -= SIZE
        if self.direction == 'right':
            self.x[0] += SIZE

        # Wrap-around logic
        self.x[0] %= 1520
        self.y[0] %= 800

        self.draw()


class Obstacle:
    def __init__(self, parent_screen, num_obstacles):
        self.parent_screen = parent_screen
        self.block = pygame.image.load("resources/block.jpg").convert()
        self.positions = []
        for _ in range(num_obstacles):
            self.positions.append((random.randint(0, 24) * SIZE, random.randint(0, 19) * SIZE))

    def draw(self):
        for pos in self.positions:
            self.parent_screen.blit(self.block, pos)
        pygame.display.flip()
        
    def check_collision(self, x, y):
        return (x, y) in self.positions


class StructuralBlock:
    def __init__(self, parent_screen, blocks):
        self.parent_screen = parent_screen
        self.block = pygame.image.load("resources/block.jpg").convert()
        self.positions = blocks  

    def draw(self):
        for pos in self.positions:
            self.parent_screen.blit(self.block, pos)
        pygame.display.flip()
        
    def check_collision(self, x, y):
        return (x, y) in self.positions


class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((1520, 800)) 
        pygame.mixer.init()
        self.play_background_music()
        self.snake = Snake(self.surface, 2)
        self.snake.draw()
        self.apple = Apple(self.surface)
        self.apple.draw()
        self.level = 1
        self.difficulty = "Easy" 
        self.speed = DIFFICULTY_SETTINGS[self.difficulty]["speed"]
        self.obstacle = None 
        
        
        self.structural_blocks = StructuralBlock(self.surface, [(4 * SIZE, 4 * SIZE), (5 * SIZE, 4 * SIZE), 
                                                               (6 * SIZE, 4 * SIZE), (7 * SIZE, 4 * SIZE),
                                                               (8 * SIZE, 4 * SIZE)])

    def is_collision(self, x1, y1, x2, y2):
        if x1 >= x2 and x1 < x2 + SIZE:
            if y1 >= y2 and y1 < y2 + SIZE:
                return True
        return False
              
    def play_background_music(self):
        pygame.mixer.music.load("resources/bg_music_1.mp3")
        pygame.mixer.music.play()
              
    def play_sound(self, sound):
        sound = pygame.mixer.Sound(f"resources/{sound}.mp3")
        pygame.mixer.Sound.play(sound) 

    def render_background(self):
        bg = pygame.image.load("resources/background.jpg")
        self.surface.blit(bg, (0, 0))
        
    def update_level(self):
        self.level = (self.snake.length - 2) // 5 + 1
    
    def display_score(self):
        font = pygame.font.SysFont('times new roman', 30)
        score = font.render(f"Score: {self.snake.length - 2}  |  Level: {self.level}  |  Difficulty: {self.difficulty}", True, (255, 255, 255))
        self.surface.blit(score, (1000, 15)) 

    def play(self): 
        self.render_background() 
        self.snake.walk()
        self.apple.draw() 
        self.obstacle.draw()
        self.structural_blocks.draw()
        self.display_score()
        self.update_level()
        pygame.display.flip()
        
        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.play_sound("ding")
            self.snake.increase_length()
            self.apple.move()
        
           
            while self.obstacle.check_collision(self.apple.x, self.apple.y):
                self.apple.move()
        
        
        if self.obstacle.check_collision(self.snake.x[0], self.snake.y[0]):
            self.play_sound('crash')
            raise "Collision with Obstacle Occurred"
        
        
        if self.structural_blocks.check_collision(self.snake.x[0], self.snake.y[0]):
            self.play_sound('crash')
            raise "Collision with Structural Block Occurred"
        
        
        for i in range(1, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                self.play_sound('crash')
                raise "Self-Collision Occurred"
            
    def show_game_over(self):
        self.render_background()
        self.surface.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont('times new roman', 30)
        line1 = font.render(f"Game Over! Your score: {self.snake.length - 2}", True, (0, 0, 0))
        self.surface.blit(line1, (200, 200))
        line2 = font.render("Press Enter to play again or Escape to exit.", True, (0, 0, 0))
        self.surface.blit(line2, (200, 250))
        pygame.display.flip()
    
    def reset(self): 
        self.snake = Snake(self.surface, 2)
        self.apple = Apple(self.surface)
    
    def choose_difficulty(self):
        self.surface.fill((0, 0, 0))
        font = pygame.font.SysFont('times new roman', 50)
        title = font.render("Choose Difficulty", True, (255, 255, 255))
        self.surface.blit(title, (550, 200))

        font = pygame.font.SysFont('times new roman', 35)
        options = ["Easy", "Medium", "Hard", "Advance"]
        for i, option in enumerate(options):
            text = font.render(f"{i + 1}. {option}", True, (255, 255, 255))
            self.surface.blit(text, (650, 300 + i * 60))
        pygame.display.flip()

        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_1:
                        self.difficulty = "Easy"
                        selecting = False
                    elif event.key == K_2:
                        self.difficulty = "Medium"
                        selecting = False
                    elif event.key == K_3:
                        self.difficulty = "Hard"
                        selecting = False
                    elif event.key == K_4:
                        self.difficulty = "Advance"
                        selecting = False
            self.speed = DIFFICULTY_SETTINGS[self.difficulty]["speed"]
            self.obstacle = Obstacle(self.surface, DIFFICULTY_SETTINGS[self.difficulty]["obstacles"])
    
    def run(self):
        self.choose_difficulty()  
        running = True
        pause = False

        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    
                    if event.key == K_RETURN:
                        pygame.mixer.music.unpause()
                        pause = False
                    
                    if not pause:
                        if event.key == K_UP:
                            self.snake.move_up()

                        if event.key == K_DOWN:
                            self.snake.move_down()

                        if event.key == K_LEFT:
                            self.snake.move_left()

                        if event.key == K_RIGHT:
                            self.snake.move_right()
                    
                elif event.type == QUIT:
                    running = False
            
            try:
                if not pause:
                    self.play()
            except Exception as e:
                pygame.mixer.music.pause()
                self.show_game_over()
                pause = True
                self.reset()
            
            time.sleep(self.speed)

if __name__ == "__main__":
    game = Game()
    game.run()
