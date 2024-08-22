import pygame
import csv
import sys
import random
import pygame_gui

# Initialize Pygame
pygame.init()

# Define variables
WIDTH, HEIGHT = 551, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flap game")
manager = pygame_gui.UIManager((WIDTH, HEIGHT))
text_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((40, 200), (500, 50)),
    manager=manager,
    object_id='main_text_entry'
)
clock = pygame.time.Clock()

# Start
def show_user_name(user_name):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

        SCREEN.fill("white")

        new_text = pygame.font.SysFont("Times New Roman", 25, bold=True).render(
            f"Hello {user_name}! Welcome to my game\n   Press any key to continue",
            True,
            "black"
        )
        new_text_rect = new_text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        SCREEN.blit(new_text, new_text_rect)

        clock.tick(60)
        pygame.display.update()

# Login page
def get_user_name():
    while True:
        UI_REFRESH_RATE = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and event.ui_object_id == 'main_text_entry':
                username = event.text
                with open('score.csv', 'a', newline='') as file:
                    w = csv.writer(file)
                    w.writerow([username])
                show_user_name(username)
                return

            manager.process_events(event)

        SCREEN.fill("pink")

        manager.update(UI_REFRESH_RATE)
        manager.draw_ui(SCREEN)

        welcome_text = pygame.font.SysFont("Times New Roman", 25, bold=True).render(
            "Enter a username", True, "white"
        )
        welcome_text_rect = welcome_text.get_rect(center=(WIDTH / 4, HEIGHT / 4))
        SCREEN.blit(welcome_text, welcome_text_rect)

        cont_text = pygame.font.SysFont("Times New Roman", 20).render(
            "Press 'Enter' once done", True, "black"
        )
        cont_text_rect = cont_text.get_rect(center=(WIDTH / 2, HEIGHT / 2.7))
        SCREEN.blit(cont_text, cont_text_rect)

        pygame.display.update()

# Run the login page
get_user_name()

# Game initialization
clock = pygame.time.Clock()

# Window
win_height = 720
win_width = 551
window = pygame.display.set_mode((win_width, win_height))

# Images
bird_images = [pygame.image.load("flap/bird_down.png"),
               pygame.image.load("flap/bird_mid.png"),
               pygame.image.load("flap/bird_up.png")]
skyline_image = pygame.image.load("flap/backgroundbeach.png")
ground_image = pygame.image.load("flap/g.png")
top_pipe_image = pygame.image.load("flap/pipe_top.png")
bottom_pipe_image = pygame.image.load("flap/pipe_bottom.png")
game_over_image = pygame.image.load("flap/game_overpink.png")
start_image = pygame.image.load("flap/start.png")

# Game variables
scroll_speed = 1
bird_start_position = (100, 250)
score = 0
font = pygame.font.SysFont('Times New Roman', 26)
game_stopped = True


class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = bird_images[0]
        self.rect = self.image.get_rect()
        self.rect.center = bird_start_position
        self.image_index = 0
        self.vel = 0
        self.flap = False
        self.alive = True

    def update(self, user_input):
        if self.alive:
            self.image_index += 1
        if self.image_index >= 30:
            self.image_index = 0
        self.image = bird_images[self.image_index // 10]

        self.vel += 0.5
        if self.vel > 7:
            self.vel = 7
        if self.rect.y < 500:
            self.rect.y += int(self.vel)
        if self.vel == 0:
            self.flap = False

        self.image = pygame.transform.rotate(self.image, self.vel * -7)

        if user_input[pygame.K_SPACE] and not self.flap and self.rect.y > 0 and self.alive:
            self.flap = True
            self.vel = -7

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.enter, self.exit, self.passed = False, False, False
        self.pipe_type = pipe_type

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.x <= -win_width:
            self.kill()

        global score
        if self.pipe_type == 'bottom':
            if bird_start_position[0] > self.rect.topleft[0] and not self.passed:
                self.enter = True
            if bird_start_position[0] > self.rect.topright[0] and not self.passed:
                self.exit = True
            if self.enter and self.exit and not self.passed:
                self.passed = True
                score += 1

class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = ground_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.x <= -win_width:
            self.kill()

def quit_game():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

def save_score(username, score):
    with open('score.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow([username, score])

def main():
    global score

    bird = pygame.sprite.GroupSingle()
    bird.add(Bird())

    pipe_timer = 0
    pipes = pygame.sprite.Group()

    x_pos_ground, y_pos_ground = 0, 520
    ground = pygame.sprite.Group()
    ground.add(Ground(x_pos_ground, y_pos_ground))

    run = True
    while run:
        quit_game()

        window.fill((0, 0, 0))

        user_input = pygame.key.get_pressed()

        window.blit(skyline_image, (0, 0))

        if len(ground) <= 2:
            ground.add(Ground(win_width, y_pos_ground))

        pipes.draw(window)
        ground.draw(window)
        bird.draw(window)

        score_text = font.render('Score: ' + str(score), True, pygame.Color(255, 255, 255))
        window.blit(score_text, (20, 20))

        if bird.sprite.alive:
            pipes.update()
            ground.update()
        bird.update(user_input)

        collision_pipes = pygame.sprite.spritecollide(bird.sprites()[0], pipes, False)
        collision_ground = pygame.sprite.spritecollide(bird.sprites()[0], ground, False)
        if collision_pipes or collision_ground:
            bird.sprite.alive = False
            if collision_ground:
                window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2,
                                              win_height // 2 - game_over_image.get_height() // 2))
                score_text = pygame.font.SysFont('Times New Roman', 20).render(f"Your score is {score}", True, pygame.Color(0,0,0.5))
                window.blit(score_text, (win_width// 2 - score_text.get_width() // 2, win_height // 2 + game_over_image.get_height() // 2))

                pygame.display.update()


                waiting_for_restart = True
                while waiting_for_restart:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                score = 0
                                waiting_for_restart = False
                                # Save score to CSV file
                                save_score(username, score)


                                # You can also reset other game variables here if needed

        if pipe_timer <= 0 and bird.sprite.alive:
            x_top, x_bottom = 550, 550
            y_top = random.randint(-600, -480)
            y_bottom = y_top + random.randint(90, 130) + bottom_pipe_image.get_height()
            pipes.add(Pipe(x_top, y_top, top_pipe_image, 'top'))
            pipes.add(Pipe(x_bottom, y_bottom, bottom_pipe_image, 'bottom'))
            pipe_timer = random.randint(180, 250)
        pipe_timer -= 1

        clock.tick(60)
        pygame.display.update()

def menu():
    global game_stopped

    while game_stopped:
        quit_game()

        window.fill((0, 0, 0))
        window.blit(skyline_image, (0, 0))
        window.blit(ground_image, Ground(0, 520))
        window.blit(bird_images[0], (100, 250))
        window.blit(start_image, (win_width // 2 - start_image.get_width() // 2,
                                  win_height // 2 - start_image.get_height() // 2))

        user_input = pygame.key.get_pressed()

        pygame.display.update()



main()

