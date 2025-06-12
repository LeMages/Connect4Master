import pygame
import sys
import numpy as np
import math
from ia import IA_Decision, winning_move, is_valid_move, get_next_open_row
from design import create_gradient_background, create_token_surface, create_grid_surface, find_winning_pieces

# Initialisation de Pygame
pygame.init()

# --- Écran ---
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
FULL_WIDTH, FULL_HEIGHT = screen.get_size()
pygame.display.set_caption("Puissance 4")

# --- Paramètres modifiables ---
ROWS = 6
COLS = 7
AI_THINK_TIME = 5.0

# --- Ressources graphiques (générées dynamiquement) ---
SQUARESIZE = 0
BOARD_WIDTH, BOARD_HEIGHT = 0, 0
OFFSET_X, OFFSET_Y = 0, 0
FONT, SETTINGS_FONT = None, None
BACKGROUND_IMG, GRID_IMG = None, None
RED_TOKEN_IMG, YELLOW_TOKEN_IMG = None, None

# --- Couleurs ---
COLOR_BLUE = (20, 80, 200)
COLOR_RED = (217, 30, 24)
COLOR_YELLOW = (241, 196, 15)
COLOR_WHITE = (240, 240, 240)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GRAY = (160, 160, 160)

# --- Pièces ---
PLAYER_PIECE, AI_PIECE = 1, -1

def update_dimensions():
    """Recalcule les dimensions et régénère les ressources graphiques."""
    global SQUARESIZE, BOARD_WIDTH, BOARD_HEIGHT, OFFSET_X, OFFSET_Y, FONT, SETTINGS_FONT
    global BACKGROUND_IMG, GRID_IMG, RED_TOKEN_IMG, YELLOW_TOKEN_IMG
    
    SQUARESIZE = int(min(FULL_WIDTH / (COLS + 2), FULL_HEIGHT / (ROWS + 3)))
    BOARD_WIDTH = COLS * SQUARESIZE
    BOARD_HEIGHT = (ROWS + 1) * SQUARESIZE
    OFFSET_X = (FULL_WIDTH - BOARD_WIDTH) // 2
    OFFSET_Y = (FULL_HEIGHT - BOARD_HEIGHT) // 2
    
    FONT = pygame.font.SysFont("sans-serif", SQUARESIZE, bold=True)
    SETTINGS_FONT = pygame.font.SysFont("sans-serif", SQUARESIZE // 2, bold=True)

    BACKGROUND_IMG = create_gradient_background(FULL_WIDTH, FULL_HEIGHT, (10, 20, 40), (40, 60, 100))
    GRID_IMG = create_grid_surface(COLS, ROWS, SQUARESIZE, COLOR_BLUE)
    RED_TOKEN_IMG = create_token_surface(SQUARESIZE-10, COLOR_RED)
    YELLOW_TOKEN_IMG = create_token_surface(SQUARESIZE-10, COLOR_YELLOW)

update_dimensions()

def create_board():
    return np.zeros((ROWS, COLS), dtype=int)

def draw_pieces(board, winning_pieces=None, pulse_alpha=0):
    """Dessine les jetons sur le plateau."""
    board_to_draw = np.flip(board, 0)
    for r_disp in range(ROWS):
        for c_disp in range(COLS):
            if board_to_draw[r_disp][c_disp] != 0:
                token_img = RED_TOKEN_IMG if board_to_draw[r_disp][c_disp] == PLAYER_PIECE else YELLOW_TOKEN_IMG
                center_x = OFFSET_X + int(c_disp * SQUARESIZE + SQUARESIZE / 2)
                center_y = OFFSET_Y + int(r_disp * SQUARESIZE + SQUARESIZE / 2) + SQUARESIZE
                
                rect = token_img.get_rect(center=(center_x, center_y))
                screen.blit(token_img, rect)

                # Animation de victoire
                if winning_pieces:
                    # Convertit les coordonnées d'affichage en coordonnées logiques pour la vérification
                    r_logic = ROWS - 1 - r_disp
                    if (r_logic, c_disp) in winning_pieces:
                        # Crée une surcouche brillante de la même taille que le jeton
                        highlight = pygame.Surface(token_img.get_size(), pygame.SRCALPHA)
                        pygame.draw.circle(highlight, (255, 255, 255, pulse_alpha), 
                                           (token_img.get_width() / 2, token_img.get_height() / 2), 
                                           token_img.get_width() / 2)
                        screen.blit(highlight, rect.topleft, special_flags=pygame.BLEND_RGBA_ADD)

def draw_board(board, winning_info=None):
    screen.blit(BACKGROUND_IMG, (0, 0))
    if winning_info:
        draw_pieces(board, winning_info['pieces'], winning_info['alpha'])
    else:
        draw_pieces(board)
    screen.blit(GRID_IMG, (OFFSET_X, OFFSET_Y + SQUARESIZE))

def animate_drop(board, final_row, col, piece):
    x_pos = OFFSET_X + int(col * SQUARESIZE + SQUARESIZE / 2)
    start_y = OFFSET_Y + int(SQUARESIZE / 2)
    end_y = OFFSET_Y + int((ROWS - 1 - final_row) * SQUARESIZE + SQUARESIZE / 2) + SQUARESIZE
    current_y = start_y
    speed = SQUARESIZE / 3 
    
    token_img = RED_TOKEN_IMG if piece == PLAYER_PIECE else YELLOW_TOKEN_IMG
    clock = pygame.time.Clock()

    while current_y < end_y:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

        current_y = min(current_y + speed, end_y)
        
        draw_board(board)
        rect = token_img.get_rect(center=(x_pos, int(current_y)))
        screen.blit(token_img, rect)
        
        pygame.display.update()
        clock.tick(60)

def draw_interactive_button(text, rect, base_color, hover_color, text_color, font, mouse_pos):
    is_hovering = rect.collidepoint(mouse_pos)
    color = hover_color if is_hovering else base_color
    
    pygame.draw.rect(screen, color, rect, border_radius=15)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return is_hovering

def home_screen():
    play_button_rect = pygame.Rect(FULL_WIDTH/2 - 150, FULL_HEIGHT/2 - 60, 300, 70)
    settings_button_rect = pygame.Rect(FULL_WIDTH/2 - 150, FULL_HEIGHT/2 + 30, 300, 70)
    quit_button_rect = pygame.Rect(FULL_WIDTH/2 - 150, FULL_HEIGHT/2 + 120, 300, 70)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        screen.blit(BACKGROUND_IMG, (0, 0))
        title_label = FONT.render("Puissance 4", 1, COLOR_WHITE)
        title_rect = title_label.get_rect(center=(FULL_WIDTH / 2, FULL_HEIGHT / 4))
        screen.blit(title_label, title_rect)

        draw_interactive_button("Jouer", play_button_rect, COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_WHITE, SETTINGS_FONT, mouse_pos)
        draw_interactive_button("Paramètres", settings_button_rect, COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_WHITE, SETTINGS_FONT, mouse_pos)
        draw_interactive_button("Quitter", quit_button_rect, COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_WHITE, SETTINGS_FONT, mouse_pos)
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(mouse_pos): return "play"
                if settings_button_rect.collidepoint(mouse_pos): return "settings"
                if quit_button_rect.collidepoint(mouse_pos): return "quit"

def settings_screen():
    global ROWS, COLS, AI_THINK_TIME

    # Crée des rectangles pour les boîtes de saisie et les boutons +/-
    input_boxes = {
        'Lignes': pygame.Rect(FULL_WIDTH / 2 - 50, FULL_HEIGHT / 2 - 100, 100, 60),
        'Colonnes': pygame.Rect(FULL_WIDTH / 2 - 50, FULL_HEIGHT / 2, 100, 60),
        'Temps IA': pygame.Rect(FULL_WIDTH / 2 - 50, FULL_HEIGHT / 2 + 100, 100, 60)
    }
    buttons = {}
    for key, rect in input_boxes.items():
        buttons[f'{key}_minus'] = pygame.Rect(rect.left - 80, rect.top, 60, 60)
        buttons[f'{key}_plus'] = pygame.Rect(rect.right + 20, rect.top, 60, 60)

    back_button_rect = pygame.Rect(FULL_WIDTH/2 - 150, FULL_HEIGHT - 150, 300, 70)
    
    # Valeurs temporaires pour les paramètres
    temp_values = {'Lignes': ROWS, 'Colonnes': COLS, 'Temps IA': AI_THINK_TIME}

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(BACKGROUND_IMG, (0, 0))

        title = FONT.render("Paramètres", True, COLOR_WHITE)
        screen.blit(title, title.get_rect(center=(FULL_WIDTH / 2, FULL_HEIGHT / 4)))

        # Dessin des libellés et des valeurs
        for key, value in temp_values.items():
            rect = input_boxes[key]
            # Libellé
            label = SETTINGS_FONT.render(key, True, COLOR_WHITE)
            screen.blit(label, label.get_rect(center=(rect.centerx, rect.top - 30)))
            # Valeur dans la boîte
            pygame.draw.rect(screen, (0,0,0,100), rect) # Fond sombre semi-transparent
            val_text = f"{value:.1f}" if key == 'Temps IA' else str(value)
            val_surf = SETTINGS_FONT.render(val_text, True, COLOR_WHITE)
            screen.blit(val_surf, val_surf.get_rect(center=rect.center))
            
            # Boutons +/-
            draw_interactive_button("-", buttons[f'{key}_minus'], COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_WHITE, FONT, mouse_pos)
            draw_interactive_button("+", buttons[f'{key}_plus'], COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_WHITE, FONT, mouse_pos)

        draw_interactive_button("Retour", back_button_rect, COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_WHITE, SETTINGS_FONT, mouse_pos)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(mouse_pos):
                    # Appliquer les paramètres en quittant
                    ROWS = temp_values['Lignes']
                    COLS = temp_values['Colonnes']
                    AI_THINK_TIME = temp_values['Temps IA']
                    update_dimensions() # Très important de mettre à jour les graphismes
                    running = False

                # Gérer les clics sur les boutons +/-
                if buttons['Lignes_minus'].collidepoint(mouse_pos): temp_values['Lignes'] = max(5, temp_values['Lignes'] - 1)
                if buttons['Lignes_plus'].collidepoint(mouse_pos): temp_values['Lignes'] = min(10, temp_values['Lignes'] + 1)
                if buttons['Colonnes_minus'].collidepoint(mouse_pos): temp_values['Colonnes'] = max(5, temp_values['Colonnes'] - 1)
                if buttons['Colonnes_plus'].collidepoint(mouse_pos): temp_values['Colonnes'] = min(10, temp_values['Colonnes'] + 1)
                if buttons['Temps IA_minus'].collidepoint(mouse_pos): temp_values['Temps IA'] = max(1.0, round(temp_values['Temps IA'] - 0.5, 1))
                if buttons['Temps IA_plus'].collidepoint(mouse_pos): temp_values['Temps IA'] = min(10.0, round(temp_values['Temps IA'] + 0.5, 1))

    return "home"

def game_loop():
    board = create_board()
    game_over = False
    turn = np.random.choice([0, 1])
    winning_pieces = None
    
    while True: # Boucle principale du jeu et de l'écran de fin
        mouse_pos = pygame.mouse.get_pos()
        
        draw_board(board, {'pieces': winning_pieces, 'alpha': int(128 + 127 * math.sin(pygame.time.get_ticks() / 200))} if winning_pieces else None)
        
        # Dessin de l'interface (jeton qui flotte, indicateur de tour)
        if not game_over:
            # Jeton flottant
            if turn == 0:
                posx = max(OFFSET_X, min(mouse_pos[0], OFFSET_X + BOARD_WIDTH))
                screen.blit(RED_TOKEN_IMG, RED_TOKEN_IMG.get_rect(center=(posx, OFFSET_Y + SQUARESIZE/2)))
            # Indicateur de tour
            label_text = "Votre Tour" if turn == 0 else "Tour de l'IA"
            label_color = COLOR_RED if turn == 0 else COLOR_YELLOW
            turn_label = SETTINGS_FONT.render(label_text, 1, label_color)
            turn_rect = turn_label.get_rect(center=(FULL_WIDTH/2, OFFSET_Y / 2 + 25))
            screen.blit(turn_label, turn_rect)
        else:
            # Message de fin de partie
            if winning_pieces:
                winner = board[winning_pieces[0][0]][winning_pieces[0][1]]
                message = "Vous avez gagné !" if winner == PLAYER_PIECE else "L'IA a gagné !"
                color = COLOR_RED if winner == PLAYER_PIECE else COLOR_YELLOW
            else: # Égalité
                message = "Égalité !"
                color = COLOR_WHITE
            
            end_label = FONT.render(message, 1, color)
            end_rect = end_label.get_rect(center=(FULL_WIDTH/2, OFFSET_Y / 2 + 25))
            screen.blit(end_label, end_rect)

        pygame.display.update()

        # Gestion des événements
        if game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN)) or event.type == pygame.MOUSEBUTTONDOWN:
                    return "home"
            continue

        # Logique de jeu (si pas terminé)
        if turn == 1:
            col = IA_Decision(board.copy(), AI_THINK_TIME)
            if col is not None and is_valid_move(board, col):
                row = get_next_open_row(board, col)
                animate_drop(board, row, col, AI_PIECE)
                board[row][col] = AI_PIECE
                if winning_move(board, AI_PIECE):
                    game_over = True
                    winning_pieces = find_winning_pieces(board)
                turn = 0
            else: # Si l'IA ne peut pas jouer (bug ou grille pleine)
                turn = 0 # Redonne la main au joueur
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return "home"
            
            if turn == 0 and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                posx = mouse_pos[0]
                if OFFSET_X < posx < OFFSET_X + BOARD_WIDTH:
                    col = int(math.floor((posx - OFFSET_X) / SQUARESIZE))
                    if is_valid_move(board, col):
                        row = get_next_open_row(board, col)
                        animate_drop(board, row, col, PLAYER_PIECE)
                        board[row][col] = PLAYER_PIECE
                        if winning_move(board, PLAYER_PIECE):
                            game_over = True
                            winning_pieces = find_winning_pieces(board)
                        turn = 1
        
        # Vérifier l'égalité
        if not game_over and len([c for c in range(COLS) if is_valid_move(board, c)]) == 0:
            game_over = True


if __name__ == '__main__':
    current_screen = "home"
    while current_screen != "quit":
        if current_screen == "home":
            current_screen = home_screen()
        elif current_screen == "settings":
            current_screen = settings_screen() # Simplifié
        elif current_screen == "play":
            current_screen = game_loop()
    
    pygame.quit()
    sys.exit() 