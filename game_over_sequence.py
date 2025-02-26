#functions associated with what happens after the game ends
__version__ = '02/12/2025'
__author__ = 'Kayla Cao'

import pygame
from HighScore import HighScore


def draw_text_with_bg(screen, text, font, color, center_pos, bg_color=(0, 0, 0), border_color=(255, 255, 255)):
    """Helper function to draw text with background border"""
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center_pos)
    bg_rect = text_rect.copy()
    bg_rect.inflate_ip(20, 10)
    pygame.draw.rect(screen, bg_color, bg_rect)
    pygame.draw.rect(screen, border_color, bg_rect, 2)
    screen.blit(text_surf, text_rect)
    return text_rect


def game_over_screen(screen, font, score, window_width, window_height):
    """Draw the game over screen"""
    draw_text_with_bg(screen, 'Game Over! '+ f'Score: {score}', font, (255, 0, 0),
                     (window_width // 2, window_height // 2),
                     bg_color=(0, 0, 0), border_color=(255, 0, 0))


def user_input(screen, font, score, window_width, window_height, scores):
    """Handle user input for name entry"""
    user = ""
    smaller_font = pygame.font.Font(None, 50)
    instructions = [
        ('Enter 3 letters for your name', (255, 255, 255)), #white
        ('Press ENTER when done', (0, 255, 0)), #green
        ('Press ESC to skip', (255, 0, 0)) #red
    ]

    while True:
        screen.fill((0, 0, 0))
        game_over_screen(screen, font, score, window_width, window_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and user:
                    try:
                        scores.append(HighScore(user, score))
                        scores.sort(reverse=True)
                        with open('scores.txt', 'w') as f:
                            f.write('\n'.join(str(s) for s in scores))
                        return user
                    except Exception as e:
                        print(f"Error saving score: {e}")
                        return None
                elif event.key == pygame.K_BACKSPACE and user:
                    user = user[:-1]
                elif len(user) < 3 and event.unicode.isalpha():
                    user += event.unicode.upper()

        # Name entry text (moved up)
        draw_text_with_bg(screen, f'Enter name: {user}', font, (255, 255, 255),
                         (window_width // 2, window_height // 2 - 200),
                         border_color=(255, 255, 255))

        # Instructions with increased spacing
        for i, (text, color) in enumerate(instructions):
            draw_text_with_bg(screen, text, smaller_font, color,
                            (window_width // 2, window_height - 200 + (i * 60)),
                            border_color=color)  # Border color matches text color

        pygame.display.flip()


def highscores_screen(screen, font, score, window_width, window_height, scores):
    """Display high scores screen"""
    smaller_font = pygame.font.Font(None, 50)

    while True:
        screen.fill((0, 0, 0))
        # Title
        draw_text_with_bg(screen, 'HIGH SCORES', font, (255, 255, 0),
                         (window_width // 2, 100),
                         border_color=(255, 255, 0))

        # High scores with increased spacing
        for i, highscore in enumerate(scores[:5]):
            color = (255, 255, 0) if highscore.score == score else (255, 255, 255)
            draw_text_with_bg(screen, f"{i + 1}. {str(highscore)}", smaller_font,
                            color, (window_width // 2, 200 + (i * 70)),  # Increased spacing between scores
                            border_color=color)  # Border color matches text color

        # Exit instruction
        draw_text_with_bg(screen, 'Press any key to exit', smaller_font, (255, 0, 0),
                         (window_width // 2, window_height - 100),
                         border_color=(255, 0, 0))  # Red border matches red text

        pygame.display.flip()

        if any(event.type in (pygame.QUIT, pygame.KEYDOWN)
               for event in pygame.event.get()):
            break