# Tower Defense: Bear vs. Hunters, a game where you, the bear, defend your cub from hunters by throwing stones at them!
__version__ = '02/12/2025'
__author__ = 'Kayla Cao'

#my flint sessions are here:
# https://app.flintk12.com/activity/pygame-debug-le-1fe068/session/1c0a2697-fc30-4c50-ad34-ffb100283e5c
# https://app.flintk12.com/activity/pygame-debug-le-1fe068/session/1b0ae618-4f11-4cd0-b91c-311d00223566
# https://app.flintk12.com/activity/pygame-debug-le-1fe068/session/91661eb7-4f3f-487e-8017-3b4fa08b5542
# https://app.flintk12.com/activity/pygame-debug-le-1fe068/session/979163c2-1bca-4e17-9669-1d5a13ee34d6

import pygame
import random
from HighScore import HighScore
from game_over_sequence import *

def load_scores():
    """Load high scores from file, create file if it doesn't exist"""
    try:
        with open("scores.txt", "r") as f:
            scores = []
            for line in f:
                temp = line.split()
                scores.append(HighScore(temp[0], int(temp[1])))
        scores.sort(reverse=True)
        return scores
    except FileNotFoundError:
        with open("scores.txt", "w") as f:
            pass
        return []

def load_assets():
    """Load all game assets"""
    assets = {'images': {}, 'sounds': {}}

    # Load and scale images with convert_alpha for transparency
    try:
        # Load bear
        bear_img = pygame.image.load('img/madbear.png').convert_alpha()
        assets['images']['bear'] = pygame.transform.scale(bear_img, (130, 200))

        # Load baby
        baby_img = pygame.image.load('img/babybear.png').convert_alpha()
        assets['images']['baby'] = pygame.transform.scale(baby_img, (100, 150))

        # Load hunter
        hunter_img = pygame.image.load('img/hunter.png').convert_alpha()
        assets['images']['hunter'] = pygame.transform.scale(hunter_img, (100, 100))

        # Load stones
        assets['images']['stones'] = []
        for i in range(1, 6):
            stone_img = pygame.image.load(f'img/stone{i}.png').convert_alpha()
            assets['images']['stones'].append(pygame.transform.scale(stone_img, (60, 60)))

    except Exception as e:
        print(f"Error loading images: {e}")
        return None

    # Load sounds
    sound_files = {
        'hit': ('sounds/hit.wav', 0.4),
        'trombone': ('sounds/cartoon-trombone-fail.wav', 0.3),
        'yay': ('sounds/cartoon-yay.wav', 0.5)
    }

    for sound_name, (file_path, volume) in sound_files.items():
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(volume)
            assets['sounds'][sound_name] = sound
        except Exception as e:
            print(f"Could not load {sound_name} sound: {e}")
            assets['sounds'][sound_name] = None

    return assets

def spawn_hunter(hunter_image, window_width):
    """Create and add a new hunter"""
    hunter_rect = hunter_image.get_rect()
    hunter_rect.x = random.randint(0, window_width - 100)
    hunter_rect.y = -200
    return hunter_rect

def quit_game():
    """Clean up and quit the game"""
    pygame.mixer.quit()
    pygame.quit()

def main():
    pygame.init()
    pygame.mixer.init()

    # Initialize game controllers
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        joystick.init()

    # Window setup
    window_width = 600
    window_height = 800
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Tower Defense")

    # Load all assets
    assets = load_assets()
    if assets is None:
        return

    # Create game objects
    bear_rect = assets['images']['bear'].get_rect()
    bear_rect.center = (window_width // 2, window_height - 100)

    baby_rect = assets['images']['baby'].get_rect()
    baby_rect.center = (window_width // 2, window_height - 50)

    hunters = []  # List to store hunter rectangles
    stones = []   # List to store stone rectangles and images

    # Game variables
    hunter_spawn_timer = 0
    stone_cooldown = 0
    score = 0
    lives = 3
    paused = False
    scores = load_scores()

    # Constants
    HUNTER_SPEED = 4
    STONE_SPEED = 7
    STONE_COOLDOWN = 30
    BEAR_SPEED = 5
    FPS = 60

    # Fonts
    font = pygame.font.Font(None, 74)
    score_font = pygame.font.Font(None, 30)

    # Clock for frame rate control
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 7:  # Start button
                    paused = not paused

        screen.fill((0, 0, 0))

        if not paused:
            # Update stone cooldown
            if stone_cooldown > 0:
                stone_cooldown -= 1

            # Handle input
            keys = pygame.key.get_pressed()

            # Movement with both keyboard and controller
            move_amount = 0
            if keys[pygame.K_LEFT]:
                move_amount = -BEAR_SPEED
            elif keys[pygame.K_RIGHT]:
                move_amount = BEAR_SPEED

            # Controller input
            if joysticks:
                # Get horizontal axis value (-1.0 to 1.0)
                axis = joysticks[0].get_axis(0)
                # Add dead zone to prevent drift
                if abs(axis) > 0.2:
                    move_amount = axis * BEAR_SPEED

            bear_rect.x += move_amount
            bear_rect.clamp_ip(screen.get_rect())

            # Stone throwing with both keyboard and controller
            if (keys[pygame.K_UP] or
                (joysticks and joysticks[0].get_button(0))) and stone_cooldown == 0:
                stone_image = random.choice(assets['images']['stones'])
                stone_rect = stone_image.get_rect()
                stone_rect.centerx = bear_rect.centerx
                stone_rect.top = bear_rect.top
                stones.append((stone_rect, stone_image))
                stone_cooldown = STONE_COOLDOWN

            # Spawn hunters
            hunter_spawn_timer += 1
            spawn_delay = random.randint(45, 100)
            if hunter_spawn_timer >= spawn_delay:
                hunter_spawn_timer = 0
                hunters.append(spawn_hunter(assets['images']['hunter'], window_width))

            # Update hunters
            for hunter in hunters[:]:
                hunter.y += HUNTER_SPEED
                if hunter.top > window_height:
                    hunters.remove(hunter)
                    lives -= 1
                    if lives <= 0:
                        if assets['sounds']['trombone']:
                            assets['sounds']['trombone'].play()
                        running = False

            # Update stones and check collisions
            for stone_rect, stone_image in stones[:]:
                stone_rect.y -= STONE_SPEED
                if stone_rect.bottom < 0:
                    stones.remove((stone_rect, stone_image))
                else:
                    # Check collisions with hunters
                    for hunter in hunters[:]:
                        if stone_rect.colliderect(hunter):
                            if assets['sounds']['hit']:
                                assets['sounds']['hit'].play()
                            hunters.remove(hunter)
                            stones.remove((stone_rect, stone_image))
                            score += 1
                            break

            # Check collisions with bear/baby
            for hunter in hunters[:]:
                if hunter.colliderect(bear_rect) or hunter.colliderect(baby_rect):
                    hunters.remove(hunter)
                    lives -= 1
                    if lives <= 0:
                        if assets['sounds']['trombone']:
                            assets['sounds']['trombone'].play()
                        running = False

            # Draw game objects
            for hunter in hunters:
                screen.blit(assets['images']['hunter'], hunter)
            for stone_rect, stone_image in stones:
                screen.blit(stone_image, stone_rect)
            screen.blit(assets['images']['bear'], bear_rect)
            screen.blit(assets['images']['baby'], baby_rect)

        else:
            # Draw pause screen
            draw_text_with_bg(screen, 'PAUSED', font, (255, 0, 0),
                            (window_width // 2, window_height // 2),
                            border_color=(255, 0, 0))

        # draw lives and score with matching border colors
        draw_text_with_bg(screen, f'Score: {score}', score_font, (255, 0, 0),
                         (window_width - 70, 25), border_color=(255, 0, 0))
        draw_text_with_bg(screen, f'Lives: {lives}', score_font, (255, 255, 255),
                         (50, 25), border_color=(255, 255, 255))

        pygame.display.flip()

    #after game ends
    # Game over sequence
    screen.fill((0, 0, 0))
    pygame.time.wait(1500)  # Wait for trombone sound

    # Get user input and save score
    user = user_input(screen, font, score, window_width, window_height, scores)

    # Check if score is in top 5
    scores.sort(reverse=True)
    is_top_5 = len(scores) < 5 or any(score >= s.score for s in scores[:5])

    # Play celebration sound if in top 5
    if is_top_5 and user and assets['sounds']['yay']:
        assets['sounds']['yay'].play()
        pygame.time.wait(500)

    # Show high scores
    highscores_screen(screen, font, score, window_width, window_height, scores)

    quit_game()

if __name__ == '__main__':
    main()