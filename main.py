import pygame
import sys
import os
import random

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 500
PIPE_HEIGHT = 400


# Oyun ici hızlar
BACKGROUND_SPEED = 1
PIPE_START_SPEED = 3
PIPE_MAX_SPEED = 9
framepersecond = 32

# Yer çekimi ivmesi
GRAVITY = 2
MAX_FALL_SPEED = 20


def calculate_upper_pipe_y_and_gap_size():
    return random.randint(-200, -20), random.randint(25, 45)

def draw_background(screen, background_img, background_rects):
    for background_rect in background_rects:
        screen.blit(background_img, background_rect)

def draw_bird(screen, bird_img, bird_rect):
    screen.blit(bird_img, bird_rect)

def draw_pipes(screen, pipe_img, upper_pipes, lower_pipes):
    for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
        screen.blit(pipe_img[0], (upper_pipe['x'], upper_pipe['y']))
        screen.blit(pipe_img[1], (lower_pipe['x'], lower_pipe['y']))
    
def check_add_pipe(upper_pipes, lower_pipes):
    rightmost_x = max(upper_pipe['x'] for upper_pipe in upper_pipes)
    if rightmost_x <= SCREEN_WIDTH * 3 / 4:
        pipe_y, gap_size = calculate_upper_pipe_y_and_gap_size()
        upper_pipes.append({'x': SCREEN_WIDTH, 'y': pipe_y})
        lower_pipes.append({'x': SCREEN_WIDTH, 'y': pipe_y + gap_size + PIPE_HEIGHT})

def check_remove_pipe(upper_pipes, lower_pipes, pipe_img):
    for u_pipe, l_pipe in zip(upper_pipes, lower_pipes):
        if u_pipe['x'] + pipe_img[0].get_width() < 0:
            upper_pipes.remove(u_pipe)
            lower_pipes.remove(l_pipe)
   
def handle_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "toggle_pause"
            elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                return "flap"  # "space" veya "yukarı ok" tuşlarına basıldığında kuşu zıplat
            elif event.key == pygame.K_r:  # "r" tuşuna basıldığında oyunu yeniden başlat
                return "restart"
            elif event.key == pygame.K_q:  # "q" tuşuna basıldığında oyunu kapat
                pygame.quit()
                sys.exit()
    return None

def update_game_state(screen, bird_rect, bird_img, upper_pipes, lower_pipes, pipe_img, background_rects, score, pipe_speed):
    # Kuşun çarpma kontrolü
    if bird_rect.top <= 0 or bird_rect.bottom >= SCREEN_HEIGHT:
        return True, score, pipe_speed
        
    bird_collision_rect = pygame.Rect(bird_rect.x + 5, bird_rect.y + 5, bird_rect.width - 10, bird_rect.height - 10)
    playerMidPos = SCREEN_WIDTH // 5 + bird_img.get_width()/2
    
    for u_pipe, l_pipe in zip(upper_pipes, lower_pipes):
        upper_pipe_rect = pygame.Rect(u_pipe['x'], u_pipe['y'], pipe_img[0].get_width() - 20, pipe_img[0].get_height() - 10)
        lower_pipe_rect = pygame.Rect(l_pipe['x'], l_pipe['y'], pipe_img[1].get_width() - 20, pipe_img[1].get_height() - 10)
        
        if bird_collision_rect.colliderect(upper_pipe_rect) or bird_collision_rect.colliderect(lower_pipe_rect):
            return True, score, pipe_speed
            
        pipeMidPos = u_pipe['x'] + pipe_img[0].get_width() / 2
        if pipeMidPos <= playerMidPos < pipeMidPos + 4: 
            score += 1
            if score % 2 == 0:
                pipe_speed += 1
        
    # Arkaplanları kaydır
    for background_rect in background_rects:
        background_rect.x -= BACKGROUND_SPEED
        if background_rect.right <= 0:
            background_rect.x = SCREEN_WIDTH
            
    return False, score, pipe_speed
    
def game_loop(screen, background_img, bird_img, bird_rect, background_rects, pipe_img, upper_pipes, lower_pipes):
    paused = False
    framepersecond_clock = pygame.time.Clock()
    score = 0
    
    bird_velocity_y = 0
    bird_flap_velocity = -15
    pipe_speed = PIPE_START_SPEED
    
    while True:
        action = handle_input()
        if action == "toggle_pause":
            paused = not paused
        elif action == "flap":
            bird_velocity_y = bird_flap_velocity  # Kuşu zıplat
        elif action == "restart":
            main()

        if not paused:
            collision, score, pipe_speed = update_game_state(screen, bird_rect, bird_img, upper_pipes, lower_pipes, pipe_img, background_rects, score, pipe_speed)
            if collision:
                paused = True
                if bird_rect.top <= 0:
                    bird_rect.top = 0
                elif bird_rect.bottom >= SCREEN_HEIGHT:
                    bird_rect.bottom = SCREEN_HEIGHT

            bird_velocity_y += GRAVITY
            bird_velocity_y = min(bird_velocity_y, MAX_FALL_SPEED)  # Düşme hızını maksimum düşme hızıyla sınırla
            bird_rect.y += bird_velocity_y

            for background_rect in background_rects:
                background_rect.x -= BACKGROUND_SPEED
                if background_rect.right <= 0:
                    background_rect.x = SCREEN_WIDTH

            for u_pipe, l_pipe in zip(upper_pipes, lower_pipes):
                u_pipe['x'] -= pipe_speed
                l_pipe['x'] -= pipe_speed

            check_add_pipe(upper_pipes, lower_pipes)
            
            check_remove_pipe(upper_pipes, lower_pipes, pipe_img)

            screen.fill((0, 0, 0))

            draw_background(screen, background_img, background_rects)

            draw_pipes(screen, pipe_img, upper_pipes, lower_pipes)

            draw_bird(screen, bird_img, bird_rect)

            font = pygame.font.Font(None, 36)
            text = font.render("Score: " + str(score), True, (255, 255, 255))
            screen.blit(text, (10, 10))

            pygame.display.update()

        framepersecond_clock.tick(framepersecond)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird")

    background_img = pygame.image.load(os.path.join("images", "background.jpg")).convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    bird_img = pygame.image.load(os.path.join("images", "bird.png")).convert_alpha()
    bird_img = pygame.transform.scale(bird_img, (50, 50))  # Kuş resmini boyutlandır

    pipe_img = (
        pygame.transform.rotate(pygame.image.load(os.path.join("images", "pipe.png")).convert_alpha(), 180),
        pygame.image.load(os.path.join("images", "pipe.png")).convert_alpha()
    )

    bird_rect = bird_img.get_rect()
    bird_rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)  # Ekranın sol ortasında başlat

    bird_width = bird_rect.width
    bird_height = bird_rect.height
    
    background_rects = []
    for i in range(2):
        background_rects.append(background_img.get_rect())

    background_rects[1].x = SCREEN_WIDTH

    upper_pipes = []
    lower_pipes = []
    
    pipe_y, gap_size = calculate_upper_pipe_y_and_gap_size()
    upper_pipes.append({'x': 3 * SCREEN_WIDTH // 4, 'y': pipe_y})
    lower_pipes.append({'x': 3 * SCREEN_WIDTH // 4, 'y': pipe_y + gap_size + PIPE_HEIGHT})

    pipe_y, gap_size = calculate_upper_pipe_y_and_gap_size()
    upper_pipes.append({'x': SCREEN_WIDTH // 2, 'y': pipe_y})
    lower_pipes.append({'x': SCREEN_WIDTH // 2, 'y': pipe_y + gap_size + PIPE_HEIGHT})

    game_loop(screen, background_img, bird_img, bird_rect, background_rects, pipe_img, upper_pipes, lower_pipes)

if __name__ == "__main__":
    main()
